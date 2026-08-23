#!/usr/bin/env python3
"""Host-neutral control-plane adapter and read model for Lattice."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from state_engine import LatticeError, StateStore, utc_now


ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_EVENTS = {
    "action_claimed",
    "workspace_created",
    "workspace_abandoned",
    "policy_checked",
    "worker_failed",
    "worker_timed_out",
    "lease_expired",
    "recovery_completed",
}


def _decode(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def record_lifecycle_event(
    store: StateStore,
    *,
    project_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    role: str = "runtime",
    host: str | None = None,
    workspace_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist a host/runtime event without allowing it to rewrite project truth."""
    if event_type not in LIFECYCLE_EVENTS:
        raise LatticeError("Unsupported lifecycle event: " + event_type)
    store._require_project(project_id)
    event_payload = dict(payload or {})
    if host:
        event_payload["host"] = host
    if workspace_id:
        event_payload["workspace_id"] = workspace_id
    with store.conn:
        revision = store._bump_revision()
        store._event(
            revision,
            project_id,
            event_type,
            entity_type,
            entity_id,
            role,
            event_payload,
        )
    store.export_snapshot()
    return {
        "revision": revision,
        "project_id": project_id,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": event_payload,
    }


def recover_expired_leases(
    store: StateStore,
    project_id: str | None = None,
) -> dict[str, Any]:
    """Remove expired leases, retain an audit event, and recompute affected frontiers."""
    now = utc_now()
    parameters: tuple[Any, ...]
    where = "expires_at <= ?"
    parameters = (now,)
    if project_id:
        store._require_project(project_id)
        where += " AND project_id = ?"
        parameters = (now, project_id)
    expired = [
        dict(row)
        for row in store.conn.execute(
            "SELECT * FROM leases WHERE " + where + " ORDER BY project_id, expires_at, id",
            parameters,
        ).fetchall()
    ]
    if not expired:
        return {"recovered": 0, "leases": [], "frontiers": {}}

    by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with store.conn:
        for lease in expired:
            by_project[lease["project_id"]].append(lease)
            store.conn.execute("DELETE FROM leases WHERE id = ?", (lease["id"],))
            revision = store._bump_revision()
            store._event(
                revision,
                lease["project_id"],
                "lease_expired",
                "lease",
                lease["id"],
                "runtime",
                {
                    "action_key": lease["action_key"],
                    "action_kind": lease["action_kind"],
                    "target_id": lease["target_id"],
                    "leased_by": lease["leased_by"],
                    "expires_at": lease["expires_at"],
                },
            )
        for affected_project, leases in by_project.items():
            revision = store._bump_revision()
            store._event(
                revision,
                affected_project,
                "recovery_completed",
                "project",
                affected_project,
                "runtime",
                {"expired_lease_ids": [lease["id"] for lease in leases]},
            )
    store.export_snapshot()
    return {
        "recovered": len(expired),
        "leases": expired,
        "frontiers": {
            affected_project: store.frontier(affected_project, limit=10)
            for affected_project in sorted(by_project)
        },
    }


def claim_for_host(
    store: StateStore,
    *,
    project_id: str,
    role: str,
    actor: str,
    host: str,
    workspace_id: str | None = None,
    action_key: str | None = None,
    ttl_minutes: int | None = None,
) -> dict[str, Any]:
    """Recover stale work, claim one derived action, and persist the runtime boundary event."""
    recovery = recover_expired_leases(store, project_id)
    claimed = store.claim(project_id, role, actor, action_key, ttl_minutes)
    event = record_lifecycle_event(
        store,
        project_id=project_id,
        event_type="action_claimed",
        entity_type="lease",
        entity_id=claimed["lease_id"],
        role=role,
        host=host,
        workspace_id=workspace_id,
        payload={
            "actor": actor,
            "action_key": claimed["action"]["action_key"],
            "action_kind": claimed["action"]["kind"],
            "target_id": claimed["action"]["target_id"],
            "expires_at": claimed["expires_at"],
        },
    )
    claimed["control_revision"] = event["revision"]
    claimed["recovery"] = {"recovered": recovery["recovered"]}
    return claimed


