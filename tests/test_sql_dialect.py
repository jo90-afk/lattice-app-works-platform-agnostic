from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from sql_dialect import PostgresConnectionAdapter, postgres_schema, postgres_sql  # noqa: E402


class RecordingCursor:
    def __init__(self, rows=None, description=None):
        self.calls = []
        self.rows = list(rows or [])
        self.description = description

    def execute(self, sql, params=()):
        self.calls.append((sql, params))
        return self

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def fetchall(self):
        rows = self.rows
        self.rows = []
        return rows


class RecordingConnection:
    def __init__(self):
        self.cursors = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        cursor = RecordingCursor()
        self.cursors.append(cursor)
        return cursor

    def commit(self): self.commits += 1
    def rollback(self): self.rollbacks += 1
    def close(self): self.closed = True


class SQLDialectTest(unittest.TestCase):
    def test_query_translation_covers_state_store_sqlite_idioms(self):
        self.assertEqual(
            postgres_sql("SELECT * FROM projects WHERE id = ?"),
            "SELECT * FROM projects WHERE id = %s",
        )
        ignored = postgres_sql("INSERT OR IGNORE INTO meta(key, value) VALUES(?, ?)")
        self.assertEqual(
            ignored,
            "INSERT INTO meta(key, value) VALUES(%s, %s) ON CONFLICT DO NOTHING",
        )
        self.assertEqual(postgres_sql("SELECT last_insert_rowid()"), "SELECT LASTVAL()")

    def test_schema_translation_removes_sqlite_bootstrap_and_uses_bigserial_events(self):
        source = (ROOT / "runtime" / "schema.sql").read_text(encoding="utf-8")
        rendered = postgres_schema(source)
        self.assertNotIn("PRAGMA foreign_keys", rendered)
        self.assertNotIn("AUTOINCREMENT", rendered)
        self.assertIn("id BIGSERIAL PRIMARY KEY", rendered)
        self.assertIn("one_active_objective_per_project", rendered)
        self.assertIn("events_by_project_revision", rendered)

    def test_connection_adapter_translates_placeholders_without_driver_dependency(self):
        raw = RecordingConnection()
        connection = PostgresConnectionAdapter(raw)
        connection.execute("SELECT * FROM projects WHERE id = ?", ("project-001",))
        self.assertEqual(
            raw.cursors[0].calls[0],
            ("SELECT * FROM projects WHERE id = %s", ("project-001",)),
        )
        connection.commit()
        self.assertEqual(raw.commits, 1)


if __name__ == "__main__":
    unittest.main()
