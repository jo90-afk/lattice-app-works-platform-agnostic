from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from capabilities import capabilities  # noqa: E402
from migrate import create_backup, migration_status, restore_backup  # noqa: E402


class PublicBetaPackagingTest(unittest.TestCase):
    def test_capabilities_report_public_and_compatibility_versions_separately(self) -> None:
        result = capabilities(ROOT)
        self.assertEqual(result["format"], "lattice-capabilities")
        self.assertEqual(result["release"], (ROOT / "VERSION").read_text(encoding="utf-8").strip())
        self.assertEqual(result["compatibility"]["agency_version"], "0.0.4")
        self.assertEqual(result["compatibility"]["state_snapshot_schema"], 1)
        self.assertEqual(result["compatibility"]["host_adapter_protocol"], 1)
        self.assertIn("renew", result["host_adapter_operations"])
        self.assertEqual(result["state_backends"]["default"], "sqlite")

    def fixture_root(self, folder: str) -> Path:
        root = Path(folder)
        (root / "runtime").mkdir(parents=True)
        (root / "state").mkdir(parents=True)
        (root / ".lattice").mkdir(parents=True)
        (root / "VERSION").write_text("0.1.0\n", encoding="utf-8")
        (root / "runtime" / "policy.json").write_text(
            json.dumps({"agency_version": "0.0.4", "schema_version": 1}), encoding="utf-8"
        )
        snapshot = {
            "format": "lattice-state-snapshot",
            "schema_version": 1,
            "agency_version": "0.0.4",
            "revision": 4,
            "ephemeral_state_excluded": ["leases"],
            "tables": {"projects": []},
        }
        (root / "state" / "current.json").write_text(
            json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return root

    def test_backup_and_restore_round_trip_portable_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = self.fixture_root(folder)
            backup = root / "backup.json"
            original = (root / "state" / "current.json").read_text(encoding="utf-8")
            created = create_backup(backup, root)
            self.assertEqual(created["format"], "lattice-state-backup")
            (root / "state" / "current.json").write_text("{}\n", encoding="utf-8")
            restored = restore_backup(backup, root)
            self.assertEqual(restored["schema_version"], 1)
            self.assertEqual((root / "state" / "current.json").read_text(encoding="utf-8"), original)

    def test_restore_refuses_active_local_leases(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = self.fixture_root(folder)
            backup = root / "backup.json"
            create_backup(backup, root)
            db = sqlite3.connect(root / ".lattice" / "state.db")
            db.execute("CREATE TABLE leases(id TEXT, expires_at TEXT)")
            expires = (datetime.now(timezone.utc) + timedelta(hours=1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            db.execute("INSERT INTO leases VALUES('lease-1', ?)", (expires,))
            db.commit()
            db.close()
            with self.assertRaisesRegex(RuntimeError, "active"):
                restore_backup(backup, root)

    def test_migration_status_distinguishes_package_from_schema(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            root = self.fixture_root(folder)
            previous = os.environ.pop("LATTICE_DATABASE_URL", None)
            try:
                status = migration_status(root)
            finally:
                if previous is not None:
                    os.environ["LATTICE_DATABASE_URL"] = previous
            self.assertEqual(status["release"], "0.1.0")
            self.assertEqual(status["runtime_schema"], 1)
            self.assertFalse(status["migration_required"])
            self.assertTrue(status["can_run_current_runtime"])


if __name__ == "__main__":
    unittest.main()
