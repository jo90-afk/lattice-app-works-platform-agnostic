#!/usr/bin/env python3
"""Local AI-provider setup for Lattice.

Secrets are stored outside the repository and project state. The public status
surface intentionally exposes only provider/model/configuration metadata.
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


def credentials_path() -> Path:
    override = os.environ.get("LATTICE_CREDENTIALS_PATH")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".lattice" / "providers.json"


def _read_file() -> dict[str, Any]:
    path = credentials_path()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def provider_status() -> dict[str, Any]:
    stored = _read_file()
    provider = str(stored.get("provider") or "").strip().lower()
    model = str(stored.get("model") or "").strip()
    if provider in PROVIDERS:
        key = str(stored.get("api_key") or "")
        if key:
            return {
                "configured": True,
                "provider": provider,
                "provider_label": PROVIDERS[provider]["label"],
                "model": model or PROVIDERS[provider]["default_model"],
                "credential_source": "local credential store",
            }
    for candidate, spec in PROVIDERS.items():
        if os.environ.get(spec["env"]):
            return {
                "configured": True,
                "provider": candidate,
                "provider_label": spec["label"],
                "model": model or spec["default_model"],
                "credential_source": "environment",
            }
    return {
        "configured": False,
        "provider": None,
        "provider_label": None,
        "model": None,
        "credential_source": None,
    }


def save_provider(provider: str, api_key: str, model: str | None = None) -> dict[str, Any]:
    provider = provider.strip().lower()
    if provider not in PROVIDERS:
        raise ValueError("Unsupported provider")
    api_key = api_key.strip()
    if not api_key:
        raise ValueError("API key is required")
    model = (model or "").strip() or PROVIDERS[provider]["default_model"]
    path = credentials_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.parent.chmod(0o700)
    except OSError:
        pass
    payload = {"provider": provider, "model": model, "api_key": api_key}
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        temp.chmod(0o600)
    except OSError:
        pass
    temp.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return provider_status()


def clear_provider() -> None:
    path = credentials_path()
    if path.exists():
        path.unlink()
