"""Case implementations for adversarial Lattice evaluation scenarios."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from concurrency import claim_for_host_atomic
from evaluation_fingerprint import acceptance_state, semantic_state
from lifecycle import review_action, submit_action
from scheduler import Worker, candidate_plan, dispatch
from state_engine import StateStore


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _portfolio_fingerprints(store: StateStore, project_ids: list[str]) -> tuple[str, str]:
    ordered = sorted(project_ids)
    return (
        _hash([semantic_state(store, project_id) for project_id in ordered]),
        _hash([acceptance_state(store, project_id) for project_id in ordered]),
    )


def _event_count(store: StateStore, project_ids: list[str], event_type: str) -> int:
    placeholders = ",".join("?" for _ in project_ids)
    return int(
        store.conn.execute(
            f"SELECT COUNT(*) FROM events WHERE project_id IN ({placeholders}) AND event_type = ?",
            (*project_ids, event_type),
        ).fetchone()[0]
    )


def _result(
    store: StateStore,
    *,
    scenario_id: str,
    run_id: str,
    host: str,
    project_ids: list[str],
    passed: bool,
    started: float,
    context_bytes: int = 0,
    routine_transitions: int | None = None,
    routine_autonomous_transitions: int | None = None,
    accepted_changes: int | None = None,
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
    state_fp, acceptance_fp = _portfolio_fingerprints(store, project_ids)
    if routine_transitions is None:
        routine_transitions = sum(
            _event_count(store, project_ids, event_type)
            for event_type in ("action_submitted", "verification_recorded", "milestone_acceptance_recorded")
        )
    if routine_autonomous_transitions is None:
        routine_autonomous_transitions = routine_transitions
    if accepted_changes is None:
        accepted_changes = _event_count(store, project_ids, "milestone_accepted")
    return {
        "format": "lattice-evaluation-result",
        "version": 1,
        "scenario_id": scenario_id,
        "run_id": run_id,
        "host": host,
        "outcome": "passed" if passed else "failed",
        "state_fingerprint": state_fp,
        "acceptance_fingerprint": acceptance_fp,
        "routine_transitions": routine_transitions,
        "routine_autonomous_transitions": routine_autonomous_transitions,
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


def _seed_project(
    store: StateStore,
    project_id: str,
    *,
    owner_role: str = "application",
    truth_id: str | None = None,
    condition_id: str | None = None,
) -> tuple[str, str, str]:
    objective_id = f"{project_id}-objective"
    milestone_id = f"{project_id}-milestone"
    resolved_condition = condition_id or f"{project_id}-condition"
    store.ensure_project(project_id, project_id.replace("-", " ").title())
    store.add_objective(
        project_id,
        f"Objective for {project_id}",
        "Bounded adversarial evaluation objective.",
        "product",
        objective_id=objective_id,
    )
    store.add_milestone(
        project_id,
        objective_id,
        f"Milestone for {project_id}",
        1,
        True,
        milestone_id=milestone_id,
    )
    truth_ids: list[str] = []
    if truth_id:
        store.add_truth(
            project_id,
            "evaluation.premise",
            "The original evaluation premise is accepted.",
            "accepted",
            "frontier",
            "director",
            material=True,
            truth_id=truth_id,
        )
        truth_ids.append(truth_id)
    store.add_condition(
        project_id,
        objective_id,
        milestone_id,
        "evaluation.condition",
        "Evaluation condition is satisfied",
        "Complete the bounded adversarial evaluation work.",
        owner_role,
        "quality",
        "director",
        truth_ids=truth_ids,
        condition_id=resolved_condition,
    )
    return objective_id, milestone_id, resolved_condition


def ambiguous_requirements(store: StateStore, run_id: str, host: str, _folder: Path) -> dict[str, Any]:
    started = time.perf_counter()
    project_id = "eval-ambiguous"
    objective_id = f"{project_id}-objective"
    milestone_id = f"{project_id}-milestone"
    store.ensure_project(project_id, "Ambiguous Requirements Evaluation")
    store.add_objective(
        project_id,
        "Resolve materially ambiguous external requirement",
        "No specialist work should be guessed before the authority boundary is resolved.",
        "product",
        objective_id=objective_id,
    )
    store.add_milestone(
        project_id,
        objective_id,
        "Requirement is sufficiently specified",
        1,
        True,
        milestone_id=milestone_id,
    )
    exception = store.raise_exception(
        project_id,
        "missing-external-requirement",
        "Choose the external behavior required",
        "Two materially different externally visible behaviors are both compatible with the supplied requirement.",
        "major",
        "principal",
        "director",
        True,
        "milestone",
        milestone_id,
    )
    observed_now = datetime.now(timezone.utc).replace(microsecond=0)
    blocked_since = (observed_now - timedelta(seconds=90)).isoformat().replace("+00:00", "Z")
    with store.conn:
        store.conn.execute(
            "UPDATE exceptions SET created_at = ?, updated_at = ? WHERE id = ?",
            (blocked_since, blocked_since, exception["id"]),
        )
    frontier = store.frontier(project_id, None, 20)
    plan = candidate_plan(
        store,
        [Worker("application-available", "application", host, "application-workspace")],
        limit=5,
    )
    blocked_seconds = (
        observed_now - datetime.fromisoformat(blocked_since.replace("Z", "+00:00"))
    ).total_seconds()
    passed = bool(
        frontier
        and all(action["role"] == "principal" for action in frontier)
        and plan["assignments"] == []
        and exception["principal_only"]
    )
    return _result(
        store,
        scenario_id="ambiguous-requirements-escalation",
        run_id=run_id,
        host=host,
        project_ids=[project_id],
        passed=passed,
        started=started,
        escalations=1,
        unnecessary_escalations=0,
        blocked_seconds_missing_information=max(0.0, blocked_seconds),
    )


def contradictory_information(store: StateStore, run_id: str, host: str, _folder: Path) -> dict[str, Any]:
    started = time.perf_counter()
    project_id = "eval-contradiction"
    truth_id = "eval-original-truth"
    _objective, milestone_id, condition_id = _seed_project(
        store,
        project_id,
        truth_id=truth_id,
        condition_id="eval-contradiction-condition",
    )
    context = 0
    owner = claim_for_host_atomic(
        store,
        project_id=project_id,
        role="application",
        actor="application-contradiction",
        host=host,
        workspace_id="owner-workspace",
    )
    context += len(json.dumps(owner["action"], sort_keys=True).encode("utf-8"))
    submit_action(
        store,
        owner["lease_id"],
        "application",
        "Result valid under original accepted premise",
        ["artifact://evaluation/contradiction/original"],
        "evidence://evaluation/contradiction/original",
    )
    verifier = claim_for_host_atomic(
        store,
        project_id=project_id,
        role="quality",
        actor="quality-contradiction",
        host=host,
        workspace_id="verification-workspace",
    )
    context += len(json.dumps(verifier["action"], sort_keys=True).encode("utf-8"))
    review_action(
        store,
        verifier["lease_id"],
        "quality",
        "SATISFIED",
        "Result satisfies the original premise",
        "evidence://evaluation/contradiction/review",
    )
    before = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())
    accepted_before = store.conn.execute(
        "SELECT accepted_truth_version FROM condition_truths WHERE condition_id = ? AND truth_id = ?",
        (condition_id, truth_id),
    ).fetchone()["accepted_truth_version"]
    store.move_truth(truth_id, "background", "director", "original premise temporarily settled")
    contrary_id = "eval-contrary-truth"
    store.add_truth(
        project_id,
        "evaluation.premise.contrary",
        "New evidence says the original evaluation premise is not reliable.",
        "accepted",
        "frontier",
        "director",
        material=True,
        truth_id=contrary_id,
    )
    store.link_truths(contrary_id, truth_id, "contradicts", "director")
    after = dict(store.conn.execute("SELECT * FROM conditions WHERE id = ?", (condition_id,)).fetchone())
    original = dict(store.conn.execute("SELECT * FROM truths WHERE id = ?", (truth_id,)).fetchone())
    contrary = dict(store.conn.execute("SELECT * FROM truths WHERE id = ?", (contrary_id,)).fetchone())
    accepted_after = store.conn.execute(
        "SELECT accepted_truth_version FROM condition_truths WHERE condition_id = ? AND truth_id = ?",
        (condition_id, truth_id),
    ).fetchone()["accepted_truth_version"]
    frontier = store.frontier(project_id, "application", 20)
    milestone_status = store.conn.execute(
        "SELECT status FROM milestones WHERE id = ?", (milestone_id,)
    ).fetchone()["status"]
    passed = bool(
        before["status"] == "satisfied"
        and accepted_before == 1
        and after["status"] == "unknown"
        and after["state_version"] > before["state_version"]
        and original["epistemic_status"] == "contested"
        and original["attention_state"] == "frontier"
        and contrary["epistemic_status"] == "contested"
        and accepted_after == accepted_before
        and any(action["target_id"] == condition_id for action in frontier)
        and milestone_status == "active"
    )
    return _result(
        store,
        scenario_id="contradictory-new-information",
        run_id=run_id,
        host=host,
        project_ids=[project_id],
        passed=passed,
        started=started,
        context_bytes=context,
        state_divergence_incidents=0 if passed else 1,
    )


def multi_project_contention(store: StateStore, run_id: str, host: str, folder: Path) -> dict[str, Any]:
    started = time.perf_counter()
    project_ids = ["eval-priority-a", "eval-priority-b", "eval-priority-c"]
    for project_id in project_ids:
        _seed_project(store, project_id)
    registry = folder / "registry.md"
    registry.write_text(
        """# Evaluation registry\n\n**Concurrency limit:** 2 specialist agents\n\n| Project ID | Name | Priority | Status |\n| --- | --- | --- | --- |\n| eval-priority-b | B | 1 | active |\n| eval-priority-a | A | 2 | active |\n| eval-priority-c | C | 3 | active |\n""",
        encoding="utf-8",
    )
    workers = [
        Worker("application-1", "application", host, "workspace-1"),
        Worker("application-2", "application", host, "workspace-2"),
        Worker("application-3", "application", host, "workspace-3"),
    ]
    plan = candidate_plan(store, workers, registry_path=registry)
    first_projects = [item["project_id"] for item in plan["assignments"]]
    first = dispatch(store, workers, registry_path=registry)
    context = sum(
        len(json.dumps(claim["action"], sort_keys=True).encode("utf-8"))
        for claim in first["claims"]
    )
    for claim in first["claims"]:
        submit_action(
            store,
            claim["lease_id"],
            "application",
            f"Bounded result for {claim['action']['project_id']}",
            [f"artifact://evaluation/portfolio/{claim['action']['project_id']}"],
            f"evidence://evaluation/portfolio/{claim['action']['project_id']}",
        )
    second = dispatch(store, workers, registry_path=registry)
    context += sum(
        len(json.dumps(claim["action"], sort_keys=True).encode("utf-8"))
        for claim in second["claims"]
    )
    second_projects = [claim["action"]["project_id"] for claim in second["claims"]]
    for claim in second["claims"]:
        if claim["action"]["kind"] == "satisfy_condition":
            submit_action(
                store,
                claim["lease_id"],
                "application",
                f"Bounded result for {claim['action']['project_id']}",
                [f"artifact://evaluation/portfolio/{claim['action']['project_id']}"],
                f"evidence://evaluation/portfolio/{claim['action']['project_id']}",
            )
    pending_projects = {
        str(row["project_id"])
        for row in store.conn.execute(
            """SELECT DISTINCT c.project_id FROM submissions s
               JOIN conditions c ON c.id = s.condition_id WHERE s.status = 'pending'"""
        ).fetchall()
    }
    passed = bool(
        first["plan"]["portfolio_capacity"] == 2
        and first_projects == ["eval-priority-b", "eval-priority-a"]
        and len(first["claims"]) == 2
        and "eval-priority-c" in second_projects
        and pending_projects == set(project_ids)
    )
    return _result(
        store,
        scenario_id="multi-project-capacity-contention",
        run_id=run_id,
        host=host,
        project_ids=project_ids,
        passed=passed,
        started=started,
        context_bytes=context,
        routine_transitions=3,
        routine_autonomous_transitions=3,
    )


CASES: dict[str, Callable[[StateStore, str, str, Path], dict[str, Any]]] = {
    "ambiguous-requirements-escalation": ambiguous_requirements,
    "contradictory-new-information": contradictory_information,
    "multi-project-capacity-contention": multi_project_contention,
}
