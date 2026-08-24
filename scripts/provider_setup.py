#!/usr/bin/env python3
"""Local AI-provider setup and role/model preferences for Lattice.

Credentials live outside the repository and project state. Role preferences are
non-secret local runtime configuration and may identify provider/model choices.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

PROVIDERS = {
    "openai": {"label": "OpenAI", "env": "OPENAI_API_KEY", "default_model": "gpt-5.6-sol"},
    "anthropic": {"label": "Anthropic", "env": "ANTHROPIC_API_KEY", "default_model": "claude-sonnet"},
    "google": {"label": "Google", "env": "GOOGLE_API_KEY", "default_model": "gemini"},
}

ROLES = (
    "director", "product", "experience", "architecture", "application",
    "services", "intelligence", "quality", "security", "release", "assurance",
)


def config_dir() -> Path:
    override = os.environ.get("LATTICE_CONFIG_DIR")
    return Path(override).expanduser() if override else Path.home() / ".lattice"


def credentials_path() -> Path:
    return config_dir() / "providers.json"


def preferences_path() -> Path:
    return config_dir() / "models.json"


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_private(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        temp.chmod(0o600)
    except OSError:
        pass
    temp.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def configured_providers() -> list[dict[str, Any]]:
    stored = _read(credentials_path()).get("providers") or {}
    result: list[dict[str, Any]] = []
    for provider, spec in PROVIDERS.items():
        entry = stored.get(provider) if isinstance(stored, dict) else None
        has_stored = bool(isinstance(entry, dict) and entry.get("api_key"))
        has_env = bool(os.environ.get(spec["env"]))
        if has_stored or has_env:
            result.append({
                "provider": provider,
                "label": spec["label"],
                "credential_source": "local credential store" if has_stored else "environment",
            })
    return result


def save_provider(provider: str, api_key: str) -> None:
    provider = provider.strip().lower()
    if provider not in PROVIDERS:
        raise ValueError("Unsupported provider")
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key is required")
    payload = _read(credentials_path())
    providers = payload.setdefault("providers", {})
    providers[provider] = {"api_key": api_key}
    _write_private(credentials_path(), payload)


def save_model_preferences(
    fallback_provider: str,
    fallback_model: str,
    role_assignments: dict[str, dict[str, str]],
) -> None:
    fallback_provider = fallback_provider.strip().lower()
    fallback_model = fallback_model.strip()
    if fallback_provider not in PROVIDERS:
        raise ValueError("Unsupported fallback provider")
    if not fallback_model:
        raise ValueError("Fallback model is required")
    normalized: dict[str, dict[str, str]] = {}
    for role, assignment in role_assignments.items():
        if role not in ROLES:
            raise ValueError(f"Unsupported role: {role}")
        provider = str(assignment.get("provider") or "").strip().lower()
        model = str(assignment.get("model") or "").strip()
        if not provider and not model:
            continue
        if provider not in PROVIDERS or not model:
            raise ValueError(f"Role {role} requires provider and model")
        normalized[role] = {"provider": provider, "model": model}
    _write_private(
        preferences_path(),
        {
            "fallback": {"provider": fallback_provider, "model": fallback_model},
            "roles": normalized,
        },
    )


def runtime_model_status() -> dict[str, Any]:
    providers = configured_providers()
    preferences = _read(preferences_path())
    fallback = preferences.get("fallback") if isinstance(preferences.get("fallback"), dict) else None
    roles = preferences.get("roles") if isinstance(preferences.get("roles"), dict) else {}
    return {
        "configured": bool(providers and fallback),
        "providers": providers,
        "fallback": fallback,
        "roles": roles,
    }


def resolve_model(role: str) -> dict[str, str] | None:
    status = runtime_model_status()
    assignment = status.get("roles", {}).get(role)
    if isinstance(assignment, dict):
        return {"provider": str(assignment["provider"]), "model": str(assignment["model"])}
    fallback = status.get("fallback")
    if isinstance(fallback, dict):
        return {"provider": str(fallback["provider"]), "model": str(fallback["model"])}
    return None
