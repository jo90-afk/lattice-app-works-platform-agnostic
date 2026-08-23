from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from control_plane import read_model  # noqa: E402
from state_engine import StateStore  # noqa: E402


class EvidenceObservabilityTest(unittest.TestCase):
    def test_read_model_joins_submission_review_and_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with StateStore(ROOT, folder / "state.db", folder / "current.json") as store:
                store.ensure_project("project-001", "Evidence Project")
                store.add_objective(
                    "project-001", "Prove the increment", "Evidence must be inspectable.",
                    "product", objective_id="objective-001",
                )
                store.add_milestone(
                    "project-001", "objective-001", "Evidence accepted", 1, True,
                    milestone_id="milestone-001",
                )
                store.add_condition(
                    "project-001", "objective-001", "milestone-001", "evidence.visible",
                    "Evidence is visible", "Expose submission and review evidence.",
                    "application", "quality", "director", condition_id="condition-001",
                )
                author = store.claim("project-001", "application", "builder-1")
                store.submit(
                    author["lease_id"], "application", "Implemented",
                    [], "evidence://submission/1",
                )
                verifier = store.claim("project-001", "quality", "verifier-1")
                store.review(
                    verifier["lease_id"], "quality", "SATISFIED", "Verified",
                    "evidence://review/1",
                )
                model = read_model(store, "project-001")
                project = model["projects"][0]

                self.assertTrue(project["readiness"]["ready"])
                self.assertEqual(len(project["evidence_chain"]), 2)
                sources = {item["source_ref"] for item in project["evidence_chain"]}
                self.assertEqual(sources, {"evidence://submission/1", "evidence://review/1"})
                review = next(item for item in project["evidence_chain"] if item["entity_type"] == "review")
                self.assertEqual(review["condition_id"], "condition-001")
                self.assertEqual(review["condition_status"], "satisfied")
                self.assertEqual(review["review_verdict"], "SATISFIED")


if __name__ == "__main__":
    unittest.main()
