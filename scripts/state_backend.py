#!/usr/bin/env python3
"""Operational transaction adapters for concurrency-critical Lattice writes."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Protocol


class StateBackendError(RuntimeError):
    """A state backend could not provide the required transaction semantics."""


class StateBackend(Protocol):
    name: str

    def begin_project_write(self, project_id: str) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


@dataclass
class SQLiteStateBackend:
    """Serialize a concurrency-critical write using SQLite's single writer lock."""

    connection: Any
    name: str = "sqlite"

    def begin_project_write(self, project_id: str) -> None:
        del project_id
        self.connection.execute("BEGIN IMMEDIATE")

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        if getattr(self.connection, "in_transaction", True):
            self.connection.rollback()


def project_lock_key(project_id: str) -> int:
    """Stable signed 63-bit advisory-lock key shared across runtimes."""
    digest = hashlib.sha256(project_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") & 0x7FFF_FFFF_FFFF_FFFF


@dataclass
class PostgresStateBackend:
    """Postgres transaction boundary using a project advisory lock."""

    connection: Any
    name: str = "postgres"

    def begin_project_write(self, project_id: str) -> None:
        cursor = self.connection.cursor()
        cursor.execute("BEGIN")
        cursor.execute("SELECT pg_advisory_xact_lock(%s)", (project_lock_key(project_id),))

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()


def backend_for_store(store: Any) -> StateBackend:
    """Return the transaction backend matching the store connection dialect."""
    connection = store.conn
    if getattr(connection, "dialect", None) == "postgres":
        return PostgresStateBackend(connection.raw)
    return SQLiteStateBackend(connection)
