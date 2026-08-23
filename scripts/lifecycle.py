#!/usr/bin/env python3
"""Guarded action lifecycle wrappers for Lattice's host-neutral runtime."""

from __future__ import annotations

from typing import Any, Callable

from hooks import dispatch_hooks
from state_engine import LatticeError, StateStore


ACTION_EVENTS = {
    "action_released",
    "action_submitted",
    "action_failed",
    "verification_recorded",
    "milestone_acceptance_recorded",
    "commitment_fulfillment_recorded",
    "exception_resolution_recorded",
}


def _lease_context(store: StateStore, lease_id: str) -> dict[str, Any]:
    return dict(store._require_lease(lease_id))


def _record_committed_event(
    store: StateStore,
    *,
    project_id: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    role: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Record post-transition telemetry without making hook failure undo committed work."""
    if event_type not in ACTION_EVENTS:
        raise LatticeError("Unsupported action lifecycle event: " + event_type)
    semantic_revision = store.project_revision(project_id)
    with store.conn:
        store._event(
            semantic_revision,
            project_id,
            event_type,
            entity_type,
            entity_id,
            role,
            payload,
        )
        event_id = int(store.conn.execute("SELECT last_insert_rowid()").fetchone()[0])
    store.export_snapshot()
    envelope = {
        "event_id": event_id,
        "semantic_revision": semantic_revision,
        "project_id": project_id,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "payload": payload,
    }
    try:
        envelope["hooks"] = dispatch_hooks(store.root, event_type, envelope)
        envelope["hook_error"] = None
    except LatticeError as error:
        failure_payload = {
            "failed_event_type": event_type,
            "failed_event_id": event_id,
            "error": str(error),
            "committed": True,
        }
        with store.conn:
            store._event(
                semantic_revision,
                project_id,
                "hook_failed",
                "lifecycle_event",
                str(event_id),
                "runtime",
                failure_payload,
            )
        store.export_snapshot()
        envelope["hooks"] = []
        envelope["hook_error"] = str(error)
    return envelope


def _finish(
    store: StateStore,
    lease_id: str,
    role: str,
    operation: Callable[[], Any],
    *,
    event_type: str,
    entity_type: str,
    entity_id: Callable[[Any, dict[str, Any]], str],
    payload: Callable[[Any, dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    lease = _lease_context(store, lease_id)
    result = operation()
    event = _record_committed_event(
        store,
        project_id=lease["project_id"],
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id(result, lease),
        role=role,
        payload={
            "lease_id": lease_id,
            "action_key": lease["action_key"],
            "action_kind": lease["action_kind"],
            "target_id": lease["target_id"],
            **payload(result, lease),
        },
    )
    return {"result": result, "lifecycle": event}


def release_action(store: StateStore, lease_id: str, role: str) -> dict[str, Any]:
    lease = _lease_context(store, lease_id)
    store.release_lease(lease_id, role)
    event = _record_committed_event(
        store,
        project_id=lease["project_id"],
        event_type="action_released",
        entity_type="lease",
        entity_id=lease_id,
        role=role,
        payload={
            "lease_id": lease_id,
            "action_key": lease["action_key"],
            "action_kind": lease["action_kind"],
            "target_id": lease["target_id"],
        },
    )
    return {"released": lease_id, "lifecycle": event}


def submit_action(
    store: StateStore,
    lease_id: str,
    role: str,
    summary: str,
    artifact_refs: list[str],
    evidence_ref: str | None = None,
) -> dict[str, Any]:
    return _finish(
        store,
        lease_id,
        role,
        lambda: store.submit(lease_id, role, summary, artifact_refs, evidence_ref),
        event_type="action_submitted",
        entity_type="submission",
        entity_id=lambda result, _: str(result["id"]),
        payload=lambda result, _: {
            "condition_id": result["condition_id"],
            "attempt_no": result["attempt_no"],
        },
    )


def fail_action(store: StateStore, lease_id: str, role: str, summary: str) -> dict[str, Any]:
    return _finish(
        store,
        lease_id,
        role,
        lambda: store.fail_action(lease_id, role, summary),
        event_type="action_failed",
        entity_type="condition",
        entity_id=lambda _result, lease: str(lease["target_id"]),
        payload=lambda result, _: {"blocked": bool(result["blocked"]), "summary": summary},
    )


def review_action(
    store: StateStore,
    lease_id: str,
    role: str,
    verdict: str,
    summary: str,
    evidence_ref: str | None = None,
) -> dict[str, Any]:
    return _finish(
        store,
        lease_id,
        role,
        lambda: store.review(lease_id, role, verdict, summary, evidence_ref),
        event_type="verification_recorded",
        entity_type="review",
        entity_id=lambda result, _: str(result["review_id"]),
        payload=lambda result, _: {
            "verdict": verdict,
            "condition_id": result["condition"]["id"],
            "condition_status": result["condition"]["status"],
        },
    )


def advance_action(store: StateStore, lease_id: str, role: str, summary: str) -> dict[str, Any]:
    return _finish(
        store,
        lease_id,
        role,
        lambda: store.advance_milestone(lease_id, role, summary),
        event_type="milestone_acceptance_recorded",
        entity_type="milestone",
        entity_id=lambda result, _: str(result["accepted_milestone"]),
        payload=lambda result, _: {"next_milestone": result["next_milestone"], "summary": summary},
    )


def fulfill_commitment_action(
    store: StateStore, lease_id: str, role: str, summary: str
) -> dict[str, Any]:
    return _finish(
        store,
        lease_id,
        role,
        lambda: store.fulfill_commitment(lease_id, role, summary),
        event_type="commitment_fulfillment_recorded",
        entity_type="commitment",
        entity_id=lambda result, _: str(result["id"]),
        payload=lambda _result, _: {"summary": summary},
    )


def resolve_exception_action(
    store: StateStore, lease_id: str, role: str, resolution: str
) -> dict[str, Any]:
    return _finish(
        store,
        lease_id,
        role,
        lambda: store.resolve_exception(lease_id, role, resolution),
        event_type="exception_resolution_recorded",
        entity_type="exception",
        entity_id=lambda result, _: str(result["id"]),
        payload=lambda _result, _: {"resolution": resolution},
    )
