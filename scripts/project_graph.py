#!/usr/bin/env python3
"""Project consequence graph derived from canonical Lattice relationships."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from state_engine import StateStore


def _node(node_type: str, entity_id: str, label: str, **data: Any) -> dict[str, Any]:
    return {
        "id": f"{node_type}:{entity_id}",
        "type": node_type,
        "entity_id": entity_id,
        "label": label,
        **data,
    }


def consequence_graph(store: StateStore, project_id: str) -> dict[str, Any]:
    """Return the active project's consequence relationships without storing a graph."""
    project = dict(store._require_project(project_id))
    objective = store.conn.execute(
        "SELECT * FROM objectives WHERE project_id = ? AND status = 'active'",
        (project_id,),
    ).fetchone()

    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, str]] = []

    def add(node: dict[str, Any]) -> None:
        nodes[node["id"]] = node

    def edge(source: str, target: str, relation: str) -> None:
        edges.append({"source": source, "target": target, "relation": relation})

    project_node = _node("project", project_id, project["name"], status=project["status"])
    add(project_node)

    objective_id = objective["id"] if objective else None
    if objective:
        objective_node = _node(
            "objective",
            objective["id"],
            objective["title"],
            status=objective["status"],
            priority=objective["priority"],
        )
        add(objective_node)
        edge(project_node["id"], objective_node["id"], "pursues")

    milestone_query = "SELECT * FROM milestones WHERE project_id = ?"
    milestone_values: tuple[Any, ...] = (project_id,)
    if objective_id:
        milestone_query += " AND objective_id = ?"
        milestone_values = (project_id, objective_id)
    milestone_query += " ORDER BY ordinal, created_at, id"
    milestones = store.conn.execute(milestone_query, milestone_values).fetchall()
    milestone_ids = [str(row["id"]) for row in milestones]
    for milestone in milestones:
        node = _node(
            "milestone",
            milestone["id"],
            milestone["title"],
            status=milestone["status"],
            ordinal=milestone["ordinal"],
        )
        add(node)
        edge(
            f"objective:{milestone['objective_id']}" if objective_id else project_node["id"],
            node["id"],
            "contains",
        )

    if not milestone_ids:
        return {
            "format": "lattice-project-consequence-graph",
            "version": 1,
            "project_id": project_id,
            "semantic_revision": store.project_revision(project_id),
            "scope": {"objective_id": objective_id, "milestone_ids": []},
            "nodes": list(nodes.values()),
            "edges": edges,
            "counts": dict(defaultdict(int)),
        }

    placeholders = ",".join("?" for _ in milestone_ids)
    conditions = store.conn.execute(
        f"SELECT * FROM conditions WHERE milestone_id IN ({placeholders}) ORDER BY priority DESC, key",
        milestone_ids,
    ).fetchall()
    condition_ids = [str(row["id"]) for row in conditions]
    for condition in conditions:
        node = _node(
            "condition",
            condition["id"],
            condition["title"],
            status=condition["status"],
            owner_role=condition["owner_role"],
            verifier_role=condition["verifier_role"],
            severity=condition["severity"],
            state_version=condition["state_version"],
        )
        add(node)
        edge(node["id"], f"milestone:{condition['milestone_id']}", "gates")

    if condition_ids:
        c_placeholders = ",".join("?" for _ in condition_ids)
        for row in store.conn.execute(
            f"""SELECT ci.condition_id, r.* FROM condition_inputs ci
                JOIN records r ON r.id = ci.record_id
                WHERE ci.condition_id IN ({c_placeholders})
                ORDER BY r.kind, r.key""",
            condition_ids,
        ).fetchall():
            node = _node(
                "record",
                row["id"],
                row["title"],
                kind=row["kind"],
                status=row["status"],
                version=row["version"],
            )
            add(node)
            edge(node["id"], f"condition:{row['condition_id']}", "constrains")

        for row in store.conn.execute(
            f"""SELECT ct.condition_id, ct.relevance, ct.accepted_truth_version, t.*
                FROM condition_truths ct JOIN truths t ON t.id = ct.truth_id
                WHERE ct.condition_id IN ({c_placeholders})
                ORDER BY t.attention_state, t.key""",
            condition_ids,
        ).fetchall():
            node = _node(
                "truth",
                row["id"],
                row["statement"],
                epistemic_status=row["epistemic_status"],
                attention_state=row["attention_state"],
                version=row["version"],
                material=bool(row["material"]),
            )
            add(node)
            edge(node["id"], f"condition:{row['condition_id']}", "premise_for")

        for row in store.conn.execute(
            f"""SELECT condition_id, depends_on_condition_id FROM condition_dependencies
                WHERE condition_id IN ({c_placeholders})""",
            condition_ids,
        ).fetchall():
            edge(
                f"condition:{row['depends_on_condition_id']}",
                f"condition:{row['condition_id']}",
                "must_precede",
            )

        submissions = store.conn.execute(
            f"SELECT * FROM submissions WHERE condition_id IN ({c_placeholders}) ORDER BY created_at, id",
            condition_ids,
        ).fetchall()
        submission_ids = [str(row["id"]) for row in submissions]
        for submission in submissions:
            node = _node(
                "submission",
                submission["id"],
                submission["summary"],
                status=submission["status"],
                role=submission["role"],
                attempt_no=submission["attempt_no"],
                state_version=submission["state_version"],
            )
            add(node)
            edge(node["id"], f"condition:{submission['condition_id']}", "claims_satisfaction_of")

        if submission_ids:
            s_placeholders = ",".join("?" for _ in submission_ids)
            reviews = store.conn.execute(
                f"SELECT * FROM reviews WHERE submission_id IN ({s_placeholders}) ORDER BY created_at, id",
                submission_ids,
            ).fetchall()
            for review in reviews:
                node = _node(
                    "review",
                    review["id"],
                    review["summary"],
                    verdict=review["verdict"],
                    role=review["role"],
                    review_kind=review["review_kind"],
                )
                add(node)
                edge(node["id"], f"submission:{review['submission_id']}", "verifies")

        evidence = store.conn.execute(
            """SELECT e.* FROM evidence e
               WHERE e.project_id = ?
               ORDER BY e.created_at, e.id""",
            (project_id,),
        ).fetchall()
        for item in evidence:
            target = f"{item['entity_type']}:{item['entity_id']}"
            if target not in nodes:
                continue
            node = _node(
                "evidence",
                item["id"],
                item["summary"],
                role=item["role"],
                source_ref=item["source_ref"],
            )
            add(node)
            edge(node["id"], target, "supports")

    for exception in store.conn.execute(
        "SELECT * FROM exceptions WHERE project_id = ? AND status = 'open' ORDER BY created_at, id",
        (project_id,),
    ).fetchall():
        node = _node(
            "exception",
            exception["id"],
            exception["title"],
            severity=exception["severity"],
            owner_role=exception["owner_role"],
            principal_only=bool(exception["principal_only"]),
        )
        add(node)
        target = (
            f"{exception['target_type']}:{exception['target_id']}"
            if exception["target_type"] and exception["target_id"]
            else project_node["id"]
        )
        if target in nodes:
            edge(node["id"], target, "blocks")

    for commitment in store.conn.execute(
        "SELECT * FROM commitments WHERE project_id = ? AND status = 'open' ORDER BY created_at, id",
        (project_id,),
    ).fetchall():
        node = _node(
            "commitment",
            commitment["id"],
            commitment["title"],
            owner_role=commitment["owner_role"],
            blocking=bool(commitment["blocking"]),
            due_at=commitment["due_at"],
        )
        add(node)
        if commitment["blocking"]:
            active = next((m for m in milestones if m["status"] == "active"), None)
            edge(node["id"], f"milestone:{active['id']}" if active else project_node["id"], "blocks")
        else:
            edge(project_node["id"], node["id"], "owes")

    for action in store.frontier(project_id, limit=1000):
        node = _node(
            "action",
            action["action_key"],
            action["title"],
            kind=action["kind"],
            role=action["role"],
            score=action["score"],
            derived=True,
        )
        add(node)
        target_type = {
            "satisfy_condition": "condition",
            "review_submission": "submission",
            "advance_milestone": "milestone",
            "resolve_exception": "exception",
            "fulfill_commitment": "commitment",
        }.get(action["kind"])
        if target_type:
            target = f"{target_type}:{action['target_id']}"
            if target in nodes:
                edge(node["id"], target, "derived_for")

    counts = defaultdict(int)
    for node in nodes.values():
        counts[node["type"]] += 1

    return {
        "format": "lattice-project-consequence-graph",
        "version": 1,
        "project_id": project_id,
        "semantic_revision": store.project_revision(project_id),
        "scope": {"objective_id": objective_id, "milestone_ids": milestone_ids},
        "nodes": sorted(nodes.values(), key=lambda item: (item["type"], item["id"])),
        "edges": sorted(edges, key=lambda item: (item["source"], item["relation"], item["target"])),
        "counts": dict(sorted(counts.items())),
    }
