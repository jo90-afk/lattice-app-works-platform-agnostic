#!/usr/bin/env python3
"""Fail CI when public release metadata drifts from VERSION."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    errors: list[str] = []

    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f"VERSION is not a semantic version: {version!r}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if not readme.startswith(f"# Lattice App Works {version}\n"):
        errors.append("README heading does not match VERSION")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## {version}\n" not in changelog:
        errors.append("CHANGELOG has no section for VERSION")

    seed = json.loads((ROOT / "seed" / "SEED-MANIFEST.json").read_text(encoding="utf-8"))
    if seed.get("version") != version:
        errors.append("seed/SEED-MANIFEST.json version does not match VERSION")

    if errors:
        print("Release version validation failed:")
        for error in errors:
            print("- " + error)
        return 1

    print(f"Release version metadata is consistent: {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
