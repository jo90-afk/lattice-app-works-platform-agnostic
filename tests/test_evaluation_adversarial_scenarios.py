from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evaluation import summarize_results  # noqa: E402
from evaluation_adversarial_scenarios import run_adversarial_scenario  # noqa: E402


class AdversarialEvaluationScenarioTest(unittest.TestCase):
    def test_ambiguous_requirement_stops_at_principal_boundary(self):
        result = run_adversarial_scenario(
            "ambiguous-requirements-escalation",
            host="local",
            run_id="ambiguous-local",
        )
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["escalations"], 1)
        self.assertEqual(result["unnecessary_escalations"], 0)
        self.assertEqual(result["routine_transitions"], 0)
        self.assertGreaterEqual(result["blocked_seconds_missing_information"], 90)

    def test_contradiction_invalidates_previously_satisfied_condition(self):
        result = run_adversarial_scenario(
            "contradictory-new-information",
            host="local",
            run_id="contradiction-local",
        )
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["routine_transitions"], 2)
        self.assertEqual(result["routine_autonomous_transitions"], 2)
        self.assertEqual(result["state_divergence_incidents"], 0)
        self.assertGreater(result["context_bytes"], 0)

    def test_portfolio_contention_preserves_capacity_and_progress(self):
        result = run_adversarial_scenario(
            "multi-project-capacity-contention",
            host="local",
            run_id="portfolio-local",
        )
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["routine_transitions"], 3)
        self.assertEqual(result["routine_autonomous_transitions"], 3)
        self.assertEqual(result["state_divergence_incidents"], 0)
        self.assertGreater(result["context_bytes"], 0)

    def test_new_scenarios_contribute_real_escalation_and_blocked_time_metrics(self):
        results = [
            run_adversarial_scenario("ambiguous-requirements-escalation", run_id="ambiguous"),
            run_adversarial_scenario("contradictory-new-information", run_id="contradiction"),
            run_adversarial_scenario("multi-project-capacity-contention", run_id="portfolio"),
        ]
        summary = summarize_results(results)
        self.assertEqual(summary["outcomes"]["passed"], 3)
        self.assertEqual(summary["metrics"]["unnecessary_escalation_rate"], 0.0)
        self.assertGreaterEqual(summary["metrics"]["blocked_seconds_missing_information"], 90)
        self.assertEqual(summary["metrics"]["state_divergence_incidents"], 0)


if __name__ == "__main__":
    unittest.main()
