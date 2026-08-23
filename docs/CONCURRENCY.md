# Concurrency Semantics

Lattice 0.0.6 makes ownership and shared-writer semantics explicit without introducing a second project-state model.

## Atomic hosted claim

Hosted claims execute inside the selected backend's project-write transaction boundary. SQLite uses `BEGIN IMMEDIATE`, so frontier derivation, project WIP checks, role WIP checks, and lease insertion occur while competing local writers are serialized. Postgres uses a project-scoped transaction advisory lock, allowing unrelated projects to proceed independently while writes to the same project serialize.

The durable `action_claimed` event remains operational telemetry and does not advance semantic project revision.

## Lease renewal

Long-running workers may renew an active lease through the versioned host-adapter `renew` operation. Renewal requires the original project, leasing role, and leasing actor. It may extend but never shorten the current expiry.

Renewal does not grant new authority and does not change project truth. It only extends the lifetime of authority already granted by the original claim. A worker cannot renew another actor's lease or revive an expired lease.

Example envelope:

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "renew",
  "project_id": "first-project",
  "host": "codex",
  "workspace_id": "worktree-42",
  "lease_id": "lease-abc123",
  "actor": "worker-1",
  "role": "application",
  "ttl_minutes": 30
}
```

## Operational state backends

`scripts/state_backend.py` defines the transaction boundary used by concurrency-critical operations. It deliberately does not define a second truth model or snapshot format.

The implementations are:

- `SQLiteStateBackend` — default local backend; serializes writers with `BEGIN IMMEDIATE`.
- `PostgresStateBackend` — shared-writer backend; acquires a deterministic project-scoped `pg_advisory_xact_lock` inside the connection's current DB-API transaction.

Claim, renewal, release, submission, failure, verification, milestone acceptance, commitment fulfillment, and exception resolution enter the same backend project-write boundary before invoking the existing guarded `StateStore` transition. The backend does not replace those transitions; it serializes the authority decision around them.

## Postgres StateStore

`scripts/postgres_store.py` runs the canonical `StateStore` semantics on a supplied DB-API Postgres connection. It uses the compatibility layer in `scripts/sql_dialect.py` for parameter syntax and sqlite3.Row-compatible result access, renders Postgres DDL from the canonical `runtime/schema.sql`, and preserves `state/current.json` as the portable snapshot contract.

Snapshot export uses explicit primary/composite key ordering rather than SQLite `rowid`. Snapshot import repairs the Postgres `events.id` sequence after inserting portable explicit event IDs, so subsequent events continue monotonically.

Postgres driver selection remains outside the core. The default installation is still Python's standard library plus SQLite. A shared deployment installs a compatible `psycopg` driver and sets:

```bash
export LATTICE_DATABASE_URL='postgresql://user:password@host/database'
python3 scripts/shared_host_adapter.py --file envelope.json
```

`scripts/store_factory.py` loads `psycopg` only when a Postgres URL is explicitly configured. The ordinary local CLI remains SQLite-first.

## Validation

CI starts a real Postgres service and runs the guarded lifecycle through it: objective and milestone creation, condition derivation, hosted claim, submission, independent verification, and Assurance acceptance. The same test then exports the portable snapshot, rebuilds a clean Postgres schema from it, verifies semantic state survives, and proves event sequencing continues after the imported maximum ID.

Postgres support is therefore gated by the same semantic lifecycle rather than by adapter-unit tests alone.

## Invariants

Every operational backend preserves these rules:

- one active lease per action key;
- project and role WIP limits are checked atomically with lease creation;
- lease renewal requires the current owner;
- expired authority cannot be resurrected;
- semantic revisions are distinct from operational event sequence;
- unrelated projects do not share a project-scoped lock in distributed backends;
- acceptance and verification remain guarded state transitions rather than host-side convention;
- `state/current.json` remains the portable snapshot contract.
