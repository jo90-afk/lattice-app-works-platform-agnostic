# Concurrency Semantics

Lattice 0.0.6 makes ownership and shared-writer semantics explicit without introducing a second project-state model.

## Atomic hosted claim

Hosted claims execute inside the selected backend's project-write transaction boundary. SQLite uses `BEGIN IMMEDIATE`; Postgres uses a project-scoped transaction advisory lock, allowing unrelated projects to proceed independently while writes to the same project serialize. Operational claim telemetry does not advance semantic project revision.

## Lease renewal

Long-running workers may renew an active lease through the versioned host-adapter `renew` operation. Renewal requires the original project, leasing role, and leasing actor, may extend but never shorten expiry, and cannot revive expired authority.

## Artifact write ownership

Canonical role write domains in `agency.yaml` are executable concurrency policy. Repository-local artifacts must stay inside the leased project capsule and the leasing role's declared paths. Logical external references such as `artifact://...` do not claim repository ownership. The bounded scheduler also avoids intentionally co-scheduling same-project roles whose canonical write domains overlap.

## Truth compare-and-swap

Truth replacement requires an exact observed version. `truth-revise --expected-version` acquires the project write boundary, rereads the truth, and rejects stale writers rather than overwriting a newer proposition.

## Serialized hosted delta acceptance

Hosted deltas recheck `base_revision` inside the project write boundary immediately before semantic mutation. `scripts/hosted_delta.py` fast-rejects stale deltas, atomically claims the requested action, then performs the commit-time revision check. Once one delta changes project semantics, another delta based on the old revision is rejected and any coordination lease is released.

The primary `scripts/lattice.py` claim and `apply-delta` commands use the 0.0.6 atomic paths.

## Intrinsic shared-store serialization

Project serialization is also intrinsic to `PostgresStateStore`, not only to host wrappers. Direct semantic operations for project status, objectives, milestones, records, truths, truth links/attention, readiness conditions, commitments, and exceptions enter the same project advisory lock before calling the canonical `StateStore` implementation.

This closes the gap where two legitimate callers could bypass host wrappers and race the same project record. A concurrent same-record test requires both writers to succeed as successive versions rather than producing a duplicate version, constraint failure, or lost update.

Higher-level wrappers may acquire the same project lock before calling the store. Postgres transaction advisory locks are re-entrant for the owning transaction, so intrinsic locking does not create a second authority system; it makes the existing boundary unavoidable for shared semantic writes.

## Operational state backends

`scripts/state_backend.py` defines the concurrency-critical transaction boundary without defining a second truth model or snapshot format:

- `SQLiteStateBackend` uses `BEGIN IMMEDIATE` for the default local store.
- `PostgresStateBackend` uses deterministic project-scoped `pg_advisory_xact_lock` for shared writers.

## Postgres global revision allocation

Different projects intentionally use different advisory locks, so the global portable-snapshot revision cannot be protected by any one project lock. `PostgresStateStore._bump_revision()` allocates revisions atomically with `UPDATE ... RETURNING`. Concurrent mutations in different projects therefore receive distinct monotonic global revisions while retaining independent project locks.

## Shared state and validation

A live Postgres store is authoritative after one-time empty-store bootstrap; repository snapshots cannot silently rewind it. Portable checkpoint publication is explicit through `scripts/shared_state_checkpoint.py`. SQLite remains the dependency-free default; Postgres is loaded only when a shared store is configured.

CI starts a real Postgres service and uses separate connections to prove:

- competing truth revisions produce one winner and one stale writer;
- same-base hosted deltas produce one semantic winner;
- simultaneous different-project writes allocate unique global revisions;
- simultaneous direct writes to the same record serialize into distinct successive versions; and
- claim, verification, Assurance, snapshot round-trip, and event sequencing remain intact.

## Invariants

- one active lease per action key;
- project and role WIP limits are atomic with lease creation;
- lease renewal requires the current owner;
- repository artifacts stay inside canonical role write domains;
- overlapping role write domains are not intentionally co-scheduled inside one project;
- shared semantic writes serialize intrinsically by project;
- truth replacement rejects stale observed versions;
- hosted deltas recheck project revision at semantic commit;
- expired authority cannot be resurrected;
- semantic revision remains distinct from operational event sequence;
- unrelated projects do not share project locks;
- global Postgres snapshot revisions remain unique under cross-project concurrency;
- acceptance and verification remain guarded state transitions;
- `state/current.json` remains the portable checkpoint contract.
