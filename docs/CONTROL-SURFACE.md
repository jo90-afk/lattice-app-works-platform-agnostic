# Local Control Surface and Hooks

The control surface exposes canonical Lattice state to a human supervisor without creating a second writable control path. The 0.0.7 surface uses the same configured operational backend as workers, including Postgres when `LATTICE_DATABASE_URL` is set.

## Unified claim path

`python3 scripts/lattice.py claim` accepts optional host metadata and defaults to `local`:

```bash
python3 scripts/lattice.py claim \
  --project first-project \
  --role application \
  --actor worker-1 \
  --host codex \
  --workspace worktree-42
```

Before the claim is made, expired leases for the project are recovered and audited. The claim remains subject to the existing frontier, role, WIP, and shared-state concurrency guards.

Use `python3 scripts/lattice.py inspect` for the host-neutral read projection and `python3 scripts/lattice.py recover --project <id>` for explicit recovery.

## Complete action lifecycle

Completed leased actions have a host-neutral lifecycle wrapper in `scripts/lifecycle.py` for release, submission, failure, verification, milestone acceptance, commitment fulfillment, and exception resolution.

For example:

```bash
python3 scripts/lifecycle.py submit \
  --lease <lease-id> \
  --role application \
  --summary "Increment implemented" \
  --artifact projects/first-project/platform/result.txt
```

The guarded state transition commits first. Lattice then emits an operational lifecycle event carrying the lease, action key, target, outcome identity, and current semantic revision. Post-transition hook failure is audited as `hook_failed` with `committed: true`; it cannot retroactively turn accepted state into a failed operation.

Operational event types include:

- `action_released`
- `action_submitted`
- `action_failed`
- `verification_recorded`
- `milestone_acceptance_recorded`
- `commitment_fulfillment_recorded`
- `exception_resolution_recorded`

## Semantic revision and event sequence

Hosted deltas are guarded by the project's semantic revision: the last revision that changed governed project state. Operational lifecycle telemetry does not advance that revision.

The control read model exposes a separate `event_sequence` based on durable event IDs. This lets hosts and the human control surface observe claims, workspaces, timeouts, recovery, and hook failures without making those observations invalidate otherwise-current hosted work.

A lifecycle event therefore carries both an `event_id` and the semantic revision at which it occurred. `state_revision` and hosted `base_revision` continue to mean semantic project state, not telemetry sequence.

## 0.0.7 supervision projection

`scripts/supervision_model.py` composes the existing control-plane read model with human-supervision context. It is a projection only; it does not persist new portfolio or project entities.

The projection adds:

- configured state backend identity;
- portfolio-order project presentation;
- counts for active projects, ready actions, in-flight leases, pending verification, exceptions, and Principal decisions;
- the existing Principal-only decision inbox;
- recent accepted semantic changes across the selected portfolio or project;
- operational counts for claims, completions, recovery, lease expiry, worker failure, hook failure, and claim aborts;
- observed host identities from lifecycle telemetry.

The existing project projection remains intact underneath it: objective, milestone, semantic revision, readiness, frontier, active leases, pending verification, exceptions, frontier truths, evidence chain, and recent events.

## Decision-grade Principal inbox

The Principal inbox is not a task list. It contains only open `principal_only` exceptions and open commitments owned by `principal`.

Each item is projected with enough context to decide without reconstructing the project from chat history:

- the exact decision required;
- the authority rule that prevented an agent role from deciding it;
- active project, objective, milestone, and semantic revision;
- the exact durable target state when the exception names one;
- durable evidence directly attached to that target, including submission/review evidence for condition targets;
- only choices already supported by the state machine; and
- the state consequence of each choice.

For a Principal-only exception the supported choices are `resolve` with an explicit durable resolution, or `leave_open`. For a Principal-owned commitment they are `fulfill` with a recorded summary, or `leave_open`. The browser renders those choices and consequences for supervision but still exposes no mutation buttons or forms. A later write interaction must route through the same guarded claim/resolve/fulfill transitions rather than inventing UI authority.

Routine remediation, ordinary verification, and Director-owned commitments remain outside the inbox.

## Local control surface

Start the dependency-free local server:

```bash
python3 scripts/control_server.py
```

It binds to `127.0.0.1:8765` by default and serves:

- `/` — human portfolio/project supervision and the Principal decision inbox;
- `/api/state` — the complete read-only supervision projection as JSON;
- `/health` — process health.

The server opens state through `scripts/store_factory.py`. Local installations therefore read SQLite by default; shared installations with `LATTICE_DATABASE_URL` read the same authoritative Postgres state used by remote workers. The UI may not silently fall back to a different store.

## Lifecycle hooks

`runtime/hooks.json` maps lifecycle event names to ordered argv arrays. It is empty by default.

```json
{
  "action_claimed": [
    ["python3", "integrations/on_claim.py"]
  ],
  "verification_recorded": [
    ["python3", "integrations/on_verification.py"]
  ]
}
```

Hooks receive the event envelope as JSON on stdin, run from the repository root in declaration order, and execute directly rather than through a shell.

Lifecycle hooks are post-commit integrations. A nonzero hook exit is recorded as `hook_failed`; it does not pretend that the triggering durable event never happened. For an `action_claimed` hook failure, Lattice fails closed before handing the claim to a worker: it releases the lease and records `claim_aborted`, returning the action to the normally derived frontier. For completion events, the state transition remains committed and the hook failure is observable for integration recovery.

Hooks do not receive a separate state mutation API. Any project-state change must still go through a guarded Lattice operation.

## Validation

The surface is validated against the same repository contract and Postgres-backed concurrency suite as the runtime. Rendering tests also require it to remain read-only: there are no mutation forms, buttons, or hidden UI write paths.
