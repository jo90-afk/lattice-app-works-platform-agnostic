#!/usr/bin/env python3
"""Machine-readable Lattice public-beta capability negotiation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def capabilities(root: Path = ROOT) -> dict:
    release = (root / "VERSION").read_text(encoding="utf-8").strip()
    policy = json.loads((root / "runtime" / "policy.json").read_text(encoding="utf-8"))
    host_schema = json.loads((root / "runtime" / "host-adapter.schema.json").read_text(encoding="utf-8"))
    host_version = int(host_schema["properties"]["version"]["const"])
    operations = list(host_schema["properties"]["operation"]["enum"])
    return {
        "format": "lattice-capabilities",
        "version": 1,
        "release": release,
        "compatibility": {
            "agency_version": policy["agency_version"],
            "state_snapshot_schema": int(policy["schema_version"]),
            "host_adapter_protocol": host_version,
            "hosted_delta_schema": 1,
            "control_read_model": 1,
            "github_observation_protocol": 1,
        },
        "state_backends": {
            "default": "sqlite",
            "supported": ["sqlite", "postgres"],
            "postgres_optional_dependency": "psycopg>=3.2,<4",
        },
        "host_adapter_operations": operations,
        "features": [
            "active-frontier",
            "durable-truth-ledger",
            "bounded-leases",
            "independent-verification",
            "assurance-acceptance",
            "exception-supervision",
            "recovery",
            "shared-postgres-writers",
            "portable-snapshot",
            "evaluation-evidence",
            "github-state-reconciliation",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()
    payload = capabilities()
    print(json.dumps(payload, sort_keys=True, separators=(",", ":") if args.compact else None, indent=None if args.compact else 2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
