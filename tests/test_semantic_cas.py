from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from hosted_delta import apply_delta_serialized  # noqa: E402
from semantic_writes import revise_truth_cas  # noqa: E402
from state_engine import LatticeError, StateStore  # noqa: E402


class SemanticCASTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.store.ensure_project("project-001", "CAS Project")

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_truth_revision_requires_exact_observed_version(self) -> None:
        truth = self.store.add_truth(
            "project-001",
            "world.fact",
            "First statement",
            "observed",
            "frontier",
            "director",
            truth_id="truth-001",
        )
        self.assertEqual(truth["version"], 1)
        accepted = revise_truth_cas(
            self.store,
            truth_id="truth-001",
            changed_by="director",
            reason="new evidence",
            expected_version=1,
            statement="Second statement",
        )
        self.assertEqual(accepted["version"], 2)
        self.assertEqual(accepted["truth"]["statement"], "Second statement")
        with self.assertRaisesRegex(LatticeError, "expected version 1, current 2"):
            revise_truth_cas(
                self.store,
                truth_id="truth-001",
                changed_by="director",
                reason="stale writer",
                expected_version=1,
                statement="Stale third statement",
            )
        current = self.store.conn.execute(
            "SELECT statement, version FROM truths WHERE id = 'truth-001'"
        ).fetchone()
        self.assertEqual(current["statement"], "Second statement")
        self.assertEqual(current["version"], 2)

    def test_two_hosted_deltas_from_same_revision_cannot_both_commit(self) -> None:
        objective = self.store.add_objective(
            "project-001", "Deliver", "Two independent actions", "product",
            objective_id="objective-001",
        )
        milestone = self.store.add_milestone(
            "project-001", objective["id"], "Both done", 1, True,
            milestone_id="milestone-001",
        )
        self.store.add_condition(
            "project-001", objective["id"], milestone["id"], "app.done",
            "App done", "Application action", "application", "quality", "director",
            condition_id="condition-app",
        )
        self.store.add_condition(
            "project-001", objective["id"], milestone["id"], "service.done",
            "Service done", "Service action", "services", "quality", "director",
            condition_id="condition-services",
        )
        base = self.store.project_revision("project-001")
        frontier = self.store.frontier("project-001", None, 10)
        actions = {item["role"]: item for item in frontier}

        first = {
            "format": "lattice-state-delta",
            "schema_version": 1,
            "project_id": "project-001",
            "base_revision": base,
            "role": "application",
            "actor": "hosted-app",
            "action_key": actions["application"]["action_key"],
            "outcome": {
                "type": "submit",
                "summary": "App complete",
                "artifact_refs": ["artifact://app-output"],
            },
        }
        second = {
            "format": "lattice-state-delta",
            "schema_version": 1,
            "project_id": "project-001",
            "base_revision": base,
            "role": "services",
            "actor": "hosted-services",
            "action_key": actions["services"]["action_key"],
            "outcome": {
                "type": "submit",
                "summary": "Service complete",
                "artifact_refs": ["artifact://service-output"],
            },
        }

        accepted = apply_delta_serialized(self.store, first)
        self.assertGreater(accepted["accepted_revision"], base)
        with self.assertRaisesRegex(LatticeError, "Hosted delta is stale"):
            apply_delta_serialized(self.store, second)
        submissions = int(
            self.store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]
        )
        self.assertEqual(submissions, 1)


if __name__ == "__main__":
    unittest.main()
