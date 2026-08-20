#!/usr/bin/env python3
"""Validate Lattice 0.0.3 boundaries without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import tempfile
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


def require(paths: list[str]) -> None:
    for relative in paths:
        if not (ROOT / relative).is_file():
            fail("Missing required file: " + relative)


def project_ids() -> list[str]:
    folder = ROOT / "projects"
    if not folder.is_dir():
        return []
    return sorted(path.name for path in folder.iterdir() if path.is_dir() and (path / "PROJECT.md").is_file())


def validate_roles() -> None:
    agency = text(ROOT / "agency.yaml")
    section = re.search(r"^roles:\n(?P<body>.*?)^readiness:", agency, re.MULTILINE | re.DOTALL)
    if section is None:
        fail("agency.yaml has no roles section followed by readiness")
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
            fail("Role has no artifact write domains: " + role)
        else:
            patterns.extend(re.findall(r"^      - ([^\n]+)$", writes.group("paths"), re.MULTILINE))
    expected = {
        "director", "product", "experience", "architecture", "android", "services",
        "intelligence", "quality", "security", "release", "assurance",
    }
    if set(found) != expected:
        fail("Expected 11 canonical roles; found " + ", ".join(found))
    if len(patterns) != 22 or len(set(patterns)) != len(patterns):
        fail("Expected 22 unique artifact write domains")


def validate_state_contract() -> None:
    required = [
        "runtime/schema.sql", "runtime/policy.json", "state/current.json", "state/README.md",
        "scripts/state_engine.py", "scripts/lattice.py",
    ]
    require(required)
    try:
        policy = json.loads(text(ROOT / "runtime" / "policy.json"))
        snapshot = json.loads(text(ROOT / "state" / "current.json"))
    except json.JSONDecodeError as error:
        fail("Invalid state JSON: " + str(error))
        return
    if policy.get("agency_version") != "0.0.3" or policy.get("schema_version") != 1:
        fail("Runtime policy version is not 0.0.3/schema 1")
    if snapshot.get("format") != "lattice-state-snapshot" or snapshot.get("schema_version") != 1:
        fail("Portable state snapshot format is invalid")
    tables = snapshot.get("tables", {})
    required_tables = {
        "projects", "objectives", "milestones", "records", "record_versions", "truths",
        "truth_versions", "truth_links", "truth_transitions", "conditions", "condition_inputs",
        "condition_truths", "condition_dependencies", "condition_reviewers", "submissions",
        "reviews", "evidence", "commitments", "exceptions", "events",
    }
    if set(tables) != required_tables:
        fail("Portable snapshot tables are incomplete or include ephemeral state")
    if "leases" in tables or "leases" not in snapshot.get("ephemeral_state_excluded", []):
        fail("Action leases must be excluded from the portable snapshot")
    snapshot_projects = {row.get("id") for row in tables.get("projects", [])}
    if snapshot_projects != set(project_ids()):
        fail("Project capsules and operational-state project IDs do not match")
    schema = text(ROOT / "runtime" / "schema.sql")
    for fragment in (
        "one_active_objective_per_project", "one_active_milestone_per_project",
        "one_planned_milestone_per_project",
        "truth_transitions", "one_open_exception_per_key", "leases_by_capacity",
    ):
        if fragment not in schema:
            fail("Runtime schema lacks invariant: " + fragment)
    try:
        from state_engine import StateStore

        with tempfile.TemporaryDirectory() as folder:
            local = Path(folder)
            store = StateStore(ROOT, local / "state.db", ROOT / "state" / "current.json")
            try:
                if store.conn.execute("PRAGMA foreign_key_check").fetchall():
                    fail("Snapshot violates SQLite foreign keys")
                store.status()
                store.frontier(project_ids()[0], limit=3)
            finally:
                store.close()
    except (ImportError, sqlite3.Error, ValueError, KeyError) as error:
        fail("State engine cannot load the portable snapshot: " + str(error))


def validate_no_process_backlog() -> None:
    forbidden_templates = {
        "work-order.md", "handoff.md", "qa-cycle.md", "verification.md",
        "gate-decision.md", "change-request.md", "review-finding.md", "release-gate.md",
    }
    present = {path.name for path in (ROOT / "templates").glob("*.md")}
    for name in sorted(forbidden_templates & present):
        fail("Obsolete routine-process template remains active: templates/" + name)
    for project in project_ids():
        capsule = ROOT / "projects" / project
        for path in capsule.rglob("*"):
            if path.is_dir() and path.name in {"orders", "handoffs", "verifications", "gate-decisions"}:
                fail("Project contains an active process-backlog directory: " + str(path.relative_to(ROOT)))
    guidance = text(ROOT / "AGENTS.md")
    for fragment in (
        "Lattice has no ordinary work-order backlog",
        "No agent edits `state/current.json`",
        "Moving a truth from frontier to background",
        "Ordinary agents cannot create durable commitments",
    ):
        if fragment not in guidance:
            fail("AGENTS.md lacks required active-frontier rule: " + fragment)


def validate_boundaries() -> None:
    kernel = [ROOT / "AGENTS.md", ROOT / "agency.yaml"]
    for folder in ("agents", "governance", "runtime"):
        kernel.extend(sorted(path for path in (ROOT / folder).rglob("*") if path.is_file()))
    for path in kernel:
        if "<PROJECT_ID>" in text(path):
            fail("Project placeholder leaked into Agency Kernel: " + str(path.relative_to(ROOT)))
    if "platform: chatgpt_work" in text(ROOT / "agency.yaml"):
        fail("agency.yaml retains a default ChatGPT Work platform")
    for project in project_ids():
        capsule = ROOT / "projects" / project
        if list(capsule.rglob("AGENTS.md")) or list(capsule.rglob("agency.yaml")):
            fail("Project capsule copied Agency Kernel files: " + project)


def validate_adapters() -> None:
    required = [
        "CLAUDE.md", "adapters/README.md", "adapters/local/README.md",
        "adapters/codex/README.md", "adapters/claude/README.md",
        "adapters/chatgpt-work/README.md", "adapters/chatgpt-work/PROJECT-INSTRUCTIONS.md",
        "scripts/export_chatgpt_work.py", "docs/HOSTED-DELTA-PROTOCOL.md",
    ]
    require(required)
    if "@AGENTS.md" not in text(ROOT / "CLAUDE.md"):
        fail("CLAUDE.md does not import canonical AGENTS.md")
    readme = text(ROOT / "README.md")
    for fragment in ("## Initialize the seed", "objective-add", "condition-add", "truth-list"):
        if fragment not in readme:
            fail("README initialization is incomplete: " + fragment)


def validate_exports() -> None:
    from export_chatgpt_work import build_pack, write_export

    require(["exports/chatgpt-work/README.md"])
    project = project_ids()[0]
    expected = build_pack(project)
    if "# Active Frontier Projection" not in expected or project not in expected:
        fail("ChatGPT Work exporter did not produce a scoped frontier projection")
        return
    with tempfile.TemporaryDirectory() as folder:
        destination = Path(folder) / project
        write_export(project, destination, False)
        pack = destination / ("Lattice_ChatGPT_Work_Pack_" + project + ".md")
        instructions = destination / "PROJECT-INSTRUCTIONS.md"
        manifest_path = destination / "source-manifest.json"
        delta = destination / "STATE-DELTA-TEMPLATE.json"
        for path in (pack, instructions, manifest_path, delta):
            if not path.is_file():
                fail("ChatGPT Work exporter omitted: " + path.name)
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("version") != "0.0.3":
                fail("ChatGPT Work manifest has the wrong version")
            if manifest.get("pack_sha256") != hashlib.sha256(expected.encode()).hexdigest():
                fail("ChatGPT Work pack hash does not match")
            if instructions.read_text(encoding="utf-8") != text(
                ROOT / "adapters" / "chatgpt-work" / "PROJECT-INSTRUCTIONS.md"
            ):
                fail("ChatGPT Work instructions do not match the adapter")
        except (json.JSONDecodeError, FileNotFoundError) as error:
            fail("Invalid generated ChatGPT Work export: " + str(error))


def validate_github() -> None:
    required = [
        ".github/ISSUE_TEMPLATE/config.yml", ".github/ISSUE_TEMPLATE/new-project.yml",
        ".github/ISSUE_TEMPLATE/agency-maintenance.yml", ".github/ISSUE_TEMPLATE/defect.yml",
        ".github/PULL_REQUEST_TEMPLATE.md", ".github/CODEOWNERS.example",
        ".github/workflows/validate.yml",
    ]
    require(required)
    workflow = text(ROOT / ".github" / "workflows" / "validate.yml")
    for fragment in ("pull_request:", "workflow_dispatch:", "scripts/lattice.py validate", "unittest discover"):
        if fragment not in workflow:
            fail("GitHub validation workflow is incomplete: " + fragment)


def validate_privacy() -> None:
    patterns = [
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"\bghp_[A-Za-z0-9]{30,}\b"),
        re.compile(r"\bgithub_pat_[A-Za-z0-9_]{30,}\b"),
        re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"(?<![A-Za-z0-9])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        re.compile(r"(?<![A-Za-z0-9])(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}(?![A-Za-z0-9])"),
    ]
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".lattice", "__pycache__"} for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".sql", ""}:
            continue
        body = text(path)
        for pattern in patterns:
            if pattern.search(body):
                fail("Potential credential or direct contact data found in: " + str(path.relative_to(ROOT)))


def main() -> int:
    require([
        "README.md", "AGENTS.md", "agency.yaml", "portfolio/registry.md",
        "portfolio/status.md", "seed/SEED-MANIFEST.json", "MIGRATE-TO-0.0.3.md",
        "governance/charter.md", "governance/autonomy-policy.md",
        "governance/ownership.md", "governance/delivery-system.md",
        "docs/ACTIVE-FRONTIER.md", "docs/TRUTH-LEDGER.md",
    ])
    if not project_ids():
        fail("No project capsule exists")
    validate_roles()
    validate_state_contract()
    validate_no_process_backlog()
    validate_boundaries()
    validate_adapters()
    validate_exports()
    validate_github()
    validate_privacy()
    if ERRORS:
        print("Lattice validation failed:")
        for error in ERRORS:
            print("- " + error)
        return 1
    print(
        "Lattice validation passed: active frontier, guarded state, 11 roles, 22 write domains, "
        "truth ledger, scoped host adapters, and sanitized project capsules."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
