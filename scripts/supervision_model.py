#!/usr/bin/env python3
"""Human supervision projection composed from canonical Lattice state."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from control_plane import read_model
from project_graph import consequence_graph
from scheduler import parse_registry
from state_engine import StateStore
from supervision import principal_inbox


ACCEPTED_CHANGE_EVENTS = {
    "milestone_accepted",
    "submission_reviewed",
    "truth_recorded",
    "truth_revised",
    "truth_attention_changed",
    "record_created",
    "record_revised",
    "condition_added",
    "condition_submitted",
    "commitment_fulfilled",
    "exception_resolved",
}
OPERATIONAL_EVENTS = {
    "action_claimed",
    "action_released",
    "action_submitted",
    "action_failed",
    "verification_recorded",
    "milestone_acceptance_recorded",
    "lease_expired",
    "recovery_completed",
    "worker_failed",
    "worker_timed_out",
    "hook_failed",
    "claim_aborted",
}


def _payload(value: str | None) -> dict[str, Any]:
    try:
        decoded = json.loads(value or "{}")
        return decoded if isinstance(decoded, dict) else {}
    except json.JSONDecodeError:
        return {}


def _portfolio_order(root: Path, project_ids: list[str]) -> list[str]:
    registry = root / "portfolio" / "registry.md"
    if not registry.is_file():
        return project_ids
    registered, _capacity = parse_registry(registry)
    known = set(project_ids)
    ordered = [project_id for project_id in registered if project_id in known]
    seen = set(ordered)
    ordered.extend(project_id for project_id in project_ids if project_id not in seen)
    return ordered


def _recent_changes(store: StateStore, project_id: str | None, limit: int = 20) -> list[dict[str, Any]]:
    placeholders = ",".join("?" for _ in ACCEPTED_CHANGE_EVENTS)
    clauses = [f"event_type IN ({placeholders})"]
    values: list[Any] = list(sorted(ACCEPTED_CHANGE_EVENTS))
    if project_id:
        clauses.append("project_id = ?")
        values.append(project_id)
    rows = store.conn.execute(
        """SELECT id, revision, project_id, event_type, entity_type, entity_id,
                  role, payload_json, created_at
           FROM events WHERE """ + " AND ".join(clauses) +
        " ORDER BY id DESC LIMIT ?",
        (*values, limit),
    ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        item["payload"] = _payload(item.pop("payload_json", None))
        result.append(item)
    return result


def _operational_telemetry(store: StateStore, project_id: str | None) -> dict[str, Any]:
    placeholders = ",".join("?" for _ in OPERATIONAL_EVENTS)
    clauses = [f"event_type IN ({placeholders})"]
    values: list[Any] = list(sorted(OPERATIONAL_EVENTS))
    if project_id:
        clauses.append("project_id = ?")
        values.append(project_id)
    rows = store.conn.execute(
        """SELECT event_type, payload_json, created_at
           FROM events WHERE """ + " AND ".join(clauses) + " ORDER BY id DESC",
        values,
    ).fetchall()
    counts = Counter(str(row["event_type"]) for row in rows)
    hosts = Counter()
    for row in rows:
        host = _payload(row["payload_json"]).get("host")
        if host:
            hosts[str(host)] += 1
    completed = (
        counts["action_submitted"]
        + counts["action_failed"]
        + counts["verification_recorded"]
        + counts["milestone_acceptance_recorded"]
        + counts["action_released"]
    )
    return {
        "event_counts": dict(sorted(counts.items())),
        "hosts": dict(sorted(hosts.items())),
        "claims": counts["action_claimed"],
        "completed_transitions": completed,
        "recoveries": counts["recovery_completed"],
        "expired_leases": counts["lease_expired"],
        "worker_failures": counts["worker_failed"] + counts["worker_timed_out"],
        "hook_failures": counts["hook_failed"],
        "claim_aborts": counts["claim_aborted"],
    }


def supervision_model(
    store: StateStore,
    project_id: str | None = None,
    frontier_limit: int = 5,
) -> dict[str, Any]:
    """Compose one read-only model sufficient for Principal supervision."""
    control = read_model(store, project_id, frontier_limit)
    inbox = principal_inbox(store, project_id)
    projects = control["projects"]

    if not project_id:
        by_id = {item["project"]["id"]: item for item in projects}
        ordered_ids = _portfolio_order(store.root, list(by_id))
        projects = [by_id[project] for project in ordered_ids]

    for item in projects:
        item["consequence_graph"] = consequence_graph(store, item["project"]["id"])

    active_projects = sum(1 for item in projects if item["project"]["status"] == "active")
    in_flight = sum(len(item["active_leases"]) for item in projects)
    ready_actions = sum(len(item["frontier"]) for item in projects)
    pending_verification = sum(len(item["pending_verification"]) for item in projects)
    open_exceptions = sum(len(item["open_exceptions"]) for item in projects)

    return {
        **control,
        "projects": projects,
        "state_backend": getattr(store, "state_backend_name", "sqlite"),
        "principal_inbox": inbox,
        "portfolio": {
            "active_projects": active_projects,
            "projects_shown": len(projects),
            "ready_actions": ready_actions,
            "in_flight": in_flight,
            "pending_verification": pending_verification,
            "open_exceptions": open_exceptions,
            "principal_decisions": inbox["count"],
            "blocking_principal_decisions": inbox["blocking_count"],
        },
        "recent_accepted_changes": _recent_changes(store, project_id),
        "operational_telemetry": _operational_telemetry(store, project_id),
    }
