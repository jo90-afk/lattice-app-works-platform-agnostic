from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from lifecycle import fail_action, release_action  # noqa: E402
from state_engine import StateStore  # noqa: E402
from supervision_model import supervision_model  # noqa: E402


class SupervisionModelTest(unittest.TestCase):
    def make_store(self, folder: Path) -> StateStore:
        store = StateStore(ROOT, folder / "state.db", folder / "current.json")
        store.ensure_project("project-001", "Supervised Project")
        store.add_objective(
            "project-001",
            "Deliver",
            "Exercise supervision.",
            "product",
            objective_id="objective-001",
        )
        store.add_milestone(
            "project-001",
            "objective-001",
            "Verified",
            1,
            True,
            milestone_id="milestone-001",
        )
        return store

    def test_projection_combines_portfolio_decisions_changes_and_runtime_telemetry(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self.make_store(folder) as store:
                store.add_condition(
                    "project-001",
                    "objective-001",
                    "milestone-001",
                    "supervision.visible",
                    "Work appears in supervision",
                    "Create one derived action.",
                    "application",
                    "quality",
                    "director",
                    condition_id="condition-001",
                )
                store.add_truth(
                    "project-001",
                    "environment.ready",
                    "The supervision scenario is ready.",
                    "observed",
                    "frontier",
                    "director",
                    truth_id="truth-001",
                )
                store.raise_exception(
                    "project-001",
                    "principal-choice",
                    "Principal choice required",
                    "A deliberate human boundary.",
                    "major",
                    "director",
                    "director",
                    True,
                )
                claim = claim_for_host_atomic(
                    store,
                    project_id="project-001",
                    role="application",
                    actor="application-1",
                    host="ci",
                    workspace_id="workspace-1",
                )
                release_action(store, claim["lease_id"], "application")
                with store.conn:
                    store.conn.execute(
                        """UPDATE events SET created_at = '2026-08-23T12:00:00Z'
                           WHERE event_type = 'action_claimed' AND entity_id = ?""",
                        (claim["lease_id"],),
                    )
                    store.conn.execute(
                        """UPDATE events SET created_at = '2026-08-23T12:05:00Z'
                           WHERE event_type = 'action_released'
                             AND json_extract(payload_json, '$.lease_id') = ?""",
                        (claim["lease_id"],),
                    )

                active = claim_for_host_atomic(
                    store,
                    project_id="project-001",
                    role="application",
                    actor="application-2",
                    host="ci",
                    workspace_id="workspace-2",
                )
                model = supervision_model(store, "project-001")

            self.assertEqual(model["format"], "lattice-control-read-model")
            self.assertEqual(model["state_backend"], "sqlite")
            self.assertEqual(model["portfolio"]["active_projects"], 1)
            self.assertEqual(model["portfolio"]["principal_decisions"], 1)
            self.assertEqual(model["principal_inbox"]["count"], 1)
            telemetry = model["operational_telemetry"]
            self.assertGreaterEqual(telemetry["claims"], 2)
            self.assertGreaterEqual(telemetry["completed_transitions"], 1)
            self.assertIn("ci", telemetry["hosts"])
            self.assertEqual(telemetry["completed_action_durations_seconds"], [300])
            self.assertEqual(telemetry["median_action_duration_seconds"], 300)
            self.assertEqual(telemetry["max_action_duration_seconds"], 300)
            projected_lease = model["projects"][0]["active_leases"][0]
            self.assertEqual(projected_lease["id"], active["lease_id"])
            self.assertGreaterEqual(projected_lease["age_seconds"], 0)
            self.assertGreater(projected_lease["remaining_seconds"], 0)
            self.assertIn(
                "truth_recorded",
                [item["event_type"] for item in model["recent_accepted_changes"]],
            )

    def test_blocked_condition_age_and_retry_count_are_derived_from_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            with self.make_store(folder) as store:
                store.add_condition(
                    "project-001",
                    "objective-001",
                    "milestone-001",
                    "supervision.blocked",
                    "Blocked work is visible",
                    "Exhaust one bounded retry.",
                    "architecture",
                    "quality",
                    "director",
                    attempt_budget=1,
                    condition_id="condition-blocked",
                )
                claim = claim_for_host_atomic(
                    store,
                    project_id="project-001",
                    role="architecture",
                    actor="architect-1",
                    host="ci",
                )
                fail_action(
                    store,
                    claim["lease_id"],
                    "architecture",
                    "Bounded attempt failed",
                )
                model = supervision_model(store, "project-001")

            temporal = model["projects"][0]["temporal_health"]
            self.assertEqual(len(temporal["blocked_conditions"]), 1)
            self.assertEqual(temporal["blocked_conditions"][0]["id"], "condition-blocked")
            self.assertGreaterEqual(temporal["blocked_conditions"][0]["blocked_seconds"], 0)
            self.assertGreaterEqual(temporal["oldest_blocked_condition_seconds"], 0)
            self.assertEqual(model["operational_telemetry"]["retries"], 1)
            self.assertEqual(model["operational_telemetry"]["exceptions_raised"], 1)


if __name__ == "__main__":
    unittest.main()
