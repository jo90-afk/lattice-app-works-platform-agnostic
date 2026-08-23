from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from state_engine import StateStore  # noqa: E402
from supervision import principal_inbox  # noqa: E402


class SupervisionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.store.ensure_project("project-001", "Supervision Project")
        self.store.add_objective(
            "project-001",
            "Deliver supervised result",
            "Give the Principal enough context to decide.",
            "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001",
            "objective-001",
            "Principal boundary resolved",
            1,
            True,
            milestone_id="milestone-001",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_principal_inbox_contains_only_principal_owned_decisions_with_context(self) -> None:
        principal_exception = self.store.raise_exception(
            "project-001",
            "production-launch",
            "Approve production launch",
            "The verified release is ready for an externally visible launch decision.",
            "critical",
            "director",
            "director",
            True,
            "milestone",
            "milestone-001",
        )
        self.store.raise_exception(
            "project-001",
            "routine-defect",
            "Fix routine defect",
            "Ordinary remediation.",
            "minor",
            "director",
            "quality",
            False,
        )
        principal_commitment = self.store.add_commitment(
            "project-001",
            "Confirm external commitment",
            "Principal owns the external promise.",
            "principal",
            "director",
            blocking=True,
        )
        self.store.add_commitment(
            "project-001",
            "Routine engineering follow-up",
            "Director-owned follow-up.",
            "director",
            "director",
        )

        inbox = principal_inbox(self.store, "project-001")
        self.assertEqual(inbox["count"], 2)
        self.assertEqual(inbox["blocking_count"], 2)
        targets = {item["target_id"] for item in inbox["items"]}
        self.assertEqual(targets, {principal_exception["id"], principal_commitment["id"]})
        self.assertEqual(inbox["items"][0]["kind"], "exception")
        self.assertTrue(all(item["action_key"] for item in inbox["items"]))
        self.assertTrue(all(item["decision_required"] for item in inbox["items"]))
        self.assertTrue(all(item["authority_reason"] for item in inbox["items"]))
        self.assertTrue(all(item["supported_choices"] for item in inbox["items"]))
        self.assertTrue(all(item["affected_state"]["project"]["id"] == "project-001" for item in inbox["items"]))
        exception = next(item for item in inbox["items"] if item["kind"] == "exception")
        self.assertEqual(exception["affected_state"]["active_objective"]["id"], "objective-001")
        self.assertEqual(exception["affected_state"]["active_milestone"]["id"], "milestone-001")
        self.assertEqual(exception["affected_state"]["target"]["type"], "milestone")
        self.assertEqual(exception["affected_state"]["target"]["state"]["id"], "milestone-001")
        self.assertEqual(
            {choice["choice"] for choice in exception["supported_choices"]},
            {"resolve", "leave_open"},
        )
        commitment = next(item for item in inbox["items"] if item["kind"] == "commitment")
        self.assertEqual(
            {choice["choice"] for choice in commitment["supported_choices"]},
            {"fulfill", "leave_open"},
        )


if __name__ == "__main__":
    unittest.main()
