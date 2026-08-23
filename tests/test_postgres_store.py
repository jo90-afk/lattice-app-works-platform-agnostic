from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from lifecycle import advance_action, review_action, submit_action  # noqa: E402
from postgres_store import PostgresStateStore  # noqa: E402


POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class PostgresStateStoreTest(unittest.TestCase):
    def connect(self):
        import psycopg

        return psycopg.connect(POSTGRES_URL)

    def reset_database(self) -> None:
        connection = self.connect()
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
        connection.close()

    def setUp(self) -> None:
        self.reset_database()
        self.temporary = tempfile.TemporaryDirectory()
        self.snapshot = Path(self.temporary.name) / "current.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_guarded_lifecycle_and_snapshot_round_trip(self) -> None:
        store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            store.ensure_project("project-pg", "Postgres Project")
            store.add_objective(
                "project-pg", "Prove shared state", "Exercise canonical semantics.", "product",
                objective_id="objective-pg",
            )
            store.add_milestone(
                "project-pg", "objective-pg", "Shared state verified", 1, True,
                milestone_id="milestone-pg",
            )
            store.add_condition(
                "project-pg", "objective-pg", "milestone-pg", "postgres.contract",
                "Postgres obeys the state contract", "Run the guarded lifecycle.",
                "application", "quality", "director", condition_id="condition-pg",
            )

            claimed = claim_for_host_atomic(
                store,
                project_id="project-pg",
                role="application",
                actor="builder-pg",
                host="ci",
                workspace_id="pg-build",
            )
            submitted = submit_action(
                store,
                claimed["lease_id"],
                "application",
                "Shared-store increment produced",
                ["artifact://postgres-contract"],
                "evidence://postgres-build",
            )
            self.assertEqual(submitted["state_backend"], "postgres")

            review_claim = claim_for_host_atomic(
                store,
                project_id="project-pg",
                role="quality",
                actor="verifier-pg",
                host="ci",
                workspace_id="pg-review",
            )
            reviewed = review_action(
                store,
                review_claim["lease_id"],
                "quality",
                "SATISFIED",
                "Verified on shared state",
                "evidence://postgres-review",
            )
            self.assertEqual(reviewed["result"]["condition"]["status"], "satisfied")

            assurance_claim = claim_for_host_atomic(
                store,
                project_id="project-pg",
                role="assurance",
                actor="assurance-pg",
                host="ci",
                workspace_id="pg-assurance",
            )
            advanced = advance_action(
                store,
                assurance_claim["lease_id"],
                "assurance",
                "All conditions accepted",
            )
            self.assertEqual(advanced["result"]["accepted_milestone"], "milestone-pg")
            snapshot = store.export_snapshot()
            max_event_id = max(row["id"] for row in snapshot["tables"]["events"])
        finally:
            store.close()

        self.reset_database()
        restored = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            self.assertEqual(restored._require_project("project-pg")["name"], "Postgres Project")
            restored.ensure_project("project-after-restore", "After Restore")
            newest = restored.conn.execute("SELECT MAX(id) FROM events").fetchone()[0]
            self.assertGreater(newest, max_event_id)
            round_trip = restored.export_snapshot()
            self.assertEqual(
                round_trip["tables"]["conditions"][0]["status"],
                "satisfied",
            )
        finally:
            restored.close()


if __name__ == "__main__":
    unittest.main()
