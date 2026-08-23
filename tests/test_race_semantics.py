from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lifecycle import advance_action, review_action, submit_action  # noqa: E402
from state_engine import LatticeError, StateStore  # noqa: E402


class RaceSemanticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.db = folder / "state.db"
        self.snapshot = folder / "current.json"
        self.primary = StateStore(ROOT, self.db, self.snapshot)
        self.primary.ensure_project("project-001", "Race Project")
        self.primary.add_objective(
            "project-001", "Resolve races", "One durable winner per authority transition.",
            "product", objective_id="objective-001",
        )
        self.primary.add_milestone(
            "project-001", "objective-001", "Race safe", 1, True,
            milestone_id="milestone-001",
        )
        self.primary.add_condition(
            "project-001", "objective-001", "milestone-001", "race.safe",
            "Race behavior is safe", "Verify exactly once.",
            "application", "quality", "director", condition_id="condition-001",
        )

    def tearDown(self) -> None:
        self.primary.close()
        self.temporary.cleanup()

    def second_store(self) -> StateStore:
        return StateStore(ROOT, self.db, self.snapshot)

    def make_candidate(self) -> str:
        claim = self.primary.claim("project-001", "application", "builder")
        submit_action(self.primary, claim["lease_id"], "application", "Built", [])
        review_claim = self.primary.claim("project-001", "quality", "verifier")
        return review_claim["lease_id"]

    def test_two_verifier_processes_using_same_lease_produce_one_review(self) -> None:
        lease_id = self.make_candidate()
        contender = self.second_store()
        try:
            first = review_action(
                self.primary, lease_id, "quality", "SATISFIED", "Verifier one accepted"
            )
            self.assertEqual(first["result"]["condition"]["status"], "satisfied")
            with self.assertRaises(LatticeError):
                review_action(
                    contender, lease_id, "quality", "SATISFIED", "Verifier two stale attempt"
                )
            review_count = self.primary.conn.execute(
                "SELECT COUNT(*) FROM reviews WHERE submission_id = ?",
                (first["result"]["review_id"] and self.primary.conn.execute(
                    "SELECT submission_id FROM reviews WHERE id = ?",
                    (first["result"]["review_id"],),
                ).fetchone()[0],),
            ).fetchone()[0]
            self.assertEqual(review_count, 1)
        finally:
            contender.close()

    def test_two_assurance_processes_using_same_lease_accept_milestone_once(self) -> None:
        review_lease = self.make_candidate()
        review_action(self.primary, review_lease, "quality", "SATISFIED", "Verified")
        advance_claim = self.primary.claim("project-001", "assurance", "assurance-1")
        contender = self.second_store()
        try:
            first = advance_action(
                self.primary, advance_claim["lease_id"], "assurance", "Accept once"
            )
            self.assertEqual(first["result"]["accepted_milestone"], "milestone-001")
            with self.assertRaises(LatticeError):
                advance_action(
                    contender, advance_claim["lease_id"], "assurance", "Stale second acceptance"
                )
            milestone = self.primary.conn.execute(
                "SELECT status FROM milestones WHERE id = 'milestone-001'"
            ).fetchone()
            accepted_events = self.primary.conn.execute(
                "SELECT COUNT(*) FROM events WHERE event_type = 'milestone_accepted' AND entity_id = 'milestone-001'"
            ).fetchone()[0]
            self.assertEqual(milestone["status"], "accepted")
            self.assertEqual(accepted_events, 1)
        finally:
            contender.close()

    def test_semantic_invalidation_revokes_stale_worker_lease(self) -> None:
        self.primary.put_record(
            "project-001", "requirement.race", "requirement", "Race requirement",
            "Initial", "product", "product", record_id="record-001",
        )
        self.primary.conn.execute(
            "INSERT INTO condition_inputs(condition_id, record_id) VALUES (?, ?)",
            ("condition-001", "record-001"),
        )
        self.primary.conn.commit()
        claimed = self.primary.claim("project-001", "application", "worker-old")
        contender = self.second_store()
        try:
            contender.put_record(
                "project-001", "requirement.race", "requirement", "Race requirement",
                "Revised", "product", "product", record_id="record-001", reason="requirement revised",
            )
            with self.assertRaises(LatticeError):
                submit_action(
                    self.primary, claimed["lease_id"], "application", "Built against old requirement", []
                )
            new_frontier = self.primary.frontier("project-001", "application", 3)
            self.assertEqual(len(new_frontier), 1)
            self.assertNotEqual(new_frontier[0]["action_key"], claimed["action"]["action_key"])
        finally:
            contender.close()


if __name__ == "__main__":
    unittest.main()