def _project_read_model(store: StateStore, project: sqlite3.Row, frontier_limit: int) -> dict[str, Any]:
    project_id = project["id"]
    objective = store.conn.execute(
        "SELECT * FROM objectives WHERE project_id = ? AND status = 'active'",
        (project_id,),
    ).fetchone()
    milestone = store.conn.execute(
        "SELECT * FROM milestones WHERE project_id = ? AND status = 'active'",
        (project_id,),
    ).fetchone()
    leases = [
        dict(row)
        for row in store.conn.execute(
            "SELECT * FROM leases WHERE project_id = ? AND expires_at > ? ORDER BY created_at",
            (project_id, utc_now()),
        ).fetchall()
    ]
    pending_verification = [
        dict(row)
        for row in store.conn.execute(
            """SELECT s.id AS submission_id, s.summary, s.created_at,
                      c.id AS condition_id, c.key AS condition_key, c.title,
                      c.verifier_role
               FROM submissions s
               JOIN conditions c ON c.id = s.condition_id
               WHERE c.project_id = ? AND s.status = 'pending' AND c.status = 'candidate'
               ORDER BY s.created_at""",
            (project_id,),
        ).fetchall()
    ]
    exceptions = [
        dict(row)
        for row in store.conn.execute(
            """SELECT id, title, detail, severity, owner_role, principal_only,
                      target_type, target_id, created_at
               FROM exceptions
               WHERE project_id = ? AND status = 'open'
               ORDER BY CASE severity
                 WHEN 'critical' THEN 0 WHEN 'major' THEN 1 WHEN 'minor' THEN 2 ELSE 3 END,
                 created_at""",
            (project_id,),
        ).fetchall()
    ]
    truths = [
        dict(row)
        for row in store.conn.execute(
            """SELECT id, key, statement, epistemic_status, attention_state,
                      confidence, material, version, updated_at
               FROM truths
               WHERE project_id = ? AND attention_state = 'frontier'
               ORDER BY material DESC, updated_at DESC LIMIT 10""",
            (project_id,),
        ).fetchall()
    ]
    events = []
    for row in store.conn.execute(
        """SELECT revision, event_type, entity_type, entity_id, role,
                  payload_json, created_at
           FROM events WHERE project_id = ?
           ORDER BY revision DESC, id DESC LIMIT 12""",
        (project_id,),
    ).fetchall():
        item = dict(row)
        item["payload"] = _decode(item.pop("payload_json"), {})
        events.append(item)
    return {
        "project": dict(project),
        "objective": dict(objective) if objective else None,
        "milestone": dict(milestone) if milestone else None,
        "frontier": store.frontier(project_id, limit=frontier_limit),
        "active_leases": leases,
        "pending_verification": pending_verification,
        "open_exceptions": exceptions,
        "frontier_truths": truths,
        "recent_events": events,
    }


def read_model(
    store: StateStore,
    project_id: str | None = None,
    frontier_limit: int = 5,
) -> dict[str, Any]:
    """Return the stable control-surface projection without mutating state."""
    if frontier_limit < 1:
        raise LatticeError("frontier_limit must be at least 1")
    if project_id:
        projects = [store._require_project(project_id)]
    else:
        projects = store.conn.execute(
            "SELECT * FROM projects ORDER BY CASE status WHEN 'active' THEN 0 WHEN 'paused' THEN 1 ELSE 2 END, created_at, id"
        ).fetchall()
    return {
        "format": "lattice-control-read-model",
        "version": 1,
        "generated_at": utc_now(),
        "revision": store.revision,
        "projects": [_project_read_model(store, project, frontier_limit) for project in projects],
    }


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Operate Lattice's host-neutral control plane.")
    commands = result.add_subparsers(dest="command", required=True)

    inspect = commands.add_parser("inspect")
    inspect.add_argument("--project")
    inspect.add_argument("--frontier-limit", type=int, default=5)

    recover = commands.add_parser("recover")
    recover.add_argument("--project")

    claim = commands.add_parser("claim")
    claim.add_argument("--project", required=True)
    claim.add_argument("--role", required=True)
    claim.add_argument("--actor", required=True)
    claim.add_argument("--host", required=True)
    claim.add_argument("--workspace")
    claim.add_argument("--action-key")
    claim.add_argument("--ttl", type=int)

    event = commands.add_parser("event")
    event.add_argument("--project", required=True)
    event.add_argument("--event-type", required=True, choices=sorted(LIFECYCLE_EVENTS - {"action_claimed", "lease_expired", "recovery_completed"}))
    event.add_argument("--entity-type", required=True)
    event.add_argument("--entity-id", required=True)
    event.add_argument("--role", default="runtime")
    event.add_argument("--host")
    event.add_argument("--workspace")
    event.add_argument("--payload-json")

    return result


def main() -> int:
    args = parser().parse_args()
    try:
        with StateStore(ROOT) as store:
            if args.command == "inspect":
                emit(read_model(store, args.project, args.frontier_limit))
            elif args.command == "recover":
                emit(recover_expired_leases(store, args.project))
            elif args.command == "claim":
                emit(
                    claim_for_host(
                        store,
                        project_id=args.project,
                        role=args.role,
                        actor=args.actor,
                        host=args.host,
                        workspace_id=args.workspace,
                        action_key=args.action_key,
                        ttl_minutes=args.ttl,
                    )
                )
            elif args.command == "event":
                payload = json.loads(args.payload_json) if args.payload_json else {}
                if not isinstance(payload, dict):
                    raise LatticeError("--payload-json must decode to an object")
                emit(
                    record_lifecycle_event(
                        store,
                        project_id=args.project,
                        event_type=args.event_type,
                        entity_type=args.entity_type,
                        entity_id=args.entity_id,
                        role=args.role,
                        host=args.host,
                        workspace_id=args.workspace,
                        payload=payload,
                    )
                )
            else:
                raise LatticeError("Unsupported command: " + args.command)
    except (LatticeError, sqlite3.Error, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Lattice rejected the operation: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
