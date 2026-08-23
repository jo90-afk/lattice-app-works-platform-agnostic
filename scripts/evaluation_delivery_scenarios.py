#!/usr/bin/env python3
"""Executable 0.0.8 delivery, migration, and remediation evaluation scenarios."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from concurrency import claim_for_host_atomic
from evaluation import validate_result, validate_scenarios
from evaluation_fingerprint import acceptance_fingerprint, state_fingerprint
from lifecycle import advance_action, fail_action, review_action, submit_action
from state_engine import LatticeError, StateStore

ROOT = Path(__file__).resolve().parents[1]


def _context_bytes(claim: dict[str, Any]) -> int:
    return len(json.dumps(claim["action"], sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _event_count(store: StateStore, project_id: str, event_type: str) -> int:
    return int(
        store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE project_id = ? AND event_type = ?",
            (project_id, event_type),
        ).fetchone()[0]
    )


def _result(
    store: StateStore,
    *,
    project_id: str,
    scenario_id: str,
    run_id: str,
    host: str,
    passed: bool,
    started: float,
    context_bytes: int,
    routine_transitions: int,
    accepted_changes: int,
    state_divergence_incidents: int = 0,
    verification_defects_presented: int = 0,
    verification_catches: int = 0,
    escalations: int = 0,
    unnecessary_escalations: int = 0,
) -> dict[str, Any]:
    return {
        "format": "lattice-evaluation-result",
        "version": 1,
        "scenario_id": scenario_id,
        "run_id": run_id,
        "host": host,
        "outcome": "passed" if passed else "failed",
        "state_fingerprint": state_fingerprint(store, project_id),
        "acceptance_fingerprint": acceptance_fingerprint(store, project_id),
        "routine_transitions": routine_transitions,
        "routine_autonomous_transitions": routine_transitions,
        "accepted_changes": accepted_changes,
        "false_acceptances": 0,
        "escalations": escalations,
        "unnecessary_escalations": unnecessary_escalations,
        "worker_losses": 0,
        "recoveries_succeeded": 0,
        "state_divergence_incidents": state_divergence_incidents,
        "verification_defects_presented": verification_defects_presented,
        "verification_catches": verification_catches,
        "blocked_seconds_missing_information": 0,
        "context_bytes": context_bytes,
        "duration_seconds": time.perf_counter() - started,
    }


def _claim(store: StateStore, project_id: str, role: str, actor: str, host: str) -> dict[str, Any]:
    return claim_for_host_atomic(
        store,
        project_id=project_id,
        role=role,
        actor=actor,
        host=host,
        workspace_id=f"eval-{project_id}-{actor}",
    )


def _cross_component_refactor(store: StateStore, run_id: str, host: str) -> dict[str, Any]:
    started = time.perf_counter()
    project_id = "eval-refactor"
    objective_id = "eval-refactor-objective"
    milestone_id = "eval-refactor-milestone"
    contract_id = "eval-refactor-contract"
    app_condition = "eval-refactor-application"
    services_condition = "eval-refactor-services"

    store.ensure_project(project_id, "Cross Component Refactor Evaluation")
    store.add_objective(
        project_id,
        "Refactor two components without changing their shared contract",
        "Application and Services change independently while preserving one governed interface.",
        "product",
        objective_id=objective_id,
    )
    store.add_milestone(
        project_id,
        objective_id,
        "Both component changes preserve the contract",
        1,
        True,
        milestone_id=milestone_id,
    )
    store.put_record(
        project_id,
        "contract.shared-interface",
        "contract",
        "Shared interface invariant",
        "Request and response semantics remain unchanged across the refactor.",
        "architecture",
        "architecture",
        record_id=contract_id,
    )
    for condition_id, key, title, owner in (
        (app_condition, "refactor.application", "Application refactor preserves contract", "application"),
        (services_condition, "refactor.services", "Services refactor preserves contract", "services"),
    ):
        store.add_condition(
            project_id,
            objective_id,
            milestone_id,
            key,
            title,
            "Refactor the owned component without changing the shared interface contract.",
            owner,
            "quality",
            "director",
            input_record_ids=[contract_id],
            condition_id=condition_id,
        )

    context = 0
    for role in ("application", "services"):
        claim = _claim(store, project_id, role, f"{role}-refactor", host)
        context += _context_bytes(claim)
        submit_action(
            store,
            claim["lease_id"],
            role,
            f"{role} refactor complete with shared contract preserved",
            [f"artifact://evaluation/refactor/{role}"],
            f"evidence://evaluation/refactor/{role}",
        )

    for index in range(2):
        review = _claim(store, project_id, "quality", f"quality-refactor-{index}", host)
        context += _context_bytes(review)
        review_action(
            store,
            review["lease_id"],
            "quality",
            "SATISFIED",
            "Independent contract regression passed",
            f"evidence://evaluation/refactor/review-{index}",
        )

    assurance = _claim(store, project_id, "assurance", "assurance-refactor", host)
    context += _context_bytes(assurance)
    advance_action(store, assurance["lease_id"], "assurance", "Both refactor conditions independently verified")

    conditions = {
        row["id"]: dict(row)
        for row in store.conn.execute(
            "SELECT * FROM conditions WHERE project_id = ?", (project_id,)
        ).fetchall()
    }
    accepted_inputs = {
        row["condition_id"]: row["accepted_record_version"]
        for row in store.conn.execute(
            "SELECT condition_id, accepted_record_version FROM condition_inputs WHERE record_id = ?",
            (contract_id,),
        ).fetchall()
    }
    milestone = store.conn.execute("SELECT status FROM milestones WHERE id = ?", (milestone_id,)).fetchone()
    passed = bool(
        milestone
        and milestone["status"] == "accepted"
        and conditions[app_condition]["status"] == "satisfied"
        and conditions[services_condition]["status"] == "satisfied"
        and accepted_inputs[app_condition] == 1
        and accepted_inputs[services_condition] == 1
    )
    return _result(
        store,
        project_id=project_id,
        scenario_id="cross-component-refactor",
        run_id=run_id,
        host=host,
        passed=passed,
        started=started,
        context_bytes=context,
        routine_transitions=5,
        accepted_changes=_event_count(store, project_id, "milestone_accepted"),
        state_divergence_incidents=0 if passed else 1,
    )


def _migration_work(store: StateStore, run_id: str, host: str) -> dict[str, Any]:
    started = time.perf_counter()
    project_id = "eval-migration"
    objective_id = "eval-migration-objective"
    milestone_id = "eval-migration-milestone"
    contract_id = "eval-migration-contract"
    condition_id = "eval-migration-condition"

    store.ensure_project(project_id, "Migration Evaluation")
    store.add_objective(
        project_id,
        "Migrate a versioned interface without carrying stale acceptance forward",
        "Acceptance under v1 must be invalidated when v2 becomes the current governed contract.",
        "product",
        objective_id=objective_id,
    )
    store.add_milestone(
        project_id,
        objective_id,
        "Version two is independently verified",
        1,
        True,
        milestone_id=milestone_id,
    )
    store.put_record(
        project_id,
        "contract.migration-interface",
        "contract",
        "Migration interface v1",
        "Version one payload semantics.",
        "architecture",
        "architecture",
        record_id=contract_id,
    )
    store.add_condition(
        project_id,
        objective_id,
        milestone_id,
        "migration.compatible",
        "Migrated implementation matches current interface",
        "The implementation must be verified against the current contract version.",
        "application",
        "quality",
        "director",
        input_record_ids=[contract_id],
        condition_id=condition_id,
    )

    context = 0
    owner_v1 = _claim(store, project_id, "application", "application-migration-v1", host)
    context += _context_bytes(owner_v1)
    submit_action(
        store,
        owner_v1["lease_id"],
        "application",
        "Version one migration implementation",
        ["artifact://evaluation/migration/v1"],
        "evidence://evaluation/migration/v1",
    )
    quality_v1 = _claim(store, project_id, "quality", "quality-migration-v1", host)
    context += _context_bytes(quality_v1)
    review_action(
        store,
        quality_v1["lease_id"],
        "quality",
        "SATISFIED",
        "Version one implementation matches version one contract",
        "evidence://evaluation/migration/review-v1",
    )
    before = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())
    accepted_before = store.conn.execute(
        "SELECT accepted_record_version FROM condition_inputs WHERE condition_id = ? AND record_id = ?",
        (condition_id, contract_id),
    ).fetchone()["accepted_record_version"]

    store.put_record(
        project_id,
        "contract.migration-interface",
        "contract",
        "Migration interface v2",
        "Version two payload semantics with the migrated field representation.",
        "architecture",
        "architecture",
        reason="migration contract advanced to version two",
    )
    invalidated = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())

    owner_v2 = _claim(store, project_id, "application", "application-migration-v2", host)
    context += _context_bytes(owner_v2)
    submit_action(
        store,
        owner_v2["lease_id"],
        "application",
        "Version two migration implementation",
        ["artifact://evaluation/migration/v2"],
        "evidence://evaluation/migration/v2",
    )
    quality_v2 = _claim(store, project_id, "quality", "quality-migration-v2", host)
    context += _context_bytes(quality_v2)
    review_action(
        store,
        quality_v2["lease_id"],
        "quality",
        "SATISFIED",
        "Version two implementation matches current contract",
        "evidence://evaluation/migration/review-v2",
    )
    assurance = _claim(store, project_id, "assurance", "assurance-migration", host)
    context += _context_bytes(assurance)
    advance_action(store, assurance["lease_id"], "assurance", "Current migration contract independently verified")

    after = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())
    accepted_after = store.conn.execute(
        "SELECT accepted_record_version FROM condition_inputs WHERE condition_id = ? AND record_id = ?",
        (condition_id, contract_id),
    ).fetchone()["accepted_record_version"]
    milestone = store.conn.execute("SELECT status FROM milestones WHERE id = ?", (milestone_id,)).fetchone()
    passed = bool(
        before["status"] == "satisfied"
        and accepted_before == 1
        and invalidated["status"] == "unknown"
        and invalidated["state_version"] > before["state_version"]
        and after["status"] == "satisfied"
        and accepted_after == 2
        and milestone
        and milestone["status"] == "accepted"
    )
    return _result(
        store,
        project_id=project_id,
        scenario_id="migration-work",
        run_id=run_id,
        host=host,
        passed=passed,
        started=started,
        context_bytes=context,
        routine_transitions=5,
        accepted_changes=_event_count(store, project_id, "milestone_accepted"),
        state_divergence_incidents=0 if passed else 1,
    )


def _ci_remediation(store: StateStore, run_id: str, host: str) -> dict[str, Any]:
    started = time.perf_counter()
    project_id = "eval-ci-remediation"
    objective_id = "eval-ci-objective"
    milestone_id = "eval-ci-milestone"
    condition_id = "eval-ci-condition"

    store.ensure_project(project_id, "CI Remediation Evaluation")
    store.add_objective(
        project_id,
        "Repair a failing CI gate through bounded remediation",
        "A routine first failure should return actionable work rather than escalate prematurely.",
        "quality",
        objective_id=objective_id,
    )
    store.add_milestone(
        project_id,
        objective_id,
        "The corrected change passes independent verification",
        1,
        True,
        milestone_id=milestone_id,
    )
    store.add_condition(
        project_id,
        objective_id,
        milestone_id,
        "ci.green",
        "CI regression is repaired",
        "Diagnose the failing gate, make a bounded correction, and pass independent verification.",
        "application",
        "quality",
        "director",
        attempt_budget=3,
        condition_id=condition_id,
    )

    context = 0
    first = _claim(store, project_id, "application", "application-ci-first", host)
    context += _context_bytes(first)
    failure = fail_action(
        store,
        first["lease_id"],
        "application",
        "Targeted check still fails after first bounded attempt",
    )
    after_failure = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())
    open_exceptions = int(
        store.conn.execute(
            "SELECT COUNT(*) FROM exceptions WHERE project_id = ? AND status = 'open'",
            (project_id,),
        ).fetchone()[0]
    )

    second = _claim(store, project_id, "application", "application-ci-second", host)
    context += _context_bytes(second)
    submit_action(
        store,
        second["lease_id"],
        "application",
        "Root cause corrected; targeted CI gate now passes",
        ["artifact://evaluation/ci-remediation/fix"],
        "evidence://evaluation/ci-remediation/targeted-check",
    )
    quality = _claim(store, project_id, "quality", "quality-ci", host)
    context += _context_bytes(quality)
    review_action(
        store,
        quality["lease_id"],
        "quality",
        "SATISFIED",
        "Independent regression verifies the repaired gate",
        "evidence://evaluation/ci-remediation/review",
    )
    assurance = _claim(store, project_id, "assurance", "assurance-ci", host)
    context += _context_bytes(assurance)
    advance_action(store, assurance["lease_id"], "assurance", "Remediation independently verified")

    final_condition = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())
    milestone = store.conn.execute("SELECT status FROM milestones WHERE id = ?", (milestone_id,)).fetchone()
    passed = bool(
        failure["result"]["blocked"] is False
        and after_failure["status"] == "unmet"
        and after_failure["attempt_count"] == 1
        and open_exceptions == 0
        and final_condition["status"] == "satisfied"
        and final_condition["attempt_count"] == 2
        and milestone
        and milestone["status"] == "accepted"
    )
    return _result(
        store,
        project_id=project_id,
        scenario_id="ci-remediation",
        run_id=run_id,
        host=host,
        passed=passed,
        started=started,
        context_bytes=context,
        routine_transitions=4,
        accepted_changes=_event_count(store, project_id, "milestone_accepted"),
        escalations=0,
        unnecessary_escalations=0,
    )


SCENARIOS: dict[str, Callable[[StateStore, str, str], dict[str, Any]]] = {
    "cross-component-refactor": _cross_component_refactor,
    "migration-work": _migration_work,
    "ci-remediation": _ci_remediation,
}


def run_delivery_scenario(scenario_id: str, *, host: str = "local", run_id: str | None = None) -> dict[str, Any]:
    registry = validate_scenarios()
    scenario_ids = {item["id"] for item in registry["scenarios"]}
    if scenario_id not in SCENARIOS:
        raise LatticeError("Executable delivery evaluation scenario not implemented: " + scenario_id)
    with tempfile.TemporaryDirectory(prefix="lattice-delivery-eval-") as temporary:
        folder = Path(temporary)
        with StateStore(ROOT, db_path=folder / "state.db", snapshot_path=folder / "state.json") as store:
            result = SCENARIOS[scenario_id](store, run_id or f"{scenario_id}:{host}", host)
            return validate_result(result, scenario_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run delivery-oriented Lattice evaluation scenarios.")
    parser.add_argument("scenario", choices=sorted(SCENARIOS))
    parser.add_argument("--host", default="local")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    try:
        result = run_delivery_scenario(args.scenario, host=args.host, run_id=args.run_id)
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["outcome"] == "passed" else 1
    except LatticeError as error:
        print(json.dumps({"error": str(error)}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
