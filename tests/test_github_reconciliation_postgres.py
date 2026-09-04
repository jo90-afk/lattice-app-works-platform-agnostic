from __future__ import annotations

import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from github_reconciliation import reconcile_github_state
from postgres_store import PostgresStateStore
from state_engine import LatticeError, json_text
from test_github_reconciliation import NOW, observations, tracking

POSTGRES_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL")


@unittest.skipUnless(POSTGRES_URL, "LATTICE_TEST_POSTGRES_URL not configured")
class GitHubReconcilePostgresTest(unittest.TestCase):
    def test_competing_observations_have_one_winner_and_safe_replay(self):
        import psycopg
        connection = psycopg.connect(POSTGRES_URL, autocommit=True)
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
        connection.close()
        with tempfile.TemporaryDirectory() as folder:
            snapshot = Path(folder) / "missing.json"

            def open_store():
                return PostgresStateStore(ROOT, psycopg.connect(POSTGRES_URL), snapshot_path=snapshot)

            with open_store() as setup:
                setup.ensure_project("product", "Example product")
                setup.put_record("product", "github.tracking", "contract", "GitHub tracking",
                                 json_text(tracking()), "director", "director")
                revision = setup.project_revision("product")
            stores = [open_store(), open_store()]
            barrier = threading.Barrier(2)
            outcomes = []

            def run(store, capture):
                try:
                    barrier.wait(timeout=10)
                    result = reconcile_github_state(store, project_id="product", envelope=capture,
                                                     expected_revision=revision, role="director", now=NOW)
                    outcomes.append(("ok", result, capture))
                except Exception as error:
                    outcomes.append(("error", error, capture))
                finally:
                    store.close()

            threads = [threading.Thread(target=run, args=(stores[0], observations())),
                       threading.Thread(target=run, args=(stores[1], observations(captured_at="2026-09-04T19:30:00Z")))]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=20)
                self.assertFalse(thread.is_alive(), "GitHub observation writer stalled")
            self.assertEqual(sum(kind == "ok" for kind, _, _ in outcomes), 1)
            self.assertEqual(sum(kind == "error" for kind, _, _ in outcomes), 1)
            error = next(result for kind, result, _ in outcomes if kind == "error")
            self.assertIsInstance(error, LatticeError)
            self.assertIn("expected project revision", str(error))
            winner = next(capture for kind, _, capture in outcomes if kind == "ok")
            with open_store() as verify:
                replay = reconcile_github_state(verify, project_id="product", envelope=winner,
                                                expected_revision=revision, role="director", now=NOW)
                self.assertTrue(replay["replayed"])
                self.assertEqual(verify.conn.execute("SELECT COUNT(*) FROM truth_versions").fetchone()[0], 1)
                self.assertEqual(verify.conn.execute("SELECT COUNT(*) FROM milestones").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
