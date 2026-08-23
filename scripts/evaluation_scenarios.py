#!/usr/bin/env python3
"""Executable bounded evaluation scenarios over real Lattice transitions."""

from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from concurrency import claim_for_host_atomic
from control_plane import recover_expired_leases
from evaluation import validate_result, validate_scenarios
from evaluation_fingerprint import acceptance_fingerprint, state_fingerprint
from lifecycle import advance_action, review_action, submit_action
from state_engine import LatticeError, StateStore

ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = "eval-project"
OBJECTIVE_ID = "eval-objective"
MILESTONE_ID = "eval-milestone"
CONDITION_ID = "eval-condition"
TRUTH_ID = "eval-truth"


def _context_bytes(claim: dict[str, Any]) -> int:
    return len(json.dumps(claim["action"], sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _seed(store: StateStore, *, attempt_budget: int = 3) -> None:
    store.ensure_project(PROJECT_ID, "Evaluation Project")
    store.add_objective(
        PROJECT_ID,
        "Deliver the bounded evaluation result",
        "Exercise guarded owner, verifier, and acceptance transitions.",
        "product",
        objective_id=OBJECTIVE_ID,
    )
    store.add_milestone(
        PROJECT_ID,
        OBJECTIVE_ID,
        "Evaluation result is independently verified",
        1,
        True,
        milestone_id=MILESTONE_ID,
    )
    store.add_truth(
        PROJECT_ID,
        "evaluation.requirement.confirmed",
        "The bounded evaluation requirement is confirmed.",
        "accepted",
        "frontier",
        "director",
        material=True,
        truth_id=TRUTH_ID,
    )
    store.add_condition(
        PROJECT_ID,
        OBJECTIVE_ID,
        MILESTONE_ID,
        "evaluation.result.acceptable",
        "Evaluation result is acceptable",
        "The bounded result is produced and independently verified.",
        "application",
        "quality",
        "director",
        truth_ids=[TRUTH_ID],
        attempt_budget=attempt_budget,
        condition_id=CONDITION_ID,
    )


def _claim(store: StateStore, role: str, actor: str, host: str, workspace: str) -> dict[str, Any]:
    return claim_for_host_atomic(
        store,
        project_id=PROJECT_ID,
        role=role,
        actor=actor,
        host=host,
        workspace_id=workspace,
    )


def _event_count(store: StateStore, event_type: str) -> int:
    return int(
        store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE project_id = ? AND event_type = ?",
            (PROJECT_ID, event_type),
        ).fetchone()[0]
    )


def _routine_counts(store: StateStore) -> tuple[int, int]:
    routine = sum(
        _event_count(store, event_type)
        for event_type in (
            "action_submitted",
            "verification_recorded",
            "milestone_acceptance_recorded",
        )
    )
    principal = int(
        store.conn.execute(
            "SELECT COUNT(*) FROM events WHERE project_id = ? AND role = 'principal'",
            (PROJECT_ID,),
        ).fetchone()[0]
    )
    return routine, max(0, routine - principal)


def _base_result(
    store: StateStore,
    *,
    scenario_id: str,
    run_id: str,
    host: str,
    outcome: str,
    context_bytes: int,
    started: float,
    false_acceptances: int = 0,
    escalations: int = 0,
    unnecessary_escalations: int = 0,
    worker_losses: int = 0,
    recoveries_succeeded: int = 0,
    state_divergence_incidents: int = 0,
    verification_defects_presented: int = 0,
    verification_catches: int = 0,
    blocked_seconds_missing_information: float = 0,
) -> dict[str, Any]:
    routine, autonomous = _routine_counts(store)
    accepted_changes = _event_count(store, "milestone_accepted")
    return {
        "format": "lattice-evaluation-result",
        "version": 1,
        "scenario_id": scenario_id,
        "run_id": run_id,
        "host": host,
        "outcome": outcome,
        "state_fingerprint": state_fingerprint(store, PROJECT_ID),
        "acceptance_fingerprint": acceptance_fingerprint(store, PROJECT_ID),
        "routine_transitions": routine,
        "routine_autonomous_transitions": autonomous,
        "accepted_changes": accepted_changes,
        "false_acceptances": false_acceptances,
        "escalations": escalations,
        "unnecessary_escalations": unnecessary_escalations,
        "worker_losses": worker_losses,
        "recoveries_succeeded": recoveries_succeeded,
        "state_divergence_incidents": state_divergence_incidents,
        "verification_defects_presented": verification_defects_presented,
        "verification_catches": verification_catches,
        "blocked_seconds_missing_information": blocked_seconds_missing_information,
        "context_bytes": context_bytes,
        "duration_seconds": time.perf_counter() - started,
    }


def _greenfield(store: StateStore, run_id: str, host: str) -> dict[str, Any]:
    started = time.perf_counter()
    _seed(store)
    context = 0
    owner = _claim(store, "application", "application-eval", host, "owner-workspace")
    context += _context_bytes(owner)
    submit_action(
        store,
        owner["lease_id"],
        "application",
        "Bounded feature result produced",
        ["artifact://evaluation/greenfield/result"],
        "evidence://evaluation/greenfield/build",
    )
    verifier = _claim(store, "quality", "quality-eval", host, "verification-workspace")
    context += _context_bytes(verifier)
    review_action(
        store,
        verifier["lease_id"],
        "quality",
        "SATISFIED",
        "Independent evaluation verification passed",
        "evidence://evaluation/greenfield/review",
    )
    assurance = _claim(store, "assurance", "assurance-eval", host, "assurance-workspace")
    context += _context_bytes(assurance)
    advance_action(store, assurance["lease_id"], "assurance", "Verified result accepted")
    milestone = store.conn.execute("SELECT status FROM milestones WHERE id = ?", (MILESTONE_ID,)).fetchone()
    condition = store.conn.execute("SELECT status FROM conditions WHERE id = ?", (CONDITION_ID,)).fetchone()
    passed = bool(milestone and milestone["status"] == "accepted" and condition and condition["status"] == "satisfied")
    return _base_result(
        store,
        scenario_id="greenfield-feature-delivery",
        run_id=run_id,
        host=host,
        outcome="passed" if passed else "failed",
        context_bytes=context,
        started=started,
    )


def _verifier_disagreement(store: StateStore, run_id: str, host: str) -> dict[str, Any]:
    started = time.perf_counter()
    _seed(store)
    context = 0
    owner = _claim(store, "application", "application-eval", host, "owner-workspace")
    context += _context_bytes(owner)
    submit_action(
        store,
        owner["lease_id"],
        "application",
        "Seeded result contains the evaluation defect",
        ["artifact://evaluation/verifier-disagreement/defective-result"],
        "evidence://evaluation/verifier-disagreement/owner",
    )
    verifier = _claim(store, "quality", "quality-eval", host, "verification-workspace")
    context += _context_bytes(verifier)
    review_action(
        store,
        verifier["lease_id"],
        "quality",
        "NOT_SATISFIED",
        "Seeded defect detected; acceptance must remain blocked",
        "evidence://evaluation/verifier-disagreement/catch",
    )
    condition = store.conn.execute("SELECT status FROM conditions WHERE id = ?", (CONDITION_ID,)).fetchone()
    milestone = store.conn.execute("SELECT status FROM milestones WHERE id = ?", (MILESTONE_ID,)).fetchone()
    no_acceptance = _event_count(store, "milestone_accepted") == 0
    passed = bool(
        condition
        and condition["status"] != "satisfied"
        and milestone
        and milestone["status"] != "accepted"
        and no_acceptance
    )
    return _base_result(
        store,
        scenario_id="verifier-disagreement",
        run_id=run_id,
        host=host,
        outcome="passed" if passed else "failed",
        context_bytes=context,
        started=started,
        false_acceptances=0 if no_acceptance else 1,
        verification_defects_presented=1,
        verification_catches=1 if passed else 0,
    )


def _worker_recovery(store: StateStore, run_id: str, host: str) -> dict[str, Any]:
    started = time.perf_counter()
    _seed(store)
    context = 0
    vanished = _claim(store, "application", "application-vanished", host, "vanished-workspace")
    context += _context_bytes(vanished)

    # Evaluation-only fault injection: expire the already-guarded lease to model host loss
    # without sleeping. Recovery itself uses the production recovery boundary.
    with store.conn:
        store.conn.execute(
            "UPDATE leases SET expires_at = '2000-01-01T00:00:00Z' WHERE id = ?",
            (vanished["lease_id"],),
        )
    recovery = recover_expired_leases(store, PROJECT_ID)
    recovered = recovery["recovered"] == 1

    owner = _claim(store, "application", "application-reclaimed", host, "reclaimed-workspace")
    context += _context_bytes(owner)
    submit_action(
        store,
        owner["lease_id"],
        "application",
        "Recovered action completed without reconstructing intent",
        ["artifact://evaluation/recovery/result"],
        "evidence://evaluation/recovery/build",
    )
    verifier = _claim(store, "quality", "quality-eval", host, "verification-workspace")
    context += _context_bytes(verifier)
    review_action(
        store,
        verifier["lease_id"],
        "quality",
        "SATISFIED",
        "Recovered result independently verified",
        "evidence://evaluation/recovery/review",
    )
    assurance = _claim(store, "assurance", "assurance-eval", host, "assurance-workspace")
    context += _context_bytes(assurance)
    advance_action(store, assurance["lease_id"], "assurance", "Recovered verified result accepted")
    condition = store.conn.execute("SELECT status FROM conditions WHERE id = ?", (CONDITION_ID,)).fetchone()
    passed = bool(recovered and condition and condition["status"] == "satisfied")
    return _base_result(
        store,
        scenario_id="worker-crash-and-lease-expiry",
        run_id=run_id,
        host=host,
        outcome="passed" if passed else "failed",
        context_bytes=context,
        started=started,
        worker_losses=1,
        recoveries_succeeded=1 if recovered else 0,
    )


SCENARIOS: dict[str, Callable[[StateStore, str, str], dict[str, Any]]] = {
    "greenfield-feature-delivery": _greenfield,
    "verifier-disagreement": _verifier_disagreement,
    "worker-crash-and-lease-expiry": _worker_recovery,
}


def run_scenario(scenario_id: str, *, host: str = "local", run_id: str | None = None) -> dict[str, Any]:
    registry = validate_scenarios()
    scenario_ids = {item["id"] for item in registry["scenarios"]}
    if scenario_id not in SCENARIOS:
        raise LatticeError("Executable evaluation scenario not implemented yet: " + scenario_id)
    resolved_run_id = run_id or f"{scenario_id}:{host}"
    with tempfile.TemporaryDirectory(prefix="lattice-eval-") as temporary:
        folder = Path(temporary)
        with StateStore(ROOT, db_path=folder / "state.db", snapshot_path=folder / "state.json") as store:
            result = SCENARIOS[scenario_id](store, resolved_run_id, host)
            return validate_result(result, scenario_ids)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run bounded executable Lattice evaluation scenarios.")
    result.add_argument("scenario", choices=sorted(SCENARIOS))
    result.add_argument("--host", default="local")
    result.add_argument("--run-id")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        print(json.dumps(run_scenario(args.scenario, host=args.host, run_id=args.run_id), indent=2, sort_keys=True))
    except LatticeError as error:
        print(json.dumps({"error": str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
