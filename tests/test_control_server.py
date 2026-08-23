from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from control_plane import read_model  # noqa: E402
from control_server import render_html  # noqa: E402
from state_engine import StateStore  # noqa: E402


class ControlServerTest(unittest.TestCase):
    def test_rendered_surface_contains_project_state_without_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with StateStore(ROOT, db_path=folder / "state.db", snapshot_path=folder / "current.json") as store:
                store.ensure_project("project-001", "Control Surface Project")
                store.add_objective(
                    "project-001",
                    "Make supervision legible",
                    "Expose the current state.",
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
                model = read_model(store, "project-001")
            page = render_html(model)
            self.assertIn("Control Surface Project", page)
            self.assertIn("Make supervision legible", page)
            self.assertIn("Surface is readable", page)
            self.assertIn("This surface is read-only", page)
            self.assertNotIn("<form", page)


if __name__ == "__main__":
    unittest.main()
