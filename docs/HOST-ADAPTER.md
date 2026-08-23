# Host Adapter Contract

Lattice treats coding agents and hosted runtimes as replaceable execution hosts. The host adapter is the boundary between those runtimes and Lattice's durable project state.

The adapter is intentionally small. It does not ask a host to understand Lattice's internal tables, and it does not let a host write durable truth directly.

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

## One claim path

The ordinary Lattice CLI now claims through the control-plane adapter. Existing local usage still works because `--host` defaults to `local`:

```bash
python3 scripts/lattice.py claim \
  --project first-project \
  --role application \
  --actor worker-1
```

A host can attach its own identity and workspace:

```bash
python3 scripts/lattice.py claim \
  --project first-project \
  --role application \
  --actor worker-1 \
  --host codex \
  --workspace codex-worktree-42
```

Every claim first audits and clears expired leases for the project, then delegates to the existing guarded `StateStore.claim` transition, and finally records `action_claimed` with runtime metadata. There is no second claim implementation for hosts.

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
python3 scripts/lattice.py inspect
```

Inspect one project:

```bash
python3 scripts/lattice.py inspect --project first-project
```

Reading this projection does not mutate state.

## Local human control surface

The first human surface is intentionally read-only. It is a thin presentation of the same read model rather than a second application state.

```bash
python3 scripts/control_server.py
```

By default it binds only to `127.0.0.1:8765` and serves:

- `/` — compact portfolio/project supervision view;
- `/api/state` — the control read model as JSON;
- `/health` — process health.

The page shows the active objective and milestone, ready work, active workers, pending verification, and open exceptions. There are no mutation controls in this slice; decisions still go through guarded state transitions.

## Lifecycle hooks

`runtime/hooks.json` provides deterministic hook dispatch around lifecycle events. The file maps an event name to an ordered list of argv arrays. It is empty by default.

Example:

```json
{
  "action_claimed": [
    ["python3", "integrations/on_claim.py"]
  ]
}
```

Each hook:

- runs from the repository root;
- receives the lifecycle event envelope as JSON on stdin;
- runs in declaration order;
- uses direct argv execution rather than shell interpolation;
- must exit successfully or the lifecycle operation reports failure.

Hooks may enforce or integrate around runtime events, but they do not receive direct authority to rewrite Lattice state. If a hook needs a state change, it must call a normal guarded operation.

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

Supported externally reported events are:

- `workspace_created`
- `workspace_abandoned`
- `policy_checked`
- `worker_failed`
- `worker_timed_out`

The adapter itself owns `action_claimed`, `lease_expired`, and `recovery_completed` so a host cannot forge those transitions through the CLI.

## Recovery

Leases remain intentionally ephemeral and excluded from the portable snapshot. If a worker disappears while its local runtime database survives, an expired lease can be reclaimed without reconstructing intent from a conversation log.

```bash
python3 scripts/lattice.py recover --project first-project
```

Recovery:

1. finds expired leases;
2. removes them from operational state;
3. records one durable `lease_expired` event per lease;
4. records `recovery_completed` for each affected project;
5. dispatches configured hooks;
6. recomputes the active frontier.

The original action returns to the frontier only if the durable project state still makes it ready. If another state transition has made the action stale, it does not reappear.

## Why runtime events are durable

The lease itself is not project truth. The fact that an agent attempted work, disappeared, or required recovery can still be useful operational evidence. Lattice therefore persists lifecycle events while keeping leases out of the portable snapshot.

This separation is deliberate: execution hosts can come and go without becoming a second authority over the project model.

## Remaining 0.0.5 work

The next implementation slices should:

- add submit/fail/release lifecycle boundaries where they improve recovery and observability;
- make host adapters invokable through one machine envelope rather than only CLI flags;
- expand the human surface from status visibility into an explicit Principal decision inbox;
- package reusable expertise as host-neutral skills without moving authority out of the Agency Kernel.
