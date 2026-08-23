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

    def test_global_inspect_and_recover_do_not_require_host_or_project(self) -> None:
        inspected = handle_envelope(self.store, self.base("inspect"))
        self.assertEqual(inspected["format"], "lattice-control-read-model")
        self.assertEqual(inspected["projects"][0]["project"]["id"], "project-001")
        recovered = handle_envelope(self.store, self.base("recover"))
        self.assertEqual(recovered["recovered"], 0)

    def test_claim_and_complete_share_one_guarded_runtime_path(self) -> None:
        claim = self.base("claim") | {
            "project_id": "project-001",
            "host": "codex",
            "workspace_id": "worktree-1",
            "actor": "builder-1",
            "role": "application",
        }
        claimed = handle_envelope(self.store, claim)
        complete = self.base("complete") | {
            "project_id": "project-001",
            "host": "codex",
            "lease_id": claimed["lease_id"],
            "role": "application",
            "outcome": {
                "type": "submit",
                "summary": "Adapter result",
                "artifact_refs": ["artifact.txt"],
            },
        }
        completed = handle_envelope(self.store, complete)
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

    def test_completion_cannot_cross_project_boundary(self) -> None:
        self.store.ensure_project("project-002", "Other Project")
        claimed = handle_envelope(
            self.store,
            self.base("claim") | {
                "project_id": "project-001",
                "host": "local",
                "actor": "builder-1",
                "role": "application",
            },
        )
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
