from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SeedInitializationTest(unittest.TestCase):
    def test_fresh_seed_initializes_and_validates(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "lattice"
            shutil.copytree(
                ROOT,
                target,
                ignore=shutil.ignore_patterns(".lattice", "__pycache__", "*.pyc"),
            )
            command = [
                sys.executable,
                "scripts/lattice.py",
                "initialize",
                "--principal-alias",
                "Repository Owner",
                "--project-id",
                "sample-001",
                "--project-name",
                "Sample Project",
            ]
            initialized = subprocess.run(command, cwd=target, text=True, capture_output=True)
            self.assertEqual(initialized.returncode, 0, initialized.stderr + initialized.stdout)
            self.assertTrue((target / "projects" / "sample-001" / "PROJECT.md").is_file())
            self.assertFalse((target / "projects" / "example-001").exists())
            snapshot = json.loads((target / "state" / "current.json").read_text(encoding="utf-8"))
            self.assertEqual(snapshot["tables"]["projects"][0]["id"], "sample-001")
            self.assertEqual(snapshot["tables"]["projects"][0]["status"], "active")
            self.assertTrue(
                (target / "exports" / "chatgpt-work" / "sample-001" / "source-manifest.json").is_file()
            )

            created = subprocess.run(
                [
                    sys.executable, "scripts/lattice.py", "project-create",
                    "--project-id", "second-001", "--project-name", "Second Project",
                ],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertEqual(created.returncode, 0, created.stderr + created.stdout)
            self.assertTrue((target / "projects" / "second-001" / "PROJECT.md").is_file())
            snapshot = json.loads((target / "state" / "current.json").read_text(encoding="utf-8"))
            projects = {row["id"]: row for row in snapshot["tables"]["projects"]}
            self.assertEqual(projects["second-001"]["status"], "paused")

            activated = subprocess.run(
                [
                    sys.executable, "scripts/lattice.py", "project-status",
                    "--project", "second-001", "--status", "active",
                ],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertEqual(activated.returncode, 0, activated.stderr + activated.stdout)

            validated = subprocess.run(
                [sys.executable, "scripts/lattice.py", "validate"],
                cwd=target,
                text=True,
                capture_output=True,
            )
            self.assertEqual(validated.returncode, 0, validated.stderr + validated.stdout)


if __name__ == "__main__":
    unittest.main()
