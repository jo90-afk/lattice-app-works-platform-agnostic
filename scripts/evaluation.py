#!/usr/bin/env python3
"""Repeatable 0.0.8 evaluation contracts and autonomy metrics."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENARIOS = ROOT / "evals" / "scenarios.json"

REQUIRED_SCENARIOS = {
    "greenfield-feature-delivery",
    "cross-component-refactor",
    "migration-work",
    "ci-remediation",
    "ambiguous-requirements-escalation",
    "contradictory-new-information",
    "worker-crash-and-lease-expiry",
    "verifier-disagreement",
    "concurrent-artifact-conflict",
    "multi-project-capacity-contention",
}
REQUIRED_SIGNALS = {
    "routine_autonomy",
    "false_acceptance",
    "escalation",
    "recovery",
    "state_divergence",
    "verification",
    "blocked_missing_information",
    "context_volume",
    "accepted_change",
}
RESULT_COUNTERS = {
    "routine_transitions",
    "routine_autonomous_transitions",
    "accepted_changes",
    "false_acceptances",
    "escalations",
    "unnecessary_escalations",
    "worker_losses",
    "recoveries_succeeded",
    "state_divergence_incidents",
    "verification_defects_presented",
    "verification_catches",
    "blocked_seconds_missing_information",
    "context_bytes",
}


class EvaluationError(ValueError):
    pass


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError(f"Could not read evaluation JSON {path}: {error}") from error


def validate_scenarios(path: Path = DEFAULT_SCENARIOS) -> dict[str, Any]:
    payload = _read_json(path)
    if not isinstance(payload, dict) or payload.get("format") != "lattice-evaluation-scenarios":
        raise EvaluationError("Scenario registry must use lattice-evaluation-scenarios format")
    if payload.get("version") != 1:
        raise EvaluationError("Unsupported evaluation scenario registry version")
    scenarios = payload.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios:
        raise EvaluationError("Scenario registry must contain scenarios")
    ids: set[str] = set()
    covered_signals: set[str] = set()
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            raise EvaluationError("Every evaluation scenario must be an object")
        scenario_id = scenario.get("id")
        if not isinstance(scenario_id, str) or not scenario_id:
            raise EvaluationError("Every evaluation scenario requires an id")
        if scenario_id in ids:
            raise EvaluationError(f"Duplicate evaluation scenario: {scenario_id}")
        ids.add(scenario_id)
        if not scenario.get("category") or not scenario.get("purpose"):
            raise EvaluationError(f"Scenario {scenario_id} requires category and purpose")
        signals = scenario.get("required_signals")
        if not isinstance(signals, list) or not signals:
            raise EvaluationError(f"Scenario {scenario_id} requires at least one signal")
        unknown = set(signals) - REQUIRED_SIGNALS
        if unknown:
            raise EvaluationError(
                f"Scenario {scenario_id} uses unknown signals: {', '.join(sorted(unknown))}"
            )
        covered_signals.update(signals)
    missing = REQUIRED_SCENARIOS - ids
    if missing:
        raise EvaluationError("Scenario registry is missing roadmap scenarios: " + ", ".join(sorted(missing)))
    missing_signals = REQUIRED_SIGNALS - covered_signals
    if missing_signals:
        raise EvaluationError("Scenario registry does not exercise metrics: " + ", ".join(sorted(missing_signals)))
    return payload


def validate_result(result: dict[str, Any], scenario_ids: set[str]) -> dict[str, Any]:
    if result.get("format") != "lattice-evaluation-result" or result.get("version") != 1:
        raise EvaluationError("Each result must use lattice-evaluation-result version 1")
    scenario_id = result.get("scenario_id")
    if scenario_id not in scenario_ids:
        raise EvaluationError(f"Unknown evaluation scenario result: {scenario_id}")
    for field in ("run_id", "host", "state_fingerprint", "acceptance_fingerprint"):
        if not isinstance(result.get(field), str) or not result[field]:
            raise EvaluationError(f"Result {scenario_id} requires non-empty {field}")
    if result.get("outcome") not in {"passed", "failed"}:
        raise EvaluationError(f"Result {scenario_id} outcome must be passed or failed")
    for field in RESULT_COUNTERS:
        value = result.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
            raise EvaluationError(f"Result {scenario_id} requires non-negative numeric {field}")
    if result["routine_autonomous_transitions"] > result["routine_transitions"]:
        raise EvaluationError("routine_autonomous_transitions cannot exceed routine_transitions")
    if result["false_acceptances"] > result["accepted_changes"]:
        raise EvaluationError("false_acceptances cannot exceed accepted_changes")
    if result["unnecessary_escalations"] > result["escalations"]:
        raise EvaluationError("unnecessary_escalations cannot exceed escalations")
    if result["recoveries_succeeded"] > result["worker_losses"]:
        raise EvaluationError("recoveries_succeeded cannot exceed worker_losses")
    if result["verification_catches"] > result["verification_defects_presented"]:
        raise EvaluationError("verification_catches cannot exceed verification_defects_presented")
    return result


def _ratio(numerator: float, denominator: float) -> float | None:
    return None if denominator == 0 else numerator / denominator


def summarize_results(results: list[dict[str, Any]], scenarios_path: Path = DEFAULT_SCENARIOS) -> dict[str, Any]:
    registry = validate_scenarios(scenarios_path)
    scenario_ids = {item["id"] for item in registry["scenarios"]}
    validated = [validate_result(dict(item), scenario_ids) for item in results]
    if not validated:
        raise EvaluationError("At least one evaluation result is required")

    totals = {field: sum(float(item[field]) for item in validated) for field in RESULT_COUNTERS}
    durations = [float(item["duration_seconds"]) for item in validated if isinstance(item.get("duration_seconds"), (int, float)) and item["duration_seconds"] >= 0]
    context_per_change = _ratio(totals["context_bytes"], totals["accepted_changes"])

    portability: dict[str, dict[str, set[str]]] = {}
    for item in validated:
        scenario = portability.setdefault(
            item["scenario_id"], {"state": set(), "acceptance": set(), "hosts": set()}
        )
        scenario["state"].add(item["state_fingerprint"])
        scenario["acceptance"].add(item["acceptance_fingerprint"])
        scenario["hosts"].add(item["host"])
    portability_violations = [
        scenario_id
        for scenario_id, values in sorted(portability.items())
        if len(values["hosts"]) > 1 and (len(values["state"]) > 1 or len(values["acceptance"]) > 1)
    ]

    return {
        "format": "lattice-evaluation-summary",
        "version": 1,
        "runs": len(validated),
        "scenarios_run": sorted({item["scenario_id"] for item in validated}),
        "hosts": sorted({item["host"] for item in validated}),
        "outcomes": {
            "passed": sum(1 for item in validated if item["outcome"] == "passed"),
            "failed": sum(1 for item in validated if item["outcome"] == "failed"),
        },
        "metrics": {
            "routine_autonomy_rate": _ratio(
                totals["routine_autonomous_transitions"], totals["routine_transitions"]
            ),
            "false_acceptance_rate": _ratio(
                totals["false_acceptances"], totals["accepted_changes"]
            ),
            "unnecessary_escalation_rate": _ratio(
                totals["unnecessary_escalations"], totals["escalations"]
            ),
            "recovery_success_rate": _ratio(
                totals["recoveries_succeeded"], totals["worker_losses"]
            ),
            "state_divergence_incidents": int(totals["state_divergence_incidents"]),
            "verification_catch_rate": _ratio(
                totals["verification_catches"], totals["verification_defects_presented"]
            ),
            "blocked_seconds_missing_information": totals["blocked_seconds_missing_information"],
            "context_bytes_per_accepted_change": context_per_change,
            "median_run_duration_seconds": statistics.median(durations) if durations else None,
        },
        "portability": {
            "scenarios_compared_across_hosts": sum(
                1 for values in portability.values() if len(values["hosts"]) > 1
            ),
            "equivalence_violations": portability_violations,
        },
    }


def _load_results(paths: list[Path]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for path in paths:
        payload = _read_json(path)
        if isinstance(payload, list):
            results.extend(payload)
        elif isinstance(payload, dict):
            results.append(payload)
        else:
            raise EvaluationError(f"Evaluation result file must contain an object or array: {path}")
    return results


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Validate and summarize Lattice autonomy evaluations.")
    commands = result.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    summarize = commands.add_parser("summarize")
    summarize.add_argument("results", nargs="+", type=Path)
    summarize.add_argument("--scenarios", type=Path, default=DEFAULT_SCENARIOS)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "validate":
            payload = validate_scenarios(args.scenarios)
            print(json.dumps({"ok": True, "scenarios": len(payload["scenarios"])}, indent=2))
        elif args.command == "summarize":
            print(json.dumps(summarize_results(_load_results(args.results), args.scenarios), indent=2, sort_keys=True))
        else:
            raise EvaluationError("Unsupported evaluation command")
    except EvaluationError as error:
        print("Lattice evaluation rejected input: " + str(error), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
