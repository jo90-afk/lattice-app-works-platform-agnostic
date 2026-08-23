#!/usr/bin/env python3
"""Guarded action lifecycle wrappers for Lattice's host-neutral runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable

from hooks import dispatch_hooks
from state_backend import backend_for_store
from state_engine import LatticeError, StateStore

ROOT = Path(__file__).resolve().parents[1]
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
    backend = backend_for_store(store)
    try:
        backend.begin_project_write(lease["project_id"])
        result = operation()
    except Exception:
        backend.rollback()
        raise
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
            "state_backend": backend.name,
            **payload(result, lease),
        },
    )
    return {"result": result, "lifecycle": event, "state_backend": backend.name}


def release_action(store: StateStore, lease_id: str, role: str) -> dict[str, Any]:
    lease = _lease_context(store, lease_id)
    backend = backend_for_store(store)
    try:
        backend.begin_project_write(lease["project_id"])
        store.release_lease(lease_id, role)
    except Exception:
        backend.rollback()
        raise
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
            "state_backend": backend.name,
        },
    )
    return {"released": lease_id, "lifecycle": event, "state_backend": backend.name}


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


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Complete a leased Lattice action with lifecycle telemetry.")
    commands = result.add_subparsers(dest="command", required=True)

    def leased(name: str) -> argparse.ArgumentParser:
        command = commands.add_parser(name)
        command.add_argument("--lease", required=True)
        command.add_argument("--role", required=True)
        return command

    leased("release")
    submit = leased("submit")
    submit.add_argument("--summary", required=True)
    submit.add_argument("--artifact", action="append", default=[])
    submit.add_argument("--evidence-ref")
    fail = leased("fail")
    fail.add_argument("--summary", required=True)
    review = leased("review")
    review.add_argument("--verdict", required=True, choices=("SATISFIED", "NOT_SATISFIED", "CONCUR", "BLOCK"))
    review.add_argument("--summary", required=True)
    review.add_argument("--evidence-ref")
    advance = leased("advance")
    advance.add_argument("--summary", required=True)
    fulfill = leased("commitment-fulfill")
    fulfill.add_argument("--summary", required=True)
    resolve = leased("exception-resolve")
    resolve.add_argument("--resolution", required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        with StateStore(ROOT) as store:
            if args.command == "release":
                value = release_action(store, args.lease, args.role)
            elif args.command == "submit":
                value = submit_action(store, args.lease, args.role, args.summary, args.artifact, args.evidence_ref)
            elif args.command == "fail":
                value = fail_action(store, args.lease, args.role, args.summary)
            elif args.command == "review":
                value = review_action(store, args.lease, args.role, args.verdict, args.summary, args.evidence_ref)
            elif args.command == "advance":
                value = advance_action(store, args.lease, args.role, args.summary)
            elif args.command == "commitment-fulfill":
                value = fulfill_commitment_action(store, args.lease, args.role, args.summary)
            elif args.command == "exception-resolve":
                value = resolve_exception_action(store, args.lease, args.role, args.resolution)
            else:
                raise LatticeError("Unsupported lifecycle command: " + str(args.command))
    except (LatticeError, KeyError, ValueError) as error:
        print("Lattice rejected the operation: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
