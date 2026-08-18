#!/usr/bin/env python3
"""Create deterministic ChatGPT Work source packs from canonical Lattice files."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8").rstrip() + "\n"


def source_block(relative: str) -> str:
    return "## Source: " + relative + "\n\n" + read(relative).rstrip() + "\n"


def kernel_paths() -> list[str]:
    result = ["AGENTS.md", "agency.yaml"]
    for directory in ("governance", "agents", "templates", "prompts"):
        result.extend(
            path.relative_to(ROOT).as_posix()
            for path in sorted((ROOT / directory).rglob("*.md"))
        )
    return result


def project_paths(project_id: str) -> list[str]:
    folder = ROOT / "projects" / project_id
    if not folder.is_dir():
        raise ValueError("Unknown project: " + project_id)
    return [
        path.relative_to(ROOT).as_posix()
        for path in sorted(path for path in folder.rglob("*") if path.is_file())
    ]


def build_pack(project_id: str) -> str:
    parts = [
        "# Lattice ChatGPT Work Source Pack — " + project_id,
        "Generated labelled snapshot of the canonical repository. Set the accompanying "
        "PROJECT-INSTRUCTIONS.md as ChatGPT Project instructions before using this pack.",
        "# Agency Kernel",
    ]
    parts.extend(source_block(path).rstrip() for path in kernel_paths())
    parts.append("# Portfolio Registry")
    parts.extend(source_block(path).rstrip() for path in ("portfolio/registry.md", "portfolio/status.md"))
    parts.append("# Project Capsule — " + project_id)
    parts.extend(source_block(path).rstrip() for path in project_paths(project_id))
    return "\n\n".join(parts).rstrip() + "\n"


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_export(project_id: str, destination: Path, overwrite: bool) -> None:
    if destination.exists():
        if not overwrite:
            raise FileExistsError("Destination exists: " + str(destination))
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    instructions = read("adapters/chatgpt-work/PROJECT-INSTRUCTIONS.md")
    pack = build_pack(project_id)
    pack_name = "Lattice_ChatGPT_Work_Pack_" + project_id + ".md"
    (destination / "PROJECT-INSTRUCTIONS.md").write_text(instructions, encoding="utf-8")
    (destination / pack_name).write_text(pack, encoding="utf-8")
    manifest = {
        "format": "lattice-chatgpt-work-source-pack",
        "version": "2.2.0",
        "project_id": project_id,
        "pack_file": pack_name,
        "pack_sha256": sha256(pack),
        "project_instructions_sha256": sha256(instructions),
        "source_layers": ["agency_kernel", "portfolio_registry", "project_capsule"],
        "snapshot_rule": "Regenerate after substantive canonical source changes.",
    }
    (destination / "source-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (destination / "README.md").write_text(
        "# ChatGPT Work export — " + project_id + "\n\n"
        "1. Copy PROJECT-INSTRUCTIONS.md into the ChatGPT Project instructions field.\n"
        "2. Upload " + pack_name + " as a Project source.\n"
        "3. Use a Work chat in that Project.\n"
        "4. Reconcile exact changed files into the repository, then regenerate this export.\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    output = args.output or ROOT / "exports" / "chatgpt-work" / args.project
    write_export(args.project, output, args.overwrite)
    print("Wrote ChatGPT Work source pack: " + str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
