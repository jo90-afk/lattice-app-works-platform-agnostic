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

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_principal_inbox_contains_only_principal_owned_decisions(self) -> None:
        principal_exception = self.store.raise_exception(
            "project-001",
            "production-launch",
            "Approve production launch",
            "The verified release is ready for an externally visible launch decision.",
            "critical",
            "director",
            "director",
            True,
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


if __name__ == "__main__":
    unittest.main()
