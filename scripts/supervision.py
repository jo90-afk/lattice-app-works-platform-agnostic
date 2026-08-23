#!/usr/bin/env python3
"""Human-supervision projections derived from durable Lattice state."""

from __future__ import annotations

from typing import Any

from state_engine import StateStore


SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "note": 3}
TARGET_TABLES = {
    "condition": "conditions",
    "truth": "truths",
    "record": "records",
    "milestone": "milestones",
    "objective": "objectives",
    "commitment": "commitments",
    "exception": "exceptions",
}


def _project_context(store: StateStore, project_id: str) -> dict[str, Any]:
    project = dict(store._require_project(project_id))
    objective = store.conn.execute(
        "SELECT * FROM objectives WHERE project_id = ? AND status = 'active'",
        (project_id,),
    ).fetchone()
    milestone = store.conn.execute(
        "SELECT * FROM milestones WHERE project_id = ? AND status = 'active'",
        (project_id,),
    ).fetchone()
    return {
        "project": project,
        "active_objective": dict(objective) if objective else None,
        "active_milestone": dict(milestone) if milestone else None,
        "semantic_revision": store.project_revision(project_id),
    }


def _target_state(
    store: StateStore,
    project_id: str,
    target_type: str | None,
    target_id: str | None,
) -> dict[str, Any] | None:
    if not target_type or not target_id:
        return None
    table = TARGET_TABLES.get(target_type)
    if table is None:
        return {"type": target_type, "id": target_id, "state": None}
    row = store.conn.execute(
        f"SELECT * FROM {table} WHERE id = ? AND project_id = ?",
        (target_id, project_id),
    ).fetchone()
    return {
        "type": target_type,
        "id": target_id,
        "state": dict(row) if row else None,
    }


def _decision_evidence(
    store: StateStore,
    project_id: str,
    target_type: str | None,
    target_id: str | None,
    limit: int = 12,
) -> list[dict[str, Any]]:
    if not target_id:
        return []
    rows = store.conn.execute(
        """SELECT id, entity_type, entity_id, role, summary, source_ref,
                  content_hash, created_at
           FROM evidence
           WHERE project_id = ? AND entity_id = ?
           ORDER BY created_at DESC, id DESC LIMIT ?""",
        (project_id, target_id, limit),
    ).fetchall()
    evidence = [dict(row) for row in rows]

    if target_type == "condition" and len(evidence) < limit:
        linked = store.conn.execute(
            """SELECT e.id, e.entity_type, e.entity_id, e.role, e.summary,
                      e.source_ref, e.content_hash, e.created_at
               FROM evidence e
               LEFT JOIN submissions s
                 ON e.entity_type = 'submission' AND s.id = e.entity_id
               LEFT JOIN reviews r
                 ON e.entity_type = 'review' AND r.id = e.entity_id
               LEFT JOIN submissions rs ON rs.id = r.submission_id
               WHERE e.project_id = ?
                 AND (s.condition_id = ? OR rs.condition_id = ?)
               ORDER BY e.created_at DESC, e.id DESC LIMIT ?""",
            (project_id, target_id, target_id, limit - len(evidence)),
        ).fetchall()
        seen = {item["id"] for item in evidence}
        evidence.extend(dict(row) for row in linked if row["id"] not in seen)
    return evidence[:limit]


def _exception_choices(item: dict[str, Any]) -> list[dict[str, str]]:
    consequence = "The exception closes and its recorded resolution becomes durable project history."
    if item.get("target_type") == "condition" and item.get("target_id"):
        consequence += " If that condition is blocked, it returns to unmet with its attempt count reset for remediation."
    return [
        {
            "choice": "resolve",
            "label": "Resolve with an explicit recorded decision",
            "consequence": consequence,
        },
        {
            "choice": "leave_open",
            "label": "Leave unresolved",
            "consequence": "No state changes. The exception remains visible and continues blocking readiness when its severity or target makes it blocking.",
        },
    ]


def _commitment_choices(item: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "choice": "fulfill",
            "label": "Confirm fulfillment with a recorded summary",
            "consequence": "The commitment closes and fulfillment is recorded as durable project history.",
        },
        {
            "choice": "leave_open",
            "label": "Leave open",
            "consequence": "No state changes. The obligation remains open" + (" and continues blocking milestone readiness." if item.get("blocking") else "."),
        },
    ]


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

    project_contexts: dict[str, dict[str, Any]] = {}

    def context_for(pid: str) -> dict[str, Any]:
        if pid not in project_contexts:
            project_contexts[pid] = _project_context(store, pid)
        return project_contexts[pid]

    items: list[dict[str, Any]] = []
    for row in exception_rows:
        item = dict(row)
        context = context_for(item["project_id"])
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
                "decision_required": "Decide whether and how to resolve this exception: " + item["title"],
                "authority_reason": "This exception is explicitly marked principal_only; current agency authority does not permit an agent role to resolve it.",
                "affected_state": {
                    **context,
                    "target": _target_state(
                        store,
                        item["project_id"],
                        item.get("target_type"),
                        item.get("target_id"),
                    ),
                },
                "evidence": _decision_evidence(
                    store,
                    item["project_id"],
                    item.get("target_type"),
                    item.get("target_id"),
                ),
                "supported_choices": _exception_choices(item),
            }
        )
    for row in commitment_rows:
        item = dict(row)
        context = context_for(item["project_id"])
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
                "decision_required": "Confirm whether this Principal-owned commitment has been fulfilled: " + item["title"],
                "authority_reason": "The durable commitment is owned by the Principal; no agent role has authority to mark the Principal's obligation fulfilled.",
                "affected_state": {
                    **context,
                    "target": {"type": "commitment", "id": item["id"], "state": item},
                },
                "evidence": _decision_evidence(
                    store,
                    item["project_id"],
                    "commitment",
                    item["id"],
                ),
                "supported_choices": _commitment_choices(item),
            }
        )
    items.sort(key=lambda item: (-item["score"], item["created_at"], item["action_key"]))
    return {
        "count": len(items),
        "blocking_count": sum(1 for item in items if item["blocking"]),
        "items": items,
    }
