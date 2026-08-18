#!/usr/bin/env python3
"""Validate portable Lattice boundaries without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail("Missing required file: " + str(path.relative_to(ROOT)))
        return ""


def require_files(paths: list[str]) -> None:
    for relative in paths:
        if not (ROOT / relative).is_file():
            fail("Missing required file: " + relative)


def roles() -> None:
    agency = text(ROOT / "agency.yaml")
    section = re.search(r"^roles:\n(?P<body>.*?)^gates:", agency, re.MULTILINE | re.DOTALL)
    if section is None:
        fail("agency.yaml has no roles section followed by gates")
        return
    found: list[str] = []
    patterns: list[str] = []
    blocks = re.compile(r"^  (?P<role>[a-z]+):\n(?P<body>.*?)(?=^  [a-z]+:|\Z)", re.MULTILINE | re.DOTALL)
    for match in blocks.finditer(section.group("body")):
        role = match.group("role")
        body = match.group("body")
        found.append(role)
        prompt = re.search(r"^    prompt: (?P<path>agents/[a-z]+\.md)$", body, re.MULTILINE)
        if prompt is None or not (ROOT / prompt.group("path")).is_file():
            fail("Role has no canonical prompt: " + role)
        writes = re.search(r"^    writes:\n(?P<paths>(?:      - [^\n]+\n)+)", body, re.MULTILINE)
        if writes is None:
            fail("Role has no write domains: " + role)
        else:
            patterns.extend(re.findall(r"^      - ([^\n]+)$", writes.group("paths"), re.MULTILINE))
    expected = {"director", "product", "experience", "architecture", "android", "services", "intelligence", "quality", "security", "release", "assurance"}
    if set(found) != expected:
        fail("Expected 11 canonical roles")
    if len(patterns) != 22 or len(set(patterns)) != len(patterns):
        fail("Expected 22 disjoint write domains")


def boundaries() -> None:
    kernel = [ROOT / "AGENTS.md", ROOT / "agency.yaml"]
    for folder in ("agents", "governance", "templates"):
        kernel.extend(sorted((ROOT / folder).glob("*.md")))
    for path in kernel:
        body = text(path)
        if "plos-001" in body or "Personal Life OS" in body:
            fail("Project state leaked into Agency Kernel: " + str(path.relative_to(ROOT)))
    if "platform: chatgpt_work" in text(ROOT / "agency.yaml"):
        fail("agency.yaml retains a default ChatGPT Work platform")
    capsule = ROOT / "projects" / "plos-001"
    if not (capsule / "PROJECT.md").is_file():
        fail("Missing plos-001 project capsule")
    if list(capsule.rglob("AGENTS.md")) or list(capsule.rglob("agency.yaml")):
        fail("Project capsule copied Agency Kernel files")


def adapters() -> None:
    required = [
        "CLAUDE.md", "adapters/README.md", "adapters/local/README.md",
        "adapters/codex/README.md", "adapters/claude/README.md",
        "adapters/chatgpt-work/README.md",
        "adapters/chatgpt-work/PROJECT-INSTRUCTIONS.md",
        "scripts/lattice.py", "scripts/export_chatgpt_work.py",
    ]
    require_files(required)
    if "@AGENTS.md" not in text(ROOT / "CLAUDE.md"):
        fail("CLAUDE.md does not import canonical AGENTS.md")
    for relative in required[1:7]:
        body = text(ROOT / relative)
        if "Personal Life OS" in body or "plos-001" in body:
            fail("Project-specific state leaked into adapter: " + relative)


def provenance() -> None:
    try:
        data = json.loads(text(ROOT / "docs" / "source-provenance.json"))
    except json.JSONDecodeError:
        fail("Invalid source provenance JSON")
        return
    inventory = [
        item
        for bundle in data.get("source_bundles", {}).values()
        for item in bundle.get("virtual_files", [])
    ]
    if len(inventory) != 129:
        fail("Expected 129 preserved source artifacts")
    for relative in inventory:
        if not (ROOT / relative).is_file():
            fail("Provenance references missing source: " + relative)
    require_files(["docs/portable-build-manifest.json"])


def export() -> None:
    from export_chatgpt_work import build_pack
    project = "plos-001"
    folder = ROOT / "exports" / "chatgpt-work" / project
    pack = folder / "Lattice_ChatGPT_Work_Pack_plos-001.md"
    instructions = folder / "PROJECT-INSTRUCTIONS.md"
    manifest = folder / "source-manifest.json"
    require_files([str(pack.relative_to(ROOT)), str(instructions.relative_to(ROOT)), str(manifest.relative_to(ROOT))])
    expected = build_pack(project)
    if text(pack) != expected:
        fail("ChatGPT Work pack is stale; regenerate it")
    if text(instructions) != text(ROOT / "adapters" / "chatgpt-work" / "PROJECT-INSTRUCTIONS.md"):
        fail("ChatGPT Work instruction export is stale")
    try:
        data = json.loads(text(manifest))
        if data.get("pack_sha256") != hashlib.sha256(expected.encode()).hexdigest():
            fail("ChatGPT Work export hash does not match")
    except json.JSONDecodeError:
        fail("Invalid ChatGPT Work export manifest")


def github() -> None:
    required = [
        ".github/ISSUE_TEMPLATE/config.yml",
        ".github/ISSUE_TEMPLATE/new-project.yml",
        ".github/ISSUE_TEMPLATE/agency-maintenance.yml",
        ".github/ISSUE_TEMPLATE/defect.yml",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/CODEOWNERS.example",
        ".github/workflows/validate.yml",
    ]
    require_files(required)
    workflow = text(ROOT / ".github" / "workflows" / "validate.yml")
    for fragment in ("pull_request:", "workflow_dispatch:", "scripts/validate_lattice.py"):
        if fragment not in workflow:
            fail("GitHub validation workflow is incomplete: " + fragment)


def secrets() -> None:
    patterns = [
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}"),
    ]
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ""}:
            continue
        body = text(path)
        for pattern in patterns:
            if pattern.search(body):
                fail("Potential credential found in: " + str(path.relative_to(ROOT)))


def main() -> int:
    require_files([
        "README.md", "AGENTS.md", "agency.yaml", "portfolio/registry.md",
        "portfolio/status.md", "projects/plos-001/PROJECT.md",
        "governance/charter.md", "governance/autonomy-policy.md",
        "governance/ownership.md", "governance/delivery-system.md",
    ])
    roles()
    boundaries()
    adapters()
    provenance()
    export()
    github()
    secrets()
    if ERRORS:
        print("Lattice portability validation failed:")
        for error in ERRORS:
            print("- " + error)
        return 1
    print("Lattice portability validation passed: 11 roles, 22 write domains, 129 source artifacts, and a current ChatGPT Work pack.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
