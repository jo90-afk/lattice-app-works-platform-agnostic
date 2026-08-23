#!/usr/bin/env python3
"""Host-neutral semantic fingerprints for bounded Lattice evaluation runs."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from state_engine import StateStore


def _json(value: str | None, default: Any) -> Any:
    try:
        decoded = json.loads(value or "")
        return decoded
    except json.JSONDecodeError:
        return default


def _hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def semantic_state(store: StateStore, project_id: str) -> dict[str, Any]:
    """Return stable project meaning, excluding runtime/generated identity and time."""
    project = dict(store._require_project(project_id))
    objectives = [
        dict(row)
        for row in store.conn.execute(
            "SELECT id, title, description, status, priority, owner_role FROM objectives WHERE project_id = ? ORDER BY id",
            (project_id,),
        ).fetchall()
    ]
    milestones = [
        dict(row)
        for row in store.conn.execute(
            "SELECT id, objective_id, title, ordinal, status FROM milestones WHERE project_id = ? ORDER BY ordinal, id",
            (project_id,),
        ).fetchall()
    ]
    records = [
        dict(row)
        for row in store.conn.execute(
            "SELECT key, kind, title, body, status, version, owner_role, source_ref, content_hash FROM records WHERE project_id = ? ORDER BY key",
            (project_id,),
        ).fetchall()
    ]
    truths = [
        dict(row)
        for row in store.conn.execute(
            "SELECT key, statement, epistemic_status, attention_state, confidence, source_ref, material, version, created_by FROM truths WHERE project_id = ? ORDER BY key",
            (project_id,),
        ).fetchall()
    ]
    truth_links = [
        dict(row)
        for row in store.conn.execute(
            """SELECT f.key AS from_key, t.key AS to_key, l.relation
               FROM truth_links l
               JOIN truths f ON f.id = l.from_truth_id
               JOIN truths t ON t.id = l.to_truth_id
               WHERE f.project_id = ? AND t.project_id = ?
               ORDER BY f.key, t.key, l.relation""",
            (project_id, project_id),
        ).fetchall()
    ]
    conditions = [
        dict(row)
        for row in store.conn.execute(
            """SELECT id, objective_id, milestone_id, key, title, description, owner_role,
                      verifier_role, priority, severity, status, state_version,
                      attempt_count, attempt_budget
               FROM conditions WHERE project_id = ? ORDER BY key""",
            (project_id,),
        ).fetchall()
    ]
    condition_inputs = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, r.key AS record_key, ci.accepted_record_version
               FROM condition_inputs ci
               JOIN conditions c ON c.id = ci.condition_id
               JOIN records r ON r.id = ci.record_id
               WHERE c.project_id = ? ORDER BY c.key, r.key""",
            (project_id,),
        ).fetchall()
    ]
    condition_truths = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, t.key AS truth_key,
                      ct.accepted_truth_version, ct.relevance
               FROM condition_truths ct
               JOIN conditions c ON c.id = ct.condition_id
               JOIN truths t ON t.id = ct.truth_id
               WHERE c.project_id = ? ORDER BY c.key, t.key""",
            (project_id,),
        ).fetchall()
    ]
    dependencies = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, d.key AS depends_on_key,
                      cd.accepted_state_version
               FROM condition_dependencies cd
               JOIN conditions c ON c.id = cd.condition_id
               JOIN conditions d ON d.id = cd.depends_on_condition_id
               WHERE c.project_id = ? ORDER BY c.key, d.key""",
            (project_id,),
        ).fetchall()
    ]
    reviewers = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, cr.role, cr.review_kind
               FROM condition_reviewers cr
               JOIN conditions c ON c.id = cr.condition_id
               WHERE c.project_id = ? ORDER BY c.key, cr.role""",
            (project_id,),
        ).fetchall()
    ]
    submissions = []
    for row in store.conn.execute(
        """SELECT c.key AS condition_key, s.state_version, s.attempt_no, s.role,
                  s.summary, s.artifact_refs_json, s.evidence_ref, s.status
           FROM submissions s JOIN conditions c ON c.id = s.condition_id
           WHERE c.project_id = ? ORDER BY c.key, s.attempt_no, s.role, s.summary""",
        (project_id,),
    ).fetchall():
        item = dict(row)
        item["artifact_refs"] = _json(item.pop("artifact_refs_json"), [])
        submissions.append(item)
    reviews = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, s.attempt_no, r.role, r.review_kind,
                      r.verdict, r.summary, r.evidence_ref
               FROM reviews r
               JOIN submissions s ON s.id = r.submission_id
               JOIN conditions c ON c.id = s.condition_id
               WHERE c.project_id = ?
               ORDER BY c.key, s.attempt_no, r.role""",
            (project_id,),
        ).fetchall()
    ]
    evidence = [
        dict(row)
        for row in store.conn.execute(
            """SELECT e.entity_type, e.role, e.summary, e.source_ref, e.content_hash
               FROM evidence e WHERE e.project_id = ?
               ORDER BY e.entity_type, e.role, e.summary, COALESCE(e.source_ref, '')""",
            (project_id,),
        ).fetchall()
    ]
    commitments = [
        dict(row)
        for row in store.conn.execute(
            """SELECT title, detail, owner_role, priority, blocking, status, version, created_by
               FROM commitments WHERE project_id = ?
               ORDER BY title, owner_role""",
            (project_id,),
        ).fetchall()
    ]
    exceptions = [
        dict(row)
        for row in store.conn.execute(
            """SELECT dedupe_key, title, detail, severity, owner_role, principal_only,
                      target_type, target_id, status, resolution, version, raised_by
               FROM exceptions WHERE project_id = ? ORDER BY dedupe_key""",
            (project_id,),
        ).fetchall()
    ]
    return {
        "project": {
            "id": project["id"],
            "name": project["name"],
            "status": project["status"],
            "max_wip": project["max_wip"],
        },
        "objectives": objectives,
        "milestones": milestones,
        "records": records,
        "truths": truths,
        "truth_links": truth_links,
        "conditions": conditions,
        "condition_inputs": condition_inputs,
        "condition_truths": condition_truths,
        "condition_dependencies": dependencies,
        "condition_reviewers": reviewers,
        "submissions": submissions,
        "reviews": reviews,
        "evidence": evidence,
        "commitments": commitments,
        "exceptions": exceptions,
    }


