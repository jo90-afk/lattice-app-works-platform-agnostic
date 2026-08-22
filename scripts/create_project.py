#!/usr/bin/env python3
"""Create one isolated project capsule and register its operational state."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from export_chatgpt_work import write_export
from state_engine import StateStore


ROOT = Path(__file__).resolve().parents[1]
VALID_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def add_registry_row(project_id: str, name: str) -> None:
    path = ROOT / "portfolio" / "registry.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.startswith("| Project ID |")),
        None,
    )
    if header_index is None:
        raise RuntimeError("Portfolio registry has no project table")
    insertion = header_index + 2
    while insertion < len(lines) and lines[insertion].startswith("|"):
        insertion += 1
    lines.insert(
        insertion,
        f"| {project_id} | {name} | Unranked | Proposed | projects/{project_id}/ |",
    )
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def create_capsule(project_id: str, name: str) -> Path:
    root = ROOT / "projects" / project_id
    if root.exists():
        raise RuntimeError("Project capsule already exists: " + project_id)
    (root / "project").mkdir(parents=True)
    (root / "work").mkdir()
    (root / "sources" / "principal").mkdir(parents=True)
    (root / "assurance").mkdir()
    (root / "PROJECT.md").write_text(
        f"# Project Capsule — {name}\n\n"
        f"**Project ID:** {project_id}  \n"
        "**State:** PROPOSED — AWAITING MANDATE\n\n"
        "This capsule inherits the Lattice Agency Kernel. Confirm the mandate in "
        "`work/bootstrap.md`, then establish one active objective and milestone through the guarded CLI.\n",
        encoding="utf-8",
    )
    (root / "project" / "manifest.md").write_text(
        f"# Project Manifest — {name}\n\n"
        f"**Project ID:** {project_id}  \n"
        "**Lifecycle:** Proposed\n\n"
        "## Activation\n\n"
        "Record platforms, builder roles, data boundaries, external services, and release constraints "
        "only after mandate confirmation. Keep machine-readable platform and service selections in "
        "`project/capabilities.json`. This manifest cannot redefine agency governance.\n",
        encoding="utf-8",
    )
    (root / "project" / "capabilities.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "application_platforms": [],
                "cross_platform_strategy": "undecided",
                "service_capabilities": [],
                "intelligence_capabilities": [],
                "release_targets": [],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / "work" / "bootstrap.md").write_text(
        f"# Bootstrap Record — {project_id}\n\n"
        "**Status:** AWAITING PRINCIPAL\n\n"
        "Confirm the intended outcome, non-goals, privacy boundary, consequence boundaries, "
        "and portfolio priority before activating an objective.\n",
        encoding="utf-8",
    )
    (root / "sources" / "README.md").write_text(
        "# Project sources\n\nStore only project-authorized source material here.\n",
        encoding="utf-8",
    )
    (root / "assurance" / "README.md").write_text(
        "# Assurance artifacts\n\nRoutine readiness is structured state. Store only requested human-readable audits here.\n",
        encoding="utf-8",
    )
    return root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--project-name", required=True)
    args = parser.parse_args()
    if not VALID_ID.fullmatch(args.project_id):
        raise SystemExit("Project ID must use lowercase letters, digits, and hyphens.")
    if not args.project_name.strip():
        raise SystemExit("Project name cannot be blank.")

    with StateStore(ROOT) as store:
        if store.conn.execute("SELECT 1 FROM projects WHERE id = ?", (args.project_id,)).fetchone():
            raise SystemExit("Project is already registered: " + args.project_id)
        create_capsule(args.project_id, args.project_name.strip())
        store.ensure_project(args.project_id, args.project_name.strip(), status="paused")
        add_registry_row(args.project_id, args.project_name.strip())
        write_export(
            args.project_id,
            ROOT / "exports" / "chatgpt-work" / args.project_id,
            False,
        )
    print("Created proposed Lattice project: " + args.project_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
