#!/usr/bin/env python3
"""Concurrency-safe semantic writes that require an explicit observed version."""

from __future__ import annotations

from typing import Any

from state_backend import backend_for_store
from state_engine import LatticeError, StateStore


def revise_truth_cas(
    store: StateStore,
    *,
    truth_id: str,
    changed_by: str,
    reason: str,
    expected_version: int,
    statement: str | None = None,
    epistemic_status: str | None = None,
    confidence: float | None = None,
    source_ref: str | None = None,
    material: bool | None = None,
) -> dict[str, Any]:
    """Revise a truth only if it is still the exact version the caller observed."""
    if expected_version < 1:
        raise LatticeError("expected_version must be at least 1")
    observed = store.conn.execute(
        "SELECT project_id FROM truths WHERE id = ?", (truth_id,)
    ).fetchone()
    if observed is None:
        raise LatticeError("Unknown truth: " + truth_id)
    project_id = str(observed["project_id"])
    backend = backend_for_store(store)
    try:
        backend.begin_project_write(project_id)
        current = store.conn.execute(
            "SELECT version FROM truths WHERE id = ?", (truth_id,)
        ).fetchone()
        if current is None:
            raise LatticeError("Unknown truth: " + truth_id)
        current_version = int(current["version"])
        if current_version != expected_version:
            raise LatticeError(
                f"Truth {truth_id} changed: expected version {expected_version}, current {current_version}"
            )
        result = store.revise_truth(
            truth_id,
            changed_by,
            reason,
            statement,
            epistemic_status,
            confidence,
            source_ref,
            material,
        )
    except Exception:
        backend.rollback()
        raise
    return {
        "truth": result,
        "previous_version": expected_version,
        "version": int(result["version"]),
        "state_backend": backend.name,
    }
