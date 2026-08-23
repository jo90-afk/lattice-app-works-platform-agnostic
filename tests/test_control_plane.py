from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

import sys

sys.path.insert(0, str(SCRIPTS))

from control_plane import (  # noqa: E402
    claim_for_host,
    read_model,
    record_lifecycle_event,
    recover_expired_leases,
)
from state_engine import LatticeError, StateStore  # noqa: E402


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
        self.assertIsInstance(model["event_sequence"], int)
        project = model["projects"][0]
        self.assertEqual(project["project"]["id"], "project-001")
        self.assertEqual(project["objective"]["id"], "objective-001")
        self.assertEqual(project["milestone"]["id"], "milestone-001")
        self.assertEqual(project["semantic_revision"], self.store.project_revision("project-001"))
        self.assertEqual(project["frontier"][0]["kind"], "satisfy_condition")
        self.assertEqual(project["active_leases"], [])
        self.assertEqual(self.store.revision, before)

    def test_host_claim_records_runtime_boundary_without_staling_action(self) -> None:
        semantic_before = self.store.project_revision("project-001")
        result = claim_for_host(
            self.store,
            project_id="project-001",
            role="application",
            actor="builder-1",
            host="codex",
            workspace_id="workspace-123",
        )
        self.assertEqual(result["action"]["kind"], "satisfy_condition")
        self.assertEqual(result["action"]["state_revision"], semantic_before)
        self.assertEqual(result["control_revision"], semantic_before)
        self.assertEqual(self.store.project_revision("project-001"), semantic_before)
        self.assertEqual(result["recovery"]["recovered"], 0)
        event = self.store.conn.execute(
            "SELECT * FROM events WHERE event_type = 'action_claimed' ORDER BY id DESC LIMIT 1"
        ).fetchone()
        self.assertIsNotNone(event)
        self.assertEqual(event["entity_id"], result["lease_id"])
        self.assertEqual(event["revision"], semantic_before)
        self.assertEqual(event["id"], result["control_event_id"])
        self.assertIn('"host":"codex"', event["payload_json"])
        self.assertIn('"workspace_id":"workspace-123"', event["payload_json"])

    def test_operational_telemetry_does_not_stale_hosted_delta(self) -> None:
        action = self.store.frontier("project-001", role="application", limit=1)[0]
        base_revision = action["state_revision"]
        record_lifecycle_event(
            self.store,
            project_id="project-001",
            event_type="workspace_created",
            entity_type="workspace",
            entity_id="workspace-1",
            host="codex",
        )
        self.assertEqual(self.store.project_revision("project-001"), base_revision)
        result = self.store.apply_delta(
            {
                "format": "lattice-state-delta",
                "schema_version": 1,
                "project_id": "project-001",
                "base_revision": base_revision,
                "role": "application",
                "action_key": action["action_key"],
                "outcome": {"type": "fail", "summary": "hosted failure"},
            }
        )
        self.assertFalse(result["blocked"])
        with self.assertRaises(LatticeError):
            self.store.apply_delta(
                {
                    "format": "lattice-state-delta",
                    "schema_version": 1,
                    "project_id": "project-001",
                    "base_revision": base_revision,
                    "role": "application",
                    "action_key": action["action_key"],
                    "outcome": {"type": "fail", "summary": "stale retry"},
                }
            )

    def test_claim_hook_failure_releases_lease_and_records_abort(self) -> None:
        semantic_before = self.store.project_revision("project-001")
        with patch("control_plane.dispatch_hooks", side_effect=LatticeError("hook exited 7")):
            with self.assertRaises(LatticeError):
                claim_for_host(
                    self.store,
                    project_id="project-001",
                    role="application",
                    actor="builder-1",
                    host="local",
                )
        active = self.store.conn.execute(
            "SELECT COUNT(*) FROM leases WHERE project_id = 'project-001'"
        ).fetchone()[0]
        self.assertEqual(active, 0)
        event_types = [
            row["event_type"]
            for row in self.store.conn.execute(
                "SELECT event_type FROM events WHERE project_id = 'project-001' ORDER BY id"
            ).fetchall()
        ]
        self.assertIn("action_claimed", event_types)
        self.assertIn("hook_failed", event_types)
        self.assertIn("claim_aborted", event_types)
        self.assertEqual(self.store.project_revision("project-001"), semantic_before)
        frontier = self.store.frontier("project-001", role="application", limit=1)
        self.assertEqual(frontier[0]["kind"], "satisfy_condition")

    def test_expired_lease_recovery_records_abandoned_workspace_and_returns_action(self) -> None:
        claimed = claim_for_host(
            self.store,
            project_id="project-001",
            role="application",
            actor="builder-1",
            host="codex",
            workspace_id="workspace-expired",
        )
        semantic_before = self.store.project_revision("project-001")
        with self.store.conn:
            self.store.conn.execute(
                "UPDATE leases SET expires_at = '2000-01-01T00:00:00Z' WHERE id = ?",
                (claimed["lease_id"],),
            )
        result = recover_expired_leases(self.store, "project-001")
        self.assertEqual(result["recovered"], 1)
        self.assertEqual(result["leases"][0]["id"], claimed["lease_id"])
        self.assertEqual(
            result["abandoned_workspaces"],
            [{"project_id": "project-001", "workspace_id": "workspace-expired"}],
        )
        self.assertEqual(result["frontiers"]["project-001"][0]["kind"], "satisfy_condition")
        self.assertEqual(self.store.project_revision("project-001"), semantic_before)
        events = self.store.conn.execute(
            "SELECT event_type, entity_id, payload_json FROM events WHERE project_id = 'project-001' ORDER BY id"
        ).fetchall()
        event_types = [row["event_type"] for row in events]
        self.assertIn("workspace_abandoned", event_types)
        self.assertIn("lease_expired", event_types)
        self.assertIn("recovery_completed", event_types)
        abandoned = next(row for row in events if row["event_type"] == "workspace_abandoned")
        self.assertEqual(abandoned["entity_id"], "workspace-expired")
        self.assertIn('"lease_id":"' + claimed["lease_id"] + '"', abandoned["payload_json"])
        lease = self.store.conn.execute(
            "SELECT * FROM leases WHERE id = ?", (claimed["lease_id"],)
        ).fetchone()
        self.assertIsNone(lease)

    def test_recovery_does_not_duplicate_host_reported_workspace_abandonment(self) -> None:
        claimed = claim_for_host(
            self.store,
            project_id="project-001",
            role="application",
            actor="builder-1",
            host="codex",
            workspace_id="workspace-explicit",
        )
        record_lifecycle_event(
            self.store,
            project_id="project-001",
            event_type="workspace_abandoned",
            entity_type="workspace",
            entity_id="workspace-explicit",
            host="codex",
            workspace_id="workspace-explicit",
            payload={"reason": "host_shutdown"},
        )
        with self.store.conn:
            self.store.conn.execute(
                "UPDATE leases SET expires_at = '2000-01-01T00:00:00Z' WHERE id = ?",
                (claimed["lease_id"],),
            )
        result = recover_expired_leases(self.store, "project-001")
        self.assertEqual(result["abandoned_workspaces"], [])
        count = self.store.conn.execute(
            """SELECT COUNT(*) FROM events
               WHERE project_id = 'project-001' AND event_type = 'workspace_abandoned'
                 AND entity_id = 'workspace-explicit'"""
        ).fetchone()[0]
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
