from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

import sys

sys.path.insert(0, str(SCRIPTS))

from control_plane import claim_for_host, read_model, recover_expired_leases  # noqa: E402
from state_engine import StateStore  # noqa: E402


class ControlPlaneTest(unittest.TestCase):
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
            "project-001",
            "Deliver one bounded increment",
            "Exercise the control-plane projection.",
            "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001",
            "objective-001",
            "Increment verified",
            1,
            True,
            milestone_id="milestone-001",
        )
        self.store.add_condition(
            "project-001",
            "objective-001",
            "milestone-001",
            "condition.core",
            "Core behavior is verified",
            "Implement and verify the bounded behavior.",
            "application",
            "quality",
            "director",
            condition_id="condition-001",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def test_read_model_exposes_control_surface_without_mutation(self) -> None:
        before = self.store.revision
        model = read_model(self.store, "project-001")
        self.assertEqual(model["format"], "lattice-control-read-model")
        self.assertEqual(model["version"], 1)
        self.assertEqual(model["revision"], before)
        project = model["projects"][0]
        self.assertEqual(project["project"]["id"], "project-001")
        self.assertEqual(project["objective"]["id"], "objective-001")
        self.assertEqual(project["milestone"]["id"], "milestone-001")
        self.assertEqual(project["frontier"][0]["kind"], "satisfy_condition")
        self.assertEqual(project["active_leases"], [])
        self.assertEqual(self.store.revision, before)

    def test_host_claim_records_runtime_boundary(self) -> None:
        result = claim_for_host(
            self.store,
            project_id="project-001",
            role="application",
            actor="builder-1",
            host="codex",
            workspace_id="workspace-123",
        )
        self.assertEqual(result["action"]["kind"], "satisfy_condition")
        self.assertEqual(result["recovery"]["recovered"], 0)
        event = self.store.conn.execute(
            "SELECT * FROM events WHERE event_type = 'action_claimed' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        self.assertIsNotNone(event)
        self.assertEqual(event["entity_id"], result["lease_id"])
        self.assertIn('"host":"codex"', event["payload_json"])
        self.assertIn('"workspace_id":"workspace-123"', event["payload_json"])

    def test_expired_lease_recovery_is_audited_and_action_returns_to_frontier(self) -> None:
        claimed = claim_for_host(
            self.store,
            project_id="project-001",
            role="application",
            actor="builder-1",
            host="local",
        )
        with self.store.conn:
            self.store.conn.execute(
                "UPDATE leases SET expires_at = '2000-01-01T00:00:00Z' WHERE id = ?",
                (claimed["lease_id"],),
            )
        result = recover_expired_leases(self.store, "project-001")
        self.assertEqual(result["recovered"], 1)
        self.assertEqual(result["leases"][0]["id"], claimed["lease_id"])
        self.assertEqual(result["frontiers"]["project-001"][0]["kind"], "satisfy_condition")
        event_types = [
            row["event_type"]
            for row in self.store.conn.execute(
                "SELECT event_type FROM events WHERE project_id = 'project-001' ORDER BY id"
            ).fetchall()
        ]
        self.assertIn("lease_expired", event_types)
        self.assertIn("recovery_completed", event_types)
        lease = self.store.conn.execute(
            "SELECT * FROM leases WHERE id = ?", (claimed["lease_id"],)
        ).fetchone()
        self.assertIsNone(lease)


if __name__ == "__main__":
    unittest.main()
