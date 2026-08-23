#!/usr/bin/env python3
"""Recovery helpers for idempotent completion and artifact reconciliation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from hooks import dispatch_hooks
from state_engine import LatticeError, StateStore


COMPLETION_EVENT_TYPES = {
    "action_released",
    "action_submitted",
    "action_failed",
    "verification_recorded",
    "milestone_acceptance_recorded",
    "commitment_fulfillment_recorded",
    "exception_resolution_recorded",
}
OUTCOME_EVENT_TYPES = {
    "release": "action_released",
    "submit": "action_submitted",
    "fail": "action_failed",
    "review": "verification_recorded",
    "advance": "milestone_acceptance_recorded",
    "commitment_fulfill": "commitment_fulfillment_recorded",
    "exception_resolve": "exception_resolution_recorded",
}
SEMANTIC_EVENT_TYPES = {
    "submit": "condition_submitted",
    "fail": "condition_attempt_failed",
    "review": "submission_reviewed",
    "advance": "milestone_accepted",
    "commitment_fulfill": "commitment_fulfilled",
    "exception_resolve": "exception_resolved",
}


def _payload(row: Any) -> dict[str, Any]:
    return json.loads(row["payload_json"] or "{}")


def _intent_hash(project_id: str, role: str, outcome: dict[str, Any]) -> str:
    encoded = json.dumps(
        {"project_id": project_id, "role": role, "outcome": outcome},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def completion_for_lease(store: StateStore, lease_id: str) -> dict[str, Any] | None:
    """Return the durable completion event for a lease, if one already committed."""
    rows = store.conn.execute(
        """SELECT id, revision, project_id, event_type, entity_type, entity_id,
                  role, payload_json, created_at
           FROM events
           WHERE event_type IN (?, ?, ?, ?, ?, ?, ?)
           ORDER BY id DESC""",
        tuple(sorted(COMPLETION_EVENT_TYPES)),
    ).fetchall()
    for row in rows:
        payload = _payload(row)
        if payload.get("lease_id") != lease_id:
            continue
        return {
            "event_id": int(row["id"]),
            "semantic_revision": int(row["revision"]),
            "project_id": row["project_id"],
            "event_type": row["event_type"],
            "entity_type": row["entity_type"],
            "entity_id": row["entity_id"],
            "role": row["role"],
            "payload": payload,
            "created_at": row["created_at"],
        }
    return None


def replay_completion(
    store: StateStore,
    *,
    lease_id: str,
    project_id: str,
    role: str,
) -> dict[str, Any] | None:
    completion = completion_for_lease(store, lease_id)
    if completion is None:
        return None
    if completion["project_id"] != project_id:
        raise LatticeError("Completion retry project does not match the committed lease result")
    if completion["role"] != role:
        raise LatticeError("Completion retry role does not match the committed lease result")
    return {
        "replayed": True,
        "already_committed": True,
        "completion": completion,
    }


def completion_start_for_lease(store: StateStore, lease_id: str) -> dict[str, Any] | None:
    row = store.conn.execute(
        """SELECT id, revision, project_id, event_type, entity_type, entity_id,
                  role, payload_json, created_at
           FROM events
           WHERE event_type = 'completion_started' AND entity_type = 'lease' AND entity_id = ?
           ORDER BY id DESC LIMIT 1""",
        (lease_id,),
    ).fetchone()
    if row is None:
        return None
    return {
        "event_id": int(row["id"]),
        "semantic_revision": int(row["revision"]),
        "project_id": row["project_id"],
        "role": row["role"],
        "payload": _payload(row),
        "created_at": row["created_at"],
    }


def begin_completion(
    store: StateStore,
    *,
    lease: dict[str, Any],
    outcome: dict[str, Any],
) -> dict[str, Any]:
    """Persist an operational intent marker immediately before semantic completion."""
    project_id = str(lease["project_id"])
    role = str(lease["role"])
    fingerprint = _intent_hash(project_id, role, outcome)
    existing = completion_start_for_lease(store, str(lease["id"]))
    if existing is not None:
        if existing["payload"].get("intent_hash") != fingerprint:
            raise LatticeError("A different completion intent is already recorded for this lease")
        return existing

    semantic_revision = store.project_revision(project_id)
    payload = {
        "lease_id": lease["id"],
        "action_key": lease["action_key"],
        "action_kind": lease["action_kind"],
        "target_id": lease["target_id"],
        "outcome_type": outcome["type"],
        "intent_hash": fingerprint,
    }
    with store.conn:
        store._event(
            semantic_revision,
            project_id,
            "completion_started",
            "lease",
            str(lease["id"]),
            role,
            payload,
        )
        event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
    store.export_snapshot()
    return {
        "event_id": event_id,
        "semantic_revision": semantic_revision,
        "project_id": project_id,
        "role": role,
        "payload": payload,
    }


def _matching_semantic_event(
    store: StateStore,
    *,
    start: dict[str, Any],
    outcome: dict[str, Any],
) -> Any | None:
    outcome_type = str(outcome["type"])
    semantic_type = SEMANTIC_EVENT_TYPES.get(outcome_type)
    if semantic_type is None:
        return None
    target_id = str(start["payload"]["target_id"])
    rows = store.conn.execute(
        """SELECT id, revision, project_id, event_type, entity_type, entity_id,
                  role, payload_json, created_at
           FROM events
           WHERE id > ? AND project_id = ? AND event_type = ? AND role = ?
           ORDER BY id""",
        (start["event_id"], start["project_id"], semantic_type, start["role"]),
    ).fetchall()
    for row in rows:
        payload = _payload(row)
        if outcome_type == "submit" and payload.get("condition_id") == target_id:
            return row
        if outcome_type == "review" and payload.get("submission_id") == target_id:
            return row
        if outcome_type in {"fail", "advance", "commitment_fulfill", "exception_resolve"}:
            if str(row["entity_id"]) == target_id:
                return row
    return None


def _lease_expired_after_start(store: StateStore, start: dict[str, Any]) -> Any | None:
    return store.conn.execute(
        """SELECT id, revision, project_id, event_type, entity_type, entity_id,
                  role, payload_json, created_at
           FROM events
           WHERE id > ? AND project_id = ? AND event_type = 'lease_expired'
             AND entity_id = ?
           ORDER BY id LIMIT 1""",
        (start["event_id"], start["project_id"], start["payload"]["lease_id"]),
    ).fetchone()


def _reconciled_payload(
    store: StateStore,
    start: dict[str, Any],
    outcome: dict[str, Any],
    semantic_event: Any | None,
) -> tuple[str, str, dict[str, Any]]:
    outcome_type = str(outcome["type"])
    target_id = str(start["payload"]["target_id"])
    payload = {
        "lease_id": start["payload"]["lease_id"],
        "action_key": start["payload"]["action_key"],
        "action_kind": start["payload"]["action_kind"],
        "target_id": target_id,
        "reconciled": True,
        "completion_started_event_id": start["event_id"],
    }
    entity_id = target_id
    entity_type = "lease" if outcome_type == "release" else start["payload"]["action_kind"]

    if semantic_event is not None:
        source_payload = _payload(semantic_event)
        payload["source_semantic_event_id"] = int(semantic_event["id"])
        if outcome_type == "submit":
            entity_type = "submission"
            entity_id = str(semantic_event["entity_id"])
            payload["condition_id"] = target_id
            payload["attempt_no"] = source_payload.get("attempt_no")
        elif outcome_type == "fail":
            entity_type = "condition"
            payload["blocked"] = source_payload.get("blocked")
            payload["summary"] = outcome.get("summary", "")
        elif outcome_type == "review":
            entity_type = "review"
            entity_id = str(semantic_event["entity_id"])
            payload["verdict"] = outcome.get("verdict")
            payload["condition_id"] = source_payload.get("condition_id")
        elif outcome_type == "advance":
            entity_type = "milestone"
            payload["next_milestone"] = source_payload.get("next_milestone")
            payload["summary"] = outcome.get("summary", "")
        elif outcome_type == "commitment_fulfill":
            entity_type = "commitment"
            payload["summary"] = outcome.get("summary", "")
        elif outcome_type == "exception_resolve":
            entity_type = "exception"
            payload["resolution"] = outcome.get("resolution", "")
    return entity_type, entity_id, payload


def _record_reconciled_completion(
    store: StateStore,
    *,
    start: dict[str, Any],
    outcome: dict[str, Any],
    semantic_event: Any | None,
) -> dict[str, Any]:
    event_type = OUTCOME_EVENT_TYPES[str(outcome["type"])]
    entity_type, entity_id, payload = _reconciled_payload(store, start, outcome, semantic_event)
    semantic_revision = store.project_revision(str(start["project_id"]))
    with store.conn:
        store._event(
            semantic_revision,
            str(start["project_id"]),
            event_type,
            entity_type,
            entity_id,
            str(start["role"]),
            payload,
        )
        event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
        store._event(
            semantic_revision,
            str(start["project_id"]),
            "completion_reconciled",
            "lifecycle_event",
            str(event_id),
            "runtime",
            {
                "lease_id": start["payload"]["lease_id"],
                "completion_event_id": event_id,
                "completion_started_event_id": start["event_id"],
            },
        )
    store.export_snapshot()

    envelope = {
        "event_id": event_id,
        "semantic_revision": semantic_revision,
        "project_id": str(start["project_id"]),
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": payload,
    }
    try:
        envelope["hooks"] = dispatch_hooks(store.root, event_type, envelope)
        envelope["hook_error"] = None
    except LatticeError as error:
        with store.conn:
            store._event(
                semantic_revision,
                str(start["project_id"]),
                "hook_failed",
                "lifecycle_event",
                str(event_id),
                "runtime",
                {
                    "failed_event_type": event_type,
                    "failed_event_id": event_id,
                    "error": str(error),
                    "committed": True,
                    "reconciled": True,
                },
            )
        store.export_snapshot()
        envelope["hooks"] = []
        envelope["hook_error"] = str(error)
    return envelope


def reconcile_interrupted_completion(
    store: StateStore,
    *,
    lease_id: str,
    project_id: str,
    role: str,
    outcome: dict[str, Any],
) -> dict[str, Any] | None:
    """Reconstruct final completion telemetry when semantic mutation committed before process loss."""
    start = completion_start_for_lease(store, lease_id)
    if start is None:
        return None
    if start["project_id"] != project_id or start["role"] != role:
        raise LatticeError("Completion retry does not match the recorded completion intent")
    if start["payload"].get("intent_hash") != _intent_hash(project_id, role, outcome):
        raise LatticeError("Completion retry outcome differs from the recorded completion intent")

    active_lease = store.conn.execute("SELECT 1 FROM leases WHERE id = ?", (lease_id,)).fetchone()
    if active_lease is not None:
        return None

    expired = _lease_expired_after_start(store, start)
    if expired is not None:
        raise LatticeError(
            "The lease expired after completion started but before a matching semantic transition committed; "
            "re-claim the current frontier instead of replaying the stale completion."
        )

    outcome_type = str(outcome["type"])
    semantic_event = _matching_semantic_event(store, start=start, outcome=outcome)
    if outcome_type != "release" and semantic_event is None:
        raise LatticeError(
            "Completion intent exists but no lease or matching semantic transition can be reconciled."
        )

    completion = _record_reconciled_completion(
        store,
        start=start,
        outcome=outcome,
        semantic_event=semantic_event,
    )
    return {
        "replayed": True,
        "already_committed": True,
        "reconciled": True,
        "completion": completion,
    }


def validate_project_artifacts(
    root: Path,
    project_id: str,
    artifact_refs: list[str],
) -> list[str]:
    """Require declared repo-local project artifacts to exist before state mutation."""
    root = root.resolve()
    project_root = (root / "projects" / project_id).resolve()
    prefix = f"projects/{project_id}/"
    verified: list[str] = []
    for ref in artifact_refs:
        if not isinstance(ref, str) or not ref.startswith(prefix):
            continue
        candidate = (root / ref).resolve()
        try:
            candidate.relative_to(project_root)
        except ValueError as error:
            raise LatticeError("Artifact reference escapes the project capsule: " + ref) from error
        if not candidate.is_file():
            raise LatticeError("Declared project artifact is not present in the repository: " + ref)
        verified.append(ref)
    return verified
