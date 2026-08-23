from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from lifecycle import review_action, submit_action  # noqa: E402
from project_graph import consequence_graph  # noqa: E402
from state_engine import StateStore  # noqa: E402


class ProjectGraphTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.store.ensure_project("project-001", "Graph Project")
        self.store.add_objective(
            "project-001",
            "Deliver graph-backed increment",
            "Exercise consequence relationships.",
            "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001",
            "objective-001",
            "Increment is verified",
            1,
            True,
            milestone_id="milestone-001",
        )
        self.record = self.store.put_record(
            "project-001",
            "requirement.output",
            "requirement",
            "Output remains deterministic",
            "The increment produces deterministic output.",
            "product",
            "product",
            record_id="record-001",
        )
        self.truth = self.store.add_truth(
            "project-001",
            "environment.input_available",
            "Required input is available.",
            "observed",
            "frontier",
            "director",
            truth_id="truth-001",
        )
        self.store.add_condition(
            "project-001",
            "objective-001",
            "milestone-001",
            "increment.prepared",
            "Increment prerequisites are prepared",
            "Establish prerequisite state.",
            "architecture",
            "quality",
            "director",
            input_record_ids=[self.record["id"]],
            truth_ids=[self.truth["id"]],
            condition_id="condition-prereq",
        )
        self.store.add_condition(
            "project-001",
            "objective-001",
            "milestone-001",
            "increment.works",
            "Increment works as required",
            "Produce and verify the increment.",
            "application",
            "quality",
            "director",
            depends_on=["condition-prereq"],
            condition_id="condition-main",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def edges(self, graph):
        return {
            (edge["source"], edge["relation"], edge["target"])
            for edge in graph["edges"]
        }

    def test_graph_explains_why_frontier_work_exists(self) -> None:
        graph = consequence_graph(self.store, "project-001")
        edges = self.edges(graph)
        node_ids = {node["id"] for node in graph["nodes"]}

        self.assertEqual(graph["format"], "lattice-project-consequence-graph")
        self.assertEqual(graph["scope"]["objective_id"], "objective-001")
        self.assertIn("record:record-001", node_ids)
        self.assertIn("truth:truth-001", node_ids)
        self.assertIn("condition:condition-prereq", node_ids)
        self.assertIn("condition:condition-main", node_ids)
        self.assertIn(
            ("record:record-001", "constrains", "condition:condition-prereq"),
            edges,
        )
        self.assertIn(
            ("truth:truth-001", "premise_for", "condition:condition-prereq"),
            edges,
        )
        self.assertIn(
            ("condition:condition-prereq", "must_precede", "condition:condition-main"),
            edges,
        )
        self.assertIn(
            ("condition:condition-prereq", "gates", "milestone:milestone-001"),
            edges,
        )
        action_edges = [edge for edge in graph["edges"] if edge["relation"] == "derived_for"]
        self.assertEqual(len(action_edges), 1)
        self.assertEqual(action_edges[0]["target"], "condition:condition-prereq")

    def test_graph_retains_submission_review_and_evidence_relationships(self) -> None:
        prereq_claim = claim_for_host_atomic(
            self.store,
            project_id="project-001",
            role="architecture",
            actor="architect-1",
            host="ci",
            workspace_id="arch-workspace",
        )
        submitted = submit_action(
            self.store,
            prereq_claim["lease_id"],
            "architecture",
            "Prerequisite established",
            ["artifact://graph/prerequisite"],
            "evidence://graph/prerequisite-build",
        )
        review_claim = claim_for_host_atomic(
            self.store,
            project_id="project-001",
            role="quality",
            actor="quality-1",
            host="ci",
            workspace_id="quality-workspace",
        )
        reviewed = review_action(
            self.store,
            review_claim["lease_id"],
            "quality",
            "SATISFIED",
            "Prerequisite independently verified",
            "evidence://graph/prerequisite-review",
        )

        graph = consequence_graph(self.store, "project-001")
        edges = self.edges(graph)
        submission_id = submitted["result"]["id"]
        review_id = reviewed["result"]["review_id"]

        self.assertIn(
            (f"submission:{submission_id}", "claims_satisfaction_of", "condition:condition-prereq"),
            edges,
        )
        self.assertIn(
            (f"review:{review_id}", "verifies", f"submission:{submission_id}"),
            edges,
        )
        evidence_nodes = [node for node in graph["nodes"] if node["type"] == "evidence"]
        self.assertEqual(len(evidence_nodes), 2)
        self.assertTrue(any(edge["relation"] == "supports" for edge in graph["edges"]))
        action_edges = [edge for edge in graph["edges"] if edge["relation"] == "derived_for"]
        self.assertEqual(len(action_edges), 1)
        self.assertEqual(action_edges[0]["target"], "condition:condition-main")


if __name__ == "__main__":
    unittest.main()
