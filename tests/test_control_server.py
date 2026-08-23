from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from control_server import render_html  # noqa: E402
from state_engine import StateStore  # noqa: E402
from supervision_model import supervision_model  # noqa: E402


class ControlServerTest(unittest.TestCase):
    def test_rendered_surface_contains_portfolio_supervision_without_actions(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with StateStore(ROOT, db_path=folder / "state.db", snapshot_path=folder / "current.json") as store:
                store.ensure_project("project-001", "Control Surface Project")
                store.add_objective(
                    "project-001",
                    "Make supervision legible",
                    "Expose current state.",
                    "product",
                    objective_id="objective-001",
                )
                store.add_milestone(
                    "project-001",
                    "objective-001",
                    "Surface is readable",
                    1,
                    True,
                    milestone_id="milestone-001",
                )
                model = supervision_model(store, "project-001")
                page = render_html(model)

            self.assertEqual(model["state_backend"], "sqlite")
            self.assertEqual(model["portfolio"]["active_projects"], 1)
            self.assertIn("Control Surface Project", page)
            self.assertIn("Make supervision legible", page)
            self.assertIn("Surface is readable", page)
            self.assertIn("Human supervision", page)
            self.assertIn("Principal inbox", page)
            self.assertIn("Recent accepted changes", page)
            self.assertIn("Operational telemetry", page)
            self.assertIn("Milestone readiness", page)
            self.assertIn("Evidence chain", page)
            self.assertIn("This surface is read-only", page)
            self.assertNotIn("<form", page)


if __name__ == "__main__":
    unittest.main()
