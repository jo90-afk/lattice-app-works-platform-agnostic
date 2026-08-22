from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

import sys

sys.path.insert(0, str(SCRIPTS))

from state_engine import LatticeError, StateStore  # noqa: E402


class StateEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(
            ROOT,
            db_path=folder / "state.db",
            snapshot_path=folder / "current.json",
        )
        self.store.ensure_project("project-001", "Test Project")
        self.store.add_objective(
            "project-001", "Deliver a safe increment", "Bounded test objective", "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001", "objective-001", "Increment ready", 1, True,
            milestone_id="milestone-001",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def add_inputs(self) -> tuple[str, str]:
        record = self.store.put_record(
            "project-001", "requirement.core", "requirement", "Core behavior",
            "The observable behavior is present.", "product", "product",
            source_ref="projects/project-001/product/brief.md", record_id="record-001",
        )
        self.store.put_record(
            "project-001", "constraint.unrelated", "constraint", "Unrelated constraint",
            "This should not enter the scoped context.", "architecture", "architecture",
            record_id="record-unrelated",
        )
        truth = self.store.add_truth(
            "project-001", "world.user-needs-flow", "The user needs this flow.",
            "accepted", "background", "product", confidence=0.9, material=True,
            truth_id="truth-001",
        )
        return record["id"], truth["id"]

    def add_condition(self, attempt_budget: int = 3) -> None:
        record_id, truth_id = self.add_inputs()
        self.store.add_condition(
            "project-001", "objective-001", "milestone-001", "condition.core",
            "Core behavior is verified", "Implement the behavior and retain decisive evidence.",
            "application", "quality", "director", priority=80, severity="major",
            attempt_budget=attempt_budget, input_record_ids=[record_id], truth_ids=[truth_id],
            condition_id="condition-001",
        )

    def satisfy_condition(self) -> None:
        action = self.store.frontier("project-001", "application")[0]
        lease = self.store.claim("project-001", "application", "builder-1", action["action_key"])
        self.store.submit(
            lease["lease_id"], "application", "Implemented and tested.",
            ["projects/project-001/platform/web/feature.ts"], "test-output.txt",
        )
        review_action = self.store.frontier("project-001", "quality")[0]
        review_lease = self.store.claim(
            "project-001", "quality", "reviewer-1", review_action["action_key"]
        )
        self.store.review(
            review_lease["lease_id"], "quality", "SATISFIED",
            "Acceptance proof is reproducible.", "quality-evidence.txt",
        )

    def test_frontier_uses_scoped_context_and_truth_lifecycle(self) -> None:
        self.add_condition()
        truth = self.store.truth_ledger("project-001")[0]
        self.assertEqual(truth["attention_state"], "frontier")
        self.assertEqual(truth["transitions"][-1]["from_attention"], "background")

        action = self.store.frontier("project-001", "application")[0]
        record_ids = [item["id"] for item in action["context"]["relevant_records"]]
        self.assertEqual(record_ids, ["record-001"])
        self.assertNotIn("record-unrelated", json.dumps(action))

        lease = self.store.claim("project-001", "application", "builder-1", action["action_key"])
        with self.assertRaises(LatticeError):
            self.store.claim("project-001", "application", "builder-2")
        self.store.submit(
            lease["lease_id"], "application", "Implemented and tested.",
            ["projects/project-001/platform/web/feature.ts"], "test-output.txt",
        )

        self.assertEqual(self.store.frontier("project-001", "application"), [])
        review_action = self.store.frontier("project-001", "quality")[0]
        review_lease = self.store.claim(
            "project-001", "quality", "reviewer-1", review_action["action_key"]
        )
        review = self.store.review(
            review_lease["lease_id"], "quality", "SATISFIED",
            "Acceptance proof is reproducible.", "quality-evidence.txt",
        )
        self.assertEqual(review["condition"]["status"], "satisfied")
        self.assertTrue(self.store.readiness("project-001")["ready"])

        advance_action = self.store.frontier("project-001", "assurance")[0]
        advance_lease = self.store.claim(
            "project-001", "assurance", "assurance-1", advance_action["action_key"]
        )
        result = self.store.advance_milestone(
            advance_lease["lease_id"], "assurance", "All readiness predicates passed."
        )
        self.assertEqual(result["truths_moved_to_background"], ["truth-001"])
        background = self.store.truth_ledger("project-001", "background")
        self.assertEqual(background[0]["id"], "truth-001")
        self.assertEqual(background[0]["transitions"][-1]["to_attention"], "background")

    def test_input_revision_invalidates_active_condition(self) -> None:
        self.add_condition()
        self.satisfy_condition()
        condition = self.store.conn.execute(
            "SELECT * FROM conditions WHERE id = 'condition-001'"
        ).fetchone()
        self.assertEqual(condition["status"], "satisfied")

        self.store.put_record(
            "project-001", "requirement.core", "requirement", "Core behavior",
            "The observable behavior has changed.", "product", "product",
            source_ref="projects/project-001/product/brief.md", reason="requirement changed",
        )
        condition = self.store.conn.execute(
            "SELECT * FROM conditions WHERE id = 'condition-001'"
        ).fetchone()
        self.assertEqual(condition["status"], "unknown")
        self.assertEqual(condition["attempt_count"], 0)
        self.assertEqual(len(self.store.frontier("project-001", "application")), 1)

    def test_retry_budget_promotes_one_exception_without_a_backlog(self) -> None:
        self.add_condition(attempt_budget=2)
        for attempt in range(2):
            action = self.store.frontier("project-001", "application")[0]
            lease = self.store.claim(
                "project-001", "application", "builder-1", action["action_key"]
            )
            result = self.store.fail_action(
                lease["lease_id"], "application", f"Attempt {attempt + 1} could not satisfy the condition."
            )
        self.assertTrue(result["blocked"])
        self.assertEqual(self.store.frontier("project-001", "application"), [])
        exceptions = self.store.conn.execute(
            "SELECT * FROM exceptions WHERE project_id = 'project-001' AND status = 'open'"
        ).fetchall()
        self.assertEqual(len(exceptions), 1)
        director_frontier = self.store.frontier("project-001", "director")
        self.assertEqual(director_frontier[0]["kind"], "resolve_exception")

    def test_contradiction_reactivates_background_truths_and_preserves_versions(self) -> None:
        first = self.store.add_truth(
            "project-001", "world.state-a", "The system is available.", "accepted",
            "background", "product", truth_id="truth-a",
        )
        second = self.store.add_truth(
            "project-001", "world.state-b", "The system is unavailable.", "observed",
            "background", "quality", truth_id="truth-b",
        )
        self.store.link_truths(first["id"], second["id"], "contradicts", "quality")
        ledger = {item["id"]: item for item in self.store.truth_ledger("project-001")}
        self.assertEqual(ledger["truth-a"]["attention_state"], "frontier")
        self.assertEqual(ledger["truth-b"]["attention_state"], "frontier")
        self.assertEqual(ledger["truth-a"]["epistemic_status"], "contested")
        self.assertEqual(ledger["truth-b"]["epistemic_status"], "contested")
        versions = self.store.conn.execute(
            "SELECT COUNT(*) FROM truth_versions WHERE truth_id = 'truth-a'"
        ).fetchone()[0]
        self.assertEqual(versions, 2)

    def test_snapshot_round_trip_excludes_leases(self) -> None:
        self.add_condition()
        action = self.store.frontier("project-001", "application")[0]
        self.store.claim("project-001", "application", "builder-1", action["action_key"])
        snapshot = self.store.export_snapshot()
        self.assertNotIn("leases", snapshot["tables"])

        folder = Path(self.temporary.name)
        copy_store = StateStore(
            ROOT,
            db_path=folder / "copy.db",
            snapshot_path=folder / "current.json",
        )
        try:
            self.assertEqual(copy_store.revision, self.store.revision)
            self.assertEqual(len(copy_store.frontier("project-001", "application")), 1)
        finally:
            copy_store.close()

    def test_mandatory_review_must_concur(self) -> None:
        record_id, truth_id = self.add_inputs()
        self.store.add_condition(
            "project-001", "objective-001", "milestone-001", "condition.reviewed",
            "Change passes functional and security review", "Both reviewers must approve.",
            "application", "quality", "director", input_record_ids=[record_id],
            truth_ids=[truth_id], mandatory_reviewers=["security"],
            condition_id="condition-reviewed",
        )
        action = self.store.frontier("project-001", "application")[0]
        lease = self.store.claim("project-001", "application", "builder", action["action_key"])
        self.store.submit(lease["lease_id"], "application", "Ready for review.", ["feature.ts"])

        quality_action = self.store.frontier("project-001", "quality")[0]
        quality_lease = self.store.claim(
            "project-001", "quality", "quality-review", quality_action["action_key"]
        )
        quality_result = self.store.review(
            quality_lease["lease_id"], "quality", "SATISFIED", "Functional proof passes."
        )
        self.assertEqual(quality_result["condition"]["status"], "candidate")

        security_action = self.store.frontier("project-001", "security")[0]
        security_lease = self.store.claim(
            "project-001", "security", "security-review", security_action["action_key"]
        )
        security_result = self.store.review(
            security_lease["lease_id"], "security", "CONCUR", "Security boundary is preserved."
        )
        self.assertEqual(security_result["condition"]["status"], "satisfied")

    def test_hosted_delta_is_single_action_and_revision_guarded(self) -> None:
        self.add_condition()
        action = self.store.frontier("project-001", "application")[0]
        stale = {
            "format": "lattice-state-delta",
            "schema_version": 1,
            "base_revision": self.store.project_revision("project-001"),
            "project_id": "project-001",
            "action_key": action["action_key"],
            "role": "application",
            "actor": "chatgpt-work",
            "outcome": {
                "type": "submit",
                "summary": "Hosted result.",
                "artifact_refs": ["projects/project-001/platform/web/feature.ts"],
            },
        }
        self.store.add_truth(
            "project-001", "world.unrelated", "An unrelated observation exists.",
            "observed", "background", "product",
        )
        with self.assertRaises(LatticeError):
            self.store.apply_delta(stale)

        current_action = self.store.frontier("project-001", "application")[0]
        stale["base_revision"] = self.store.project_revision("project-001")
        stale["action_key"] = current_action["action_key"]
        result = self.store.apply_delta(stale)
        self.assertEqual(result["status"], "pending")

    def test_unrelated_project_mutation_does_not_stale_hosted_action(self) -> None:
        self.add_condition()
        action = self.store.frontier("project-001", "application")[0]
        base_revision = self.store.project_revision("project-001")
        self.store.ensure_project("project-002", "Unrelated Project")
        self.store.add_truth(
            "project-002", "world.other", "Another project's state changed.",
            "observed", "frontier", "product",
        )
        self.assertEqual(self.store.project_revision("project-001"), base_revision)
        delta = {
            "format": "lattice-state-delta",
            "schema_version": 1,
            "base_revision": base_revision,
            "project_id": "project-001",
            "action_key": action["action_key"],
            "role": "application",
            "actor": "chatgpt-work",
            "outcome": {"type": "submit", "summary": "Project-local result."},
        }
        result = self.store.apply_delta(delta)
        self.assertEqual(result["status"], "pending")

    def test_only_director_or_principal_creates_commitment(self) -> None:
        with self.assertRaises(LatticeError):
            self.store.add_commitment(
                "project-001", "Ship by Friday", "External deadline", "release", "quality"
            )
        commitment = self.store.add_commitment(
            "project-001", "Ship by Friday", "External deadline", "release", "director",
            blocking=True, commitment_id="commitment-001",
        )
        self.assertEqual(commitment["status"], "open")
        action = self.store.frontier("project-001", "release")[0]
        lease = self.store.claim("project-001", "release", "release-1", action["action_key"])
        fulfilled = self.store.fulfill_commitment(
            lease["lease_id"], "release", "Release candidate delivered."
        )
        self.assertEqual(fulfilled["status"], "fulfilled")

    def test_attention_transition_does_not_rewrite_truth_content_version(self) -> None:
        truth = self.store.add_truth(
            "project-001", "world.settled", "The migration completed.", "accepted",
            "frontier", "release", truth_id="truth-settled",
        )
        moved = self.store.move_truth(
            truth["id"], "background", "director", "No active milestone depends on it."
        )
        self.assertEqual(moved["version"], 1)
        versions = self.store.conn.execute(
            "SELECT COUNT(*) FROM truth_versions WHERE truth_id = 'truth-settled'"
        ).fetchone()[0]
        transitions = self.store.conn.execute(
            "SELECT COUNT(*) FROM truth_transitions WHERE truth_id = 'truth-settled'"
        ).fetchone()[0]
        self.assertEqual(versions, 1)
        self.assertEqual(transitions, 1)

    def test_only_immediate_successor_is_planned_and_its_truth_activates_on_advance(self) -> None:
        next_truth = self.store.add_truth(
            "project-001", "world.next-stage", "The next-stage dependency is available.",
            "accepted", "background", "architecture", truth_id="truth-next",
        )
        self.store.add_milestone(
            "project-001", "objective-001", "Successor", 2, False,
            milestone_id="milestone-002",
        )
        with self.assertRaises(LatticeError):
            self.store.add_milestone(
                "project-001", "objective-001", "Speculative third stage", 3, False,
                milestone_id="milestone-003",
            )
        self.store.add_condition(
            "project-001", "objective-001", "milestone-002", "condition.next",
            "Next stage can begin", "The successor dependency is proven.",
            "architecture", "quality", "director", truth_ids=[next_truth["id"]],
            condition_id="condition-next",
        )
        self.assertEqual(
            self.store.truth_ledger("project-001", "background")[0]["id"], "truth-next"
        )

        self.add_condition()
        self.satisfy_condition()
        advance_action = self.store.frontier("project-001", "assurance")[0]
        advance_lease = self.store.claim(
            "project-001", "assurance", "assurance-1", advance_action["action_key"]
        )
        result = self.store.advance_milestone(
            advance_lease["lease_id"], "assurance", "Current milestone accepted."
        )
        self.assertEqual(result["next_milestone"], "milestone-002")
        promoted = {item["id"]: item for item in self.store.truth_ledger("project-001")}
        self.assertEqual(promoted["truth-next"]["attention_state"], "frontier")
        self.assertEqual(promoted["truth-next"]["transitions"][-1]["from_attention"], "background")


if __name__ == "__main__":
    unittest.main()
