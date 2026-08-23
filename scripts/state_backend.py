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
        del project_id  # SQLite serializes all writers for this local database.
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
    """Reference Postgres transaction boundary using a project advisory lock.

    The connection is any DB-API-style connection whose cursor supports execute().
    No Postgres driver is imported here; deployments may supply psycopg or another
    compatible driver without making it a dependency of the local-first core.
    """

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
    """Return the backend used by the current local StateStore.

    StateStore remains SQLite-backed in this slice; routing this decision through
    one function lets concurrency-critical operations stop depending on SQLite
    syntax before the full shared-store constructor is introduced.
    """
    return SQLiteStateBackend(store.conn)
