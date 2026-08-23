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

from hooks import dispatch_hooks
from state_engine import LatticeError, StateStore, utc_now


ROOT = Path(__file__).resolve().parents[1]
LIFECYCLE_EVENTS = {
    "action_claimed",
    "claim_aborted",
    "workspace_created",
    "workspace_abandoned",
    "policy_checked",
    "worker_failed",
    "worker_timed_out",
    "lease_expired",
    "recovery_completed",
    "hook_failed",
}
INTERNAL_LIFECYCLE_EVENTS = {
    "action_claimed",
    "claim_aborted",
    "lease_expired",
    "recovery_completed",
    "hook_failed",
}


def _decode(value: str | None, fallback: Any) -> Any:
    if not value:
        return fallback
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return fallback


def _event_sequence(store: StateStore) -> int:
    row = store.conn.execute("SELECT COALESCE(MAX(id), 0) FROM events").fetchone()
    return int(row[0])


def _claim_runtime_context(store: StateStore, lease_id: str) -> dict[str, Any]:
    row = store.conn.execute(
        """SELECT payload_json FROM events
           WHERE event_type = 'action_claimed' AND entity_type = 'lease' AND entity_id = ?
           ORDER BY id DESC LIMIT 1""",
        (lease_id,),
    ).fetchone()
    return _decode(row["payload_json"], {}) if row else {}


def _workspace_already_abandoned(store: StateStore, project_id: str, workspace_id: str) -> bool:
    return store.conn.execute(
        """SELECT 1 FROM events
           WHERE project_id = ? AND event_type = 'workspace_abandoned'
             AND entity_type = 'workspace' AND entity_id = ?
           LIMIT 1""",
        (project_id, workspace_id),
    ).fetchone() is not None


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
    run_hooks: bool = True,
) -> dict[str, Any]:
    """Persist operational telemetry without advancing semantic project revision."""
    if event_type not in LIFECYCLE_EVENTS:
        raise LatticeError("Unsupported lifecycle event: " + event_type)
    store._require_project(project_id)
    event_payload = dict(payload or {})
    if host:
        event_payload["host"] = host
    if workspace_id:
        event_payload["workspace_id"] = workspace_id

    semantic_revision = store.project_revision(project_id)
    with store.conn:
        store._event(
            semantic_revision,
            project_id,
            event_type,
            entity_type,
            entity_id,
            role,
            event_payload,
        )
        event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
    store.export_snapshot()

    result = {
        "event_id": event_id,
        "revision": semantic_revision,
        "semantic_revision": semantic_revision,
        "project_id": project_id,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": event_payload,
    }
    if not run_hooks:
        result["hooks"] = []
        return result

    try:
        result["hooks"] = dispatch_hooks(store.root, event_type, result)
    except LatticeError as error:
        record_lifecycle_event(
            store,
            project_id=project_id,
            event_type="hook_failed",
            entity_type="lifecycle_event",
            entity_id=str(event_id),
            role="runtime",
            host=host,
            workspace_id=workspace_id,
            payload={
                "failed_event_type": event_type,
                "failed_event_id": event_id,
                "error": str(error),
            },
            run_hooks=False,
        )
        raise
    return result


