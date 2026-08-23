from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from concurrency import claim_for_host_atomic  # noqa: E402
from lifecycle import advance_action, review_action, submit_action  # noqa: E402
from postgres_store import PostgresStateStore  # noqa: E402
from scheduler import Worker, candidate_plan, dispatch  # noqa: E402


POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")
PROJECTS = ("exit-alpha", "exit-beta", "exit-gamma")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class PostgresConcurrencyExitTest(unittest.TestCase):
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
        folder = Path(self.temporary.name)
        self.snapshot = folder / "checkpoint.json"
        self.registry = folder / "registry.md"
        self.registry.write_text(
            "# Portfolio Registry\n\n"
            "**Concurrency limit:** 3 specialist threads.\n\n"
            "| Project ID | Project | Priority | State | Capsule |\n"
            "| --- | --- | --- | --- | --- |\n"
            "| exit-alpha | Alpha | 1 | Active | projects/exit-alpha/ |\n"
            "| exit-beta | Beta | 2 | Active | projects/exit-beta/ |\n"
            "| exit-gamma | Gamma | 3 | Active | projects/exit-gamma/ |\n",
            encoding="utf-8",
        )
        store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            for project_id in PROJECTS:
                store.ensure_project(project_id, project_id.title())
                store.add_objective(
                    project_id,
                    "Deliver concurrently",
                    "Prove bounded multi-project shared execution.",
                    "product",
                    objective_id=f"objective-{project_id}",
                )
                store.add_milestone(
                    project_id,
                    f"objective-{project_id}",
                    "Concurrent result accepted",
                    1,
                    True,
                    milestone_id=f"milestone-{project_id}",
                )
                store.add_condition(
                    project_id,
                    f"objective-{project_id}",
                    f"milestone-{project_id}",
                    "exit.concurrent",
                    "Concurrent worker result is independently verified",
                    "Complete one isolated project increment.",
                    "application",
                    "quality",
                    "director",
                    condition_id=f"condition-{project_id}",
                )
        finally:
            store.close()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def workers(self, role: str) -> list[Worker]:
        return [
            Worker(
                actor=f"{role}-{project_id}",
                role=role,
                host="ci",
                workspace_id=f"{role}-workspace-{project_id}",
            )
            for project_id in PROJECTS
        ]

    def run_concurrently(self, function, values):
        barrier = threading.Barrier(len(values))
        outcomes = []
        outcome_lock = threading.Lock()

        def run(value):
            try:
                barrier.wait(timeout=10)
                result = function(value)
                with outcome_lock:
                    outcomes.append(("ok", value, result))
            except Exception as error:  # surfaced below with the project/lease identity
                with outcome_lock:
                    outcomes.append(("error", value, error))

        threads = [threading.Thread(target=run, args=(value,)) for value in values]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=15)
        self.assertTrue(all(not thread.is_alive() for thread in threads), "concurrent workers did not finish")
        errors = [(value, error) for kind, value, error in outcomes if kind == "error"]
        self.assertEqual(errors, [], f"concurrent worker errors: {errors}")
        return [result for kind, _value, result in outcomes if kind == "ok"]

    def test_multi_project_workers_converge_without_queue_or_social_coordination(self) -> None:
        coordinator = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            before_revision = coordinator.revision
            before_events = coordinator.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            plan = candidate_plan(
                coordinator,
                self.workers("application"),
                registry_path=self.registry,
            )
            self.assertEqual([item["project_id"] for item in plan["assignments"]], list(PROJECTS))
            self.assertEqual(coordinator.revision, before_revision)
            self.assertEqual(
                coordinator.conn.execute("SELECT COUNT(*) FROM leases").fetchone()[0],
                0,
            )
            self.assertEqual(
                coordinator.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                before_events,
            )

            dispatched = dispatch(
                coordinator,
                self.workers("application"),
                registry_path=self.registry,
            )
            self.assertEqual(dispatched["rejected"], [])
            self.assertEqual(len(dispatched["claims"]), 3)
            claims_by_project = {
                claim["action"]["project_id"]: claim
                for claim in dispatched["claims"]
            }
            self.assertEqual(set(claims_by_project), set(PROJECTS))
            self.assertEqual(
                coordinator.conn.execute("SELECT COUNT(*) FROM leases").fetchone()[0],
                3,
            )
        finally:
            coordinator.close()

        def submit_project(project_id: str):
            store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
            try:
                claim = claims_by_project[project_id]
                return submit_action(
                    store,
                    claim["lease_id"],
                    "application",
                    f"Completed isolated increment for {project_id}",
                    [f"artifact://0.0.6-exit/{project_id}"],
                    f"evidence://0.0.6-exit/{project_id}/build",
                )
            finally:
                store.close()

        submitted = self.run_concurrently(submit_project, PROJECTS)
        self.assertEqual(len(submitted), 3)

        review_claims = {}
        for project_id in PROJECTS:
            store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
            try:
                review_claims[project_id] = claim_for_host_atomic(
                    store,
                    project_id=project_id,
                    role="quality",
                    actor=f"quality-{project_id}",
                    host="ci",
                    workspace_id=f"quality-workspace-{project_id}",
                )
            finally:
                store.close()

        def review_project(project_id: str):
            store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
            try:
                return review_action(
                    store,
                    review_claims[project_id]["lease_id"],
                    "quality",
                    "SATISFIED",
                    f"Independent verification passed for {project_id}",
                    f"evidence://0.0.6-exit/{project_id}/review",
                )
            finally:
                store.close()

        reviewed = self.run_concurrently(review_project, PROJECTS)
        self.assertEqual(len(reviewed), 3)

        assurance_claims = {}
        for project_id in PROJECTS:
            store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
            try:
                assurance_claims[project_id] = claim_for_host_atomic(
                    store,
                    project_id=project_id,
                    role="assurance",
                    actor=f"assurance-{project_id}",
                    host="ci",
                    workspace_id=f"assurance-workspace-{project_id}",
                )
            finally:
                store.close()

        def accept_project(project_id: str):
            store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
            try:
                return advance_action(
                    store,
                    assurance_claims[project_id]["lease_id"],
                    "assurance",
                    f"Accepted independently verified result for {project_id}",
                )
            finally:
                store.close()

        accepted = self.run_concurrently(accept_project, PROJECTS)
        self.assertEqual(len(accepted), 3)

        final_store = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            self.assertEqual(final_store.conn.execute("SELECT COUNT(*) FROM leases").fetchone()[0], 0)
            self.assertEqual(
                final_store.conn.execute(
                    "SELECT COUNT(*) FROM milestones WHERE status = 'accepted'"
                ).fetchone()[0],
                3,
            )
            self.assertEqual(
                final_store.conn.execute(
                    "SELECT COUNT(*) FROM conditions WHERE status = 'satisfied'"
                ).fetchone()[0],
                3,
            )
            self.assertEqual(
                final_store.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0],
                3,
            )
            self.assertEqual(
                final_store.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0],
                3,
            )
            revisions = [
                int(row["revision"])
                for row in final_store.conn.execute(
                    "SELECT revision FROM events WHERE event_type IN ('condition_submitted', 'submission_reviewed', 'milestone_accepted') ORDER BY id"
                ).fetchall()
            ]
            self.assertEqual(len(revisions), 9)
            self.assertEqual(len(set(revisions)), 9)
            for project_id in PROJECTS:
                self.assertEqual(final_store.frontier(project_id, limit=1000), [])
        finally:
            final_store.close()


if __name__ == "__main__":
    unittest.main()
