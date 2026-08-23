from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evaluation import summarize  # noqa: E402
from evaluation_delivery_scenarios import run_delivery_scenario  # noqa: E402


class DeliveryEvaluationScenarioTest(unittest.TestCase):
    def test_cross_component_refactor_converges_under_one_shared_contract(self) -> None:
        result = run_delivery_scenario(
            "cross-component-refactor", host="test", run_id="test-refactor"
        )
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["accepted_changes"], 1)
        self.assertEqual(result["state_divergence_incidents"], 0)
        self.assertEqual(result["routine_transitions"], 5)

    def test_migration_revalidates_after_contract_version_change(self) -> None:
        result = run_delivery_scenario(
            "migration-work", host="test", run_id="test-migration"
        )
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["accepted_changes"], 1)
        self.assertEqual(result["state_divergence_incidents"], 0)

    def test_ci_remediation_uses_retry_without_unnecessary_escalation(self) -> None:
        result = run_delivery_scenario(
            "ci-remediation", host="test", run_id="test-ci"
        )
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["accepted_changes"], 1)
        self.assertEqual(result["escalations"], 0)
        self.assertEqual(result["unnecessary_escalations"], 0)
        self.assertEqual(result["routine_transitions"], 4)

    def test_final_three_scenarios_aggregate_without_failures(self) -> None:
        results = [
            run_delivery_scenario(name, host="test", run_id=f"aggregate-{name}")
            for name in ("cross-component-refactor", "migration-work", "ci-remediation")
        ]
        summary = summarize(results)
        self.assertEqual(summary["outcomes"].get("failed", 0), 0)
        self.assertEqual(summary["outcomes"]["passed"], 3)
        self.assertEqual(summary["metrics"]["state_divergence_incidents"], 0)


if __name__ == "__main__":
    unittest.main()