def acceptance_state(store: StateStore, project_id: str) -> dict[str, Any]:
    """Return only governed acceptance semantics for cross-host comparison."""
    milestones = [
        dict(row)
        for row in store.conn.execute(
            "SELECT id, objective_id, ordinal, status FROM milestones WHERE project_id = ? ORDER BY ordinal, id",
            (project_id,),
        ).fetchall()
    ]
    conditions = [
        dict(row)
        for row in store.conn.execute(
            """SELECT key, milestone_id, status, state_version, attempt_count, attempt_budget,
                      owner_role, verifier_role
               FROM conditions WHERE project_id = ? ORDER BY key""",
            (project_id,),
        ).fetchall()
    ]
    accepted_inputs = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, r.key AS record_key, ci.accepted_record_version
               FROM condition_inputs ci
               JOIN conditions c ON c.id = ci.condition_id
               JOIN records r ON r.id = ci.record_id
               WHERE c.project_id = ? AND ci.accepted_record_version IS NOT NULL
               ORDER BY c.key, r.key""",
            (project_id,),
        ).fetchall()
    ]
    accepted_truths = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, t.key AS truth_key, ct.accepted_truth_version
               FROM condition_truths ct
               JOIN conditions c ON c.id = ct.condition_id
               JOIN truths t ON t.id = ct.truth_id
               WHERE c.project_id = ? AND ct.accepted_truth_version IS NOT NULL
               ORDER BY c.key, t.key""",
            (project_id,),
        ).fetchall()
    ]
    reviews = [
        dict(row)
        for row in store.conn.execute(
            """SELECT c.key AS condition_key, s.attempt_no, r.role, r.review_kind, r.verdict
               FROM reviews r
               JOIN submissions s ON s.id = r.submission_id
               JOIN conditions c ON c.id = s.condition_id
               WHERE c.project_id = ? ORDER BY c.key, s.attempt_no, r.role""",
            (project_id,),
        ).fetchall()
    ]
    return {
        "milestones": milestones,
        "conditions": conditions,
        "accepted_inputs": accepted_inputs,
        "accepted_truths": accepted_truths,
        "reviews": reviews,
    }


def state_fingerprint(store: StateStore, project_id: str) -> str:
    return _hash(semantic_state(store, project_id))


def acceptance_fingerprint(store: StateStore, project_id: str) -> str:
    return _hash(acceptance_state(store, project_id))
