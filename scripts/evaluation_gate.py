#!/usr/bin/env python3
"""Fail-closed aggregate gate for Lattice evaluation result files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evaluation import EvaluationError, summarize_results


def load_results(paths: list[Path]) -> list[dict]:
    results: list[dict] = []
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            results.extend(payload)
        elif isinstance(payload, dict):
            results.append(payload)
        else:
            raise EvaluationError(f"Evaluation result file must contain an object or array: {path}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Require all supplied Lattice evaluation results to pass.")
    parser.add_argument("results", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        results = load_results(args.results)
        summary = summarize_results(results)
    except (OSError, json.JSONDecodeError, EvaluationError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, indent=2))
        return 2
    failed = [
        {"scenario_id": item.get("scenario_id"), "run_id": item.get("run_id")}
        for item in results
        if item.get("outcome") != "passed"
    ]
    print(json.dumps({"ok": not failed, "failed": failed, "summary": summary}, indent=2, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
