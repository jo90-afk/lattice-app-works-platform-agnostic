#!/usr/bin/env python3
"""Small SQL compatibility layer for one StateStore across SQLite and Postgres."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable


def postgres_sql(sql: str) -> str:
    """Translate the limited SQLite query idioms used by StateStore to Postgres."""
    ignored_insert = "INSERT OR IGNORE" in sql.upper()
    translated = sql.replace("?", "%s")
    translated = re.sub(
        r"INSERT\s+OR\s+IGNORE\s+INTO",
        "INSERT INTO",
        translated,
        flags=re.IGNORECASE,
    )
    if ignored_insert:
        translated = translated.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
    translated = translated.replace("SELECT last_insert_rowid()", "SELECT LASTVAL()")
    return translated


def postgres_schema(sqlite_schema: str) -> str:
    """Render the canonical SQLite schema into its Postgres-compatible form."""
    lines = [
        line for line in sqlite_schema.splitlines()
        if not line.strip().upper().startswith("PRAGMA ")
    ]
    rendered = "\n".join(lines)
    rendered = re.sub(
        r"id\s+INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT",
        "id BIGSERIAL PRIMARY KEY",
        rendered,
        flags=re.IGNORECASE,
    )
    return rendered.strip() + "\n"


@dataclass
class PostgresCursorAdapter:
    cursor: Any

    def fetchone(self):
        row = self.cursor.fetchone()
        return _row_dict(self.cursor, row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [_row_dict(self.cursor, row) for row in rows]


class PostgresConnectionAdapter:
    """Expose the subset of sqlite3.Connection consumed by StateStore."""

    dialect = "postgres"

    def __init__(self, connection: Any) -> None:
        self.raw = connection
        self._in_transaction = False

    @property
    def in_transaction(self) -> bool:
        return self._in_transaction

    def execute(self, sql: str, parameters: Iterable[Any] = ()) -> PostgresCursorAdapter:
        cursor = self.raw.cursor()
        cursor.execute(postgres_sql(sql), tuple(parameters))
        self._in_transaction = True
        return PostgresCursorAdapter(cursor)

    def executescript(self, script: str) -> None:
        cursor = self.raw.cursor()
        cursor.execute(script)
        self._in_transaction = True

    def commit(self) -> None:
        self.raw.commit()
        self._in_transaction = False

    def rollback(self) -> None:
        self.raw.rollback()
        self._in_transaction = False

    def close(self) -> None:
        self.raw.close()

    def __enter__(self) -> "PostgresConnectionAdapter":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()


def _row_dict(cursor: Any, row: Any):
    if row is None or isinstance(row, dict):
        return row
    description = getattr(cursor, "description", None)
    if description and isinstance(row, (tuple, list)):
        names = [column[0] for column in description]
        return dict(zip(names, row))
    return row
