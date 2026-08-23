#!/usr/bin/env python3
"""Execute host-adapter envelopes against the configured shared state store."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from host_adapter import handle_envelope
from state_engine import LatticeError
from store_factory import open_state_store

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute one Lattice host-adapter envelope using LATTICE_DATABASE_URL when configured."
    )
    parser.add_argument("--file", help="JSON envelope file; stdin is used when omitted")
    args = parser.parse_args()
    try:
        raw = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
        envelope = json.loads(raw)
        with open_state_store(ROOT) as store:
            result = handle_envelope(store, envelope)
    except (OSError, json.JSONDecodeError, LatticeError, KeyError, ValueError, TypeError) as error:
        print("Lattice rejected the shared host envelope: " + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
