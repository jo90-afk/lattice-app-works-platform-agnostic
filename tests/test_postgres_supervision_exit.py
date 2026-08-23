from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from control_server import render_html  # noqa: E402
from lifecycle import advance_action, fail_action, review_action, submit_action  # noqa: E402
from postgres_store import PostgresStateStore  # noqa: E402
from supervision_model import supervision_model  # noqa: E402


POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class PostgresSupervisionExitTest(unittest.TestCase):
    def connect(self):
        import psycopg

        return psycopg.connect(POSTGRES_URL)

    def reset_database(self) -> None:
        connection = self.connect()
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
        connection.close()

    def setUp(self) -> None:
        self.reset_database()
        self.temporary = tempfile.TemporaryDirectory()
        self.snapshot = Path(self.temporary.name) / "checkpoint.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def seed_condition(
        self,
        store,
        project_id: str,
        project_name: str,
        owner_role: str,
        *,
        attempt_budget: int | None = None,
    ) -> None:
        store.ensure_project(project_id, project_name)
        store.add_objective(
            project_id,
            f"Objective for {project_name}",
            "Integrated human-supervision exit scenario.",
            "product",
            objective_id=f"objective-{project_id}",
        )
        store.add_milestone(
            project_id,
            f"objective-{project_id}",
            f"Milestone for {project_name}",
            1,
            True,
            milestone_id=f"milestone-{project_id}",
        )
        store.add_truth(
            project_id,
            "scenario.context",
            f"Canonical context for {project_name} is available.",
            "observed",
            "frontier",
            "director",
            truth_id=f"truth-{project_id}",
        )
        store.add_condition(
            project_id,
            f"objective-{project_id}",
            f"milestone-{project_id}",
            "scenario.result",
            f"Result for {project_name} is acceptable",
            "Complete and verify this project's bounded result.",
            owner_role,
            "quality",
            "director",
            attempt_budget=attempt_budget,
            truth_ids=[f"truth-{project_id}"],
            condition_id=f"condition-{project_id}",
        )

    def test_one_surface_explains_doing_changed_and_human_attention_state(self) -> None:
        store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            self.seed_condition(store, "doing-001", "Doing Project", "application")
            self.seed_condition(store, "changed-001", "Changed Project", "services")
            self.seed_condition(
                store,
                "blocked-001",
                "Blocked Project",
                "architecture",
                attempt_budget=1,
            )

            doing_claim = claim_for_host_atomic(
                store,
                project_id="doing-001",
                role="application",
                actor="application-doing",
                host="ci",
                workspace_id="doing-workspace",
            )

            changed_claim = claim_for_host_atomic(
                store,
                project_id="changed-001",
                role="services",
                actor="services-changed",
                host="ci",
                workspace_id="changed-workspace",
            )
            changed_submission = submit_action(
                store,
                changed_claim["lease_id"],
                "services",
                "Shared result delivered",
                ["artifact://0.0.7-exit/changed"],
                "evidence://0.0.7-exit/changed/build",
            )
            changed_review_claim = claim_for_host_atomic(
                store,
                project_id="changed-001",
                role="quality",
                actor="quality-changed",
                host="ci",
                workspace_id="changed-review",
            )
            changed_review = review_action(
                store,
                changed_review_claim["lease_id"],
                "quality",
                "SATISFIED",
                "Independent review passed",
                "evidence://0.0.7-exit/changed/review",
            )
            changed_assurance_claim = claim_for_host_atomic(
                store,
                project_id="changed-001",
                role="assurance",
                actor="assurance-changed",
                host="ci",
                workspace_id="changed-assurance",
            )
            advance_action(
                store,
                changed_assurance_claim["lease_id"],
                "assurance",
                "Verified result accepted",
            )

            blocked_claim = claim_for_host_atomic(
                store,
                project_id="blocked-001",
                role="architecture",
                actor="architecture-blocked",
                host="ci",
                workspace_id="blocked-workspace",
            )
            fail_action(
                store,
                blocked_claim["lease_id"],
                "architecture",
                "Bounded attempt failed and requires remediation",
            )
            principal_exception = store.raise_exception(
                "blocked-001",
                "external-risk-acceptance",
                "Decide whether to accept the external consequence",
                "The remaining consequence crosses the Principal authority boundary.",
                "critical",
                "director",
                "director",
                True,
                "condition",
                "condition-blocked-001",
            )

            model = supervision_model(store)
            page = render_html(model)

            projects = {item["project"]["id"]: item for item in model["projects"]}
            self.assertEqual(set(projects), {"doing-001", "changed-001", "blocked-001"})
            self.assertEqual(model["state_backend"], "postgres")
            self.assertEqual(model["portfolio"]["active_projects"], 3)
            self.assertEqual(model["portfolio"]["in_flight"], 1)
            self.assertEqual(projects["doing-001"]["active_leases"][0]["id"], doing_claim["lease_id"])
            self.assertGreaterEqual(projects["doing-001"]["active_leases"][0]["age_seconds"], 0)
            self.assertGreater(projects["doing-001"]["active_leases"][0]["remaining_seconds"], 0)

            self.assertEqual(changed_submission["result"]["status"], "pending")
            self.assertEqual(changed_review["result"]["condition"]["status"], "satisfied")
            self.assertEqual(projects["changed-001"]["milestone"], None)
            self.assertIn(
                "milestone_accepted",
                [change["event_type"] for change in model["recent_accepted_changes"]],
            )
            changed_graph = projects["changed-001"]["consequence_graph"]
            changed_edges = {
                (edge["source"], edge["relation"], edge["target"])
                for edge in changed_graph["edges"]
            }
            submission_id = changed_submission["result"]["id"]
            review_id = changed_review["result"]["review_id"]
            self.assertIn(
                (f"submission:{submission_id}", "claims_satisfaction_of", "condition:condition-changed-001"),
                changed_edges,
            )
            self.assertIn(
                (f"review:{review_id}", "verifies", f"submission:{submission_id}"),
                changed_edges,
            )
            self.assertTrue(any(edge["relation"] == "supports" for edge in changed_graph["edges"]))

            blocked_temporal = projects["blocked-001"]["temporal_health"]
            self.assertEqual(len(blocked_temporal["blocked_conditions"]), 1)
            self.assertEqual(blocked_temporal["blocked_conditions"][0]["id"], "condition-blocked-001")
            self.assertGreaterEqual(blocked_temporal["blocked_conditions"][0]["blocked_seconds"], 0)
            self.assertEqual(model["principal_inbox"]["count"], 1)
            decision = model["principal_inbox"]["items"][0]
            self.assertEqual(decision["target_id"], principal_exception["id"])
            self.assertEqual(decision["project_id"], "blocked-001")
            self.assertIn("principal_only", decision["authority_reason"])
            self.assertIn("does not permit an agent role", decision["authority_reason"])
            self.assertEqual(decision["affected_state"]["target"]["state"]["id"], "condition-blocked-001")
            self.assertEqual(
                {choice["choice"] for choice in decision["supported_choices"]},
                {"resolve", "leave_open"},
            )

            telemetry = model["operational_telemetry"]
            self.assertGreaterEqual(telemetry["claims"], 5)
            self.assertEqual(telemetry["retries"], 1)
            self.assertGreaterEqual(telemetry["exceptions_raised"], 2)
            self.assertEqual(telemetry["reviews"], 1)
            self.assertEqual(telemetry["verification_failure_rate"], 0.0)
            self.assertIn("ci", telemetry["hosts"])

            # The portfolio page exposes management state and live agents; deeper evidence lives on project detail.
            for phrase in (
                "Project Portfolio",
                "Doing Project",
                "Changed Project",
                "Blocked Project",
                "Needs your decision",
                "Decide whether to accept the external consequence",
                "Active Projects",
                "Agents",
                "Application",
                "Architecture",
                "Director",
                "Working",
                "Blocked",
                "Project detail",
            ):
                self.assertIn(phrase, page)
            self.assertNotIn("What changed", page)
            self.assertNotIn("Inspect evidence and consequence state", page)
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
