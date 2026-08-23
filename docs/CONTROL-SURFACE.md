# Local Control Surface and Hooks

The 0.0.5 runtime integration puts ordinary claims through the host-neutral control-plane boundary and exposes the same read model to a local human supervisor.

## Unified claim path

`python3 scripts/lattice.py claim` now accepts optional host metadata and defaults to `local`:

```bash
python3 scripts/lattice.py claim \
  --project first-project \
  --role application \
  --actor worker-1 \
  --host codex \
  --workspace worktree-42
```

Before the claim is made, expired leases for the project are recovered and audited. The claim remains subject to the existing frontier, role, and WIP guards.

Use `python3 scripts/lattice.py inspect` for the read-only control projection and `python3 scripts/lattice.py recover --project <id>` for explicit recovery.

## Semantic revision and event sequence

Hosted deltas are guarded by the project's semantic revision: the last revision that changed project truth, readiness, commitments, exceptions, or another governed project-state entity. Operational lifecycle telemetry does not advance that revision.

The control read model exposes a separate `event_sequence` based on durable event IDs. This lets hosts and the human control surface observe claims, workspaces, timeouts, recovery, and hook failures without making those observations invalidate otherwise-current hosted work.

A lifecycle event therefore carries both an `event_id` and the semantic revision at which it occurred. `state_revision` and hosted `base_revision` continue to mean semantic project state, not telemetry sequence.

## Local control surface

Start the dependency-free local server:

```bash
python3 scripts/control_server.py
```

It binds to `127.0.0.1:8765` by default and serves:

- `/` — human portfolio/project status;
- `/api/state` — the read model as JSON;
- `/health` — process health.

The first surface is intentionally read-only. It shows active objective and milestone, ready work, active workers, pending verification, and open exceptions. Authority remains in guarded state transitions.

## Lifecycle hooks

`runtime/hooks.json` maps lifecycle event names to ordered argv arrays. It is empty by default.

```json
{
  "action_claimed": [
    ["python3", "integrations/on_claim.py"]
  ]
}
```

Hooks receive the event envelope as JSON on stdin, run from the repository root in declaration order, and execute directly rather than through a shell.

Lifecycle hooks are post-commit integrations. A nonzero hook exit is recorded as `hook_failed`; it does not pretend that the triggering durable event never happened. For an `action_claimed` hook failure, Lattice fails closed before handing the claim to a worker: it releases the lease and records `claim_aborted`, returning the action to the normally derived frontier. This prevents an error response from leaving hidden in-flight work behind.

Hooks do not receive a separate state mutation API. Any project-state change must still go through a guarded Lattice operation.

## Validation

This integration is validated against the repository's active seed contract, including capsule/state agreement, machine-readable capabilities, release-version consistency, and the absence of legacy process-backlog artifacts.
