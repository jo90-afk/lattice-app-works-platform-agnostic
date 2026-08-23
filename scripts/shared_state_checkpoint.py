#!/usr/bin/env python3
"""Publish a portable checkpoint from the configured operational state store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from state_engine import LatticeError
from store_factory import open_state_store

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write a deliberate portable checkpoint from SQLite or shared Postgres state."
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "state" / "current.json"),
        help="Checkpoint destination; defaults to state/current.json",
    )
    args = parser.parse_args()
    try:
        destination = Path(args.output).resolve()
        with open_state_store(ROOT) as store:
            payload = store.export_snapshot(destination)
    except (OSError, LatticeError, ValueError, KeyError) as error:
        print("Lattice could not publish the state checkpoint: " + str(error), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "checkpoint": str(destination),
                "revision": payload["revision"],
                "schema_version": payload["schema_version"],
                "project_count": len(payload["tables"]["projects"]),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
