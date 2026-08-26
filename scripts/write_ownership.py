#!/usr/bin/env python3
"""Artifact write-ownership policy derived from canonical agency.yaml."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from state_engine import LatticeError


_URI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://")
_PROJECT_ARTIFACT_SCHEME = "project-artifact"
_PROJECT_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


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


def _project_artifact_parts(value: str) -> tuple[str, str] | None:
    """Parse a typed external project artifact without binding it to engine layout."""
    parsed = urlsplit(value)
    if parsed.scheme != _PROJECT_ARTIFACT_SCHEME:
        return None
    if parsed.query or parsed.fragment:
        raise LatticeError("Project artifact references cannot contain query or fragment data")
    project_id = unquote(parsed.netloc)
    if not project_id or not _PROJECT_ID.fullmatch(project_id):
        raise LatticeError("Project artifact reference has an invalid project id: " + value)
    path = _normalize_repo_path(unquote(parsed.path.lstrip("/")))
    if path in {"", "."}:
        raise LatticeError("Project artifact reference must name a project-relative path: " + value)
    return project_id, path


def _project_relative_prefix(pattern: str, project_id: str) -> str | None:
    """Translate one canonical project write domain to a project-relative prefix."""
    rendered = _prefix(pattern, project_id)
    project_root = f"projects/{project_id}"
    if rendered == project_root:
        return ""
    if rendered.startswith(project_root + "/"):
        return rendered[len(project_root) + 1 :]
    return None


def _project_relative_owned(root: Path, project_id: str, role: str, path: str) -> bool:
    patterns = role_write_domains(root).get(role, [])
    prefixes = [
        prefix
        for pattern in patterns
        if (prefix := _project_relative_prefix(pattern, project_id)) is not None
    ]
    return any(
        prefix == "" or path == prefix or path.startswith(prefix + "/")
        for prefix in prefixes
    )


def repository_artifact_owned(
    root: Path,
    project_id: str,
    role: str,
    artifact_ref: str,
) -> bool:
    """Return true for allowed logical refs or artifact paths owned by the role."""
    project_artifact = _project_artifact_parts(artifact_ref)
    if project_artifact is not None:
        ref_project_id, path = project_artifact
        return ref_project_id == project_id and _project_relative_owned(
            root, project_id, role, path
        )
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
        project_artifact = _project_artifact_parts(artifact_ref)
        if project_artifact is not None:
            ref_project_id, path = project_artifact
            if ref_project_id != project_id:
                raise LatticeError(
                    f"Artifact {artifact_ref!r} is outside project {project_id!r}"
                )
            if not _project_relative_owned(root, project_id, role, path):
                raise LatticeError(
                    f"Role {role!r} does not own external project artifact path {path!r}"
                )
            continue
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
