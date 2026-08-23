#!/usr/bin/env python3
"""Non-destructive environment preflight for Lattice public-beta setup."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MIN_PYTHON = (3, 10)
REQUIRED_PATHS = (
    "AGENTS.md",
    "agency.yaml",
    "runtime/policy.json",
    "runtime/schema.sql",
    "state/current.json",
    "seed/SEED-MANIFEST.json",
    "scripts/lattice.py",
    "scripts/initialize_seed.py",
)


def _check(name: str, ok: bool, detail: str, *, required: bool = True) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "required": required, "detail": detail}


def _run_python_script(relative: str) -> tuple[bool, str]:
    process = subprocess.run(
        [sys.executable, str(ROOT / relative)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    output = (process.stdout or process.stderr).strip()
    return process.returncode == 0, output or f"exit {process.returncode}"


def _check_writeability() -> tuple[bool, str]:
    lattice_dir = ROOT / ".lattice"
    try:
        lattice_dir.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix="doctor-", dir=lattice_dir, delete=True):
            pass
        state_dir = ROOT / "state"
        with tempfile.NamedTemporaryFile(prefix="doctor-", dir=state_dir, delete=True):
            pass
    except OSError as error:
        return False, str(error)
    return True, ".lattice/ and state/ are writable"


def _check_postgres(database_url: str) -> tuple[bool, str]:
    try:
        import psycopg
    except ImportError:
        return False, "LATTICE_DATABASE_URL is set but psycopg is not installed"
    try:
        connection = psycopg.connect(database_url, connect_timeout=5)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        finally:
            connection.close()
    except Exception as error:  # driver-specific connection errors share no stdlib base
        return False, f"Postgres connection failed: {error}"
    return True, "configured Postgres endpoint accepted a read-only connectivity check"


def doctor() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    python_ok = sys.version_info >= MIN_PYTHON
    checks.append(
        _check(
            "python",
            python_ok,
            f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}; requires >= {MIN_PYTHON[0]}.{MIN_PYTHON[1]}",
        )
    )

    missing = [relative for relative in REQUIRED_PATHS if not (ROOT / relative).is_file()]
    checks.append(
        _check(
            "repository-layout",
            not missing,
            "required kernel, runtime, state, and seed files are present"
            if not missing
            else "missing: " + ", ".join(missing),
        )
    )

    version_ok, version_detail = _run_python_script("scripts/check_version.py")
    checks.append(_check("release-metadata", version_ok, version_detail))

    contract_ok, contract_detail = _run_python_script("scripts/validate_lattice.py")
    checks.append(_check("repository-contract", contract_ok, contract_detail))

    writable, writable_detail = _check_writeability()
    checks.append(_check("local-writeability", writable, writable_detail))

    database_url = os.environ.get("LATTICE_DATABASE_URL")
    if database_url:
        postgres_ok, postgres_detail = _check_postgres(database_url)
        checks.append(_check("postgres", postgres_ok, postgres_detail))
        backend = "postgres"
    else:
        checks.append(
            _check(
                "postgres",
                True,
                "not configured; SQLite remains the dependency-free local backend",
                required=False,
            )
        )
        backend = "sqlite"

    git_path = shutil.which("git")
    checks.append(
        _check(
            "git",
            bool(git_path),
            f"git available at {git_path}" if git_path else "git not found; runtime works, but clone/commit workflow will not",
            required=False,
        )
    )

    required_failures = [item["name"] for item in checks if item["required"] and not item["ok"]]
    optional_warnings = [item["name"] for item in checks if not item["required"] and not item["ok"]]
    return {
        "format": "lattice-doctor",
        "version": 1,
        "ok": not required_failures,
        "release": (ROOT / "VERSION").read_text(encoding="utf-8").strip() if (ROOT / "VERSION").is_file() else None,
        "state_backend": backend,
        "required_failures": required_failures,
        "optional_warnings": optional_warnings,
        "checks": checks,
    }


def _human(payload: dict[str, Any]) -> str:
    lines = [
        f"Lattice doctor: {'ready' if payload['ok'] else 'not ready'}",
        f"release {payload.get('release') or 'unknown'} · {payload['state_backend']} state",
    ]
    for item in payload["checks"]:
        if item["ok"]:
            marker = "OK"
        elif item["required"]:
            marker = "FAIL"
        else:
            marker = "WARN"
        lines.append(f"[{marker}] {item['name']}: {item['detail']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit the machine-readable preflight result")
    args = parser.parse_args()
    payload = doctor()
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_human(payload))
    return 0 if payload["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
