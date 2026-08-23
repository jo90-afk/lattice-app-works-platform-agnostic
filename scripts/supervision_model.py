#!/usr/bin/env python3
"""Human supervision projection composed from canonical Lattice state."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
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
COMPLETION_EVENTS = {
    "action_released",
    "action_submitted",
    "action_failed",
    "verification_recorded",
    "milestone_acceptance_recorded",
    "commitment_fulfillment_recorded",
    "exception_resolution_recorded",
}


def _payload(value: str | None) -> dict[str, Any]:
    try:
        decoded = json.loads(value or "{}")
        return decoded if isinstance(decoded, dict) else {}
    except json.JSONDecodeError:
        return {}


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _age_seconds(value: str, now: datetime) -> int:
    return max(0, int((now - _parse_time(value)).total_seconds()))


def _remaining_seconds(value: str, now: datetime) -> int:
    return int((_parse_time(value) - now).total_seconds())


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


def _action_durations(store: StateStore, project_id: str | None) -> list[int]:
    clauses: list[str] = []
    values: list[Any] = []
    if project_id:
        clauses.append("project_id = ?")
        values.append(project_id)
    where = (" WHERE " + " AND ".join(clauses)) if clauses else ""
    rows = store.conn.execute(
        """SELECT id, project_id, event_type, entity_type, entity_id,
                  payload_json, created_at FROM events""" + where + " ORDER BY id",
        values,
    ).fetchall()
    claims: dict[str, datetime] = {}
    durations: list[int] = []
    completed_leases: set[str] = set()
    for row in rows:
        event_type = str(row["event_type"])
        if event_type == "action_claimed" and row["entity_type"] == "lease":
            claims[str(row["entity_id"])] = _parse_time(str(row["created_at"]))
            continue
        if event_type not in COMPLETION_EVENTS:
            continue
        lease_id = _payload(row["payload_json"]).get("lease_id")
        if not lease_id or lease_id in completed_leases or lease_id not in claims:
            continue
        duration = int((_parse_time(str(row["created_at"])) - claims[lease_id]).total_seconds())
        durations.append(max(0, duration))
        completed_leases.add(str(lease_id))
    return durations


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

    semantic_clauses = []
    semantic_values: list[Any] = []
    if project_id:
        semantic_clauses.append("project_id = ?")
        semantic_values.append(project_id)
    semantic_where = (" WHERE " + " AND ".join(semantic_clauses)) if semantic_clauses else ""
    retry_count = int(
        store.conn.execute(
            "SELECT COUNT(*) FROM events" + semantic_where +
            (" AND " if semantic_where else " WHERE ") + "event_type = 'condition_attempt_failed'",
            semantic_values,
        ).fetchone()[0]
    )
    exception_count = int(
        store.conn.execute(
            "SELECT COUNT(*) FROM events" + semantic_where +
            (" AND " if semantic_where else " WHERE ") + "event_type = 'exception_raised'",
            semantic_values,
        ).fetchone()[0]
    )

    review_clauses = []
    review_values: list[Any] = []
    if project_id:
        review_clauses.append("c.project_id = ?")
        review_values.append(project_id)
    review_where = (" WHERE " + " AND ".join(review_clauses)) if review_clauses else ""
    review_rows = store.conn.execute(
        """SELECT r.verdict FROM reviews r
           JOIN submissions s ON s.id = r.submission_id
           JOIN conditions c ON c.id = s.condition_id""" + review_where,
        review_values,
    ).fetchall()
    review_count = len(review_rows)
    negative_reviews = sum(
        1 for row in review_rows if str(row["verdict"]) in {"NOT_SATISFIED", "BLOCK"}
    )
    durations = _action_durations(store, project_id)

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
        "retries": retry_count,
        "exceptions_raised": exception_count,
        "reviews": review_count,
        "negative_reviews": negative_reviews,
        "verification_failure_rate": (negative_reviews / review_count) if review_count else None,
        "completed_action_durations_seconds": durations,
        "median_action_duration_seconds": int(median(durations)) if durations else None,
        "max_action_duration_seconds": max(durations) if durations else None,
    }


def _temporal_project_health(
    store: StateStore,
    project: dict[str, Any],
    now: datetime,
) -> dict[str, Any]:
    project_id = project["project"]["id"]
    for lease in project["active_leases"]:
        lease["age_seconds"] = _age_seconds(str(lease["created_at"]), now)
        lease["remaining_seconds"] = _remaining_seconds(str(lease["expires_at"]), now)
    for pending in project["pending_verification"]:
        pending["waiting_seconds"] = _age_seconds(str(pending["created_at"]), now)
    for exception in project["open_exceptions"]:
        exception["open_seconds"] = _age_seconds(str(exception["created_at"]), now)

    milestone = project.get("milestone")
    blocked_conditions: list[dict[str, Any]] = []
    if milestone:
        blocked_conditions = [
            dict(row)
            for row in store.conn.execute(
                """SELECT id, key, title, owner_role, verifier_role, severity,
                          attempt_count, attempt_budget, updated_at
                   FROM conditions
                   WHERE project_id = ? AND milestone_id = ? AND status = 'blocked'
                   ORDER BY updated_at, key""",
                (project_id, milestone["id"]),
            ).fetchall()
        ]
        for condition in blocked_conditions:
            condition["blocked_seconds"] = _age_seconds(str(condition["updated_at"]), now)

    waits = [lease["age_seconds"] for lease in project["active_leases"]]
    waits.extend(item["waiting_seconds"] for item in project["pending_verification"])
    waits.extend(item["open_seconds"] for item in project["open_exceptions"])
    waits.extend(item["blocked_seconds"] for item in blocked_conditions)
    return {
        "blocked_conditions": blocked_conditions,
        "oldest_attention_seconds": max(waits) if waits else None,
        "oldest_lease_seconds": max(
            (item["age_seconds"] for item in project["active_leases"]), default=None
        ),
        "oldest_verification_wait_seconds": max(
            (item["waiting_seconds"] for item in project["pending_verification"]), default=None
        ),
        "oldest_exception_seconds": max(
            (item["open_seconds"] for item in project["open_exceptions"]), default=None
        ),
        "oldest_blocked_condition_seconds": max(
            (item["blocked_seconds"] for item in blocked_conditions), default=None
        ),
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

    now = datetime.now(timezone.utc)
    for item in projects:
        item["consequence_graph"] = consequence_graph(store, item["project"]["id"])
        item["temporal_health"] = _temporal_project_health(store, item, now)

    active_projects = sum(1 for item in projects if item["project"]["status"] == "active")
    in_flight = sum(len(item["active_leases"]) for item in projects)
    ready_actions = sum(len(item["frontier"]) for item in projects)
    pending_verification = sum(len(item["pending_verification"]) for item in projects)
    open_exceptions = sum(len(item["open_exceptions"]) for item in projects)
    attention_ages = [
        item["temporal_health"]["oldest_attention_seconds"]
        for item in projects
        if item["temporal_health"]["oldest_attention_seconds"] is not None
    ]

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
            "oldest_attention_seconds": max(attention_ages) if attention_ages else None,
        },
        "recent_accepted_changes": _recent_changes(store, project_id),
        "operational_telemetry": _operational_telemetry(store, project_id),
    }
