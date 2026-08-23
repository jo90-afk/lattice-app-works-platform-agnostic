# Bounded Scheduler

The Lattice scheduler is a query over current portfolio state, not a durable work queue.

It combines four existing sources of truth:

1. project order and global specialist capacity from `portfolio/registry.md`;
2. currently derived actions from each active project's frontier;
3. live leases and project/role WIP limits;
4. an explicit list of workers currently available to receive work.

A plan leaves no durable residue. A dispatch persists only the leases successfully granted through the same atomic host-claim path used everywhere else.

## Worker input

Workers are supplied as a JSON array:

```json
[
  {
    "actor": "application-1",
    "role": "application",
    "host": "codex",
    "workspace_id": "worktree-123"
  },
  {
    "actor": "quality-1",
    "role": "quality",
    "host": "github",
    "workspace_id": "copilot-task-9"
  }
]
```

A worker already holding any live lease is not considered available. Principal actions are never auto-scheduled; they remain in the human decision boundary.

## Plan

```bash
python3 scripts/scheduler.py plan --workers workers.json
```

Planning is read-only. The result reports portfolio capacity, active specialist leases, project order, projected project slots, compatible assignments, and workers left unused.

Portfolio order is the primary project sort. Within a project the active frontier already sorts actions by readiness/risk/priority score. The scheduler makes repeated passes across projects so one ready project does not consume a second slot before other higher-order ready projects have had an opportunity to receive one.

## Dispatch

```bash
python3 scripts/scheduler.py dispatch --workers workers.json
```

Dispatch passes every proposed assignment through `claim_for_host_atomic`. A concurrent change may invalidate a proposed action between planning and claim; that claim is rejected rather than guessed or queued for retry. A later scheduler invocation simply derives the frontier again.

## Capacity rules

The scheduler respects all of these before dispatch:

- portfolio specialist concurrency limit;
- currently active specialist leases;
- each project's `max_wip`;
- one active lease per role per project under current policy;
- one active lease per supplied worker actor;
- action availability on the current frontier.

The claim transition rechecks those invariants atomically, so the scheduler is an optimization and selection layer rather than an authority layer.

## Failure behavior

A blocked or paused project contributes no schedulable action and does not stop unrelated projects. A failed claim is returned in `rejected` and creates no replacement task. Consequential repeated failures remain governed by the existing retry/exception model.

The scheduler intentionally does not maintain pending assignments, retries, job rows, work orders, or a scheduler-owned task table.
