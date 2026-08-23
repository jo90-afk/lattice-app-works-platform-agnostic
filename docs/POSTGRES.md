# Postgres Store Foundation

Postgres is the shared-writer target for Lattice 0.0.6, but support is enabled only when the same guarded `StateStore` semantics can run against it. Lattice does not maintain a second Postgres-specific truth model.

## What exists now

`scripts/state_backend.py` defines project-scoped transaction locking. `PostgresStateBackend` uses `pg_advisory_xact_lock` with a deterministic project key.

`scripts/sql_dialect.py` now supplies the SQL compatibility layer needed by the existing `StateStore` implementation:

- SQLite `?` parameters become Postgres `%s` parameters;
- `INSERT OR IGNORE` becomes `ON CONFLICT DO NOTHING`;
- `last_insert_rowid()` becomes `LASTVAL()`;
- Postgres rows preserve both `row["column"]` and `row[index]` access used by `sqlite3.Row`;
- the canonical `runtime/schema.sql` is rendered into Postgres form by removing SQLite PRAGMAs and replacing the event AUTOINCREMENT key with `BIGSERIAL`.

Run `python3 scripts/render_postgres_schema.py` to render `runtime/postgres-schema.sql` in an installation that wants an inspectable Postgres schema artifact.

## What is deliberately not claimed yet

`StateStore` still constructs SQLite by default and Postgres is not yet advertised as an operational runtime. The next enablement step must make store construction accept a compatible Postgres connection, repair event sequences after snapshot import, replace SQLite-only snapshot ordering, and run the same guarded state-engine scenarios against that connection.

No Postgres driver is a dependency of the local-first core. A distributed installation will supply a DB-API-compatible driver when Postgres construction is enabled.

## Acceptance bar

Postgres becomes a supported backend only when the shared implementation preserves:

- the portable `state/current.json` snapshot contract;
- project revision and event-sequence semantics;
- frontier derivation and WIP checks;
- lease ownership and renewal;
- condition invalidation and stale-worker rejection;
- independent verification and mandatory reviewer rules;
- exactly-once milestone acceptance under races;
- commitment and exception authority boundaries;
- recovery and idempotent hosted completion behavior.
