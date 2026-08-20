#!/usr/bin/env python3
"""Guarded SQLite state engine for Lattice's active-frontier runtime."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


SNAPSHOT_TABLES = [
    "projects",
    "objectives",
    "milestones",
    "records",
    "record_versions",
    "truths",
    "truth_versions",
    "truth_links",
    "truth_transitions",
    "conditions",
    "condition_inputs",
    "condition_truths",
    "condition_dependencies",
    "condition_reviewers",
    "submissions",
    "reviews",
    "evidence",
    "commitments",
    "exceptions",
    "events",
]

SEVERITY_SCORE = {"critical": 40, "major": 25, "minor": 10, "note": 0}


class LatticeError(RuntimeError):
    """A guarded state transition was rejected."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_id(prefix: str) -> str:
    return prefix + "-" + uuid.uuid4().hex[:12]


def stable_hash(*values: str | None) -> str:
    payload = "\x1f".join(value or "" for value in values)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def json_text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class StateStore:
    """Owns operational state; agents mutate it only through guarded methods."""

    def __init__(
        self,
        root: Path,
        db_path: Path | None = None,
        snapshot_path: Path | None = None,
    ) -> None:
        self.root = root.resolve()
        self.policy = json.loads((self.root / "runtime" / "policy.json").read_text(encoding="utf-8"))
        self.db_path = db_path or self.root / ".lattice" / "state.db"
        self.snapshot_path = snapshot_path or self.root / "state" / "current.json"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        created = not self.db_path.exists()
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA busy_timeout = 5000")
        self.conn.executescript((self.root / "runtime" / "schema.sql").read_text(encoding="utf-8"))
        self._ensure_meta()
        if self.snapshot_path.is_file():
            snapshot_raw = self.snapshot_path.read_text(encoding="utf-8")
            snapshot_hash = hashlib.sha256(snapshot_raw.encode("utf-8")).hexdigest()
            stored_hash_row = self.conn.execute(
                "SELECT value FROM meta WHERE key = 'snapshot_hash'"
            ).fetchone()
            stored_hash = stored_hash_row[0] if stored_hash_row else ""
            if created or stored_hash != snapshot_hash:
                active_leases = self.conn.execute(
                    "SELECT COUNT(*) FROM leases WHERE expires_at > ?", (utc_now(),)
                ).fetchone()[0]
                if active_leases and not created:
                    raise LatticeError(
                        "The repository snapshot changed while local action leases are active; "
                        "finish or release them before switching state revisions."
                    )
                self._load_snapshot(json.loads(snapshot_raw))
                with self.conn:
                    self.conn.execute(
                        "UPDATE meta SET value = ? WHERE key = 'snapshot_hash'", (snapshot_hash,)
                    )

    def close(self) -> None:
        self.conn.close()

    def __enter__(self) -> "StateStore":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _ensure_meta(self) -> None:
        with self.conn:
            self.conn.execute(
                "INSERT OR IGNORE INTO meta(key, value) VALUES('schema_version', ?)",
                (str(self.policy["schema_version"]),),
            )
            self.conn.execute(
                "INSERT OR IGNORE INTO meta(key, value) VALUES('agency_version', ?)",
                (self.policy["agency_version"],),
            )
            self.conn.execute("INSERT OR IGNORE INTO meta(key, value) VALUES('revision', '0')")
            self.conn.execute("INSERT OR IGNORE INTO meta(key, value) VALUES('snapshot_hash', '')")

    @property
    def revision(self) -> int:
        row = self.conn.execute("SELECT value FROM meta WHERE key = 'revision'").fetchone()
        return int(row[0]) if row else 0

    def project_revision(self, project_id: str) -> int:
        self._require_project(project_id)
        row = self.conn.execute(
            "SELECT COALESCE(MAX(revision), 0) FROM events WHERE project_id = ?", (project_id,)
        ).fetchone()
        return int(row[0])

    def _bump_revision(self) -> int:
        revision = self.revision + 1
        self.conn.execute("UPDATE meta SET value = ? WHERE key = 'revision'", (str(revision),))
        return revision

    def _event(
        self,
        revision: int,
        project_id: str | None,
        event_type: str,
        entity_type: str,
        entity_id: str,
        role: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.conn.execute(
            """INSERT INTO events(
                   revision, project_id, event_type, entity_type, entity_id, role, payload_json, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (revision, project_id, event_type, entity_type, entity_id, role, json_text(payload or {}), utc_now()),
        )

    def _validate_role(self, role: str) -> None:
        if role not in self.policy["roles"]:
            raise LatticeError("Unknown role: " + role)

    def _require_project(self, project_id: str) -> sqlite3.Row:
        row = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if row is None:
            raise LatticeError("Unknown project: " + project_id)
        return row

    def _load_snapshot(self, snapshot: dict[str, Any]) -> None:
        if snapshot.get("format") != "lattice-state-snapshot":
            raise LatticeError("Unsupported state snapshot format")
        if int(snapshot.get("schema_version", -1)) != int(self.policy["schema_version"]):
            raise LatticeError("State snapshot schema version does not match the runtime")
        tables = snapshot.get("tables")
        if not isinstance(tables, dict):
            raise LatticeError("State snapshot has no tables object")
        with self.conn:
            for table in reversed(SNAPSHOT_TABLES):
                self.conn.execute("DELETE FROM " + table)
            for table in SNAPSHOT_TABLES:
                rows = tables.get(table, [])
                if not isinstance(rows, list):
                    raise LatticeError("Invalid snapshot table: " + table)
                for row in rows:
                    if not isinstance(row, dict) or not row:
                        continue
                    columns = list(row)
                    placeholders = ", ".join("?" for _ in columns)
                    self.conn.execute(
                        "INSERT INTO " + table + " (" + ", ".join(columns) + ") VALUES (" + placeholders + ")",
                        [row[column] for column in columns],
                    )
            self.conn.execute(
                "UPDATE meta SET value = ? WHERE key = 'revision'",
                (str(int(snapshot.get("revision", 0))),),
            )

    def export_snapshot(self, destination: Path | None = None) -> dict[str, Any]:
        target = destination or self.snapshot_path
        target.parent.mkdir(parents=True, exist_ok=True)
        tables: dict[str, list[dict[str, Any]]] = {}
        for table in SNAPSHOT_TABLES:
            order = "id" if table not in {"condition_inputs", "condition_truths", "condition_dependencies", "condition_reviewers", "truth_links", "record_versions", "truth_versions"} else "rowid"
            rows = self.conn.execute("SELECT * FROM " + table + " ORDER BY " + order).fetchall()
            tables[table] = [dict(row) for row in rows]
        payload = {
            "format": "lattice-state-snapshot",
            "schema_version": self.policy["schema_version"],
            "agency_version": self.policy["agency_version"],
            "revision": self.revision,
            "exported_at": utc_now(),
            "ephemeral_state_excluded": ["leases"],
            "tables": tables,
        }
        temporary = target.with_suffix(target.suffix + ".tmp")
        serialized = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(target)
        if target.resolve() == self.snapshot_path.resolve():
            snapshot_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
            with self.conn:
                self.conn.execute(
                    "UPDATE meta SET value = ? WHERE key = 'snapshot_hash'", (snapshot_hash,)
                )
        return payload

    def import_snapshot(self, source: Path, expected_revision: int | None = None) -> None:
        snapshot = json.loads(source.read_text(encoding="utf-8"))
        if expected_revision is not None and self.revision != expected_revision:
            raise LatticeError(
                f"State revision changed: expected {expected_revision}, current {self.revision}"
            )
        self._load_snapshot(snapshot)
        self.export_snapshot()

    def ensure_project(
        self,
        project_id: str,
        name: str,
        status: str = "active",
        max_wip: int | None = None,
        role: str = "director",
    ) -> dict[str, Any]:
        self._validate_role(role)
        if role not in {"director", "principal"}:
            raise LatticeError("Only the Director or Principal may register projects")
        if status not in {"active", "paused", "closed"}:
            raise LatticeError("Invalid project status: " + status)
        now = utc_now()
        wip = max_wip or int(self.policy["default_project_wip"])
        with self.conn:
            existing = self.conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
            if existing:
                return dict(existing)
            revision = self._bump_revision()
            self.conn.execute(
                "INSERT INTO projects(id, name, status, max_wip, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (project_id, name, status, wip, now, now),
            )
            self._event(revision, project_id, "project_registered", "project", project_id, role, {"name": name})
        self.export_snapshot()
        return dict(self._require_project(project_id))

    def rename_project(self, old_id: str, new_id: str, name: str, role: str = "director") -> None:
        self._validate_role(role)
        if role not in {"director", "principal"}:
            raise LatticeError("Only the Director or Principal may initialize project identity")
        self._require_project(old_id)
        if self.conn.execute("SELECT 1 FROM projects WHERE id = ?", (new_id,)).fetchone():
            raise LatticeError("Project already exists: " + new_id)
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                "UPDATE projects SET id = ?, name = ?, status = 'active', updated_at = ? WHERE id = ?",
                (new_id, name, utc_now(), old_id),
            )
            self._event(
                revision,
                new_id,
                "project_initialized",
                "project",
                new_id,
                role,
                {"previous_id": old_id, "name": name},
            )
        self.export_snapshot()

    def set_project_status(self, project_id: str, status: str, role: str = "director") -> dict[str, Any]:
        self._validate_role(role)
        if role not in {"director", "principal"}:
            raise LatticeError("Only the Director or Principal may change project lifecycle")
        if status not in {"active", "paused", "closed"}:
            raise LatticeError("Invalid project status: " + status)
        project = self._require_project(project_id)
        if project["status"] == status:
            return dict(project)
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                "UPDATE projects SET status = ?, updated_at = ? WHERE id = ?",
                (status, utc_now(), project_id),
            )
            self._event(
                revision, project_id, "project_status_changed", "project", project_id, role,
                {"from": project["status"], "to": status},
            )
        self.export_snapshot()
        return dict(self._require_project(project_id))

    def add_objective(
        self,
        project_id: str,
        title: str,
        description: str,
        owner_role: str,
        priority: int = 50,
        objective_id: str | None = None,
        role: str = "director",
    ) -> dict[str, Any]:
        self._validate_role(role)
        if role not in {"director", "product", "principal"}:
            raise LatticeError("Only Product, the Director, or the Principal may activate an objective")
        self._validate_role(owner_role)
        project = self._require_project(project_id)
        if project["status"] != "active":
            raise LatticeError("Activate the project before creating an objective")
        if self.conn.execute(
            "SELECT 1 FROM objectives WHERE project_id = ? AND status = 'active'", (project_id,)
        ).fetchone():
            raise LatticeError("Project already has an active objective")
        identifier = objective_id or new_id("obj")
        now = utc_now()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT INTO objectives(
                       id, project_id, title, description, status, priority, owner_role, created_at, updated_at
                   ) VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?)""",
                (identifier, project_id, title, description, priority, owner_role, now, now),
            )
            self._event(revision, project_id, "objective_activated", "objective", identifier, role, {"title": title})
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM objectives WHERE id = ?", (identifier,)).fetchone())

    def add_milestone(
        self,
        project_id: str,
        objective_id: str,
        title: str,
        ordinal: int,
        activate: bool = False,
        milestone_id: str | None = None,
        role: str = "director",
    ) -> dict[str, Any]:
        self._validate_role(role)
        if role not in {"director", "product", "principal"}:
            raise LatticeError("Only Product, the Director, or the Principal may add a milestone")
        self._require_project(project_id)
        objective = self.conn.execute(
            "SELECT * FROM objectives WHERE id = ? AND project_id = ?", (objective_id, project_id)
        ).fetchone()
        if objective is None:
            raise LatticeError("Objective does not belong to project")
        if activate and self.conn.execute(
            "SELECT 1 FROM milestones WHERE project_id = ? AND status = 'active'", (project_id,)
        ).fetchone():
            raise LatticeError("Project already has an active milestone")
        if not activate:
            if not self.conn.execute(
                "SELECT 1 FROM milestones WHERE project_id = ? AND status = 'active'", (project_id,)
            ).fetchone():
                raise LatticeError("A planned successor requires an active milestone")
            if self.conn.execute(
                "SELECT 1 FROM milestones WHERE project_id = ? AND status = 'planned'", (project_id,)
            ).fetchone():
                raise LatticeError("Project already has a planned successor milestone")
        identifier = milestone_id or new_id("ms")
        status = "active" if activate else "planned"
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT INTO milestones(
                       id, project_id, objective_id, title, ordinal, status, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (identifier, project_id, objective_id, title, ordinal, status, utc_now()),
            )
            self._event(revision, project_id, "milestone_added", "milestone", identifier, role, {"status": status})
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM milestones WHERE id = ?", (identifier,)).fetchone())

    def put_record(
        self,
        project_id: str,
        key: str,
        kind: str,
        title: str,
        body: str,
        owner_role: str,
        changed_by: str,
        source_ref: str | None = None,
        status: str = "current",
        reason: str = "state updated",
        record_id: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(changed_by)
        self._validate_role(owner_role)
        if changed_by != owner_role:
            raise LatticeError("Only the declared record owner may create or revise the record")
        self._require_project(project_id)
        if kind not in {"requirement", "constraint", "decision", "artifact", "risk", "contract"}:
            raise LatticeError("Invalid record kind: " + kind)
        if status not in {"current", "invalidated", "superseded"}:
            raise LatticeError("Invalid record status: " + status)
        content_hash = stable_hash(kind, title, body, status, source_ref)
        existing = self.conn.execute(
            "SELECT * FROM records WHERE project_id = ? AND key = ?", (project_id, key)
        ).fetchone()
        if existing and existing["owner_role"] != owner_role:
            raise LatticeError("Record ownership cannot be reassigned by an ordinary state update")
        now = utc_now()
        if existing and existing["content_hash"] == content_hash and existing["owner_role"] == owner_role:
            return dict(existing)
        with self.conn:
            revision = self._bump_revision()
            if existing:
                identifier = existing["id"]
                version = existing["version"] + 1
                self.conn.execute(
                    """UPDATE records SET kind = ?, title = ?, body = ?, status = ?, version = ?,
                       owner_role = ?, source_ref = ?, content_hash = ?, updated_at = ? WHERE id = ?""",
                    (kind, title, body, status, version, owner_role, source_ref, content_hash, now, identifier),
                )
            else:
                identifier = record_id or new_id("rec")
                version = 1
                self.conn.execute(
                    """INSERT INTO records(
                           id, project_id, key, kind, title, body, status, version, owner_role,
                           source_ref, content_hash, created_at, updated_at
                       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        identifier, project_id, key, kind, title, body, status, version, owner_role,
                        source_ref, content_hash, now, now,
                    ),
                )
            self.conn.execute(
                """INSERT INTO record_versions(
                       record_id, version, title, body, status, source_ref, content_hash,
                       changed_by, change_reason, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (identifier, version, title, body, status, source_ref, content_hash, changed_by, reason, now),
            )
            self._event(
                revision, project_id, "record_created" if version == 1 else "record_revised",
                "record", identifier, changed_by, {"key": key, "version": version, "reason": reason},
            )
            if version > 1:
                self._invalidate_for_record(identifier, revision, changed_by, reason)
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM records WHERE id = ?", (identifier,)).fetchone())

    def add_truth(
        self,
        project_id: str,
        key: str,
        statement: str,
        epistemic_status: str,
        attention_state: str,
        created_by: str,
        confidence: float | None = None,
        source_ref: str | None = None,
        material: bool = False,
        truth_id: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(created_by)
        self._require_project(project_id)
        if epistemic_status not in self.policy["truth_epistemic_states"]:
            raise LatticeError("Invalid epistemic status: " + epistemic_status)
        if attention_state not in self.policy["truth_attention_states"]:
            raise LatticeError("Invalid attention state: " + attention_state)
        if confidence is not None and not 0 <= confidence <= 1:
            raise LatticeError("Confidence must be between 0 and 1")
        identifier = truth_id or new_id("truth")
        now = utc_now()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT INTO truths(
                       id, project_id, key, statement, epistemic_status, attention_state,
                       confidence, source_ref, material, version, created_by, created_at, updated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?)""",
                (
                    identifier, project_id, key, statement, epistemic_status, attention_state,
                    confidence, source_ref, int(material), created_by, now, now,
                ),
            )
            self.conn.execute(
                """INSERT INTO truth_versions(
                       truth_id, version, statement, epistemic_status, confidence, source_ref,
                       material, changed_by, change_reason, created_at
                   ) VALUES (?, 1, ?, ?, ?, ?, ?, ?, 'truth recorded', ?)""",
                (identifier, statement, epistemic_status, confidence, source_ref, int(material), created_by, now),
            )
            self._event(
                revision, project_id, "truth_recorded", "truth", identifier, created_by,
                {"key": key, "attention": attention_state, "epistemic_status": epistemic_status},
            )
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM truths WHERE id = ?", (identifier,)).fetchone())

    def revise_truth(
        self,
        truth_id: str,
        changed_by: str,
        reason: str,
        statement: str | None = None,
        epistemic_status: str | None = None,
        confidence: float | None = None,
        source_ref: str | None = None,
        material: bool | None = None,
    ) -> dict[str, Any]:
        self._validate_role(changed_by)
        current = self.conn.execute("SELECT * FROM truths WHERE id = ?", (truth_id,)).fetchone()
        if current is None:
            raise LatticeError("Unknown truth: " + truth_id)
        new_status = epistemic_status or current["epistemic_status"]
        if new_status not in self.policy["truth_epistemic_states"]:
            raise LatticeError("Invalid epistemic status: " + new_status)
        new_confidence = current["confidence"] if confidence is None else confidence
        if new_confidence is not None and not 0 <= new_confidence <= 1:
            raise LatticeError("Confidence must be between 0 and 1")
        values = {
            "statement": statement if statement is not None else current["statement"],
            "epistemic_status": new_status,
            "confidence": new_confidence,
            "source_ref": source_ref if source_ref is not None else current["source_ref"],
            "material": int(material) if material is not None else current["material"],
        }
        version = current["version"] + 1
        now = utc_now()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """UPDATE truths SET statement = ?, epistemic_status = ?, confidence = ?,
                   source_ref = ?, material = ?, version = ?, updated_at = ? WHERE id = ?""",
                (
                    values["statement"], values["epistemic_status"], values["confidence"],
                    values["source_ref"], values["material"], version, now, truth_id,
                ),
            )
            self.conn.execute(
                """INSERT INTO truth_versions(
                       truth_id, version, statement, epistemic_status, confidence, source_ref,
                       material, changed_by, change_reason, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    truth_id, version, values["statement"], values["epistemic_status"],
                    values["confidence"], values["source_ref"], values["material"],
                    changed_by, reason, now,
                ),
            )
            self._event(
                revision, current["project_id"], "truth_revised", "truth", truth_id, changed_by,
                {"version": version, "reason": reason, "previous_status": current["epistemic_status"]},
            )
            self._invalidate_for_truth(truth_id, revision, changed_by, reason)
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM truths WHERE id = ?", (truth_id,)).fetchone())

    def move_truth(
        self, truth_id: str, attention_state: str, changed_by: str, reason: str
    ) -> dict[str, Any]:
        self._validate_role(changed_by)
        if attention_state not in self.policy["truth_attention_states"]:
            raise LatticeError("Invalid attention state: " + attention_state)
        truth = self.conn.execute("SELECT * FROM truths WHERE id = ?", (truth_id,)).fetchone()
        if truth is None:
            raise LatticeError("Unknown truth: " + truth_id)
        if truth["attention_state"] == attention_state:
            return dict(truth)
        with self.conn:
            revision = self._bump_revision()
            self._move_truth_attention(truth, attention_state, changed_by, reason, revision)
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM truths WHERE id = ?", (truth_id,)).fetchone())

    def _move_truth_attention(
        self,
        truth: sqlite3.Row,
        attention_state: str,
        changed_by: str,
        reason: str,
        revision: int,
    ) -> None:
        previous = truth["attention_state"]
        if previous == attention_state:
            return
        now = utc_now()
        self.conn.execute(
            "UPDATE truths SET attention_state = ?, updated_at = ? WHERE id = ?",
            (attention_state, now, truth["id"]),
        )
        transition_id = new_id("transition")
        self.conn.execute(
            """INSERT INTO truth_transitions(
                   id, truth_id, from_attention, to_attention, reason, changed_by, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (transition_id, truth["id"], previous, attention_state, reason, changed_by, now),
        )
        self._event(
            revision, truth["project_id"], "truth_attention_changed", "truth", truth["id"], changed_by,
            {"from": previous, "to": attention_state, "reason": reason},
        )

    def link_truths(
        self,
        from_truth_id: str,
        to_truth_id: str,
        relation: str,
        created_by: str,
    ) -> None:
        self._validate_role(created_by)
        if relation not in {"supports", "contradicts", "refines", "depends_on", "supersedes"}:
            raise LatticeError("Invalid truth relation: " + relation)
        source = self.conn.execute("SELECT * FROM truths WHERE id = ?", (from_truth_id,)).fetchone()
        target = self.conn.execute("SELECT * FROM truths WHERE id = ?", (to_truth_id,)).fetchone()
        if source is None or target is None:
            raise LatticeError("Both truths must exist")
        if source["project_id"] != target["project_id"]:
            raise LatticeError("Truth links cannot cross project capsules")
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT OR IGNORE INTO truth_links(
                       from_truth_id, to_truth_id, relation, created_by, created_at
                   ) VALUES (?, ?, ?, ?, ?)""",
                (from_truth_id, to_truth_id, relation, created_by, utc_now()),
            )
            self._event(
                revision, source["project_id"], "truths_linked", "truth_link",
                from_truth_id + ":" + to_truth_id, created_by, {"relation": relation},
            )
            if relation == "contradicts":
                for truth in (source, target):
                    latest = self.conn.execute("SELECT * FROM truths WHERE id = ?", (truth["id"],)).fetchone()
                    if latest["attention_state"] != "frontier":
                        self._move_truth_attention(
                            latest, "frontier", created_by, "material contradiction detected", revision
                        )
                    if latest["epistemic_status"] not in {"false", "superseded", "contested"}:
                        version = latest["version"] + 1
                        now = utc_now()
                        self.conn.execute(
                            "UPDATE truths SET epistemic_status = 'contested', version = ?, updated_at = ? WHERE id = ?",
                            (version, now, latest["id"]),
                        )
                        self.conn.execute(
                            """INSERT INTO truth_versions(
                                   truth_id, version, statement, epistemic_status, confidence, source_ref,
                                   material, changed_by, change_reason, created_at
                               ) VALUES (?, ?, ?, 'contested', ?, ?, ?, ?, ?, ?)""",
                            (
                                latest["id"], version, latest["statement"], latest["confidence"],
                                latest["source_ref"], latest["material"], created_by,
                                "contradiction linked", now,
                            ),
                        )
                        self._invalidate_for_truth(
                            latest["id"], revision, created_by, "linked truth contradicts this proposition"
                        )
        self.export_snapshot()

    def add_condition(
        self,
        project_id: str,
        objective_id: str,
        milestone_id: str,
        key: str,
        title: str,
        description: str,
        owner_role: str,
        verifier_role: str,
        created_by: str,
        priority: int = 50,
        severity: str = "major",
        attempt_budget: int | None = None,
        input_record_ids: Iterable[str] = (),
        truth_ids: Iterable[str] = (),
        depends_on: Iterable[str] = (),
        mandatory_reviewers: Iterable[str] = (),
        condition_id: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(created_by)
        if created_by not in self.policy["condition_creators"]:
            raise LatticeError(created_by + " may not create readiness conditions")
        self._validate_role(owner_role)
        self._validate_role(verifier_role)
        if owner_role == verifier_role:
            raise LatticeError("A condition owner cannot verify its own submission")
        if severity not in SEVERITY_SCORE:
            raise LatticeError("Invalid severity: " + severity)
        self._require_project(project_id)
        milestone = self.conn.execute(
            "SELECT * FROM milestones WHERE id = ? AND project_id = ? AND objective_id = ?",
            (milestone_id, project_id, objective_id),
        ).fetchone()
        if milestone is None:
            raise LatticeError("Milestone does not belong to the project objective")
        if milestone["status"] not in {"active", "planned"}:
            raise LatticeError("Readiness conditions may be added only to active or immediate successor milestones")
        identifier = condition_id or new_id("cond")
        reviewers = list(dict.fromkeys(mandatory_reviewers))
        for reviewer in reviewers:
            self._validate_role(reviewer)
            if reviewer == owner_role:
                raise LatticeError("A condition owner cannot be a mandatory reviewer")
        inputs = list(dict.fromkeys(input_record_ids))
        truths = list(dict.fromkeys(truth_ids))
        dependencies = list(dict.fromkeys(depends_on))
        now = utc_now()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT INTO conditions(
                       id, project_id, objective_id, milestone_id, key, title, description,
                       owner_role, verifier_role, priority, severity, status, state_version,
                       attempt_count, attempt_budget, created_at, updated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'unknown', 1, 0, ?, ?, ?)""",
                (
                    identifier, project_id, objective_id, milestone_id, key, title, description,
                    owner_role, verifier_role, priority, severity,
                    attempt_budget or int(self.policy["default_retry_budget"]), now, now,
                ),
            )
            self.conn.execute(
                "INSERT INTO condition_reviewers(condition_id, role, review_kind) VALUES (?, ?, 'primary')",
                (identifier, verifier_role),
            )
            for reviewer in reviewers:
                if reviewer == verifier_role:
                    continue
                self.conn.execute(
                    "INSERT INTO condition_reviewers(condition_id, role, review_kind) VALUES (?, ?, 'mandatory')",
                    (identifier, reviewer),
                )
            for record_id in inputs:
                record = self.conn.execute(
                    "SELECT * FROM records WHERE id = ? AND project_id = ?", (record_id, project_id)
                ).fetchone()
                if record is None:
                    raise LatticeError("Condition input is not in the project: " + record_id)
                self.conn.execute(
                    "INSERT INTO condition_inputs(condition_id, record_id) VALUES (?, ?)",
                    (identifier, record_id),
                )
            for truth_id in truths:
                truth = self.conn.execute(
                    "SELECT * FROM truths WHERE id = ? AND project_id = ?", (truth_id, project_id)
                ).fetchone()
                if truth is None:
                    raise LatticeError("Condition truth is not in the project: " + truth_id)
                self.conn.execute(
                    "INSERT INTO condition_truths(condition_id, truth_id) VALUES (?, ?)",
                    (identifier, truth_id),
                )
                if milestone["status"] == "active" and truth["attention_state"] != "frontier":
                    self._move_truth_attention(
                        truth, "frontier", created_by, "linked to active readiness condition " + identifier, revision
                    )
            for dependency_id in dependencies:
                dependency = self.conn.execute(
                    "SELECT * FROM conditions WHERE id = ? AND project_id = ?", (dependency_id, project_id)
                ).fetchone()
                if dependency is None:
                    raise LatticeError("Condition dependency is not in the project: " + dependency_id)
                self.conn.execute(
                    "INSERT INTO condition_dependencies(condition_id, depends_on_condition_id) VALUES (?, ?)",
                    (identifier, dependency_id),
                )
            self._event(
                revision, project_id, "condition_added", "condition", identifier, created_by,
                {"key": key, "owner_role": owner_role, "verifier_role": verifier_role},
            )
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM conditions WHERE id = ?", (identifier,)).fetchone())

    def _invalidate_for_record(self, record_id: str, revision: int, role: str, reason: str) -> None:
        rows = self.conn.execute(
            """SELECT c.id FROM condition_inputs ci
               JOIN conditions c ON c.id = ci.condition_id
               JOIN milestones m ON m.id = c.milestone_id
               WHERE ci.record_id = ? AND m.status = 'active'""",
            (record_id,),
        ).fetchall()
        for row in rows:
            self._invalidate_condition(row["id"], revision, role, "input record changed: " + reason, set())

    def _invalidate_for_truth(self, truth_id: str, revision: int, role: str, reason: str) -> None:
        rows = self.conn.execute(
            """SELECT c.id FROM condition_truths ct
               JOIN conditions c ON c.id = ct.condition_id
               JOIN milestones m ON m.id = c.milestone_id
               WHERE ct.truth_id = ? AND m.status = 'active'""",
            (truth_id,),
        ).fetchall()
        for row in rows:
            self._invalidate_condition(row["id"], revision, role, "linked truth changed: " + reason, set())

    def _invalidate_condition(
        self,
        condition_id: str,
        revision: int,
        role: str,
        reason: str,
        visited: set[str],
    ) -> None:
        if condition_id in visited:
            return
        visited.add(condition_id)
        condition = self.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone()
        if condition is None or condition["status"] == "waived":
            return
        submission_ids = [
            row["id"]
            for row in self.conn.execute(
                "SELECT id FROM submissions WHERE condition_id = ? AND status = 'pending'", (condition_id,)
            ).fetchall()
        ]
        self.conn.execute(
            """UPDATE conditions SET status = 'unknown', state_version = state_version + 1,
               attempt_count = 0, updated_at = ? WHERE id = ?""",
            (utc_now(), condition_id),
        )
        self.conn.execute(
            "UPDATE submissions SET status = 'superseded' WHERE condition_id = ? AND status = 'pending'",
            (condition_id,),
        )
        self.conn.execute("DELETE FROM leases WHERE target_id = ?", (condition_id,))
        for submission_id in submission_ids:
            self.conn.execute("DELETE FROM leases WHERE target_id = ?", (submission_id,))
        self._event(
            revision, condition["project_id"], "condition_invalidated", "condition", condition_id, role,
            {"reason": reason},
        )
        dependents = self.conn.execute(
            "SELECT condition_id FROM condition_dependencies WHERE depends_on_condition_id = ?",
            (condition_id,),
        ).fetchall()
        for dependent in dependents:
            self._invalidate_condition(dependent["condition_id"], revision, role, "dependency invalidated", visited)

    def _active_lease_keys(self) -> set[str]:
        now = utc_now()
        return {
            row["action_key"]
            for row in self.conn.execute("SELECT action_key FROM leases WHERE expires_at > ?", (now,)).fetchall()
        }

    def _condition_context(self, condition_id: str) -> dict[str, Any]:
        condition = self.conn.execute(
            """SELECT c.*, o.title AS objective_title, m.title AS milestone_title
               FROM conditions c JOIN objectives o ON o.id = c.objective_id
               JOIN milestones m ON m.id = c.milestone_id WHERE c.id = ?""",
            (condition_id,),
        ).fetchone()
        if condition is None:
            raise LatticeError("Unknown condition: " + condition_id)
        records = [
            dict(row)
            for row in self.conn.execute(
                """SELECT r.id, r.key, r.kind, r.title, r.body, r.status, r.version,
                          r.owner_role, r.source_ref
                   FROM condition_inputs ci JOIN records r ON r.id = ci.record_id
                   WHERE ci.condition_id = ? ORDER BY r.kind, r.key""",
                (condition_id,),
            ).fetchall()
        ]
        truths = [
            dict(row)
            for row in self.conn.execute(
                """SELECT t.id, t.key, t.statement, t.epistemic_status, t.attention_state,
                          t.confidence, t.source_ref, t.material, t.version, ct.relevance
                   FROM condition_truths ct JOIN truths t ON t.id = ct.truth_id
                   WHERE ct.condition_id = ? ORDER BY t.key""",
                (condition_id,),
            ).fetchall()
        ]
        dependencies = [
            dict(row)
            for row in self.conn.execute(
                """SELECT d.id, d.key, d.title, d.status, d.state_version
                   FROM condition_dependencies cd JOIN conditions d ON d.id = cd.depends_on_condition_id
                   WHERE cd.condition_id = ? ORDER BY d.priority DESC, d.key""",
                (condition_id,),
            ).fetchall()
        ]
        attempts = [
            dict(row)
            for row in self.conn.execute(
                """SELECT id, attempt_no, summary, evidence_ref, status, created_at
                   FROM submissions WHERE condition_id = ? ORDER BY created_at DESC LIMIT 3""",
                (condition_id,),
            ).fetchall()
        ]
        return {
            "condition": dict(condition),
            "relevant_records": records,
            "relevant_truths": truths,
            "dependencies": dependencies,
            "recent_attempts": attempts,
        }

    def readiness(self, project_id: str, milestone_id: str | None = None) -> dict[str, Any]:
        project = self._require_project(project_id)
        if project["status"] != "active":
            return {"project_id": project_id, "ready": False, "reason": "project is not active"}
        if milestone_id:
            milestone = self.conn.execute(
                "SELECT * FROM milestones WHERE id = ? AND project_id = ?", (milestone_id, project_id)
            ).fetchone()
        else:
            milestone = self.conn.execute(
                "SELECT * FROM milestones WHERE project_id = ? AND status = 'active'", (project_id,)
            ).fetchone()
        if milestone is None:
            return {"project_id": project_id, "ready": False, "reason": "no active milestone"}
        conditions = [
            dict(row)
            for row in self.conn.execute(
                "SELECT id, key, title, status, severity, owner_role, verifier_role FROM conditions WHERE milestone_id = ? ORDER BY priority DESC, key",
                (milestone["id"],),
            ).fetchall()
        ]
        blockers = [
            dict(row)
            for row in self.conn.execute(
                """SELECT id, title, severity, owner_role, principal_only FROM exceptions
                   WHERE project_id = ? AND status = 'open' AND severity IN ('critical', 'major')
                   ORDER BY CASE severity WHEN 'critical' THEN 0 ELSE 1 END, created_at""",
                (project_id,),
            ).fetchall()
        ]
        blocking_commitments = [
            dict(row)
            for row in self.conn.execute(
                "SELECT id, title, owner_role, due_at FROM commitments WHERE project_id = ? AND status = 'open' AND blocking = 1",
                (project_id,),
            ).fetchall()
        ]
        complete = bool(conditions) and all(row["status"] in {"satisfied", "waived"} for row in conditions)
        return {
            "project_id": project_id,
            "milestone": dict(milestone),
            "ready": complete and not blockers and not blocking_commitments,
            "conditions": conditions,
            "open_blocking_exceptions": blockers,
            "open_blocking_commitments": blocking_commitments,
        }

    def frontier(
        self, project_id: str, role: str | None = None, limit: int | None = None
    ) -> list[dict[str, Any]]:
        project = self._require_project(project_id)
        if project["status"] != "active":
            return []
        if role:
            self._validate_role(role)
        active_lease_keys = self._active_lease_keys()
        actions: list[dict[str, Any]] = []
        conditions = self.conn.execute(
            """SELECT c.* FROM conditions c
               JOIN milestones m ON m.id = c.milestone_id
               WHERE c.project_id = ? AND m.status = 'active' AND c.status IN ('unknown', 'unmet')
                 AND NOT EXISTS (
                   SELECT 1 FROM condition_dependencies cd
                   JOIN conditions dependency ON dependency.id = cd.depends_on_condition_id
                   WHERE cd.condition_id = c.id AND dependency.status NOT IN ('satisfied', 'waived')
                 )
                 AND NOT EXISTS (
                   SELECT 1 FROM exceptions e
                   WHERE e.project_id = c.project_id AND e.status = 'open'
                     AND e.target_type = 'condition' AND e.target_id = c.id
                 )""",
            (project_id,),
        ).fetchall()
        for condition in conditions:
            action = {
                "action_key": f"condition:{condition['id']}:satisfy:v{condition['state_version']}",
                "kind": "satisfy_condition",
                "project_id": project_id,
                "target_id": condition["id"],
                "role": condition["owner_role"],
                "title": condition["title"],
                "score": condition["priority"] + SEVERITY_SCORE[condition["severity"]],
                "state_revision": self.project_revision(project_id),
                "context": self._condition_context(condition["id"]),
            }
            actions.append(action)
        review_rows = self.conn.execute(
            """SELECT s.id AS submission_id, s.summary, c.id AS condition_id, c.title,
                      c.priority, c.severity, cr.role, cr.review_kind
               FROM submissions s JOIN conditions c ON c.id = s.condition_id
               JOIN milestones m ON m.id = c.milestone_id
               JOIN condition_reviewers cr ON cr.condition_id = c.id
               LEFT JOIN reviews r ON r.submission_id = s.id AND r.role = cr.role
               WHERE c.project_id = ? AND m.status = 'active' AND c.status = 'candidate'
                 AND s.status = 'pending' AND r.id IS NULL""",
            (project_id,),
        ).fetchall()
        for row in review_rows:
            action = {
                "action_key": f"submission:{row['submission_id']}:review:{row['role']}",
                "kind": "review_submission",
                "project_id": project_id,
                "target_id": row["submission_id"],
                "condition_id": row["condition_id"],
                "role": row["role"],
                "review_kind": row["review_kind"],
                "title": "Review: " + row["title"],
                "score": row["priority"] + SEVERITY_SCORE[row["severity"]] + 15,
                "state_revision": self.project_revision(project_id),
                "context": {
                    **self._condition_context(row["condition_id"]),
                    "submission": dict(
                        self.conn.execute("SELECT * FROM submissions WHERE id = ?", (row["submission_id"],)).fetchone()
                    ),
                    "review_kind": row["review_kind"],
                },
            }
            actions.append(action)
        readiness = self.readiness(project_id)
        if readiness.get("ready"):
            milestone = readiness["milestone"]
            actions.append(
                {
                    "action_key": f"milestone:{milestone['id']}:advance",
                    "kind": "advance_milestone",
                    "project_id": project_id,
                    "target_id": milestone["id"],
                    "role": self.policy["milestone_advancer"],
                    "title": "Accept milestone: " + milestone["title"],
                    "score": 120,
                    "state_revision": self.project_revision(project_id),
                    "context": readiness,
                }
            )
        for exception in self.conn.execute(
            "SELECT * FROM exceptions WHERE project_id = ? AND status = 'open'", (project_id,)
        ).fetchall():
            actions.append(
                {
                    "action_key": f"exception:{exception['id']}:resolve:v{exception['version']}",
                    "kind": "resolve_exception",
                    "project_id": project_id,
                    "target_id": exception["id"],
                    "role": "principal" if exception["principal_only"] else exception["owner_role"],
                    "title": exception["title"],
                    "score": 70 + SEVERITY_SCORE[exception["severity"]],
                    "state_revision": self.project_revision(project_id),
                    "context": {"exception": dict(exception)},
                }
            )
        for commitment in self.conn.execute(
            "SELECT * FROM commitments WHERE project_id = ? AND status = 'open'", (project_id,)
        ).fetchall():
            actions.append(
                {
                    "action_key": f"commitment:{commitment['id']}:fulfill:v{commitment['version']}",
                    "kind": "fulfill_commitment",
                    "project_id": project_id,
                    "target_id": commitment["id"],
                    "role": commitment["owner_role"],
                    "title": commitment["title"],
                    "score": commitment["priority"] + (25 if commitment["blocking"] else 0),
                    "state_revision": self.project_revision(project_id),
                    "context": {"commitment": dict(commitment)},
                }
            )
        actions = [
            action for action in actions
            if action["action_key"] not in active_lease_keys and (role is None or action["role"] == role)
        ]
        actions.sort(key=lambda item: (-item["score"], item["action_key"]))
        return actions[: (limit or int(self.policy["default_frontier_limit"]))]

    def claim(
        self,
        project_id: str,
        role: str,
        actor: str,
        action_key: str | None = None,
        ttl_minutes: int | None = None,
    ) -> dict[str, Any]:
        self._validate_role(role)
        project = self._require_project(project_id)
        now = utc_now()
        with self.conn:
            self.conn.execute("DELETE FROM leases WHERE expires_at <= ?", (now,))
            actions = self.frontier(project_id, role, 1000)
            action = next((item for item in actions if action_key is None or item["action_key"] == action_key), None)
            if action is None:
                raise LatticeError("No matching action is currently on the active frontier")
            active_project = self.conn.execute(
                "SELECT COUNT(*) FROM leases WHERE project_id = ? AND expires_at > ?", (project_id, now)
            ).fetchone()[0]
            active_role = self.conn.execute(
                "SELECT COUNT(*) FROM leases WHERE project_id = ? AND role = ? AND expires_at > ?",
                (project_id, role, now),
            ).fetchone()[0]
            if active_project >= project["max_wip"]:
                raise LatticeError("Project work-in-progress limit reached")
            if active_role >= int(self.policy["role_wip"]):
                raise LatticeError("Role already holds an active lease in this project")
            lease_id = new_id("lease")
            expires = (
                datetime.now(timezone.utc)
                + timedelta(minutes=ttl_minutes or int(self.policy["default_lease_minutes"]))
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            self.conn.execute(
                """INSERT INTO leases(
                       id, action_key, project_id, action_kind, target_id, role, leased_by, created_at, expires_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    lease_id, action["action_key"], project_id, action["kind"], action["target_id"],
                    role, actor, now, expires,
                ),
            )
        return {"lease_id": lease_id, "expires_at": expires, "action": action}

    def release_lease(self, lease_id: str, role: str) -> None:
        self._validate_role(role)
        lease = self._require_lease(lease_id)
        if lease["role"] != role:
            raise LatticeError("Only the leasing role may release this action")
        with self.conn:
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))

    def _require_lease(self, lease_id: str) -> sqlite3.Row:
        lease = self.conn.execute("SELECT * FROM leases WHERE id = ?", (lease_id,)).fetchone()
        if lease is None:
            raise LatticeError("Unknown or expired lease: " + lease_id)
        if lease["expires_at"] <= utc_now():
            with self.conn:
                self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            raise LatticeError("Lease expired: " + lease_id)
        return lease

    def submit(
        self,
        lease_id: str,
        role: str,
        summary: str,
        artifact_refs: list[str],
        evidence_ref: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(role)
        lease = self._require_lease(lease_id)
        if lease["action_kind"] != "satisfy_condition" or lease["role"] != role:
            raise LatticeError("Lease does not authorize a condition submission for this role")
        condition = self.conn.execute("SELECT * FROM conditions WHERE id = ?", (lease["target_id"],)).fetchone()
        if condition is None or condition["status"] not in {"unknown", "unmet"}:
            raise LatticeError("Condition is no longer accepting submissions")
        submission_id = new_id("submission")
        now = utc_now()
        with self.conn:
            revision = self._bump_revision()
            attempt_no = condition["attempt_count"] + 1
            self.conn.execute(
                """INSERT INTO submissions(
                       id, condition_id, state_version, attempt_no, role, summary,
                       artifact_refs_json, evidence_ref, status, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)""",
                (
                    submission_id, condition["id"], condition["state_version"], attempt_no,
                    role, summary, json_text(artifact_refs), evidence_ref, now,
                ),
            )
            self.conn.execute(
                "UPDATE conditions SET status = 'candidate', attempt_count = ?, updated_at = ? WHERE id = ?",
                (attempt_no, now, condition["id"]),
            )
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            if evidence_ref:
                self._insert_evidence(
                    condition["project_id"], "submission", submission_id, role, summary, evidence_ref
                )
            self._event(
                revision, condition["project_id"], "condition_submitted", "submission", submission_id, role,
                {"condition_id": condition["id"], "attempt_no": attempt_no, "artifact_refs": artifact_refs},
            )
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,)).fetchone())

    def fail_action(self, lease_id: str, role: str, summary: str) -> dict[str, Any]:
        self._validate_role(role)
        lease = self._require_lease(lease_id)
        if lease["action_kind"] != "satisfy_condition" or lease["role"] != role:
            raise LatticeError("Only a leased condition action can fail this way")
        condition = self.conn.execute("SELECT * FROM conditions WHERE id = ?", (lease["target_id"],)).fetchone()
        if condition is None:
            raise LatticeError("Condition no longer exists")
        with self.conn:
            revision = self._bump_revision()
            attempts = condition["attempt_count"] + 1
            blocked = attempts >= condition["attempt_budget"]
            self.conn.execute(
                """UPDATE conditions SET status = ?, state_version = state_version + 1,
                   attempt_count = ?, updated_at = ? WHERE id = ?""",
                ("blocked" if blocked else "unmet", attempts, utc_now(), condition["id"]),
            )
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            self._event(
                revision, condition["project_id"], "condition_attempt_failed", "condition", condition["id"], role,
                {"summary": summary, "attempt_count": attempts, "blocked": blocked},
            )
            exception = None
            if blocked:
                exception = self._raise_exception_internal(
                    condition["project_id"],
                    "attempt-budget:" + condition["id"],
                    "Retry budget exhausted: " + condition["title"],
                    summary,
                    condition["severity"],
                    "director",
                    False,
                    "condition",
                    condition["id"],
                    role,
                    revision,
                )
        self.export_snapshot()
        return {"condition_id": condition["id"], "blocked": blocked, "exception": exception}

    def review(
        self,
        lease_id: str,
        role: str,
        verdict: str,
        summary: str,
        evidence_ref: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(role)
        lease = self._require_lease(lease_id)
        if lease["action_kind"] != "review_submission" or lease["role"] != role:
            raise LatticeError("Lease does not authorize this review")
        submission = self.conn.execute("SELECT * FROM submissions WHERE id = ?", (lease["target_id"],)).fetchone()
        if submission is None or submission["status"] != "pending":
            raise LatticeError("Submission is no longer pending")
        condition = self.conn.execute("SELECT * FROM conditions WHERE id = ?", (submission["condition_id"],)).fetchone()
        requirement = self.conn.execute(
            "SELECT review_kind FROM condition_reviewers WHERE condition_id = ? AND role = ?",
            (condition["id"], role),
        ).fetchone()
        if requirement is None:
            raise LatticeError("Role is not a required reviewer")
        kind = requirement["review_kind"]
        allowed = {"SATISFIED", "NOT_SATISFIED"} if kind == "primary" else {"CONCUR", "BLOCK"}
        if verdict not in allowed:
            raise LatticeError("Invalid verdict for " + kind + " review")
        negative = verdict in {"NOT_SATISFIED", "BLOCK"}
        review_id = new_id("review")
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT INTO reviews(
                       id, submission_id, role, review_kind, verdict, summary, evidence_ref, created_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (review_id, submission["id"], role, kind, verdict, summary, evidence_ref, utc_now()),
            )
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            if evidence_ref:
                self._insert_evidence(
                    condition["project_id"], "review", review_id, role, summary, evidence_ref
                )
            if negative:
                blocked = condition["attempt_count"] >= condition["attempt_budget"]
                self.conn.execute(
                    "UPDATE submissions SET status = 'rejected' WHERE id = ?", (submission["id"],)
                )
                self.conn.execute(
                    """UPDATE conditions SET status = ?, state_version = state_version + 1,
                       updated_at = ? WHERE id = ?""",
                    ("blocked" if blocked else "unmet", utc_now(), condition["id"]),
                )
                self.conn.execute("DELETE FROM leases WHERE target_id = ?", (submission["id"],))
                if blocked:
                    self._raise_exception_internal(
                        condition["project_id"],
                        "attempt-budget:" + condition["id"],
                        "Retry budget exhausted: " + condition["title"],
                        summary,
                        condition["severity"],
                        "director",
                        False,
                        "condition",
                        condition["id"],
                        role,
                        revision,
                    )
            else:
                required = self.conn.execute(
                    "SELECT COUNT(*) FROM condition_reviewers WHERE condition_id = ?", (condition["id"],)
                ).fetchone()[0]
                positive = self.conn.execute(
                    """SELECT COUNT(*) FROM reviews WHERE submission_id = ?
                       AND verdict IN ('SATISFIED', 'CONCUR')""",
                    (submission["id"],),
                ).fetchone()[0]
                if required == positive:
                    self.conn.execute(
                        "UPDATE submissions SET status = 'accepted' WHERE id = ?", (submission["id"],)
                    )
                    self.conn.execute(
                        "UPDATE conditions SET status = 'satisfied', updated_at = ? WHERE id = ?",
                        (utc_now(), condition["id"]),
                    )
                    self.conn.execute(
                        """UPDATE condition_inputs SET accepted_record_version =
                           (SELECT version FROM records WHERE records.id = condition_inputs.record_id)
                           WHERE condition_id = ?""",
                        (condition["id"],),
                    )
                    self.conn.execute(
                        """UPDATE condition_truths SET accepted_truth_version =
                           (SELECT version FROM truths WHERE truths.id = condition_truths.truth_id)
                           WHERE condition_id = ?""",
                        (condition["id"],),
                    )
                    self.conn.execute(
                        """UPDATE condition_dependencies SET accepted_state_version =
                           (SELECT state_version FROM conditions dependency
                            WHERE dependency.id = condition_dependencies.depends_on_condition_id)
                           WHERE condition_id = ?""",
                        (condition["id"],),
                    )
            self._event(
                revision, condition["project_id"], "submission_reviewed", "review", review_id, role,
                {"submission_id": submission["id"], "condition_id": condition["id"], "verdict": verdict},
            )
        self.export_snapshot()
        refreshed = self.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition["id"],)).fetchone()
        return {"review_id": review_id, "condition": dict(refreshed)}

    def _insert_evidence(
        self,
        project_id: str,
        entity_type: str,
        entity_id: str,
        role: str,
        summary: str,
        source_ref: str | None,
    ) -> str:
        identifier = new_id("evidence")
        self.conn.execute(
            """INSERT INTO evidence(
                   id, project_id, entity_type, entity_id, role, summary, source_ref, content_hash, created_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                identifier, project_id, entity_type, entity_id, role, summary, source_ref,
                stable_hash(summary, source_ref), utc_now(),
            ),
        )
        return identifier

    def add_commitment(
        self,
        project_id: str,
        title: str,
        detail: str,
        owner_role: str,
        created_by: str,
        priority: int = 50,
        due_at: str | None = None,
        blocking: bool = False,
        commitment_id: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(created_by)
        self._validate_role(owner_role)
        if created_by not in self.policy["commitment_creators"]:
            raise LatticeError("Only the Director or Principal may create durable commitments")
        self._require_project(project_id)
        identifier = commitment_id or new_id("commitment")
        now = utc_now()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """INSERT INTO commitments(
                       id, project_id, title, detail, owner_role, priority, due_at, blocking,
                       status, version, created_by, created_at, updated_at
                   ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', 1, ?, ?, ?)""",
                (
                    identifier, project_id, title, detail, owner_role, priority, due_at,
                    int(blocking), created_by, now, now,
                ),
            )
            self._event(revision, project_id, "commitment_created", "commitment", identifier, created_by)
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM commitments WHERE id = ?", (identifier,)).fetchone())

    def fulfill_commitment(self, lease_id: str, role: str, summary: str) -> dict[str, Any]:
        lease = self._require_lease(lease_id)
        if lease["action_kind"] != "fulfill_commitment" or lease["role"] != role:
            raise LatticeError("Lease does not authorize this commitment")
        commitment = self.conn.execute("SELECT * FROM commitments WHERE id = ?", (lease["target_id"],)).fetchone()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                "UPDATE commitments SET status = 'fulfilled', version = version + 1, updated_at = ? WHERE id = ?",
                (utc_now(), commitment["id"]),
            )
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            self._event(
                revision, commitment["project_id"], "commitment_fulfilled", "commitment",
                commitment["id"], role, {"summary": summary},
            )
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM commitments WHERE id = ?", (commitment["id"],)).fetchone())

    def raise_exception(
        self,
        project_id: str,
        dedupe_key: str,
        title: str,
        detail: str,
        severity: str,
        owner_role: str,
        raised_by: str,
        principal_only: bool = False,
        target_type: str | None = None,
        target_id: str | None = None,
    ) -> dict[str, Any]:
        self._validate_role(raised_by)
        self._validate_role(owner_role)
        self._require_project(project_id)
        if severity not in SEVERITY_SCORE:
            raise LatticeError("Invalid exception severity")
        with self.conn:
            existing = self.conn.execute(
                "SELECT * FROM exceptions WHERE project_id = ? AND dedupe_key = ? AND status = 'open'",
                (project_id, dedupe_key),
            ).fetchone()
            if existing:
                return dict(existing)
            revision = self._bump_revision()
            payload = self._raise_exception_internal(
                project_id, dedupe_key, title, detail, severity, owner_role, principal_only,
                target_type, target_id, raised_by, revision,
            )
        self.export_snapshot()
        return payload

    def _raise_exception_internal(
        self,
        project_id: str,
        dedupe_key: str,
        title: str,
        detail: str,
        severity: str,
        owner_role: str,
        principal_only: bool,
        target_type: str | None,
        target_id: str | None,
        raised_by: str,
        revision: int,
    ) -> dict[str, Any]:
        existing = self.conn.execute(
            "SELECT * FROM exceptions WHERE project_id = ? AND dedupe_key = ? AND status = 'open'",
            (project_id, dedupe_key),
        ).fetchone()
        if existing:
            return dict(existing)
        identifier = new_id("exception")
        now = utc_now()
        self.conn.execute(
            """INSERT INTO exceptions(
                   id, project_id, dedupe_key, title, detail, severity, owner_role, principal_only,
                   target_type, target_id, status, version, raised_by, created_at, updated_at
               ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', 1, ?, ?, ?)""",
            (
                identifier, project_id, dedupe_key, title, detail, severity, owner_role,
                int(principal_only), target_type, target_id, raised_by, now, now,
            ),
        )
        self._event(
            revision, project_id, "exception_raised", "exception", identifier, raised_by,
            {"dedupe_key": dedupe_key, "principal_only": principal_only},
        )
        return dict(self.conn.execute("SELECT * FROM exceptions WHERE id = ?", (identifier,)).fetchone())

    def resolve_exception(self, lease_id: str, role: str, resolution: str) -> dict[str, Any]:
        lease = self._require_lease(lease_id)
        if lease["action_kind"] != "resolve_exception" or lease["role"] != role:
            raise LatticeError("Lease does not authorize this exception")
        exception = self.conn.execute("SELECT * FROM exceptions WHERE id = ?", (lease["target_id"],)).fetchone()
        with self.conn:
            revision = self._bump_revision()
            self.conn.execute(
                """UPDATE exceptions SET status = 'resolved', resolution = ?, version = version + 1,
                   updated_at = ? WHERE id = ?""",
                (resolution, utc_now(), exception["id"]),
            )
            if exception["target_type"] == "condition" and exception["target_id"]:
                self.conn.execute(
                    """UPDATE conditions SET status = 'unmet', state_version = state_version + 1,
                       attempt_count = 0, updated_at = ? WHERE id = ? AND status = 'blocked'""",
                    (utc_now(), exception["target_id"]),
                )
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            self._event(
                revision, exception["project_id"], "exception_resolved", "exception",
                exception["id"], role, {"resolution": resolution},
            )
        self.export_snapshot()
        return dict(self.conn.execute("SELECT * FROM exceptions WHERE id = ?", (exception["id"],)).fetchone())

    def advance_milestone(self, lease_id: str, role: str, summary: str) -> dict[str, Any]:
        self._validate_role(role)
        lease = self._require_lease(lease_id)
        if lease["action_kind"] != "advance_milestone" or lease["role"] != role:
            raise LatticeError("Lease does not authorize milestone advancement")
        milestone = self.conn.execute("SELECT * FROM milestones WHERE id = ?", (lease["target_id"],)).fetchone()
        readiness = self.readiness(milestone["project_id"], milestone["id"])
        if not readiness.get("ready"):
            raise LatticeError("Milestone readiness predicates are not satisfied")
        with self.conn:
            revision = self._bump_revision()
            accepted_at = utc_now()
            self.conn.execute(
                "UPDATE milestones SET status = 'accepted', accepted_at = ? WHERE id = ?",
                (accepted_at, milestone["id"]),
            )
            next_milestone = self.conn.execute(
                """SELECT * FROM milestones WHERE objective_id = ? AND status = 'planned'
                   ORDER BY ordinal, created_at LIMIT 1""",
                (milestone["objective_id"],),
            ).fetchone()
            if next_milestone:
                self.conn.execute("UPDATE milestones SET status = 'active' WHERE id = ?", (next_milestone["id"],))
                linked_truths = self.conn.execute(
                    """SELECT DISTINCT t.* FROM truths t
                       JOIN condition_truths ct ON ct.truth_id = t.id
                       JOIN conditions c ON c.id = ct.condition_id
                       WHERE c.milestone_id = ? AND t.attention_state <> 'frontier'""",
                    (next_milestone["id"],),
                ).fetchall()
                for truth in linked_truths:
                    self._move_truth_attention(
                        truth, "frontier", role,
                        "successor milestone activated: " + next_milestone["title"], revision,
                    )
            else:
                self.conn.execute(
                    "UPDATE objectives SET status = 'satisfied', updated_at = ? WHERE id = ?",
                    (accepted_at, milestone["objective_id"]),
                )
            self.conn.execute("DELETE FROM leases WHERE id = ?", (lease_id,))
            self._event(
                revision, milestone["project_id"], "milestone_accepted", "milestone",
                milestone["id"], role, {"summary": summary, "next_milestone": next_milestone["id"] if next_milestone else None},
            )
            backgrounded = self._background_settled_truths(
                milestone["project_id"], revision, role, "milestone accepted: " + milestone["title"]
            )
        self.export_snapshot()
        return {
            "accepted_milestone": milestone["id"],
            "next_milestone": next_milestone["id"] if next_milestone else None,
            "truths_moved_to_background": backgrounded,
        }

    def _background_settled_truths(
        self, project_id: str, revision: int, role: str, reason: str
    ) -> list[str]:
        rows = self.conn.execute(
            """SELECT DISTINCT t.* FROM truths t
               JOIN condition_truths ct ON ct.truth_id = t.id
               WHERE t.project_id = ? AND t.attention_state = 'frontier'
                 AND NOT EXISTS (
                   SELECT 1 FROM condition_truths active_ct
                   JOIN conditions active_c ON active_c.id = active_ct.condition_id
                   JOIN milestones active_m ON active_m.id = active_c.milestone_id
                   WHERE active_ct.truth_id = t.id AND active_m.status IN ('active', 'planned')
                 )
                 AND NOT EXISTS (
                   SELECT 1 FROM truth_links tl
                   WHERE (tl.from_truth_id = t.id OR tl.to_truth_id = t.id)
                     AND tl.relation = 'contradicts'
                 )""",
            (project_id,),
        ).fetchall()
        identifiers: list[str] = []
        for truth in rows:
            self._move_truth_attention(truth, "background", role, reason, revision)
            identifiers.append(truth["id"])
        return identifiers

    def truth_ledger(
        self,
        project_id: str,
        attention_state: str | None = None,
        epistemic_status: str | None = None,
    ) -> list[dict[str, Any]]:
        self._require_project(project_id)
        clauses = ["project_id = ?"]
        values: list[Any] = [project_id]
        if attention_state:
            clauses.append("attention_state = ?")
            values.append(attention_state)
        if epistemic_status:
            clauses.append("epistemic_status = ?")
            values.append(epistemic_status)
        rows = self.conn.execute(
            "SELECT * FROM truths WHERE " + " AND ".join(clauses) + " ORDER BY attention_state, key",
            values,
        ).fetchall()
        result = []
        for row in rows:
            item = dict(row)
            item["transitions"] = [
                dict(t)
                for t in self.conn.execute(
                    "SELECT * FROM truth_transitions WHERE truth_id = ? ORDER BY rowid", (row["id"],)
                ).fetchall()
            ]
            item["links"] = [
                dict(link)
                for link in self.conn.execute(
                    """SELECT * FROM truth_links WHERE from_truth_id = ? OR to_truth_id = ?
                       ORDER BY relation, from_truth_id, to_truth_id""",
                    (row["id"], row["id"]),
                ).fetchall()
            ]
            item["condition_links"] = [
                dict(link)
                for link in self.conn.execute(
                    """SELECT c.id AS condition_id, c.key AS condition_key, c.title,
                              c.status AS condition_status, m.id AS milestone_id,
                              m.title AS milestone_title, m.status AS milestone_status,
                              ct.relevance, ct.accepted_truth_version
                       FROM condition_truths ct
                       JOIN conditions c ON c.id = ct.condition_id
                       JOIN milestones m ON m.id = c.milestone_id
                       WHERE ct.truth_id = ? ORDER BY m.ordinal, c.key""",
                    (row["id"],),
                ).fetchall()
            ]
            result.append(item)
        return result

    def status(self) -> dict[str, Any]:
        projects = []
        for project in self.conn.execute("SELECT * FROM projects ORDER BY id").fetchall():
            active_objective = self.conn.execute(
                "SELECT id, title FROM objectives WHERE project_id = ? AND status = 'active'", (project["id"],)
            ).fetchone()
            active_milestone = self.conn.execute(
                "SELECT id, title FROM milestones WHERE project_id = ? AND status = 'active'", (project["id"],)
            ).fetchone()
            projects.append(
                {
                    **dict(project),
                    "active_objective": dict(active_objective) if active_objective else None,
                    "active_milestone": dict(active_milestone) if active_milestone else None,
                    "state_revision": self.project_revision(project["id"]),
                    "frontier_count": len(self.frontier(project["id"], limit=1000)),
                    "open_commitments": self.conn.execute(
                        "SELECT COUNT(*) FROM commitments WHERE project_id = ? AND status = 'open'", (project["id"],)
                    ).fetchone()[0],
                    "open_exceptions": self.conn.execute(
                        "SELECT COUNT(*) FROM exceptions WHERE project_id = ? AND status = 'open'", (project["id"],)
                    ).fetchone()[0],
                    "frontier_truths": self.conn.execute(
                        "SELECT COUNT(*) FROM truths WHERE project_id = ? AND attention_state = 'frontier'", (project["id"],)
                    ).fetchone()[0],
                    "background_truths": self.conn.execute(
                        "SELECT COUNT(*) FROM truths WHERE project_id = ? AND attention_state = 'background'", (project["id"],)
                    ).fetchone()[0],
                }
            )
        return {"agency_version": self.policy["agency_version"], "revision": self.revision, "projects": projects}

    def apply_delta(self, delta: dict[str, Any]) -> dict[str, Any]:
        if delta.get("format") != "lattice-state-delta" or delta.get("schema_version") != 1:
            raise LatticeError("Unsupported hosted state delta")
        project_id = str(delta["project_id"])
        current_project_revision = self.project_revision(project_id)
        if int(delta.get("base_revision", -1)) != current_project_revision:
            raise LatticeError(
                f"Hosted delta is stale for {project_id}: base {delta.get('base_revision')}, "
                f"current {current_project_revision}"
            )
        role = str(delta["role"])
        actor = str(delta.get("actor") or ("hosted-" + role))
        action_key = str(delta["action_key"])
        outcome = delta.get("outcome") or {}
        claim = self.claim(project_id, role, actor, action_key)
        lease_id = claim["lease_id"]
        outcome_type = outcome.get("type")
        if outcome_type == "submit":
            return self.submit(
                lease_id, role, str(outcome.get("summary", "")),
                list(outcome.get("artifact_refs") or []), outcome.get("evidence_ref"),
            )
        if outcome_type == "review":
            return self.review(
                lease_id, role, str(outcome["verdict"]), str(outcome.get("summary", "")),
                outcome.get("evidence_ref"),
            )
        if outcome_type == "advance":
            return self.advance_milestone(lease_id, role, str(outcome.get("summary", "")))
        if outcome_type == "fail":
            return self.fail_action(lease_id, role, str(outcome.get("summary", "")))
        if outcome_type == "resolve_exception":
            return self.resolve_exception(lease_id, role, str(outcome.get("resolution", "")))
        if outcome_type == "fulfill_commitment":
            return self.fulfill_commitment(lease_id, role, str(outcome.get("summary", "")))
        self.release_lease(lease_id, role)
        raise LatticeError("Unsupported hosted delta outcome: " + str(outcome_type))
