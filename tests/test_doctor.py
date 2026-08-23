from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from doctor import doctor  # noqa: E402


class DoctorTest(unittest.TestCase):
    def test_default_local_preflight_is_machine_readable_and_ready(self) -> None:
        previous = os.environ.pop("LATTICE_DATABASE_URL", None)
        try:
            result = doctor()
        finally:
            if previous is not None:
                os.environ["LATTICE_DATABASE_URL"] = previous

        self.assertEqual(result["format"], "lattice-doctor")
        self.assertEqual(result["version"], 1)
        self.assertTrue(result["ok"])
        self.assertEqual(result["state_backend"], "sqlite")
        self.assertEqual(result["required_failures"], [])
        checks = {item["name"]: item for item in result["checks"]}
        for required in (
            "python",
            "repository-layout",
            "release-metadata",
            "repository-contract",
            "local-writeability",
        ):
            self.assertTrue(checks[required]["required"])
            self.assertTrue(checks[required]["ok"])
        self.assertFalse(checks["postgres"]["required"])

    def test_json_cli_uses_result_contract(self) -> None:
        environment = dict(os.environ)
        environment.pop("LATTICE_DATABASE_URL", None)
        process = subprocess.run(
            [sys.executable, str(SCRIPTS / "doctor.py"), "--json"],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["state_backend"], "sqlite")


if __name__ == "__main__":
    unittest.main()
