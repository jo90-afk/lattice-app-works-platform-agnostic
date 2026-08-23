from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from host_adapter import handle_envelope, validate_envelope  # noqa: E402
from state_engine import LatticeError, StateStore  # noqa: E402


class HostAdapterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        self.store.ensure_project("project-001", "Adapter Project")
        self.store.add_objective(
            "project-001", "Deliver adapter path", "Exercise host envelopes.", "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001", "objective-001", "Adapter path verified", 1, True,
            milestone_id="milestone-001",
        )
        self.store.add_condition(
            "project-001", "objective-001", "milestone-001", "adapter.works",
            "Adapter completes work", "Complete work through the adapter.",
            "application", "quality", "director", condition_id="condition-001",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def base(self, operation: str) -> dict:
        return {"format": "lattice-host-adapter", "version": 1, "operation": operation}

    def claim(self) -> dict:
        return handle_envelope(
            self.store,
            self.base("claim") | {
                "project_id": "project-001",
                "host": "codex",
                "workspace_id": "worktree-1",
                "actor": "builder-1",
                "role": "application",
            },
        )

    def submit_envelope(self, lease_id: str, artifacts: list[str] | None = None) -> dict:
        return self.base("complete") | {
            "project_id": "project-001",
            "host": "codex",
            "lease_id": lease_id,
            "role": "application",
            "outcome": {
                "type": "submit",
                "summary": "Adapter result",
                "artifact_refs": artifacts if artifacts is not None else ["artifact.txt"],
            },
        }

    def test_global_inspect_and_recover_do_not_require_host_or_project(self) -> None:
        inspected = handle_envelope(self.store, self.base("inspect"))
        self.assertEqual(inspected["format"], "lattice-control-read-model")
        self.assertEqual(inspected["projects"][0]["project"]["id"], "project-001")
        recovered = handle_envelope(self.store, self.base("recover"))
        self.assertEqual(recovered["recovered"], 0)

    def test_claim_and_complete_share_one_guarded_runtime_path(self) -> None:
        claimed = self.claim()
        completed = handle_envelope(self.store, self.submit_envelope(claimed["lease_id"]))
        self.assertEqual(completed["result"]["status"], "pending")
        self.assertEqual(completed["lifecycle"]["event_type"], "action_submitted")
        event_types = [
            row["event_type"]
            for row in self.store.conn.execute(
                "SELECT event_type FROM events WHERE project_id = 'project-001' ORDER BY id"
            ).fetchall()
        ]
        self.assertIn("action_claimed", event_types)
        self.assertIn("action_submitted", event_types)

    def test_duplicate_completion_replays_without_duplicate_state_mutation(self) -> None:
        claimed = self.claim()
        envelope = self.submit_envelope(claimed["lease_id"])
        first = handle_envelope(self.store, envelope)
        second = handle_envelope(self.store, envelope)
        self.assertFalse(first.get("replayed", False))
        self.assertTrue(second["replayed"])
        self.assertTrue(second["already_committed"])
        self.assertEqual(second["completion"]["event_type"], "action_submitted")
        submission_count = self.store.conn.execute(
            "SELECT COUNT(*) FROM submissions WHERE condition_id = 'condition-001'"
        ).fetchone()[0]
        completion_count = self.store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE event_type = 'action_submitted'"
        ).fetchone()[0]
        self.assertEqual(submission_count, 1)
        self.assertEqual(completion_count, 1)

    def test_missing_repo_artifact_rejects_before_mutation_and_preserves_lease(self) -> None:
        claimed = self.claim()
        envelope = self.submit_envelope(
            claimed["lease_id"],
            ["projects/project-001/platform/missing-result.txt"],
        )
        with self.assertRaises(LatticeError):
            handle_envelope(self.store, envelope)
        condition = self.store.conn.execute(
            "SELECT status, attempt_count FROM conditions WHERE id = 'condition-001'"
        ).fetchone()
        lease = self.store.conn.execute(
            "SELECT id FROM leases WHERE id = ?", (claimed["lease_id"],)
        ).fetchone()
        submission_count = self.store.conn.execute(
            "SELECT COUNT(*) FROM submissions WHERE condition_id = 'condition-001'"
        ).fetchone()[0]
        self.assertEqual(condition["status"], "unknown")
        self.assertEqual(condition["attempt_count"], 0)
        self.assertIsNotNone(lease)
        self.assertEqual(submission_count, 0)

    def test_completion_cannot_cross_project_boundary(self) -> None:
        self.store.ensure_project("project-002", "Other Project")
        claimed = self.claim()
        with self.assertRaises(LatticeError):
            handle_envelope(
                self.store,
                self.base("complete") | {
                    "project_id": "project-002",
                    "host": "local",
                    "lease_id": claimed["lease_id"],
                    "role": "application",
                    "outcome": {"type": "release"},
                },
            )

    def test_operation_specific_required_fields(self) -> None:
        validate_envelope(self.base("inspect"))
        validate_envelope(self.base("recover"))
        with self.assertRaises(LatticeError):
            validate_envelope(self.base("claim") | {"project_id": "project-001"})
        with self.assertRaises(LatticeError):
            validate_envelope(
                self.base("complete") | {
                    "project_id": "project-001",
                    "host": "local",
                    "lease_id": "lease-x",
                    "role": "application",
                    "outcome": {"type": "review", "summary": "missing verdict"},
                }
            )


if __name__ == "__main__":
    unittest.main()
