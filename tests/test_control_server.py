from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from control_server import apply_principal_action, render_html  # noqa: E402
from state_engine import StateStore  # noqa: E402
from supervision_model import supervision_model  # noqa: E402


class ControlServerTest(unittest.TestCase):
    def _store(self, folder: Path) -> StateStore:
        store = StateStore(ROOT, db_path=folder / "state.db", snapshot_path=folder / "current.json")
        store.ensure_project("project-001", "Control Surface Project")
        store.add_objective(
            "project-001", "Make supervision legible", "Expose current state.", "product", objective_id="objective-001"
        )
        store.add_milestone(
            "project-001", "objective-001", "Surface is readable", 1, True, milestone_id="milestone-001"
        )
        truth = store.add_truth(
            "project-001",
            "surface.context",
            "Project state is available to the supervision surface.",
            "observed",
            "frontier",
            "director",
            truth_id="truth-001",
        )
        store.add_condition(
            "project-001",
            "objective-001",
            "milestone-001",
            "surface.explains",
            "Surface explains project causality",
            "Expose why work exists and what it affects.",
            "application",
            "quality",
            "director",
            truth_ids=[truth["id"]],
            condition_id="condition-001",
        )
        store.raise_exception(
            "project-001",
            "human-boundary",
            "Authorize external publication",
            "Publication crosses the external-action authority boundary.",
            "critical",
            "director",
            "director",
            True,
            "milestone",
            "milestone-001",
        )
        return store

    def test_rendered_surface_has_decision_first_information_architecture_and_action(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self._store(folder) as store:
                model = supervision_model(store, "project-001")
                page = render_html(model)

            self.assertEqual(model["state_backend"], "sqlite")
            self.assertIn("Your decisions", page)
            self.assertIn("Projects", page)
            self.assertIn("What changed", page)
            self.assertIn("Working toward", page)
            self.assertIn("Now", page)
            self.assertIn("Next", page)
            self.assertIn("Needs attention", page)
            self.assertIn("What this controls", page)
            self.assertIn("If you act", page)
            self.assertIn("Why this is yours", page)
            self.assertIn("Inspect evidence and consequence state", page)
            self.assertIn("<form", page)
            self.assertIn("<button", page)
            self.assertIn("Resolve exception", page)
            self.assertNotIn("This surface is read-only", page)

    def test_principal_action_uses_current_guarded_action_and_closes_exception(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self._store(folder) as store:
                model = supervision_model(store, "project-001")
                item = model["principal_inbox"]["items"][0]
                result = apply_principal_action(
                    store,
                    item["action_key"],
                    "resolve",
                    "Approved publication at the current milestone boundary.",
                )
                row = store.conn.execute("SELECT status, resolution FROM exceptions WHERE id = ?", (item["target_id"],)).fetchone()
                event = store.conn.execute(
                    "SELECT payload_json FROM events WHERE event_type = 'exception_resolution_recorded' ORDER BY id DESC LIMIT 1"
                ).fetchone()

            self.assertEqual(result["kind"], "exception")
            self.assertEqual(row["status"], "resolved")
            self.assertIn("Approved publication", row["resolution"])
            self.assertIsNotNone(event)


if __name__ == "__main__":
    unittest.main()
