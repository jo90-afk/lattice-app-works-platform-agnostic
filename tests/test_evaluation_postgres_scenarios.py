from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evaluation_postgres_scenarios import run_concurrent_artifact_conflict  # noqa: E402

POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class PostgresEvaluationScenarioTest(unittest.TestCase):
    def test_concurrent_artifact_conflict_prevents_divergence_without_faking_verification_catch(self) -> None:
        result = run_concurrent_artifact_conflict(
            POSTGRES_URL,
            host="test-postgres",
            run_id="test-postgres-conflict",
        )

        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["scenario_id"], "concurrent-artifact-conflict")
        self.assertEqual(result["state_divergence_incidents"], 0)
        self.assertEqual(result["false_acceptances"], 0)
        self.assertEqual(result["verification_defects_presented"], 0)
        self.assertEqual(result["verification_catches"], 0)
        self.assertEqual(result["routine_transitions"], 2)
        self.assertEqual(result["routine_autonomous_transitions"], 2)


if __name__ == "__main__":
    unittest.main()
