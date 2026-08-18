#!/usr/bin/env python3
"""Dependency-free command line entry point for Lattice."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(name: str, args: list[str]) -> int:
    return subprocess.call([sys.executable, str(ROOT / "scripts" / name), *args], cwd=ROOT)


def status() -> int:
    projects = sorted(path.name for path in (ROOT / "projects").iterdir() if (path / "PROJECT.md").is_file())
    print("Lattice App Works Seed 2.3.0")
    print("Canonical state: Agency Kernel + Portfolio Registry + Project Capsules")
    print("Projects: " + (", ".join(projects) if projects else "none"))
    print("Run python3 scripts/lattice.py validate before delivery or commit.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate portable Lattice helpers.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    sub.add_parser("status")
    initialize = sub.add_parser("initialize")
    initialize.add_argument("--principal-alias", required=True)
    initialize.add_argument("--project-id", required=True)
    initialize.add_argument("--project-name", required=True)
    export = sub.add_parser("export-chatgpt-work")
    export.add_argument("--project", required=True)
    export.add_argument("--output")
    export.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.command == "validate":
        return run("validate_lattice.py", [])
    if args.command == "status":
        return status()
    if args.command == "initialize":
        return run("initialize_seed.py", [
            "--principal-alias", args.principal_alias,
            "--project-id", args.project_id,
            "--project-name", args.project_name,
        ])
    command = ["--project", args.project]
    if args.output:
        command.extend(["--output", args.output])
    if args.overwrite:
        command.append("--overwrite")
    return run("export_chatgpt_work.py", command)


if __name__ == "__main__":
    raise SystemExit(main())
