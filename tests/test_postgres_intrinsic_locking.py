from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from postgres_store import PostgresStateStore  # noqa: E402

POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class PostgresIntrinsicLockingTest(unittest.TestCase):
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
        self.snapshot = Path(self.temporary.name) / "missing-current.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_direct_same_record_writers_serialize_into_distinct_versions(self) -> None:
        setup = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            setup.ensure_project("project-001", "Intrinsic Lock Project")
            original = setup.put_record(
                "project-001",
                "requirement.shared",
                "requirement",
                "Shared requirement",
                "Version one",
                "product",
                "product",
                record_id="record-001",
            )
            self.assertEqual(int(original["version"]), 1)
        finally:
            setup.close()

        stores = [
            PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot),
            PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot),
        ]
        barrier = threading.Barrier(2)
        outcomes: list[tuple[str, int | str]] = []
        result_lock = threading.Lock()

        def revise(store, body):
            try:
                barrier.wait()
                result = store.put_record(
                    "project-001",
                    "requirement.shared",
                    "requirement",
                    "Shared requirement",
                    body,
                    "product",
                    "product",
                    reason="concurrent direct writer",
                )
                outcome = ("ok", int(result["version"]))
            except Exception as error:
                outcome = ("error", str(error))
            finally:
                store.close()
            with result_lock:
                outcomes.append(outcome)

        threads = [
            threading.Thread(target=revise, args=(stores[0], "Writer A")),
            threading.Thread(target=revise, args=(stores[1], "Writer B")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual([kind for kind, _ in outcomes].count("ok"), 2)
        self.assertEqual(sorted(value for kind, value in outcomes if kind == "ok"), [2, 3])

        verify = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            current = verify.conn.execute(
                "SELECT version FROM records WHERE id = 'record-001'"
            ).fetchone()
            versions = [
                int(row["version"])
                for row in verify.conn.execute(
                    "SELECT version FROM record_versions WHERE record_id = 'record-001' ORDER BY version"
                ).fetchall()
            ]
            event_revisions = [
                int(row["revision"])
                for row in verify.conn.execute(
                    """SELECT revision FROM events
                       WHERE entity_type = 'record' AND entity_id = 'record-001'
                       ORDER BY revision"""
                ).fetchall()
            ]
            self.assertEqual(int(current["version"]), 3)
            self.assertEqual(versions, [1, 2, 3])
            self.assertEqual(len(event_revisions), 3)
            self.assertEqual(len(set(event_revisions)), 3)
        finally:
            verify.close()


if __name__ == "__main__":
    unittest.main()
