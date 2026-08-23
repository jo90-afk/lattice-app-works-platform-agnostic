from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from lifecycle import release_action  # noqa: E402
from state_engine import StateStore  # noqa: E402
from supervision_model import supervision_model  # noqa: E402


class SupervisionModelTest(unittest.TestCase):
    def test_projection_combines_portfolio_decisions_changes_and_runtime_telemetry(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with StateStore(ROOT, db_path=folder / "state.db", snapshot_path=folder / "current.json") as store:
                store.ensure_project("project-001", "Supervised Project")
                store.add_objective(
                    "project-001",
                    "Deliver",
                    "Exercise supervision.",
                    "product",
                    objective_id="objective-001",
                )
                store.add_milestone(
                    "project-001",
                    "objective-001",
                    "Verified",
                    1,
                    True,
                    milestone_id="milestone-001",
                )
                store.add_condition(
                    "project-001",
                    "objective-001",
                    "milestone-001",
                    "supervision.visible",
                    "Work appears in supervision",
                    "Create one derived action.",
                    "application",
                    "quality",
                    "director",
                    condition_id="condition-001",
                )
                store.add_truth(
                    "project-001",
                    "environment.ready",
                    "The supervision scenario is ready.",
                    "observed",
                    "frontier",
                    "director",
                    truth_id="truth-001",
                )
                store.raise_exception(
                    "project-001",
                    "principal-choice",
                    "Principal choice required",
                    "A deliberate human boundary.",
                    "major",
                    "director",
                    "director",
                    True,
                )
                claim = claim_for_host_atomic(
                    store,
                    project_id="project-001",
                    role="application",
                    actor="application-1",
                    host="ci",
                    workspace_id="workspace-1",
                )
                release_action(store, claim["lease_id"], "application")

                model = supervision_model(store, "project-001")

            self.assertEqual(model["format"], "lattice-control-read-model")
            self.assertEqual(model["state_backend"], "sqlite")
            self.assertEqual(model["portfolio"]["active_projects"], 1)
            self.assertEqual(model["portfolio"]["principal_decisions"], 1)
            self.assertEqual(model["principal_inbox"]["count"], 1)
            self.assertGreaterEqual(model["operational_telemetry"]["claims"], 1)
            self.assertGreaterEqual(model["operational_telemetry"]["completed_transitions"], 1)
            self.assertIn("ci", model["operational_telemetry"]["hosts"])
            self.assertIn(
                "truth_recorded",
                [item["event_type"] for item in model["recent_accepted_changes"]],
            )


if __name__ == "__main__":
    unittest.main()
