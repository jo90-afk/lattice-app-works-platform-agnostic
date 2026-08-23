from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from state_backend import PostgresStateBackend, SQLiteStateBackend, project_lock_key  # noqa: E402


class RecordingCursor:
    def __init__(self) -> None:
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        return self


class RecordingConnection:
    def __init__(self) -> None:
        self.cursor_value = RecordingCursor()
        self.commits = 0
        self.rollbacks = 0

    def cursor(self):
        return self.cursor_value

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


class StateBackendTest(unittest.TestCase):
    def test_sqlite_backend_uses_immediate_writer_transaction(self) -> None:
        conn = sqlite3.connect(":memory:")
        try:
            backend = SQLiteStateBackend(conn)
            backend.begin_project_write("project-001")
            self.assertTrue(conn.in_transaction)
            backend.rollback()
            self.assertFalse(conn.in_transaction)
        finally:
            conn.close()

    def test_postgres_backend_uses_current_transaction_and_stable_project_lock(self) -> None:
        connection = RecordingConnection()
        backend = PostgresStateBackend(connection)
        backend.begin_project_write("project-001")
        calls = connection.cursor_value.calls
        self.assertEqual(
            calls,
            [("SELECT pg_advisory_xact_lock(%s)", (project_lock_key("project-001"),))],
        )
        self.assertEqual(project_lock_key("project-001"), project_lock_key("project-001"))
        self.assertNotEqual(project_lock_key("project-001"), project_lock_key("project-002"))
        backend.commit()
        backend.rollback()
        self.assertEqual(connection.commits, 1)
        self.assertEqual(connection.rollbacks, 1)


if __name__ == "__main__":
    unittest.main()
