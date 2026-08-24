from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from control_server import apply_principal_action, render_html  # noqa: E402, render_provider_setup_html
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

    def test_rendered_surface_is_project_first_with_live_agents_and_true_principal_exception(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self._store(folder) as store:
                model = supervision_model(store, "project-001")
                page = render_html(model)

            self.assertEqual(model["state_backend"], "sqlite")
            self.assertIn("Project Portfolio", page)
            self.assertIn("Active Projects", page)
            self.assertIn("Agents", page)
            self.assertIn("Application", page)
            self.assertIn("Ready", page)
            self.assertIn("Needs your decision", page)
            self.assertIn("Authorize external publication", page)
            self.assertIn("Project detail", page)
            self.assertNotIn("What changed", page)
            self.assertNotIn("Inspect evidence and consequence state", page)

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

    def test_provider_setup_page_supports_role_specific_models_without_showing_keys(self):
        page = render_provider_setup_html()
        self.assertIn("AI providers", page)
        self.assertIn("Default model", page)
        self.assertIn("Customize agent roles", page)
        self.assertIn("Experience", page)
        self.assertIn("Architecture", page)
        self.assertIn("password", page)
        self.assertNotIn("api_key", page)



if __name__ == "__main__":
    unittest.main()
