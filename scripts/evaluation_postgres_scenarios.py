#!/usr/bin/env python3
"""Live-Postgres 0.0.8 evaluation scenarios."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import threading
import time
from pathlib import Path
from typing import Any

from concurrency import claim_for_host_atomic
from evaluation import validate_result, validate_scenarios
from evaluation_fingerprint import acceptance_fingerprint, state_fingerprint
from hosted_delta import apply_delta_serialized
from lifecycle import review_action
from postgres_store import PostgresStateStore
from state_engine import LatticeError

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_URL = os.environ.get("LATTICE_TEST_POSTGRES_URL") or os.environ.get("LATTICE_DATABASE_URL")
PROJECT_ID = "eval-postgres-conflict"


def _connect(database_url: str):
    try:
        import psycopg
    except ImportError as error:
        raise LatticeError("Postgres evaluation requires psycopg") from error
    return psycopg.connect(database_url)


def _reset(database_url: str) -> None:
    connection = _connect(database_url)
    connection.autocommit = True
    try:
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
    finally:
        connection.close()


def _store(database_url: str, snapshot_path: Path) -> PostgresStateStore:
    return PostgresStateStore(ROOT, _connect(database_url), snapshot_path=snapshot_path)


def _seed(database_url: str, snapshot_path: Path) -> tuple[int, dict[str, dict[str, Any]]]:
    store = _store(database_url, snapshot_path)
    try:
        store.ensure_project(PROJECT_ID, "Concurrent Conflict Evaluation")
        objective = store.add_objective(
            PROJECT_ID,
            "Resolve concurrent hosted work without state ambiguity",
            "Two independent hosted workers prepare results from one observed semantic revision.",
            "product",
            objective_id="eval-conflict-objective",
        )
        milestone = store.add_milestone(
            PROJECT_ID,
            objective["id"],
            "Concurrent work is serialized and independently verified",
            1,
            True,
            milestone_id="eval-conflict-milestone",
        )
        store.add_condition(
            PROJECT_ID,
            objective["id"],
            milestone["id"],
            "application.result",
            "Application result is valid",
            "One independently prepared application result may commit from the observed state.",
            "application",
            "quality",
            "director",
            condition_id="eval-conflict-application",
        )
        store.add_condition(
            PROJECT_ID,
            objective["id"],
            milestone["id"],
            "services.result",
            "Services result is valid",
            "One independently prepared services result may commit from the observed state.",
            "services",
            "quality",
            "director",
            condition_id="eval-conflict-services",
        )
        base_revision = store.project_revision(PROJECT_ID)
        actions = {
            item["role"]: item
            for item in store.frontier(PROJECT_ID, None, 10)
            if item["role"] in {"application", "services"}
        }
        return base_revision, actions
    finally:
        store.close()


def run_concurrent_artifact_conflict(
    database_url: str,
    *,
    host: str = "postgres-ci",
    run_id: str = "postgres-conflict",
) -> dict[str, Any]:
    started = time.perf_counter()
    registry = validate_scenarios()
    scenario_ids = {item["id"] for item in registry["scenarios"]}
    with tempfile.TemporaryDirectory(prefix="lattice-postgres-eval-") as temporary:
        snapshot = Path(temporary) / "checkpoint.json"
        _reset(database_url)
        base_revision, actions = _seed(database_url, snapshot)
        if set(actions) != {"application", "services"}:
            raise LatticeError("Concurrent conflict evaluation did not derive both worker actions")

        deltas = [
            {
                "format": "lattice-state-delta",
                "schema_version": 1,
                "project_id": PROJECT_ID,
                "base_revision": base_revision,
                "role": role,
                "actor": "eval-" + role,
                "host": host,
                "workspace_id": "workspace-" + role,
                "action_key": actions[role]["action_key"],
                "outcome": {
                    "type": "submit",
                    "summary": role + " concurrent result",
                    "artifact_refs": [f"artifact://evaluation/concurrent-conflict/{role}"],
                    "evidence_ref": f"evidence://evaluation/concurrent-conflict/{role}",
                },
            }
            for role in ("application", "services")
        ]
        context_bytes = sum(
            len(json.dumps(delta, sort_keys=True, separators=(",", ":")).encode("utf-8"))
            for delta in deltas
        )

        first = _store(database_url, snapshot)
        second = _store(database_url, snapshot)
        barrier = threading.Barrier(2)
        lock = threading.Lock()
        outcomes: list[dict[str, Any]] = []

        def worker(store: PostgresStateStore, delta: dict[str, Any]) -> None:
            try:
                barrier.wait()
                result = apply_delta_serialized(store, delta)
                value = {
                    "kind": "accepted",
                    "role": delta["role"],
                    "revision": result["accepted_revision"],
                }
            except LatticeError as error:
                value = {
                    "kind": "rejected",
                    "role": delta["role"],
                    "error": str(error),
                }
            finally:
                store.close()
            with lock:
                outcomes.append(value)

        threads = [
            threading.Thread(target=worker, args=(first, deltas[0])),
            threading.Thread(target=worker, args=(second, deltas[1])),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        accepted = [item for item in outcomes if item["kind"] == "accepted"]
        rejected = [item for item in outcomes if item["kind"] == "rejected"]
        stale_rejection = len(rejected) == 1 and "Hosted delta is stale" in rejected[0]["error"]

        verify = _store(database_url, snapshot)
        try:
            submission = verify.conn.execute(
                """SELECT s.id, s.role, c.id AS condition_id
                   FROM submissions s JOIN conditions c ON c.id = s.condition_id
                   WHERE c.project_id = ?""",
                (PROJECT_ID,),
            ).fetchall()
            leases = int(
                verify.conn.execute(
                    "SELECT COUNT(*) FROM leases WHERE project_id = ?", (PROJECT_ID,)
                ).fetchone()[0]
            )
            review_passed = False
            if len(submission) == 1:
                review_claim = claim_for_host_atomic(
                    verify,
                    project_id=PROJECT_ID,
                    role="quality",
                    actor="eval-quality",
                    host=host,
                    workspace_id="workspace-quality",
                )
                context_bytes += len(
                    json.dumps(
                        review_claim["action"], sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                )
                review = review_action(
                    verify,
                    review_claim["lease_id"],
                    "quality",
                    "SATISFIED",
                    "Independent review confirms the single durable winner",
                    "evidence://evaluation/concurrent-conflict/review",
                )
                review_passed = review["result"]["condition"]["status"] == "satisfied"

            final_submissions = int(
                verify.conn.execute(
                    """SELECT COUNT(*) FROM submissions s
                       JOIN conditions c ON c.id = s.condition_id WHERE c.project_id = ?""",
                    (PROJECT_ID,),
                ).fetchone()[0]
            )
            final_reviews = int(
                verify.conn.execute(
                    """SELECT COUNT(*) FROM reviews r JOIN submissions s ON s.id = r.submission_id
                       JOIN conditions c ON c.id = s.condition_id WHERE c.project_id = ?""",
                    (PROJECT_ID,),
                ).fetchone()[0]
            )
            passed = bool(
                len(accepted) == 1
                and stale_rejection
                and final_submissions == 1
                and final_reviews == 1
                and leases == 0
                and review_passed
            )
            result = {
                "format": "lattice-evaluation-result",
                "version": 1,
                "scenario_id": "concurrent-artifact-conflict",
                "run_id": run_id,
                "host": host,
                "outcome": "passed" if passed else "failed",
                "state_fingerprint": state_fingerprint(verify, PROJECT_ID),
                "acceptance_fingerprint": acceptance_fingerprint(verify, PROJECT_ID),
                "routine_transitions": 2,
                "routine_autonomous_transitions": 2,
                "accepted_changes": 0,
                "false_acceptances": 0,
                "escalations": 0,
                "unnecessary_escalations": 0,
                "worker_losses": 0,
                "recoveries_succeeded": 0,
                "state_divergence_incidents": 0 if passed else 1,
                "verification_defects_presented": 0,
                "verification_catches": 0,
                "blocked_seconds_missing_information": 0,
                "context_bytes": context_bytes,
                "duration_seconds": time.perf_counter() - started,
            }
            return validate_result(result, scenario_ids)
        finally:
            verify.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run live-Postgres Lattice evaluation scenarios.")
    parser.add_argument("scenario", choices=["concurrent-artifact-conflict"])
    parser.add_argument("--database-url", default=DEFAULT_URL)
    parser.add_argument("--host", default="postgres-ci")
    parser.add_argument("--run-id", default="postgres-conflict")
    args = parser.parse_args()
    if not args.database_url:
        print(json.dumps({"error": "Postgres evaluation requires --database-url or LATTICE_TEST_POSTGRES_URL"}))
        return 2
    try:
        result = run_concurrent_artifact_conflict(
            args.database_url,
            host=args.host,
            run_id=args.run_id,
        )
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["outcome"] == "passed" else 1
    except LatticeError as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
