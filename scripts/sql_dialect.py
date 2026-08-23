#!/usr/bin/env python3
"""Small SQL compatibility layer for one StateStore across SQLite and Postgres."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Mapping


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


class CompatibleRow(Mapping[str, Any]):
    """Mapping row that also preserves sqlite3.Row integer indexing."""

    def __init__(self, names: list[str], values: Iterable[Any]) -> None:
        self._names = names
        self._values = tuple(values)
        self._mapping = dict(zip(names, self._values))

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._values[key]
        return self._mapping[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._names)

    def __len__(self) -> int:
        return len(self._names)


@dataclass
class PostgresCursorAdapter:
    cursor: Any

    def fetchone(self):
        row = self.cursor.fetchone()
        return _compatible_row(self.cursor, row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [_compatible_row(self.cursor, row) for row in rows]


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
        for statement in script.split(";"):
            if statement.strip():
                cursor.execute(statement)
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


def _compatible_row(cursor: Any, row: Any):
    if row is None or isinstance(row, CompatibleRow):
        return row
    if isinstance(row, dict):
        return CompatibleRow(list(row), row.values())
    description = getattr(cursor, "description", None)
    if description and isinstance(row, (tuple, list)):
        names = [column[0] for column in description]
        return CompatibleRow(names, row)
    return row
