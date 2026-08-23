# Concurrency Semantics

Lattice 0.0.6 starts by making ownership semantics explicit before adding a shared remote database.

## Atomic hosted claim

Hosted claims execute inside the selected backend's project-write transaction boundary. For SQLite, that boundary is `BEGIN IMMEDIATE`: frontier derivation, project WIP checks, role WIP checks, and lease insertion therefore occur while competing local writers are serialized. The durable `action_claimed` event remains operational telemetry and does not advance semantic project revision.

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

## Operational state backend

`scripts/state_backend.py` defines the transaction boundary used by concurrency-critical operations. It deliberately does not define a second truth model or snapshot format.

The current implementations are:

- `SQLiteStateBackend` — default local backend; serializes writers with `BEGIN IMMEDIATE`.
- `PostgresStateBackend` — reference shared-writer boundary; starts a transaction and acquires a stable project-scoped `pg_advisory_xact_lock` before guarded project writes.

The Postgres adapter accepts a DB-API-style connection and imports no Postgres driver. Local installations therefore retain the standard-library-only runtime. A distributed installation may supply its own compatible driver when the full shared-store constructor is enabled.

The advisory-lock key is derived deterministically from the project ID, so separate runtimes serialize consequential writes to the same project while unrelated projects can proceed independently.

This slice routes claim and lease renewal through the backend interface. Subsequent 0.0.6 work will move the remaining concurrency-sensitive guarded transitions behind the same boundary before enabling a Postgres-backed `StateStore`.

## Invariants

Every operational backend must preserve at least these rules:

- one active lease per action key;
- project and role WIP limits are checked atomically with lease creation;
- lease renewal requires the current owner;
- expired authority cannot be resurrected;
- semantic revisions are distinct from operational event sequence;
- unrelated projects should not share a project-scoped lock in distributed backends;
- acceptance and verification remain guarded state transitions rather than host-side convention;
- `state/current.json` remains the portable snapshot contract.
