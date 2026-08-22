#!/usr/bin/env python3
"""Resolve the smallest expertise set for one claimed Lattice role."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALID_PROJECT_ID = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")


def load_catalog(root: Path = ROOT) -> dict[str, Any]:
    path = root / "expertise" / "catalog.json"
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError("Expertise catalog is missing") from error
    except json.JSONDecodeError as error:
        raise ValueError("Expertise catalog is invalid: " + str(error)) from error
    if catalog.get("schema_version") != 1:
        raise ValueError("Unsupported expertise catalog schema")
    return catalog


def load_capabilities(project_id: str, root: Path = ROOT) -> dict[str, Any]:
    if not VALID_PROJECT_ID.fullmatch(project_id):
        raise ValueError("Invalid project ID")
    path = root / "projects" / project_id / "project" / "capabilities.json"
    if not path.is_file():
        return {
            "schema_version": 1,
            "application_platforms": [],
            "cross_platform_strategy": "undecided",
        }
    try:
        capabilities = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError("Invalid project capabilities: " + str(error)) from error
    if capabilities.get("schema_version") != 1:
        raise ValueError("Unsupported project capabilities schema")
    platforms = capabilities.get("application_platforms")
    if not isinstance(platforms, list) or any(not isinstance(value, str) for value in platforms):
        raise ValueError("application_platforms must be a list of strings")
    strategy = capabilities.get("cross_platform_strategy", "undecided")
    if not isinstance(strategy, str):
        raise ValueError("cross_platform_strategy must be a string")
    return capabilities


def normalized_platform(value: str) -> str:
    return re.sub(r"-+", "-", value.strip().lower().replace("_", "-").replace(" ", "-"))


def resolve_expertise(
    role: str,
    project_id: str,
    explicit_platforms: list[str] | None = None,
    root: Path = ROOT,
) -> dict[str, Any]:
    catalog = load_catalog(root)
    role_modules = catalog.get("role_modules") or {}
    if role not in role_modules:
        raise ValueError("No expertise module for role: " + role)

    paths = ["expertise/README.md", str(role_modules[role])]
    requested: list[str] = []
    resolved_packs: list[str] = []
    unresolved: list[str] = []

    if role == "application":
        capabilities = load_capabilities(project_id, root)
        raw_platforms = (
            explicit_platforms
            if explicit_platforms is not None
            else list(capabilities.get("application_platforms") or [])
        )
        strategy = normalized_platform(str(capabilities.get("cross_platform_strategy", "undecided")))
        if strategy not in {"", "native", "none", "undecided"}:
            raw_platforms = [*raw_platforms, strategy]

        aliases = catalog.get("platform_aliases") or {}
        packs = catalog.get("platform_packs") or {}
        for raw in raw_platforms:
            platform = normalized_platform(str(raw))
            if not platform or platform in requested:
                continue
            requested.append(platform)
            canonical = aliases.get(platform)
            if canonical in packs:
                pack = str(packs[canonical])
                if pack not in resolved_packs:
                    resolved_packs.append(pack)
                    paths.append(pack)
            else:
                unresolved.append(platform)

    missing = [path for path in paths if not (root / path).is_file()]
    if missing:
        raise ValueError("Expertise files are missing: " + ", ".join(missing))
    return {
        "schema_version": 1,
        "catalog_verified_on": catalog.get("verified_on"),
        "project_id": project_id,
        "role": role,
        "requested_platforms": requested,
        "resolved_platform_packs": resolved_packs,
        "unresolved_platforms": unresolved,
        "paths": list(dict.fromkeys(paths)),
        "unknown_platform_policy": catalog.get("unknown_platform_policy"),
    }
