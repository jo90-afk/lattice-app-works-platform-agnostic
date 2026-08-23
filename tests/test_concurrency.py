from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from host_adapter import handle_envelope  # noqa: E402
from state_engine import LatticeError, StateStore  # noqa: E402


class ConcurrencyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        folder = Path(self.temporary.name)
        self.db = folder / "state.db"
        self.snapshot = folder / "current.json"
        self.store = StateStore(ROOT, self.db, self.snapshot)
        self.store.ensure_project("project-001", "Concurrency Project")
        self.store.add_objective(
            "project-001", "Coordinate workers", "Exercise lease concurrency.", "product",
            objective_id="objective-001",
        )
        self.store.add_milestone(
            "project-001", "objective-001", "Concurrency safe", 1, True,
            milestone_id="milestone-001",
        )
        self.store.add_condition(
            "project-001", "objective-001", "milestone-001", "worker.one",
            "First worker action", "One bounded action.",
            "application", "quality", "director", condition_id="condition-001",
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temporary.cleanup()

    def envelope(self, operation: str, **values):
        return {"format": "lattice-host-adapter", "version": 1, "operation": operation, **values}

    def test_host_claim_is_marked_atomic_and_duplicate_claim_is_rejected(self) -> None:
        claim = self.envelope(
            "claim", project_id="project-001", host="codex", actor="worker-1", role="application"
        )
        first = handle_envelope(self.store, claim)
        self.assertTrue(first["atomic_claim"])
        second_store = StateStore(ROOT, self.db, self.snapshot)
        try:
            with self.assertRaises(LatticeError):
                handle_envelope(second_store, claim | {"actor": "worker-2"})
        finally:
            second_store.close()

    def test_renewal_preserves_semantic_revision_and_requires_same_actor(self) -> None:
        claimed = handle_envelope(
            self.store,
            self.envelope(
                "claim", project_id="project-001", host="codex", actor="worker-1",
                role="application", ttl_minutes=1,
            ),
        )
        before = self.store.project_revision("project-001")
        renewed = handle_envelope(
            self.store,
            self.envelope(
                "renew", project_id="project-001", host="codex", actor="worker-1",
                role="application", lease_id=claimed["lease_id"], ttl_minutes=10,
            ),
        )
        self.assertEqual(renewed["semantic_revision"], before)
        self.assertEqual(self.store.project_revision("project-001"), before)
        event = self.store.conn.execute(
            "SELECT * FROM events WHERE event_type = 'lease_renewed' AND entity_id = ?",
            (claimed["lease_id"],),
        ).fetchone()
        self.assertIsNotNone(event)
        with self.assertRaises(LatticeError):
            handle_envelope(
                self.store,
                self.envelope(
                    "renew", project_id="project-001", host="codex", actor="worker-2",
                    role="application", lease_id=claimed["lease_id"], ttl_minutes=10,
                ),
            )


if __name__ == "__main__":
    unittest.main()
