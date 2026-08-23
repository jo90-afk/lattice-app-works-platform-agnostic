#!/usr/bin/env python3
"""Postgres-backed construction for the canonical Lattice StateStore."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from sql_dialect import PostgresConnectionAdapter, postgres_schema
from state_backend import PostgresStateBackend
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
    """Run canonical StateStore semantics with intrinsic project serialization.

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

    def _bump_revision(self) -> int:
        """Atomically allocate one global snapshot revision across all projects."""
        row = self.conn.execute(
            """UPDATE meta
               SET value = (CAST(value AS BIGINT) + 1)::text
               WHERE key = 'revision'
               RETURNING value"""
        ).fetchone()
        if row is None:
            raise LatticeError("Postgres state meta has no revision row")
        return int(row[0])

    def _project_write(self, project_id: str, operation: Callable[[], Any]) -> Any:
        """Serialize a direct semantic mutation for one project.

        High-level host wrappers may already hold the same advisory lock. Postgres
        transaction advisory locks are re-entrant for the owning transaction, so
        acquiring the canonical project lock here keeps direct StateStore callers
        safe without creating a separate authority path.
        """
        backend = PostgresStateBackend(self.conn.raw)
        try:
            backend.begin_project_write(project_id)
            result = operation()
            # Canonical StateStore methods commit their semantic transition and may
            # then open a read transaction while producing the portable projection.
            # A final commit releases either that read transaction or a no-op lock
            # acquired by a method that returned without mutation.
            backend.commit()
            return result
        except Exception:
            backend.rollback()
            raise

    def _project_for_truth(self, truth_id: str) -> str:
        row = self.conn.execute(
            "SELECT project_id FROM truths WHERE id = ?", (truth_id,)
        ).fetchone()
        if row is None:
            raise LatticeError("Unknown truth: " + truth_id)
        return str(row["project_id"])

    # Direct semantic methods are project-serialized intrinsically. Leased action
    # lifecycle methods already enter the same boundary through lifecycle.py and
    # hosted_delta.py; those wrappers remain responsible for lease/revision guards.
    def ensure_project(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).ensure_project(project_id, *args, **kwargs)
        )

    def set_project_status(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).set_project_status(project_id, *args, **kwargs)
        )

    def add_objective(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).add_objective(project_id, *args, **kwargs)
        )

    def add_milestone(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).add_milestone(project_id, *args, **kwargs)
        )

    def put_record(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).put_record(project_id, *args, **kwargs)
        )

    def add_truth(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).add_truth(project_id, *args, **kwargs)
        )

    def revise_truth(self, truth_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        project_id = self._project_for_truth(truth_id)
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).revise_truth(truth_id, *args, **kwargs)
        )

    def move_truth(self, truth_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        project_id = self._project_for_truth(truth_id)
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).move_truth(truth_id, *args, **kwargs)
        )

    def link_truths(self, from_truth_id: str, *args: Any, **kwargs: Any) -> None:
        project_id = self._project_for_truth(from_truth_id)
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).link_truths(from_truth_id, *args, **kwargs)
        )

    def add_condition(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).add_condition(project_id, *args, **kwargs)
        )

    def add_commitment(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).add_commitment(project_id, *args, **kwargs)
        )

    def raise_exception(self, project_id: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._project_write(
            project_id, lambda: super(PostgresStateStore, self).raise_exception(project_id, *args, **kwargs)
        )

    def _load_snapshot(self, snapshot: dict[str, Any]) -> None:
        super()._load_snapshot(snapshot)
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
