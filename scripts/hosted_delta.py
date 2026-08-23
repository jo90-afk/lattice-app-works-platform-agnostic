#!/usr/bin/env python3
"""Serialized acceptance for revision-guarded hosted state deltas."""

from __future__ import annotations

from typing import Any

from concurrency import claim_for_host_atomic
from recovery import validate_project_artifacts
from state_backend import backend_for_store
from state_engine import LatticeError, StateStore
from write_ownership import validate_artifact_ownership


def _validate_delta(delta: dict[str, Any]) -> tuple[str, str, str, dict[str, Any], int]:
    if delta.get("format") != "lattice-state-delta" or delta.get("schema_version") != 1:
        raise LatticeError("Unsupported hosted state delta")
    project_id = str(delta.get("project_id") or "")
    role = str(delta.get("role") or "")
    action_key = str(delta.get("action_key") or "")
    if not project_id or not role or not action_key:
        raise LatticeError("Hosted delta requires project_id, role, and action_key")
    try:
        base_revision = int(delta["base_revision"])
    except (KeyError, TypeError, ValueError) as error:
        raise LatticeError("Hosted delta requires an integer base_revision") from error
    outcome = delta.get("outcome") or {}
    if not isinstance(outcome, dict):
        raise LatticeError("Hosted delta outcome must be an object")
    return project_id, role, action_key, outcome, base_revision


def _complete_under_guard(
    store: StateStore,
    *,
    lease_id: str,
    project_id: str,
    role: str,
    outcome: dict[str, Any],
    base_revision: int,
) -> dict[str, Any]:
    backend = backend_for_store(store)
    try:
        backend.begin_project_write(project_id)
        current_revision = store.project_revision(project_id)
        if current_revision != base_revision:
            store.release_lease(lease_id, role)
            raise LatticeError(
                f"Hosted delta is stale for {project_id}: base {base_revision}, current {current_revision}"
            )

        outcome_type = outcome.get("type")
        if outcome_type == "submit":
            result = store.submit(
                lease_id,
                role,
                str(outcome.get("summary", "")),
                list(outcome.get("artifact_refs") or []),
                outcome.get("evidence_ref"),
            )
        elif outcome_type == "review":
            result = store.review(
                lease_id,
                role,
                str(outcome["verdict"]),
                str(outcome.get("summary", "")),
                outcome.get("evidence_ref"),
            )
        elif outcome_type == "advance":
            result = store.advance_milestone(
                lease_id, role, str(outcome.get("summary", ""))
            )
        elif outcome_type == "fail":
            result = store.fail_action(
                lease_id, role, str(outcome.get("summary", ""))
            )
        elif outcome_type == "resolve_exception":
            result = store.resolve_exception(
                lease_id, role, str(outcome.get("resolution", ""))
            )
        elif outcome_type == "fulfill_commitment":
            result = store.fulfill_commitment(
                lease_id, role, str(outcome.get("summary", ""))
            )
        else:
            store.release_lease(lease_id, role)
            raise LatticeError("Unsupported hosted delta outcome: " + str(outcome_type))
    except Exception:
        backend.rollback()
        raise
    return {
        "result": result,
        "base_revision": base_revision,
        "accepted_revision": store.project_revision(project_id),
        "state_backend": backend.name,
    }


def apply_delta_serialized(store: StateStore, delta: dict[str, Any]) -> dict[str, Any]:
    """Accept one hosted delta with a serialized base-revision check at commit time.

    The claim is durable coordination state, not semantic project state. After the
    claim succeeds, the project backend lock is acquired again and base_revision is
    rechecked immediately before the semantic transition. Competing deltas from the
    same old revision therefore cannot both commit, even when they target different
    frontier actions.
    """
    project_id, role, action_key, outcome, base_revision = _validate_delta(delta)
    store._require_project(project_id)
    current_revision = store.project_revision(project_id)
    if current_revision != base_revision:
        raise LatticeError(
            f"Hosted delta is stale for {project_id}: base {base_revision}, current {current_revision}"
        )

    if outcome.get("type") == "submit":
        artifact_refs = list(outcome.get("artifact_refs") or [])
        validate_artifact_ownership(store.root, project_id, role, artifact_refs)
        validate_project_artifacts(store.root, project_id, artifact_refs)

    actor = str(delta.get("actor") or ("hosted-" + role))
    claim = claim_for_host_atomic(
        store,
        project_id=project_id,
        role=role,
        actor=actor,
        host=str(delta.get("host") or "hosted-delta"),
        workspace_id=delta.get("workspace_id"),
        action_key=action_key,
    )
    return _complete_under_guard(
        store,
        lease_id=claim["lease_id"],
        project_id=project_id,
        role=role,
        outcome=outcome,
        base_revision=base_revision,
    )
