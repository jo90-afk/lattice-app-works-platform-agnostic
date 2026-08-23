#!/usr/bin/env python3
"""Render runtime/postgres-schema.sql from the canonical SQLite schema."""

from __future__ import annotations

from pathlib import Path

from sql_dialect import postgres_schema

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "runtime" / "schema.sql"
TARGET = ROOT / "runtime" / "postgres-schema.sql"


def main() -> int:
    rendered = postgres_schema(SOURCE.read_text(encoding="utf-8"))
    TARGET.write_text(rendered, encoding="utf-8")
    print(f"Rendered {TARGET.relative_to(ROOT)} from {SOURCE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
