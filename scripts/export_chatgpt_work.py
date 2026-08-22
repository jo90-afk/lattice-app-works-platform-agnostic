#!/usr/bin/env python3
"""Create scoped ChatGPT Work execution packs from the active frontier."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from expertise import resolve_expertise
from state_engine import StateStore


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").rstrip() + "\n"


def source_block(relative: str) -> str:
    return "## Source: " + relative + "\n\n" + read(relative).rstrip() + "\n"


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def safe_project_source(project_id: str, reference: str) -> str | None:
    candidate = Path(reference)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    expected = Path("projects") / project_id
    if candidate.parts[:2] != expected.parts:
        return None
    path = (ROOT / candidate).resolve()
    if ROOT not in path.parents or not path.is_file():
        return None
    return candidate.as_posix()


def role_paths(actions: list[dict[str, Any]]) -> list[str]:
    roles = {"director", "assurance"}
    roles.update(str(action["role"]) for action in actions)
    paths = []
    for role in sorted(roles):
        path = "agents/" + role + ".md"
        if (ROOT / path).is_file():
            paths.append(path)
    return paths


def expertise_paths(project_id: str, actions: list[dict[str, Any]]) -> list[str]:
    roles = {"director", "assurance"}
    roles.update(str(action["role"]) for action in actions)
    paths: list[str] = []
    for role in sorted(roles):
        try:
            resolved = resolve_expertise(role, project_id)
        except ValueError:
            continue
        paths.extend(str(path) for path in resolved["paths"])
    return list(dict.fromkeys(paths))


def referenced_paths(project_id: str, actions: list[dict[str, Any]]) -> list[str]:
    paths: set[str] = set()
    for action in actions:
        context = action.get("context") or {}
        for record in context.get("relevant_records") or []:
            if record.get("source_ref"):
                safe = safe_project_source(project_id, str(record["source_ref"]))
                if safe:
                    paths.add(safe)
        submission = context.get("submission") or {}
        try:
            artifacts = json.loads(submission.get("artifact_refs_json") or "[]")
        except json.JSONDecodeError:
            artifacts = []
        for reference in artifacts:
            safe = safe_project_source(project_id, str(reference))
            if safe:
                paths.add(safe)
    return sorted(paths)


def project_core_paths(project_id: str) -> list[str]:
    candidates = [
        f"projects/{project_id}/PROJECT.md",
        f"projects/{project_id}/project/manifest.md",
        f"projects/{project_id}/project/capabilities.json",
        f"projects/{project_id}/work/bootstrap.md",
    ]
    return [path for path in candidates if (ROOT / path).is_file()]


def build_projection(
    project_id: str,
    role: str | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    with StateStore(ROOT) as store:
        actions = store.frontier(project_id, role, limit)
        status = next(
            (project for project in store.status()["projects"] if project["id"] == project_id),
            None,
        )
        return {
            "format": "lattice-host-frontier",
            "schema_version": 1,
            "agency_version": store.policy["agency_version"],
            "base_revision": store.project_revision(project_id),
            "project_id": project_id,
            "role_filter": role,
            "frontier_limit": limit,
            "project_status": status,
            "actions": actions,
            "instruction": "Select at most one action. Do not invent or persist additional actions.",
        }


def build_pack(
    project_id: str,
    role: str | None = None,
    limit: int = 3,
) -> str:
    projection = build_projection(project_id, role, limit)
    actions = projection["actions"]
    paths = [
        "AGENTS.md",
        "agency.yaml",
        "runtime/policy.json",
        "governance/charter.md",
        "governance/autonomy-policy.md",
        "docs/ACTIVE-FRONTIER.md",
        "docs/TRUTH-LEDGER.md",
        "docs/HOSTED-DELTA-PROTOCOL.md",
        *role_paths(actions),
        *expertise_paths(project_id, actions),
        "portfolio/registry.md",
        "portfolio/status.md",
        *project_core_paths(project_id),
        *referenced_paths(project_id, actions),
    ]
    unique_paths = list(dict.fromkeys(path for path in paths if (ROOT / path).is_file()))
    parts = [
        "# Lattice ChatGPT Work Execution Pack — " + project_id,
        "This is a scoped execution projection, not a second project-state store. "
        "It contains only the current bounded frontier, directly relevant facts, and role rules.",
        "# Active Frontier Projection",
        "```json\n" + json.dumps(projection, indent=2, sort_keys=True) + "\n```",
        "# Scoped Sources",
    ]
    parts.extend(source_block(path).rstrip() for path in unique_paths)
    return "\n\n".join(parts).rstrip() + "\n"


def write_export(
    project_id: str,
    destination: Path,
    overwrite: bool,
    role: str | None = None,
    limit: int = 3,
) -> None:
    if destination.exists():
        if not overwrite:
            raise FileExistsError("Destination exists: " + str(destination))
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    instructions = read("adapters/chatgpt-work/PROJECT-INSTRUCTIONS.md")
    pack = build_pack(project_id, role, limit)
    projection = build_projection(project_id, role, limit)
    pack_name = "Lattice_ChatGPT_Work_Pack_" + project_id + ".md"
    (destination / "PROJECT-INSTRUCTIONS.md").write_text(instructions, encoding="utf-8")
    (destination / pack_name).write_text(pack, encoding="utf-8")
    delta_template = {
        "format": "lattice-state-delta",
        "schema_version": 1,
        "base_revision": projection["base_revision"],
        "project_id": project_id,
        "action_key": "<copy one action_key from the pack>",
        "role": "<the action's exact role>",
        "actor": "chatgpt-work",
        "outcome": {
            "type": "submit | review | advance | fail | resolve_exception | fulfill_commitment",
            "summary": "<concise result and evidence>",
        },
    }
    (destination / "STATE-DELTA-TEMPLATE.json").write_text(
        json.dumps(delta_template, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "format": "lattice-chatgpt-work-execution-pack",
        "version": "0.0.4",
        "project_id": project_id,
        "role_filter": role,
        "base_revision": projection["base_revision"],
        "action_keys": [action["action_key"] for action in projection["actions"]],
        "pack_file": pack_name,
        "pack_sha256": sha256(pack),
        "project_instructions_sha256": sha256(instructions),
        "expertise_paths": expertise_paths(project_id, projection["actions"]),
        "scope_rule": "Only current frontier actions and directly relevant sources are included.",
    }
    (destination / "source-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "README.md").write_text(
        "# ChatGPT Work execution pack — " + project_id + "\n\n"
        "1. Set PROJECT-INSTRUCTIONS.md as the ChatGPT Project instructions.\n"
        "2. Upload " + pack_name + " as the current Project source.\n"
        "3. Ask Work to execute at most one action from the Active Frontier Projection.\n"
        "4. Reconcile returned artifact changes into the repository.\n"
        "5. Save the returned state delta and run `python3 scripts/lattice.py apply-delta --file <delta.json>`.\n"
        "6. Regenerate this pack; old packs are stale after a durable state change.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--role")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = args.output or ROOT / "exports" / "chatgpt-work" / args.project
    write_export(args.project, output, args.overwrite, args.role, args.limit)
    print("Wrote scoped ChatGPT Work execution pack: " + str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
