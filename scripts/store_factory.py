#!/usr/bin/env python3
"""Construct the local or shared Lattice state store from deployment configuration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from postgres_store import PostgresStateStore
from state_engine import LatticeError, StateStore


def open_state_store(
    root: Path,
    *,
    database_url: str | None = None,
    snapshot_path: Path | None = None,
) -> StateStore:
    """Open SQLite by default or Postgres when an explicit URL is supplied.

    Postgres driver loading is lazy so the default installation remains Python
    standard library + SQLite. Shared deployments install `psycopg` separately.
    """
    url = database_url if database_url is not None else os.environ.get("LATTICE_DATABASE_URL")
    if not url:
        return StateStore(root, snapshot_path=snapshot_path)
    if not url.startswith(("postgres://", "postgresql://")):
        raise LatticeError("Unsupported LATTICE_DATABASE_URL scheme")
    try:
        import psycopg  # type: ignore
    except ImportError as error:
        raise LatticeError(
            "Postgres state requires the optional psycopg driver; install psycopg[binary] or psycopg"
        ) from error
    connection: Any = psycopg.connect(url)
    return PostgresStateStore(root, connection, snapshot_path=snapshot_path)
