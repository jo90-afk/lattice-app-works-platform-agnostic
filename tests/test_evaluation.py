from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evaluation import (  # noqa: E402
    REQUIRED_SCENARIOS,
    EvaluationError,
    summarize_results,
    validate_scenarios,
)


def result(
    *,
    run_id: str,
    host: str = "local",
    scenario_id: str = "greenfield-feature-delivery",
    state_fingerprint: str = "state-a",
    acceptance_fingerprint: str = "accept-a",
    **overrides,
):
    payload = {
        "format": "lattice-evaluation-result",
        "version": 1,
        "scenario_id": scenario_id,
        "run_id": run_id,
        "host": host,
        "outcome": "passed",
        "state_fingerprint": state_fingerprint,
        "acceptance_fingerprint": acceptance_fingerprint,
        "routine_transitions": 10,
        "routine_autonomous_transitions": 9,
        "accepted_changes": 4,
        "false_acceptances": 0,
        "escalations": 2,
        "unnecessary_escalations": 1,
        "worker_losses": 1,
        "recoveries_succeeded": 1,
        "state_divergence_incidents": 0,
        "verification_defects_presented": 2,
        "verification_catches": 2,
        "blocked_seconds_missing_information": 120,
        "context_bytes": 4000,
        "duration_seconds": 30,
    }
    payload.update(overrides)
    return payload


class EvaluationHarnessTest(unittest.TestCase):
    def test_registry_covers_every_roadmap_scenario_and_metric_signal(self):
        registry = validate_scenarios()
        ids = {item["id"] for item in registry["scenarios"]}
        self.assertEqual(ids, REQUIRED_SCENARIOS)
        self.assertEqual(len(registry["scenarios"]), 10)

    def test_summary_computes_product_thesis_metrics(self):
        summary = summarize_results(
            [
                result(run_id="run-1"),
                result(
                    run_id="run-2",
                    routine_transitions=10,
                    routine_autonomous_transitions=10,
                    accepted_changes=6,
                    escalations=0,
                    unnecessary_escalations=0,
                    worker_losses=1,
                    recoveries_succeeded=0,
                    verification_defects_presented=2,
                    verification_catches=1,
                    blocked_seconds_missing_information=180,
                    context_bytes=6000,
                    duration_seconds=50,
                ),
            ]
        )
        metrics = summary["metrics"]
        self.assertEqual(metrics["routine_autonomy_rate"], 0.95)
        self.assertEqual(metrics["false_acceptance_rate"], 0.0)
        self.assertEqual(metrics["unnecessary_escalation_rate"], 0.5)
        self.assertEqual(metrics["recovery_success_rate"], 0.5)
        self.assertEqual(metrics["state_divergence_incidents"], 0)
        self.assertEqual(metrics["verification_catch_rate"], 0.75)
        self.assertEqual(metrics["blocked_seconds_missing_information"], 300.0)
        self.assertEqual(metrics["context_bytes_per_accepted_change"], 1000.0)
        self.assertEqual(metrics["median_run_duration_seconds"], 40.0)

    def test_cross_host_equivalence_is_measured_not_assumed(self):
        equivalent = summarize_results(
            [result(run_id="local-1", host="local"), result(run_id="github-1", host="github")]
        )
        self.assertEqual(equivalent["portability"]["scenarios_compared_across_hosts"], 1)
        self.assertEqual(equivalent["portability"]["equivalence_violations"], [])

        divergent = summarize_results(
            [
                result(run_id="local-1", host="local"),
                result(run_id="github-1", host="github", state_fingerprint="state-b"),
            ]
        )
        self.assertEqual(
            divergent["portability"]["equivalence_violations"],
            ["greenfield-feature-delivery"],
        )

    def test_invalid_metric_relationship_is_rejected(self):
        with self.assertRaises(EvaluationError):
            summarize_results(
                [result(run_id="bad", accepted_changes=1, false_acceptances=2)]
            )

    def test_unexercised_denominators_remain_unknown(self):
        summary = summarize_results(
            [
                result(
                    run_id="empty-denominators",
                    routine_transitions=0,
                    routine_autonomous_transitions=0,
                    accepted_changes=0,
                    false_acceptances=0,
                    escalations=0,
                    unnecessary_escalations=0,
                    worker_losses=0,
                    recoveries_succeeded=0,
                    verification_defects_presented=0,
                    verification_catches=0,
                    context_bytes=0,
                )
            ]
        )
        metrics = summary["metrics"]
        self.assertIsNone(metrics["routine_autonomy_rate"])
        self.assertIsNone(metrics["false_acceptance_rate"])
        self.assertIsNone(metrics["unnecessary_escalation_rate"])
        self.assertIsNone(metrics["recovery_success_rate"])
        self.assertIsNone(metrics["verification_catch_rate"])
        self.assertIsNone(metrics["context_bytes_per_accepted_change"])


if __name__ == "__main__":
    unittest.main()
