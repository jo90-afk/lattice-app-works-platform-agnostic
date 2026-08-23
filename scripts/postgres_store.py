#!/usr/bin/env python3
"""Postgres-backed construction for the canonical Lattice StateStore."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from sql_dialect import PostgresConnectionAdapter, postgres_schema
from state_engine import LatticeError, SNAPSHOT_TABLES, StateStore, utc_now


SNAPSHOT_ORDER = {
    "projects": "id",
    "objectives": "id",
    "milestones": "id",
    "records": "id",
    "record_versions": "record_id, version",
    "truths": "id",
    "truth_versions": "truth_id, version",
    "truth_links": "from_truth_id, to_truth_id, relation",
    "truth_transitions": "id",
    "conditions": "id",
    "condition_inputs": "condition_id, record_id",
    "condition_truths": "condition_id, truth_id",
    "condition_dependencies": "condition_id, depends_on_condition_id",
    "condition_reviewers": "condition_id, role",
    "submissions": "id",
    "reviews": "id",
    "evidence": "id",
    "commitments": "id",
    "exceptions": "id",
    "events": "id",
}


class PostgresStateStore(StateStore):
    """Run the guarded StateStore semantics on a supplied Postgres connection.

    Postgres is the operational authority after bootstrap. A repository snapshot is
    imported automatically only into an empty operational store. Implicit exports
    return an in-memory portable projection; callers must supply a destination to
    publish a checkpoint file.
    """

    state_backend_name = "postgres"

    def __init__(
        self,
        root: Path,
        connection: Any,
        snapshot_path: Path | None = None,
    ) -> None:
        self.root = root.resolve()
        self.policy = json.loads((self.root / "runtime" / "policy.json").read_text(encoding="utf-8"))
        self.db_path = None
        self.snapshot_path = snapshot_path or self.root / "state" / "current.json"
        self.conn = PostgresConnectionAdapter(connection)
        self.conn.executescript(
            postgres_schema((self.root / "runtime" / "schema.sql").read_text(encoding="utf-8"))
        )
        self.conn.commit()
        self._ensure_meta()

        project_count = int(self.conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0])
        if project_count == 0 and self.revision == 0 and self.snapshot_path.is_file():
            snapshot_raw = self.snapshot_path.read_text(encoding="utf-8")
            snapshot_hash = hashlib.sha256(snapshot_raw.encode("utf-8")).hexdigest()
            self._load_snapshot(json.loads(snapshot_raw))
            with self.conn:
                self.conn.execute(
                    "UPDATE meta SET value = ? WHERE key = 'snapshot_hash'", (snapshot_hash,)
                )

    def _load_snapshot(self, snapshot: dict[str, Any]) -> None:
        super()._load_snapshot(snapshot)
        # Explicit event IDs are portable snapshot data. Repair the Postgres
        # sequence so the next operational event continues after the imported max.
        with self.conn:
            self.conn.execute(
                """SELECT setval(
                       pg_get_serial_sequence('events', 'id'),
                       GREATEST(COALESCE(MAX(id), 1), 1),
                       MAX(id) IS NOT NULL
                   ) FROM events"""
            )

    def _snapshot_payload(self) -> dict[str, Any]:
        tables: dict[str, list[dict[str, Any]]] = {}
        for table in SNAPSHOT_TABLES:
            order = SNAPSHOT_ORDER[table]
            rows = self.conn.execute("SELECT * FROM " + table + " ORDER BY " + order).fetchall()
            tables[table] = [dict(row) for row in rows]
        return {
            "format": "lattice-state-snapshot",
            "schema_version": self.policy["schema_version"],
            "agency_version": self.policy["agency_version"],
            "revision": self.revision,
            "exported_at": utc_now(),
            "ephemeral_state_excluded": ["leases"],
            "tables": tables,
        }

    def export_snapshot(self, destination: Path | None = None) -> dict[str, Any]:
        payload = self._snapshot_payload()
        if destination is None:
            return payload

        target = destination.resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(target)
        if target == self.snapshot_path.resolve():
            snapshot_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
            with self.conn:
                self.conn.execute(
                    "UPDATE meta SET value = ? WHERE key = 'snapshot_hash'", (snapshot_hash,)
                )
        return payload

    def import_snapshot(self, source: Path, expected_revision: int | None = None) -> None:
        """Explicit import remains available but is never performed implicitly on a live store."""
        if expected_revision is not None and self.revision != expected_revision:
            raise LatticeError(
                f"State revision changed: expected {expected_revision}, current {self.revision}"
            )
        snapshot = json.loads(source.read_text(encoding="utf-8"))
        active_leases = int(
            self.conn.execute("SELECT COUNT(*) FROM leases WHERE expires_at > ?", (utc_now(),)).fetchone()[0]
        )
        if active_leases:
            raise LatticeError("Cannot import a shared-state checkpoint while action leases are active")
        self._load_snapshot(snapshot)
