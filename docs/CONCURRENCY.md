# Concurrency Semantics

Lattice 0.0.6 makes ownership and shared-writer semantics explicit without introducing a second project-state model.

## Atomic hosted claim

Hosted claims execute inside the selected backend's project-write transaction boundary. SQLite uses `BEGIN IMMEDIATE`, so frontier derivation, project WIP checks, role WIP checks, and lease insertion occur while competing local writers are serialized. Postgres uses a project-scoped transaction advisory lock, allowing unrelated projects to proceed independently while writes to the same project serialize.

The durable `action_claimed` event remains operational telemetry and does not advance semantic project revision.

## Lease renewal

Long-running workers may renew an active lease through the versioned host-adapter `renew` operation. Renewal requires the original project, leasing role, and leasing actor. It may extend but never shorten the current expiry.

Renewal does not grant new authority and does not change project truth. It only extends the lifetime of authority already granted by the original claim. A worker cannot renew another actor's lease or revive an expired lease.

## Artifact write ownership

The canonical role write domains in `agency.yaml` are executable concurrency policy. `scripts/write_ownership.py` reads those domains directly rather than maintaining a second permissions map.

A repository-local artifact submitted under a lease must remain inside the leased project capsule, fall inside one of the leasing role's declared write domains, and avoid traversal outside that domain. Logical external references such as `artifact://...` are evidence identities rather than claims of repository ownership.

Submission ownership is checked before semantic mutation, so a rejected cross-domain artifact leaves the lease and readiness condition unchanged. The bounded scheduler also compares active and proposed role domains and will not co-schedule roles whose declared repository paths overlap.

## Truth compare-and-swap

A truth revision is a semantic replacement, not a last-writer-wins text edit. The primary `truth-revise` command therefore requires `--expected-version`. `scripts/semantic_writes.py` acquires the project's backend write boundary, rereads the truth under that boundary, and applies the revision only when the current version is exactly the version the caller observed.

Two workers that both read truth version 1 may both formulate a proposed version 2, but only one can commit it. The other receives an explicit stale-version rejection and must reread the current truth before deciding whether its proposition still applies.

## Serialized hosted delta acceptance

Hosted deltas remain project-revision guarded, but the stale check is now repeated inside the project write boundary immediately before the semantic transition. This closes the claim-to-completion race in which two different frontier actions could both have been prepared from the same old project revision.

`scripts/hosted_delta.py` performs a fast stale check, atomically claims the requested action, then acquires the project write boundary again and compares `base_revision` with the current semantic project revision at commit time. Once one delta changes project semantics, any other delta based on the old revision is rejected and its coordination lease is released rather than guessed forward.

The primary `scripts/lattice.py apply-delta` path uses this serialized acceptance path. The primary `claim` command also uses the 0.0.6 atomic claim implementation.

## Operational state backends

`scripts/state_backend.py` defines the transaction boundary used by concurrency-critical operations. It deliberately does not define a second truth model or snapshot format.

The implementations are:

- `SQLiteStateBackend` — default local backend; serializes writers with `BEGIN IMMEDIATE`.
- `PostgresStateBackend` — shared-writer backend; acquires a deterministic project-scoped `pg_advisory_xact_lock` inside the connection's current DB-API transaction.

Claim, renewal, release, submission, failure, verification, milestone acceptance, commitment fulfillment, exception resolution, truth CAS, and hosted-delta commit checks use the same backend project-write boundary before invoking the existing guarded state transition.

## Postgres global revision allocation

Project-scoped locks intentionally permit unrelated projects to write concurrently, so they cannot safely protect the global portable-snapshot revision counter. `PostgresStateStore._bump_revision()` therefore allocates revisions with one atomic database `UPDATE ... RETURNING` against the `meta.revision` row.

That row lock is held only for the revision increment; it does not turn unrelated project writes into one global project lock. Concurrent mutations in different projects receive distinct monotonic global revisions while retaining independent project advisory locks.

## Postgres StateStore

`scripts/postgres_store.py` runs the canonical `StateStore` semantics on a supplied DB-API Postgres connection. It uses the compatibility layer in `scripts/sql_dialect.py` for parameter syntax and sqlite3.Row-compatible result access, renders Postgres DDL from canonical `runtime/schema.sql`, and preserves `state/current.json` as the portable snapshot contract.

A live Postgres store is authoritative after one-time empty-store bootstrap; repository snapshots cannot silently rewind shared operational state. Portable checkpoint publication is explicit through `scripts/shared_state_checkpoint.py`.

Postgres driver selection remains outside the core. The default installation is still Python's standard library plus SQLite. A shared deployment installs a compatible `psycopg` driver and sets `LATTICE_DATABASE_URL`; `scripts/store_factory.py` loads the driver only when that shared store is explicitly configured.

## Validation

CI starts a real Postgres service and runs the guarded lifecycle through it. Concurrency regressions additionally use separate live Postgres connections to prove:

- competing revisions of one truth version produce one winner and one stale writer;
- two hosted deltas prepared from one project revision produce one semantic winner even when they target different actions;
- simultaneous semantic writes to different projects allocate distinct global snapshot revisions; and
- the existing claim, verification, Assurance, snapshot round-trip, and event-sequence contracts remain intact.

## Invariants

Every operational backend preserves these rules:

- one active lease per action key;
- project and role WIP limits are checked atomically with lease creation;
- lease renewal requires the current owner;
- repository artifacts remain inside the leasing role's canonical write domains;
- workers with overlapping role write domains are not intentionally co-scheduled inside one project;
- truth replacement rejects stale observed versions instead of silently overwriting them;
- hosted deltas recheck project revision at serialized semantic commit;
- expired authority cannot be resurrected;
- semantic revisions are distinct from operational event sequence;
- unrelated projects do not share a project-scoped lock in distributed backends;
- global Postgres snapshot revisions remain unique under cross-project concurrency;
- acceptance and verification remain guarded state transitions rather than host-side convention;
- `state/current.json` remains the portable snapshot contract.