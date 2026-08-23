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

Hooks receive the event envelope as JSON on stdin, run from the repository root in declaration order, and fail closed on a nonzero exit. Commands are executed directly rather than through a shell.

Hooks do not receive a separate state mutation API. Any project-state change must still go through a guarded Lattice operation.

## Validation

This integration is validated against the repository's active seed contract, including capsule/state agreement, machine-readable capabilities, and the absence of legacy process-backlog artifacts.
