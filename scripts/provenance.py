#!/usr/bin/env python3
"""Derive host/workspace provenance from durable Lattice lifecycle events."""

from __future__ import annotations

import json
from typing import Any

from state_engine import StateStore


def claim_provenance(store: StateStore, lease_id: str) -> dict[str, Any]:
    """Return the durable host/workspace/action identity recorded for a lease claim."""
    row = store.conn.execute(
        """SELECT project_id, role, payload_json, created_at
           FROM events
           WHERE event_type = 'action_claimed' AND entity_type = 'lease' AND entity_id = ?
           ORDER BY id DESC LIMIT 1""",
        (lease_id,),
    ).fetchone()
    if row is None:
        return {}
    payload = json.loads(row["payload_json"] or "{}")
    return {
        "project_id": row["project_id"],
        "role": row["role"],
        "lease_id": lease_id,
        "actor": payload.get("actor"),
        "host": payload.get("host"),
        "workspace_id": payload.get("workspace_id"),
        "action_key": payload.get("action_key"),
        "action_kind": payload.get("action_kind"),
        "target_id": payload.get("target_id"),
        "claimed_at": row["created_at"],
    }


def completion_provenance(store: StateStore, lease_id: str) -> dict[str, Any]:
    """Join a claimed lease to its durable completion telemetry when available."""
    claim = claim_provenance(store, lease_id)
    completion = store.conn.execute(
        """SELECT event_type, entity_type, entity_id, role, payload_json, created_at
           FROM events
           WHERE entity_id <> ''
             AND event_type IN (
               'action_released', 'action_submitted', 'action_failed',
               'verification_recorded', 'milestone_acceptance_recorded',
               'commitment_fulfillment_recorded', 'exception_resolution_recorded'
             )
           ORDER BY id DESC"""
    ).fetchall()
    for row in completion:
        payload = json.loads(row["payload_json"] or "{}")
        if payload.get("lease_id") != lease_id:
            continue
        return {
            **claim,
            "completion_event": row["event_type"],
            "completion_entity_type": row["entity_type"],
            "completion_entity_id": row["entity_id"],
            "completed_by": row["role"],
            "completed_at": row["created_at"],
            "completion_payload": payload,
        }
    return claim
