#!/usr/bin/env python3
"""Concurrency-safe hosted claim and lease-renewal primitives for Lattice 0.0.6."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from control_plane import record_lifecycle_event, recover_expired_leases
from state_backend import backend_for_store
from state_engine import LatticeError, StateStore, utc_now


def _parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def claim_for_host_atomic(
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
    """Acquire the backend's project write boundary before granting a lease."""
    recovery = recover_expired_leases(store, project_id)
    backend = backend_for_store(store)
    try:
        backend.begin_project_write(project_id)
        claimed = store.claim(project_id, role, actor, action_key, ttl_minutes)
    except Exception:
        backend.rollback()
        raise

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
                "atomic_claim": True,
                "state_backend": backend.name,
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
                "atomic_claim": True,
                "state_backend": backend.name,
            },
            run_hooks=False,
        )
        raise

    claimed["control_event_id"] = event["event_id"]
    claimed["control_revision"] = event["semantic_revision"]
    claimed["recovery"] = {"recovered": recovery["recovered"]}
    claimed["hooks"] = event["hooks"]
    claimed["atomic_claim"] = True
    claimed["state_backend"] = backend.name
    return claimed


def renew_host_lease(
    store: StateStore,
    *,
    project_id: str,
    lease_id: str,
    role: str,
    actor: str,
    host: str,
    workspace_id: str | None = None,
    ttl_minutes: int | None = None,
) -> dict[str, Any]:
    """Renew only the still-live lease owned by the same project, role, and actor."""
    ttl = ttl_minutes or int(store.policy["default_lease_minutes"])
    if ttl < 1:
        raise LatticeError("ttl_minutes must be at least 1")

    backend = backend_for_store(store)
    try:
        backend.begin_project_write(project_id)
        row = store.conn.execute("SELECT * FROM leases WHERE id = ?", (lease_id,)).fetchone()
        if row is None:
            raise LatticeError("Unknown or expired lease: " + lease_id)
        lease = dict(row)
        now_text = utc_now()
        if lease["expires_at"] <= now_text:
            store.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            backend.commit()
            raise LatticeError("Lease expired: " + lease_id)
        if lease["project_id"] != project_id:
            raise LatticeError("Lease project does not match renewal envelope")
        if lease["role"] != role:
            raise LatticeError("Only the leasing role may renew this action")
        if lease["leased_by"] != actor:
            raise LatticeError("Only the leasing actor may renew this action")

        now = datetime.now(timezone.utc).replace(microsecond=0)
        candidate = now + timedelta(minutes=ttl)
        current = _parse_utc(lease["expires_at"])
        expires = max(current, candidate).isoformat().replace("+00:00", "Z")
        store.conn.execute("UPDATE leases SET expires_at = ? WHERE id = ?", (expires, lease_id))
        backend.commit()
    except Exception:
        backend.rollback()
        raise

    semantic_revision = store.project_revision(project_id)
    payload = {
        "lease_id": lease_id,
        "action_key": lease["action_key"],
        "action_kind": lease["action_kind"],
        "target_id": lease["target_id"],
        "actor": actor,
        "previous_expires_at": lease["expires_at"],
        "expires_at": expires,
        "host": host,
        "state_backend": backend.name,
    }
    if workspace_id:
        payload["workspace_id"] = workspace_id
    with store.conn:
        store._event(
            semantic_revision,
            project_id,
            "lease_renewed",
            "lease",
            lease_id,
            role,
            payload,
        )
    store.export_snapshot()
    return {
        "lease_id": lease_id,
        "project_id": project_id,
        "role": role,
        "actor": actor,
        "expires_at": expires,
        "semantic_revision": semantic_revision,
        "state_backend": backend.name,
    }
