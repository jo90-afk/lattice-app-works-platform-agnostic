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

from hosted_delta import apply_delta_serialized  # noqa: E402
from postgres_store import PostgresStateStore  # noqa: E402
from semantic_writes import revise_truth_cas  # noqa: E402
from state_engine import LatticeError  # noqa: E402

POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class PostgresSemanticConcurrencyTest(unittest.TestCase):
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
        self.snapshot = Path(self.temporary.name) / "missing-current.json"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def stores(self, count: int):
        return [PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot) for _ in range(count)]

    def test_competing_truth_revisions_produce_one_version_two(self) -> None:
        setup = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            setup.ensure_project("project-001", "Truth Race")
            setup.add_truth(
                "project-001", "world.fact", "Initial", "observed", "frontier",
                "director", truth_id="truth-001",
            )
        finally:
            setup.close()

        first, second = self.stores(2)
        barrier = threading.Barrier(2)
        outcomes: list[tuple[str, str]] = []
        lock = threading.Lock()

        def worker(store, statement):
            try:
                barrier.wait()
                result = revise_truth_cas(
                    store,
                    truth_id="truth-001",
                    changed_by="director",
                    reason="concurrent evidence",
                    expected_version=1,
                    statement=statement,
                )
                value = ("ok", str(result["truth"]["statement"]))
            except LatticeError as error:
                value = ("error", str(error))
            finally:
                store.close()
            with lock:
                outcomes.append(value)

        threads = [
            threading.Thread(target=worker, args=(first, "First contender")),
            threading.Thread(target=worker, args=(second, "Second contender")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(sum(kind == "ok" for kind, _ in outcomes), 1)
        self.assertEqual(sum(kind == "error" for kind, _ in outcomes), 1)
        self.assertTrue(any("current 2" in value for kind, value in outcomes if kind == "error"))

        verify = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            truth = verify.conn.execute(
                "SELECT statement, version FROM truths WHERE id = 'truth-001'"
            ).fetchone()
            versions = int(
                verify.conn.execute(
                    "SELECT COUNT(*) FROM truth_versions WHERE truth_id = 'truth-001'"
                ).fetchone()[0]
            )
            self.assertEqual(int(truth["version"]), 2)
            self.assertEqual(versions, 2)
        finally:
            verify.close()

    def test_same_base_hosted_deltas_have_one_semantic_winner(self) -> None:
        setup = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            setup.ensure_project("project-001", "Delta Race")
            objective = setup.add_objective(
                "project-001", "Deliver", "Concurrent hosted deltas", "product",
                objective_id="objective-001",
            )
            milestone = setup.add_milestone(
                "project-001", objective["id"], "Ready", 1, True,
                milestone_id="milestone-001",
            )
            setup.add_condition(
                "project-001", objective["id"], milestone["id"], "app.done",
                "App done", "App", "application", "quality", "director",
                condition_id="condition-app",
            )
            setup.add_condition(
                "project-001", objective["id"], milestone["id"], "service.done",
                "Service done", "Service", "services", "quality", "director",
                condition_id="condition-services",
            )
            base = setup.project_revision("project-001")
            actions = {item["role"]: item for item in setup.frontier("project-001", None, 10)}
        finally:
            setup.close()

        deltas = [
            {
                "format": "lattice-state-delta",
                "schema_version": 1,
                "project_id": "project-001",
                "base_revision": base,
                "role": role,
                "actor": "hosted-" + role,
                "action_key": actions[role]["action_key"],
                "outcome": {
                    "type": "submit",
                    "summary": role + " complete",
                    "artifact_refs": [f"artifact://{role}-output"],
                },
            }
            for role in ("application", "services")
        ]
        first, second = self.stores(2)
        barrier = threading.Barrier(2)
        outcomes: list[tuple[str, str]] = []
        result_lock = threading.Lock()

        def apply(store, delta):
            try:
                barrier.wait()
                result = apply_delta_serialized(store, delta)
                value = ("ok", str(result["accepted_revision"]))
            except LatticeError as error:
                value = ("error", str(error))
            finally:
                store.close()
            with result_lock:
                outcomes.append(value)

        threads = [
            threading.Thread(target=apply, args=(first, deltas[0])),
            threading.Thread(target=apply, args=(second, deltas[1])),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(sum(kind == "ok" for kind, _ in outcomes), 1)
        self.assertEqual(sum(kind == "error" for kind, _ in outcomes), 1)
        self.assertTrue(any("Hosted delta is stale" in value for kind, value in outcomes if kind == "error"))

        verify = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            self.assertEqual(int(verify.conn.execute("SELECT COUNT(*) FROM submissions").fetchone()[0]), 1)
            self.assertEqual(int(verify.conn.execute("SELECT COUNT(*) FROM leases").fetchone()[0]), 0)
        finally:
            verify.close()

    def test_cross_project_revision_allocations_are_unique(self) -> None:
        setup = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            setup.ensure_project("project-a", "Project A")
            setup.ensure_project("project-b", "Project B")
            before = setup.revision
        finally:
            setup.close()

        first, second = self.stores(2)
        barrier = threading.Barrier(2)
        errors: list[str] = []
        error_lock = threading.Lock()

        def mutate(store, project_id, key):
            try:
                barrier.wait()
                store.put_record(
                    project_id,
                    key,
                    "requirement",
                    key,
                    "Concurrent project write",
                    "product",
                    "product",
                )
            except Exception as error:
                with error_lock:
                    errors.append(str(error))
            finally:
                store.close()

        threads = [
            threading.Thread(target=mutate, args=(first, "project-a", "requirement.a")),
            threading.Thread(target=mutate, args=(second, "project-b", "requirement.b")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])

        verify = PostgresStateStore(ROOT, self.connect(), snapshot_path=self.snapshot)
        try:
            self.assertEqual(verify.revision, before + 2)
            revisions = [
                int(row["revision"])
                for row in verify.conn.execute(
                    "SELECT revision FROM events WHERE event_type = 'record_created' ORDER BY revision"
                ).fetchall()
            ]
            self.assertEqual(len(revisions), 2)
            self.assertEqual(len(set(revisions)), 2)
        finally:
            verify.close()


if __name__ == "__main__":
    unittest.main()