def recover_expired_leases(store: StateStore, project_id: str | None = None) -> dict[str, Any]:
    now = utc_now()
    where = "expires_at <= ?"
    parameters: tuple[Any, ...] = (now,)
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
        return {"recovered": 0, "leases": [], "frontiers": {}, "hook_results": [], "abandoned_workspaces": []}

    by_project: dict[str, list[dict[str, Any]]] = defaultdict(list)
    abandoned_by_project: dict[str, list[str]] = defaultdict(list)
    envelopes: list[dict[str, Any]] = []
    with store.conn:
        for lease in expired:
            project = lease["project_id"]
            by_project[project].append(lease)
            runtime_context = _claim_runtime_context(store, lease["id"])
            workspace_id = runtime_context.get("workspace_id")
            host = runtime_context.get("host")
            semantic_revision = store.project_revision(project)

            if workspace_id and not _workspace_already_abandoned(store, project, str(workspace_id)):
                workspace_payload = {
                    "lease_id": lease["id"],
                    "action_key": lease["action_key"],
                    "reason": "lease_expired",
                }
                if host:
                    workspace_payload["host"] = host
                workspace_payload["workspace_id"] = workspace_id
                store._event(
                    semantic_revision,
                    project,
                    "workspace_abandoned",
                    "workspace",
                    str(workspace_id),
                    "runtime",
                    workspace_payload,
                )
                workspace_event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
                abandoned_by_project[project].append(str(workspace_id))
                envelopes.append(
                    {
                        "event_id": workspace_event_id,
                        "revision": semantic_revision,
                        "semantic_revision": semantic_revision,
                        "project_id": project,
                        "event_type": "workspace_abandoned",
                        "entity_type": "workspace",
                        "entity_id": str(workspace_id),
                        "payload": workspace_payload,
                    }
                )

            store.conn.execute("DELETE FROM leases WHERE id = ?", (lease["id"],))
            payload = {
                "action_key": lease["action_key"],
                "action_kind": lease["action_kind"],
                "target_id": lease["target_id"],
                "leased_by": lease["leased_by"],
                "expires_at": lease["expires_at"],
            }
            if host:
                payload["host"] = host
            if workspace_id:
                payload["workspace_id"] = workspace_id
            store._event(
                semantic_revision,
                project,
                "lease_expired",
                "lease",
                lease["id"],
                "runtime",
                payload,
            )
            event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
            envelopes.append(
                {
                    "event_id": event_id,
                    "revision": semantic_revision,
                    "semantic_revision": semantic_revision,
                    "project_id": project,
                    "event_type": "lease_expired",
                    "entity_type": "lease",
                    "entity_id": lease["id"],
                    "payload": payload,
                }
            )
        for affected_project, leases in by_project.items():
            semantic_revision = store.project_revision(affected_project)
            payload = {
                "expired_lease_ids": [lease["id"] for lease in leases],
                "abandoned_workspace_ids": abandoned_by_project.get(affected_project, []),
            }
            store._event(
                semantic_revision,
                affected_project,
                "recovery_completed",
                "project",
                affected_project,
                "runtime",
                payload,
            )
            event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
            envelopes.append(
                {
                    "event_id": event_id,
                    "revision": semantic_revision,
                    "semantic_revision": semantic_revision,
                    "project_id": affected_project,
                    "event_type": "recovery_completed",
                    "entity_type": "project",
                    "entity_id": affected_project,
                    "payload": payload,
                }
            )
    store.export_snapshot()

    hook_results = []
    for envelope in envelopes:
        try:
            results = dispatch_hooks(store.root, envelope["event_type"], envelope)
        except LatticeError as error:
            record_lifecycle_event(
                store,
                project_id=envelope["project_id"],
                event_type="hook_failed",
                entity_type="lifecycle_event",
                entity_id=str(envelope["event_id"]),
                role="runtime",
                payload={
                    "failed_event_type": envelope["event_type"],
                    "failed_event_id": envelope["event_id"],
                    "error": str(error),
                },
                run_hooks=False,
            )
            raise
        hook_results.append(
            {
                "event_type": envelope["event_type"],
                "entity_id": envelope["entity_id"],
                "results": results,
            }
        )

    return {
        "recovered": len(expired),
        "leases": expired,
        "abandoned_workspaces": [
            {"project_id": pid, "workspace_id": workspace_id}
            for pid in sorted(abandoned_by_project)
            for workspace_id in abandoned_by_project[pid]
        ],
        "frontiers": {
            pid: store.frontier(pid, limit=10) for pid in sorted(by_project)
        },
        "hook_results": hook_results,
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
    recovery = recover_expired_leases(store, project_id)
    claimed = store.claim(project_id, role, actor, action_key, ttl_minutes)
    try:
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
    except LatticeError as error:
        store.release_lease(claimed["lease_id"], role)
        record_lifecycle_event(
            store,
            project_id=project_id,
            event_type="claim_aborted",
            entity_type="lease",
            entity_id=claimed["lease_id"],
            role="runtime",
            host=host,
            workspace_id=workspace_id,
            payload={
                "actor": actor,
                "action_key": claimed["action"]["action_key"],
                "reason": "post-claim hook failed",
                "error": str(error),
            },
            run_hooks=False,
        )
        raise

    claimed["control_event_id"] = event["event_id"]
    claimed["control_revision"] = event["semantic_revision"]
    claimed["recovery"] = {"recovered": recovery["recovered"]}
    claimed["hooks"] = event["hooks"]
    return claimed


def _project_read_model(
    store: StateStore, project: sqlite3.Row, frontier_limit: int
) -> dict[str, Any]:
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
                      c.id AS condition_id, c.key AS condition_key, c.title, c.verifier_role
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
        """SELECT id, revision, event_type, entity_type, entity_id, role,
                  payload_json, created_at
           FROM events WHERE project_id = ?
           ORDER BY id DESC LIMIT 12""",
        (project_id,),
    ).fetchall():
        item = dict(row)
        item["payload"] = _decode(item.pop("payload_json"), {})
        events.append(item)
    return {
        "project": dict(project),
        "semantic_revision": store.project_revision(project_id),
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
    store: StateStore, project_id: str | None = None, frontier_limit: int = 5
) -> dict[str, Any]:
    if frontier_limit < 1:
        raise LatticeError("frontier_limit must be at least 1")
    projects = (
        [store._require_project(project_id)]
        if project_id
        else store.conn.execute(
            """SELECT * FROM projects
               ORDER BY CASE status WHEN 'active' THEN 0 WHEN 'paused' THEN 1 ELSE 2 END,
               created_at, id"""
        ).fetchall()
    )
    return {
        "format": "lattice-control-read-model",
        "version": 1,
        "generated_at": utc_now(),
        "revision": store.revision,
        "event_sequence": _event_sequence(store),
        "projects": [
            _project_read_model(store, project, frontier_limit) for project in projects
        ],
    }


def emit(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Operate Lattice's host-neutral control plane."
    )
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
    event.add_argument(
        "--event-type",
        required=True,
        choices=sorted(LIFECYCLE_EVENTS - INTERNAL_LIFECYCLE_EVENTS),
    )
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