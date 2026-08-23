#!/usr/bin/env python3
"""Recovery helpers for idempotent completion and artifact reconciliation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
        payload = json.loads(row["payload_json"] or "{}")
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
