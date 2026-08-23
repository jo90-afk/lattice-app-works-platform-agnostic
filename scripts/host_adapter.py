#!/usr/bin/env python3
"""Execute versioned host-adapter envelopes against guarded Lattice state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from control_plane import claim_for_host, read_model, record_lifecycle_event, recover_expired_leases
from lifecycle import (
    advance_action,
    fail_action,
    fulfill_commitment_action,
    release_action,
    resolve_exception_action,
    review_action,
    submit_action,
)
from state_engine import LatticeError, StateStore


ROOT = Path(__file__).resolve().parents[1]
OPERATIONS = {"claim", "complete", "event", "inspect", "recover"}
EXTERNAL_EVENTS = {
    "workspace_created",
    "workspace_abandoned",
    "policy_checked",
    "worker_failed",
    "worker_timed_out",
}
OUTCOMES = {
    "release",
    "submit",
    "fail",
    "review",
    "advance",
    "commitment_fulfill",
    "exception_resolve",
}


def _required(envelope: dict[str, Any], *names: str) -> None:
    missing = [
        name for name in names
        if envelope.get(name) is None or envelope.get(name) == ""
    ]
    if missing:
        raise LatticeError("Host adapter envelope is missing: " + ", ".join(missing))


def validate_envelope(envelope: dict[str, Any]) -> None:
    if not isinstance(envelope, dict):
        raise LatticeError("Host adapter envelope must be an object")
    if envelope.get("format") != "lattice-host-adapter" or envelope.get("version") != 1:
        raise LatticeError("Unsupported host adapter format or version")
    operation = envelope.get("operation")
    if operation not in OPERATIONS:
        raise LatticeError("Unsupported host adapter operation: " + str(operation))
    if operation == "claim":
        _required(envelope, "project_id", "host", "actor", "role")
    elif operation == "complete":
        _required(envelope, "project_id", "host", "lease_id", "role", "outcome")
        outcome = envelope.get("outcome")
        if not isinstance(outcome, dict) or outcome.get("type") not in OUTCOMES:
            raise LatticeError("Unsupported host adapter completion outcome")
        outcome_type = outcome["type"]
        if outcome_type in {"submit", "fail", "advance", "commitment_fulfill"}:
            _required(outcome, "summary")
        elif outcome_type == "review":
            _required(outcome, "verdict", "summary")
            if outcome["verdict"] not in {"SATISFIED", "NOT_SATISFIED", "CONCUR", "BLOCK"}:
                raise LatticeError("Unsupported review verdict")
        elif outcome_type == "exception_resolve":
            _required(outcome, "resolution")
    elif operation == "event":
        _required(envelope, "project_id", "host", "event_type", "entity_type", "entity_id")
        if envelope["event_type"] not in EXTERNAL_EVENTS:
            raise LatticeError("Unsupported external lifecycle event: " + str(envelope["event_type"]))
    if envelope.get("frontier_limit") is not None and int(envelope["frontier_limit"]) < 1:
        raise LatticeError("frontier_limit must be at least 1")
    if envelope.get("ttl_minutes") is not None and int(envelope["ttl_minutes"]) < 1:
        raise LatticeError("ttl_minutes must be at least 1")


def _complete(store: StateStore, envelope: dict[str, Any]) -> dict[str, Any]:
    lease = dict(store._require_lease(str(envelope["lease_id"])))
    if lease["project_id"] != envelope["project_id"]:
        raise LatticeError("Completion envelope project does not match the leased action")
    if lease["role"] != envelope["role"]:
        raise LatticeError("Completion envelope role does not match the leased action")
    outcome = envelope["outcome"]
    outcome_type = outcome["type"]
    lease_id = str(envelope["lease_id"])
    role = str(envelope["role"])
    if outcome_type == "release":
        return release_action(store, lease_id, role)
    if outcome_type == "submit":
        return submit_action(
            store,
            lease_id,
            role,
            str(outcome["summary"]),
            list(outcome.get("artifact_refs") or []),
            outcome.get("evidence_ref"),
        )
    if outcome_type == "fail":
        return fail_action(store, lease_id, role, str(outcome["summary"]))
    if outcome_type == "review":
        return review_action(
            store,
            lease_id,
            role,
            str(outcome["verdict"]),
            str(outcome["summary"]),
            outcome.get("evidence_ref"),
        )
    if outcome_type == "advance":
        return advance_action(store, lease_id, role, str(outcome["summary"]))
    if outcome_type == "commitment_fulfill":
        return fulfill_commitment_action(store, lease_id, role, str(outcome["summary"]))
    if outcome_type == "exception_resolve":
        return resolve_exception_action(store, lease_id, role, str(outcome["resolution"]))
    raise LatticeError("Unsupported completion outcome: " + str(outcome_type))


def handle_envelope(store: StateStore, envelope: dict[str, Any]) -> dict[str, Any]:
    validate_envelope(envelope)
    operation = envelope["operation"]
    if operation == "claim":
        return claim_for_host(
            store,
            project_id=str(envelope["project_id"]),
            role=str(envelope["role"]),
            actor=str(envelope["actor"]),
            host=str(envelope["host"]),
            workspace_id=envelope.get("workspace_id"),
            action_key=envelope.get("action_key"),
            ttl_minutes=envelope.get("ttl_minutes"),
        )
    if operation == "complete":
        return _complete(store, envelope)
    if operation == "event":
        payload = envelope.get("payload") or {}
        if not isinstance(payload, dict):
            raise LatticeError("event payload must be an object")
        return record_lifecycle_event(
            store,
            project_id=str(envelope["project_id"]),
            event_type=str(envelope["event_type"]),
            entity_type=str(envelope["entity_type"]),
            entity_id=str(envelope["entity_id"]),
            role=str(envelope.get("role") or "runtime"),
            host=str(envelope["host"]),
            workspace_id=envelope.get("workspace_id"),
            payload=payload,
        )
    if operation == "inspect":
        return read_model(
            store,
            envelope.get("project_id"),
            int(envelope.get("frontier_limit") or 5),
        )
    if operation == "recover":
        return recover_expired_leases(store, envelope.get("project_id"))
    raise LatticeError("Unsupported host adapter operation: " + str(operation))


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute one Lattice host-adapter envelope.")
    parser.add_argument("--file", help="JSON envelope file; stdin is used when omitted")
    args = parser.parse_args()
    try:
        raw = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
        envelope = json.loads(raw)
        with StateStore(ROOT) as store:
            result = handle_envelope(store, envelope)
    except (OSError, json.JSONDecodeError, LatticeError, KeyError, ValueError, TypeError) as error:
        print("Lattice rejected the host envelope: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
