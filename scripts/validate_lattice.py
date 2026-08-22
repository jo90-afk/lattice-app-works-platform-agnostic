#!/usr/bin/env python3
"""Validate Lattice 0.0.4 boundaries without third-party dependencies."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import tempfile
from datetime import date, datetime, timezone
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
        "director", "product", "experience", "architecture", "application", "services",
        "intelligence", "quality", "security", "release", "assurance",
    }
    if set(found) != expected:
        fail("Expected 11 canonical roles; found " + ", ".join(found))
    if len(patterns) != 22 or len(set(patterns)) != len(patterns):
        fail("Expected 22 unique artifact write domains")
    if (ROOT / "agents" / "android.md").exists():
        fail("Obsolete Android-only role prompt remains active")
    if "projects/{project_id}/platform/**" not in patterns:
        fail("Application role does not own the platform-neutral application domain")


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
    if policy.get("agency_version") != "0.0.4" or policy.get("schema_version") != 1:
        fail("Runtime policy version is not 0.0.4/schema 1")
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
    for folder in ("agents", "expertise", "governance", "runtime"):
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


def validate_expertise() -> None:
    required = ["expertise/README.md", "expertise/catalog.json", "scripts/expertise.py"]
    require(required)
    try:
        catalog = json.loads(text(ROOT / "expertise" / "catalog.json"))
    except json.JSONDecodeError as error:
        fail("Invalid expertise catalog: " + str(error))
        return
    expected_roles = {
        "director", "product", "experience", "architecture", "application", "services",
        "intelligence", "quality", "security", "release", "assurance",
    }
    if catalog.get("schema_version") != 1:
        fail("Expertise catalog schema is not 1")
    try:
        verified_on = date.fromisoformat(str(catalog.get("verified_on")))
        if verified_on > datetime.now(timezone.utc).date():
            fail("Expertise catalog verification date is in the future")
    except ValueError:
        fail("Expertise catalog has no valid verification date")

    role_modules = catalog.get("role_modules") or {}
    platform_packs = catalog.get("platform_packs") or {}
    aliases = catalog.get("platform_aliases") or {}
    if set(role_modules) != expected_roles:
        fail("Expertise catalog must map every canonical agent role exactly once")
    if not platform_packs:
        fail("Expertise catalog has no application platform packs")
    if set(aliases.values()) - set(platform_packs):
        fail("Expertise aliases reference unknown platform packs")
    if not catalog.get("unknown_platform_policy"):
        fail("Expertise catalog has no unknown-platform policy")

    for role, relative in role_modules.items():
        path = ROOT / str(relative)
        if not path.is_file():
            fail("Missing role expertise module: " + str(relative))
            continue
        if text(path).count("](https://") < 2:
            fail("Role expertise lacks primary-source basis: " + role)
        prompt = text(ROOT / "agents" / (role + ".md"))
        if "scripts/lattice.py expertise" not in prompt:
            fail("Agent prompt does not selectively resolve expertise: " + role)
    for platform, relative in platform_packs.items():
        path = ROOT / str(relative)
        if not path.is_file():
            fail("Missing platform expertise pack: " + str(relative))
            continue
        if "](https://" not in text(path):
            fail("Platform expertise lacks a primary source: " + platform)

    try:
        from expertise import resolve_expertise

        for project in project_ids():
            capability_path = ROOT / "projects" / project / "project" / "capabilities.json"
            if not capability_path.is_file():
                fail("Project has no machine-readable capabilities: " + project)
                continue
            try:
                capabilities = json.loads(text(capability_path))
            except json.JSONDecodeError as error:
                fail("Invalid project capabilities for " + project + ": " + str(error))
                continue
            if capabilities.get("schema_version") != 1:
                fail("Project capabilities schema is not 1: " + project)
            for field in (
                "application_platforms", "service_capabilities",
                "intelligence_capabilities", "release_targets",
            ):
                values = capabilities.get(field)
                if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                    fail("Project capability field must be a string list: " + project + "/" + field)
                elif len(values) != len(set(values)):
                    fail("Project capability field contains duplicates: " + project + "/" + field)
            if not isinstance(capabilities.get("cross_platform_strategy"), str):
                fail("Project cross_platform_strategy must be a string: " + project)
            for role in expected_roles:
                resolve_expertise(role, project)

        project = project_ids()[0]
        known = resolve_expertise("application", project, list(aliases))
        if set(known["resolved_platform_packs"]) != set(platform_packs.values()):
            fail("Application expertise aliases do not resolve every platform pack")
        unknown = resolve_expertise("application", project, ["unlisted-future-platform"])
        if unknown["unresolved_platforms"] != ["unlisted-future-platform"]:
            fail("Unknown application platforms are not reported without rejection")
        if any(path.startswith("expertise/platforms/") for path in unknown["paths"]):
            fail("Unknown application platforms load unrelated platform packs")
    except (ImportError, ValueError, KeyError) as error:
        fail("Expertise resolver is invalid: " + str(error))


def validate_exports() -> None:
    from export_chatgpt_work import build_pack, expertise_paths, write_export

    require(["exports/chatgpt-work/README.md"])
    project = project_ids()[0]
    expected = build_pack(project)
    if "# Active Frontier Projection" not in expected or project not in expected:
        fail("ChatGPT Work exporter did not produce a scoped frontier projection")
        return
    if "## Source: expertise/README.md" not in expected:
        fail("ChatGPT Work exporter omitted selectively resolved expertise")
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
            if manifest.get("version") != "0.0.4":
                fail("ChatGPT Work manifest has the wrong version")
            if manifest.get("pack_sha256") != hashlib.sha256(expected.encode()).hexdigest():
                fail("ChatGPT Work pack hash does not match")
            if instructions.read_text(encoding="utf-8") != text(
                ROOT / "adapters" / "chatgpt-work" / "PROJECT-INSTRUCTIONS.md"
            ):
                fail("ChatGPT Work instructions do not match the adapter")
            projection_actions = json.loads(
                re.search(
                    r"# Active Frontier Projection\n\n```json\n(?P<json>.*?)\n```",
                    expected,
                    re.DOTALL,
                ).group("json")
            )["actions"]
            if manifest.get("expertise_paths") != expertise_paths(project, projection_actions):
                fail("ChatGPT Work manifest expertise scope does not match its frontier")
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
        re.compile(r"(?<![A-Za-z0-9/])(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}(?![A-Za-z0-9])"),
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
        "portfolio/status.md", "seed/SEED-MANIFEST.json", "MIGRATE-TO-0.0.4.md",
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
    validate_expertise()
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
        "truth ledger, selective expertise, open platform capabilities, scoped host adapters, "
        "and sanitized project capsules."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
