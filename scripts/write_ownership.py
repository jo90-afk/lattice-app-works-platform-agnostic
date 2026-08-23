#!/usr/bin/env python3
"""Artifact write-ownership policy derived from canonical agency.yaml."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

from state_engine import LatticeError


_URI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")


def role_write_domains(root: Path) -> dict[str, list[str]]:
    """Parse the simple `roles.<role>.writes` subset of canonical agency.yaml."""
    text = (root / "agency.yaml").read_text(encoding="utf-8")
    domains: dict[str, list[str]] = {}
    in_roles = False
    current_role: str | None = None
    in_writes = False

    for raw in text.splitlines():
        if raw == "roles:":
            in_roles = True
            current_role = None
            in_writes = False
            continue
        if not in_roles:
            continue
        if raw and not raw.startswith(" "):
            break
        role_match = re.match(r"^  ([a-z][a-z0-9_-]*):\s*$", raw)
        if role_match:
            current_role = role_match.group(1)
            domains.setdefault(current_role, [])
            in_writes = False
            continue
        if current_role is None:
            continue
        if re.match(r"^    writes:\s*$", raw):
            in_writes = True
            continue
        if re.match(r"^    [a-z][a-z0-9_-]*:\s*", raw):
            in_writes = False
            continue
        if in_writes:
            item = re.match(r"^      -\s+(.+?)\s*$", raw)
            if item:
                domains[current_role].append(item.group(1))
    return domains


def _normalize_repo_path(value: str) -> str:
    path = value.replace("\\", "/").strip()
    while path.startswith("./"):
        path = path[2:]
    pure = PurePosixPath(path)
    if pure.is_absolute() or ".." in pure.parts:
        raise LatticeError("Artifact path escapes repository ownership: " + value)
    return str(pure)


def _prefix(pattern: str, project_id: str) -> str:
    rendered = pattern.replace("{project_id}", project_id).replace("\\", "/")
    if rendered.endswith("/**"):
        rendered = rendered[:-3]
    return rendered.rstrip("/")


def repository_artifact_owned(
    root: Path,
    project_id: str,
    role: str,
    artifact_ref: str,
) -> bool:
    """Return true for external logical refs or repository paths owned by role."""
    if _URI.match(artifact_ref):
        return True
    path = _normalize_repo_path(artifact_ref)
    if not path.startswith(f"projects/{project_id}/"):
        return False
    patterns = role_write_domains(root).get(role, [])
    return any(
        path == _prefix(pattern, project_id)
        or path.startswith(_prefix(pattern, project_id) + "/")
        for pattern in patterns
    )


def validate_artifact_ownership(
    root: Path,
    project_id: str,
    role: str,
    artifact_refs: list[str],
) -> None:
    for artifact_ref in artifact_refs:
        if not repository_artifact_owned(root, project_id, role, artifact_ref):
            if _URI.match(artifact_ref):
                continue
            path = _normalize_repo_path(artifact_ref)
            if not path.startswith(f"projects/{project_id}/"):
                raise LatticeError(
                    f"Artifact {artifact_ref!r} is outside project {project_id!r}"
                )
            raise LatticeError(
                f"Role {role!r} does not own artifact path {artifact_ref!r}"
            )


def roles_conflict(root: Path, project_id: str, left_role: str, right_role: str) -> bool:
    """Whether two role domains can address the same repository path."""
    if left_role == right_role:
        return True
    domains = role_write_domains(root)
    left = [_prefix(pattern, project_id) for pattern in domains.get(left_role, [])]
    right = [_prefix(pattern, project_id) for pattern in domains.get(right_role, [])]
    return any(
        a == b or a.startswith(b + "/") or b.startswith(a + "/")
        for a in left
        for b in right
    )
