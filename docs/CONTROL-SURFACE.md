# Local Control Surface and Hooks

The 0.0.5 runtime integration puts ordinary claims through the host-neutral control-plane boundary and exposes the same read model to a local human supervisor.

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

Before the claim is made, expired leases for the project are recovered and audited. The claim remains subject to the existing frontier, role, and WIP guards.

Use `python3 scripts/lattice.py inspect` for the read-only control projection and `python3 scripts/lattice.py recover --project <id>` for explicit recovery.

## Complete action lifecycle

Claim is only the start of the runtime boundary. Completed leased actions now have a host-neutral lifecycle wrapper in `scripts/lifecycle.py` for release, submission, failure, verification, milestone acceptance, commitment fulfillment, and exception resolution.

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

Hosted deltas are guarded by the project's semantic revision: the last revision that changed project truth, readiness, commitments, exceptions, or another governed project-state entity. Operational lifecycle telemetry does not advance that revision.

The control read model exposes a separate `event_sequence` based on durable event IDs. This lets hosts and the human control surface observe claims, workspaces, timeouts, recovery, and hook failures without making those observations invalidate otherwise-current hosted work.

A lifecycle event therefore carries both an `event_id` and the semantic revision at which it occurred. `state_revision` and hosted `base_revision` continue to mean semantic project state, not telemetry sequence.

## Local control surface

Start the dependency-free local server:

```bash
python3 scripts/control_server.py
```

It binds to `127.0.0.1:8765` by default and serves:

- `/` — human portfolio/project status and the Principal decision inbox;
- `/api/state` — the read model plus the Principal decision projection as JSON;
- `/health` — process health.

The surface remains intentionally read-only. It shows active objective and milestone, ready work, active workers, pending verification, open exceptions, and a Principal inbox derived only from durable state that actually requires human authority.

The Principal inbox is not a task list. It contains only:

- open exceptions explicitly marked `principal_only`; and
- open commitments whose owner is `principal`.

Routine remediation, ordinary verification, and Director-owned commitments stay out of it. Authority remains in guarded state transitions.

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

This integration is validated against the repository's active seed contract, including capsule/state agreement, machine-readable capabilities, release-version consistency, lifecycle regression coverage, Principal-inbox derivation, and the absence of legacy process-backlog artifacts.
