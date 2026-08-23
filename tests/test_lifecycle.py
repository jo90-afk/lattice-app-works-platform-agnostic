from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lifecycle import advance_action, release_action, review_action, submit_action  # noqa: E402
from state_engine import StateStore  # noqa: E402


class LifecycleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.store.ensure_project("project-001", "Lifecycle Project")
        self.store.add_objective(
            "project-001", "Deliver", "Exercise lifecycle wrappers.", "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001", "objective-001", "Verified", 1, True,
            milestone_id="milestone-001",
        )
        self.store.add_condition(
            "project-001", "objective-001", "milestone-001", "condition.core",
            "Core behavior works", "Build it.", "application", "quality", "director",
            condition_id="condition-001",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def event_types(self) -> list[str]:
        return [
            row["event_type"]
            for row in self.store.conn.execute(
                "SELECT event_type FROM events WHERE project_id = 'project-001' ORDER BY id"
            ).fetchall()
        ]

    def test_submit_review_and_acceptance_emit_post_transition_events(self) -> None:
        claim = self.store.claim("project-001", "application", "builder")
        submitted = submit_action(
            self.store, claim["lease_id"], "application", "Built", ["artifact.txt"]
        )
        self.assertEqual(submitted["result"]["status"], "pending")
        self.assertEqual(submitted["lifecycle"]["event_type"], "action_submitted")
        self.assertEqual(submitted["state_backend"], "sqlite")
        self.assertEqual(submitted["lifecycle"]["payload"]["state_backend"], "sqlite")

        review_claim = self.store.claim("project-001", "quality", "verifier")
        reviewed = review_action(
            self.store, review_claim["lease_id"], "quality", "SATISFIED", "Verified"
        )
        self.assertEqual(reviewed["result"]["condition"]["status"], "satisfied")
        self.assertEqual(reviewed["lifecycle"]["event_type"], "verification_recorded")
        self.assertEqual(reviewed["state_backend"], "sqlite")

        advance_claim = self.store.claim("project-001", "assurance", "assurance")
        advanced = advance_action(
            self.store, advance_claim["lease_id"], "assurance", "All conditions accepted"
        )
        self.assertEqual(advanced["result"]["accepted_milestone"], "milestone-001")
        self.assertEqual(advanced["lifecycle"]["event_type"], "milestone_acceptance_recorded")
        self.assertEqual(advanced["state_backend"], "sqlite")
        self.assertIn("action_submitted", self.event_types())
        self.assertIn("verification_recorded", self.event_types())
        self.assertIn("milestone_acceptance_recorded", self.event_types())

    def test_release_returns_action_without_semantic_revision_change(self) -> None:
        before = self.store.project_revision("project-001")
        claim = self.store.claim("project-001", "application", "builder")
        result = release_action(self.store, claim["lease_id"], "application")
        self.assertEqual(result["released"], claim["lease_id"])
        self.assertEqual(result["state_backend"], "sqlite")
        self.assertEqual(result["lifecycle"]["payload"]["state_backend"], "sqlite")
        self.assertEqual(self.store.project_revision("project-001"), before)
        frontier = self.store.frontier("project-001", "application", 3)
        self.assertEqual(frontier[0]["target_id"], "condition-001")
        self.assertIn("action_released", self.event_types())


if __name__ == "__main__":
    unittest.main()
