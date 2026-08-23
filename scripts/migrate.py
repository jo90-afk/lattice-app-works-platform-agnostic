#!/usr/bin/env python3
"""Portable snapshot migration status, backup, and rollback tooling."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def migration_status(root: Path = ROOT) -> dict[str, Any]:
    policy = json.loads((root / "runtime" / "policy.json").read_text(encoding="utf-8"))
    snapshot = json.loads((root / "state" / "current.json").read_text(encoding="utf-8"))
    runtime_schema = int(policy["schema_version"])
    snapshot_schema = int(snapshot.get("schema_version", -1))
    return {
        "format": "lattice-migration-status",
        "version": 1,
        "release": (root / "VERSION").read_text(encoding="utf-8").strip(),
        "agency_version": policy["agency_version"],
        "runtime_schema": runtime_schema,
        "snapshot_schema": snapshot_schema,
        "migration_required": runtime_schema != snapshot_schema,
        "can_run_current_runtime": runtime_schema == snapshot_schema,
        "configured_backend": "postgres" if os.environ.get("LATTICE_DATABASE_URL") else "sqlite",
    }


def create_backup(output: Path, root: Path = ROOT, *, overwrite: bool = False) -> dict[str, Any]:
    if output.exists() and not overwrite:
        raise RuntimeError("Backup already exists; pass --overwrite to replace it")
    snapshot_path = root / "state" / "current.json"
    raw = snapshot_path.read_bytes()
    snapshot = json.loads(raw.decode("utf-8"))
    policy = json.loads((root / "runtime" / "policy.json").read_text(encoding="utf-8"))
    payload = {
        "format": "lattice-state-backup",
        "version": 1,
        "release": (root / "VERSION").read_text(encoding="utf-8").strip(),
        "agency_version": policy["agency_version"],
        "schema_version": int(snapshot["schema_version"]),
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "snapshot_sha256": hashlib.sha256(raw).hexdigest(),
        "snapshot": snapshot,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_bytes(_json_bytes(payload))
    temporary.replace(output)
    return {key: payload[key] for key in ("format", "version", "release", "agency_version", "schema_version", "created_at", "snapshot_sha256")}


def _active_local_leases(root: Path) -> int:
    db = root / ".lattice" / "state.db"
    if not db.is_file():
        return 0
    connection = sqlite3.connect(db)
    try:
        row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='leases'"
        ).fetchone()
        if row is None:
            return 0
        return int(connection.execute("SELECT COUNT(*) FROM leases WHERE expires_at > datetime('now')").fetchone()[0])
    finally:
        connection.close()


def restore_backup(source: Path, root: Path = ROOT) -> dict[str, Any]:
    if os.environ.get("LATTICE_DATABASE_URL"):
        raise RuntimeError(
            "Portable rollback is disabled while LATTICE_DATABASE_URL is configured; "
            "put the shared store into maintenance and use its database recovery procedure first"
        )
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("format") != "lattice-state-backup" or payload.get("version") != 1:
        raise RuntimeError("Unsupported Lattice backup format")
    policy = json.loads((root / "runtime" / "policy.json").read_text(encoding="utf-8"))
    if int(payload.get("schema_version", -1)) != int(policy["schema_version"]):
        raise RuntimeError("Backup schema does not match the current runtime; roll back code before restoring this snapshot")
    snapshot = payload.get("snapshot")
    if not isinstance(snapshot, dict) or snapshot.get("format") != "lattice-state-snapshot":
        raise RuntimeError("Backup does not contain a valid Lattice snapshot")
    raw = _json_bytes(snapshot)
    if hashlib.sha256(raw).hexdigest() != payload.get("snapshot_sha256"):
        # Historical backups may preserve the exact source serialization rather than normalized JSON.
        original_snapshot_hash = hashlib.sha256(
            (json.dumps(snapshot, indent=2, sort_keys=True) + "\n").encode("utf-8")
        ).hexdigest()
        if original_snapshot_hash != payload.get("snapshot_sha256"):
            raise RuntimeError("Backup snapshot hash does not match its manifest")
    active = _active_local_leases(root)
    if active:
        raise RuntimeError(f"Refusing rollback while {active} local action lease(s) are active")
    target = root / "state" / "current.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".restore.tmp")
    temporary.write_bytes(raw)
    temporary.replace(target)
    return {
        "restored": str(target.relative_to(root)),
        "schema_version": int(payload["schema_version"]),
        "release_from_backup": payload.get("release"),
        "next_step": "Run `python3 scripts/lattice.py doctor`, then open the local state store to reconcile the snapshot.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    backup = commands.add_parser("backup")
    backup.add_argument("--output", required=True)
    backup.add_argument("--overwrite", action="store_true")
    restore = commands.add_parser("restore")
    restore.add_argument("--file", required=True)
    args = parser.parse_args()
    try:
        if args.command == "status":
            result = migration_status()
        elif args.command == "backup":
            result = create_backup(Path(args.output).resolve(), overwrite=args.overwrite)
        else:
            result = restore_backup(Path(args.file).resolve())
    except (OSError, ValueError, KeyError, json.JSONDecodeError, sqlite3.Error, RuntimeError) as error:
        print(json.dumps({"error": str(error)}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
