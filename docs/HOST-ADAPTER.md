# Host Adapter Contract

Lattice treats coding agents and hosted runtimes as replaceable execution hosts. The host adapter is the boundary between those runtimes and Lattice's durable project state.

The first adapter implementation is intentionally small. It does not ask a host to understand Lattice's internal tables, and it does not let a host write durable truth directly.

## Boundary

A host may:

- inspect the control-plane read model;
- claim one action already derived by the active frontier;
- attach host and workspace identity to the runtime event stream;
- report lifecycle events such as workspace creation, policy checks, worker failure, or abandonment;
- request recovery of expired leases.

A host may not:

- insert or edit truths, records, conditions, reviews, commitments, or exceptions by writing the database;
- bypass role and WIP constraints when claiming an action;
- advance a milestone without the existing Assurance transition;
- treat lifecycle telemetry as project truth.

The machine-readable envelope is in `runtime/host-adapter.schema.json`.

## Control read model

The control-plane projection is read-only and stable enough for a CLI, local UI, or remote coordinator to consume. It contains, per project:

- active objective and milestone;
- currently derived frontier;
- active leases;
- pending verification;
- open exceptions;
- truths currently demanding frontier attention;
- recent durable events.

Inspect all projects:

```bash
python3 scripts/control_plane.py inspect
```

Inspect one project:

```bash
python3 scripts/control_plane.py inspect --project first-project
```

Reading this projection does not mutate state.

## Claim through a host

A host claim first recovers expired leases for the project, then delegates to the existing guarded `StateStore.claim` transition. The adapter records an `action_claimed` event with host/workspace metadata after the lease is created.

```bash
python3 scripts/control_plane.py claim \
  --project first-project \
  --role application \
  --actor worker-1 \
  --host codex \
  --workspace codex-worktree-42
```

The returned action remains the bounded execution brief produced by the active frontier. Host metadata does not enter the brief unless a later policy explicitly requires it.

## Lifecycle events

Hosts can append runtime events without changing project truth:

```bash
python3 scripts/control_plane.py event \
  --project first-project \
  --event-type workspace_created \
  --entity-type workspace \
  --entity-id codex-worktree-42 \
  --host codex \
  --workspace codex-worktree-42
```

Supported external events in this first slice are:

- `workspace_created`
- `workspace_abandoned`
- `policy_checked`
- `worker_failed`
- `worker_timed_out`

The adapter itself owns `action_claimed`, `lease_expired`, and `recovery_completed` so a host cannot forge those transitions through the CLI.

## Recovery

Leases remain intentionally ephemeral and excluded from the portable snapshot. If a worker disappears while its local runtime database survives, an expired lease can be reclaimed without reconstructing intent from a conversation log.

```bash
python3 scripts/control_plane.py recover --project first-project
```

Recovery:

1. finds expired leases;
2. removes them from operational state;
3. records one durable `lease_expired` event per lease;
4. records `recovery_completed` for each affected project;
5. recomputes the active frontier.

The original action returns to the frontier only if the durable project state still makes it ready. If another state transition has made the action stale, it does not reappear.

## Why runtime events are durable

The lease itself is not project truth. The fact that an agent attempted work, disappeared, or required recovery can still be useful operational evidence. Lattice therefore persists lifecycle events while keeping leases out of the portable snapshot.

This separation is deliberate: execution hosts can come and go without becoming a second authority over the project model.

## Next implementation slice

This adapter is the foundation for the rest of 0.0.5. The next work should:

- route the main `scripts/lattice.py claim` path through the adapter so recovery is universal rather than opt-in;
- add submit/fail/release lifecycle boundaries where they improve recovery and observability;
- add deterministic hook dispatch around adapter events;
- make host adapters invokable through one envelope rather than only CLI flags;
- expose the read model through the first local human control surface.
