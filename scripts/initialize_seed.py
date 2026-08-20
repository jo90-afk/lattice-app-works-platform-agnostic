#!/usr/bin/env python3
"""Initialize the neutral Lattice seed with one real project identity."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from export_chatgpt_work import write_export
from state_engine import StateStore


ROOT = Path(__file__).resolve().parents[1]
SEED_ID = "example-001"
VALID_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def replace_placeholders(path: Path, values: dict[str, str]) -> None:
    if not path.is_file():
        return
    body = path.read_text(encoding="utf-8")
    for token, value in values.items():
        body = body.replace(token, value)
    path.write_text(body, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--principal-alias", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--project-name", required=True)
    args = parser.parse_args()

    if not VALID_ID.fullmatch(args.project_id):
        raise SystemExit("Project ID must use lowercase letters, digits, and hyphens.")
    if not args.principal_alias.strip() or not args.project_name.strip():
        raise SystemExit("Principal alias and project name cannot be blank.")

    source = ROOT / "projects" / SEED_ID
    target = ROOT / "projects" / args.project_id
    if not source.is_dir():
        raise SystemExit("The seed project is no longer available; initialization already ran or was replaced.")
    if target.exists():
        raise SystemExit("Target project ID already exists: " + args.project_id)

    values = {
        "<PRINCIPAL_ALIAS>": args.principal_alias.strip(),
        "<PROJECT_ID>": args.project_id,
        "<PROJECT_NAME>": args.project_name.strip(),
    }
    for path in [ROOT / "portfolio" / "registry.md", ROOT / "portfolio" / "status.md"]:
        replace_placeholders(path, values)
    registry_path = ROOT / "portfolio" / "registry.md"
    registry = registry_path.read_text(encoding="utf-8")
    registry = registry.replace("**Registry state:** UNINITIALIZED SEED", "**Registry state:** INITIALIZED")
    registry = registry.replace("| Unranked | Uninitialized |", "| 1 | Active |")
    registry_path.write_text(registry, encoding="utf-8")
    status_path = ROOT / "portfolio" / "status.md"
    status = status_path.read_text(encoding="utf-8")
    status = status.replace("**State:** UNINITIALIZED SEED", "**State:** INITIALIZED")
    status = status.replace("**Active projects:** None until bootstrap is confirmed.", "**Registered projects:** 1")
    status_path.write_text(status, encoding="utf-8")
    shutil.move(str(source), str(target))
    for path in target.rglob("*"):
        replace_placeholders(path, values)

    with StateStore(ROOT) as store:
        store.rename_project(SEED_ID, args.project_id, args.project_name.strip())

    old_export = ROOT / "exports" / "chatgpt-work" / SEED_ID
    if old_export.exists():
        shutil.rmtree(old_export)
    write_export(args.project_id, ROOT / "exports" / "chatgpt-work" / args.project_id, False)

    manifest_path = ROOT / "seed" / "SEED-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.update({
        "initialized": True,
        "initial_project_id": args.project_id,
        "principal_alias": args.principal_alias.strip(),
        "operational_state": "state/current.json",
        "agency_version": "0.0.3",
    })
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("Initialized Lattice seed for project " + args.project_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
