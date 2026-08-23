from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from evaluation import summarize_results  # noqa: E402
from evaluation_scenarios import run_scenario  # noqa: E402


class ExecutableEvaluationScenarioTest(unittest.TestCase):
    def test_greenfield_run_emits_real_accepted_autonomous_result(self):
        result = run_scenario("greenfield-feature-delivery", host="local", run_id="greenfield-local")
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["accepted_changes"], 1)
        self.assertEqual(result["routine_transitions"], 3)
        self.assertEqual(result["routine_autonomous_transitions"], 3)
        self.assertEqual(result["false_acceptances"], 0)
        self.assertGreater(result["context_bytes"], 0)

    def test_seeded_defect_is_caught_without_false_acceptance(self):
        result = run_scenario("verifier-disagreement", host="local", run_id="verifier-local")
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["verification_defects_presented"], 1)
        self.assertEqual(result["verification_catches"], 1)
        self.assertEqual(result["accepted_changes"], 0)
        self.assertEqual(result["false_acceptances"], 0)

    def test_worker_loss_recovers_and_finishes_without_principal(self):
        result = run_scenario("worker-crash-and-lease-expiry", host="local", run_id="recovery-local")
        self.assertEqual(result["outcome"], "passed")
        self.assertEqual(result["worker_losses"], 1)
        self.assertEqual(result["recoveries_succeeded"], 1)
        self.assertEqual(result["accepted_changes"], 1)
        self.assertEqual(result["routine_transitions"], 3)
        self.assertEqual(result["routine_autonomous_transitions"], 3)

    def test_host_identity_does_not_change_greenfield_semantics(self):
        local = run_scenario("greenfield-feature-delivery", host="local", run_id="greenfield-local")
        github = run_scenario("greenfield-feature-delivery", host="github", run_id="greenfield-github")
        self.assertEqual(local["state_fingerprint"], github["state_fingerprint"])
        self.assertEqual(local["acceptance_fingerprint"], github["acceptance_fingerprint"])
        summary = summarize_results([local, github])
        self.assertEqual(summary["portability"]["scenarios_compared_across_hosts"], 1)
        self.assertEqual(summary["portability"]["equivalence_violations"], [])


if __name__ == "__main__":
    unittest.main()
