# Concurrency Semantics

Lattice 0.0.6 starts by making ownership semantics explicit before adding a shared remote database.

## Atomic hosted claim

Hosted claims execute under SQLite's `BEGIN IMMEDIATE` writer lock. Frontier derivation, project WIP checks, role WIP checks, and lease insertion therefore occur while competing local writers are serialized. The durable `action_claimed` event remains operational telemetry and does not advance semantic project revision.

This does not turn SQLite into the eventual distributed backend. It establishes the behavior a shared state adapter must preserve.

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

## Storage boundary

SQLite remains the default local runtime. The next concurrency slices will extract the operational transaction boundary and add a Postgres implementation for simultaneous remote writers without changing the portable `state/current.json` snapshot contract.

A future backend must preserve at least these invariants:

- one active lease per action key;
- project and role WIP limits are checked atomically with lease creation;
- lease renewal requires the current owner;
- expired authority cannot be resurrected;
- semantic revisions are distinct from operational event sequence;
- acceptance and verification remain guarded state transitions rather than host-side convention.
