#!/usr/bin/env python3
"""Deterministic, host-neutral lifecycle hook dispatch for Lattice."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from state_engine import LatticeError


HOOK_CONFIG = Path("runtime/hooks.json")


def load_hooks(root: Path) -> dict[str, list[list[str]]]:
    path = root / HOOK_CONFIG
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise LatticeError("runtime/hooks.json must contain an object")
    hooks: dict[str, list[list[str]]] = {}
    for event_type, commands in raw.items():
        if not isinstance(event_type, str) or not isinstance(commands, list):
            raise LatticeError("Invalid hook configuration")
        normalized: list[list[str]] = []
        for command in commands:
            if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
                raise LatticeError("Hook commands must be non-empty argv arrays")
            normalized.append(command)
        hooks[event_type] = normalized
    return hooks


def dispatch_hooks(
    root: Path,
    event_type: str,
    envelope: dict[str, Any],
) -> list[dict[str, Any]]:
    """Run configured hooks in declaration order with the event envelope on stdin."""
    commands = load_hooks(root).get(event_type, [])
    if not commands:
        return []
    payload = json.dumps(envelope, sort_keys=True)
    results: list[dict[str, Any]] = []
    for index, command in enumerate(commands):
        completed = subprocess.run(
            command,
            cwd=root,
            input=payload,
            text=True,
            capture_output=True,
            check=False,
        )
        result = {
            "index": index,
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        results.append(result)
        if completed.returncode != 0:
            raise LatticeError(
                f"Lifecycle hook failed for {event_type} at index {index}: "
                + (completed.stderr.strip() or completed.stdout.strip() or f"exit {completed.returncode}")
            )
    return results
