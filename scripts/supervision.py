#!/usr/bin/env python3
"""Human-supervision projections derived from durable Lattice state."""

from __future__ import annotations

from typing import Any

from state_engine import StateStore


SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "note": 3}


def principal_inbox(store: StateStore, project_id: str | None = None) -> dict[str, Any]:
    """Return only durable decisions that genuinely require the Principal."""
    clauses = ["status = 'open'", "principal_only = 1"]
    values: list[Any] = []
    if project_id:
        store._require_project(project_id)
        clauses.append("project_id = ?")
        values.append(project_id)
    exception_rows = store.conn.execute(
        "SELECT * FROM exceptions WHERE " + " AND ".join(clauses), values
    ).fetchall()

    commitment_clauses = ["status = 'open'", "owner_role = 'principal'"]
    commitment_values: list[Any] = []
    if project_id:
        commitment_clauses.append("project_id = ?")
        commitment_values.append(project_id)
    commitment_rows = store.conn.execute(
        "SELECT * FROM commitments WHERE " + " AND ".join(commitment_clauses),
        commitment_values,
    ).fetchall()

    items: list[dict[str, Any]] = []
    for row in exception_rows:
        item = dict(row)
        items.append(
            {
                "kind": "exception",
                "project_id": item["project_id"],
                "target_id": item["id"],
                "action_key": f"exception:{item['id']}:resolve:v{item['version']}",
                "title": item["title"],
                "detail": item["detail"],
                "severity": item["severity"],
                "blocking": item["severity"] in {"critical", "major"},
                "due_at": None,
                "created_at": item["created_at"],
                "score": 200 - 20 * SEVERITY_ORDER.get(item["severity"], 4),
            }
        )
    for row in commitment_rows:
        item = dict(row)
        items.append(
            {
                "kind": "commitment",
                "project_id": item["project_id"],
                "target_id": item["id"],
                "action_key": f"commitment:{item['id']}:fulfill:v{item['version']}",
                "title": item["title"],
                "detail": item["detail"],
                "severity": None,
                "blocking": bool(item["blocking"]),
                "due_at": item["due_at"],
                "created_at": item["created_at"],
                "score": int(item["priority"]) + (100 if item["blocking"] else 0),
            }
        )
    items.sort(key=lambda item: (-item["score"], item["created_at"], item["action_key"]))
    return {
        "count": len(items),
        "blocking_count": sum(1 for item in items if item["blocking"]),
        "items": items,
    }
