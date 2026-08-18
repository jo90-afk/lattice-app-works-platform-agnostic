#!/usr/bin/env python3
"""Small dependency-free command line entry point for Lattice."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(name: str, args: list[str]) -> int:
    return subprocess.call([sys.executable, str(ROOT / "scripts" / name), *args], cwd=ROOT)


def status() -> int:
    print("Lattice App Works 2.2.0")
    print("Canonical state: Agency Kernel + Portfolio Registry + Project Capsules")
    print("Registered project: plos-001 (see portfolio/registry.md)")
    print("Run python3 scripts/lattice.py validate before delivery or commit.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate portable Lattice helpers.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("status")
    export = sub.add_parser("export-chatgpt-work")
    export.add_argument("--project", required=True)
    export.add_argument("--output")
    export.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.command == "validate":
        return run("validate_lattice.py", [])
    if args.command == "status":
        return status()
    command = ["--project", args.project]
    if args.output:
        command.extend(["--output", args.output])
    if args.overwrite:
        command.append("--overwrite")
    return run("export_chatgpt_work.py", command)


if __name__ == "__main__":
    raise SystemExit(main())
