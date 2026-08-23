#!/usr/bin/env python3
"""Run adversarial 0.0.8 authority, truth, and portfolio evaluations."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from evaluation import validate_result, validate_scenarios
from evaluation_adversarial_cases import CASES
from state_engine import LatticeError, StateStore

ROOT = Path(__file__).resolve().parents[1]


def run_adversarial_scenario(
    scenario_id: str,
    *,
    host: str = "local",
    run_id: str | None = None,
) -> dict:
    registry = validate_scenarios()
    scenario_ids = {item["id"] for item in registry["scenarios"]}
    if scenario_id not in CASES:
        raise LatticeError("Adversarial evaluation scenario not implemented: " + scenario_id)
    resolved_run_id = run_id or f"{scenario_id}:{host}"
    with tempfile.TemporaryDirectory(prefix="lattice-adversarial-eval-") as temporary:
        folder = Path(temporary)
        with StateStore(
            ROOT,
            db_path=folder / "state.db",
            snapshot_path=folder / "state.json",
        ) as store:
            result = CASES[scenario_id](store, resolved_run_id, host, folder)
            return validate_result(result, scenario_ids)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run adversarial Lattice evaluation scenarios.")
    parser.add_argument("scenario", choices=sorted(CASES))
    parser.add_argument("--host", default="local")
    parser.add_argument("--run-id")
    args = parser.parse_args()
    try:
        result = run_adversarial_scenario(
            args.scenario,
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
