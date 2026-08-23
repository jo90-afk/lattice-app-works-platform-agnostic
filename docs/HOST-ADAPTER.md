# Host Adapter Contract

Lattice treats coding agents and hosted runtimes as replaceable execution hosts. The host adapter is the boundary between those runtimes and Lattice's durable project state.

Hosts do not need to understand Lattice's internal tables and do not receive direct write authority over durable truth. They exchange one versioned envelope with `scripts/host_adapter.py`; that router delegates to the same guarded state and lifecycle transitions used by the local CLI.

The machine-readable contract is `runtime/host-adapter.schema.json`.

## Operations

The v1 envelope supports five operations:

- `claim` — claim one action already derived by the active frontier;
- `complete` — complete the leased action through a guarded release, submit, fail, review, milestone acceptance, commitment fulfillment, or exception resolution transition;
- `event` — append an allowed external runtime event;
- `inspect` — read the control model globally or for one project;
- `recover` — recover expired leases globally or for one project.

Only `format`, `version`, and `operation` are universally required. `inspect` and `recover` may therefore operate globally without inventing a project or host identity. Claim, completion, and external event envelopes have operation-specific requirements.

## Execute one envelope

Pass a JSON file:

```bash
python3 scripts/host_adapter.py --file envelope.json
```

Or stream an envelope on stdin:

```bash
cat envelope.json | python3 scripts/host_adapter.py
```

Every operation either returns JSON or exits nonzero with a guarded rejection.

## Claim

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "claim",
  "project_id": "first-project",
  "host": "codex",
  "workspace_id": "worktree-42",
  "actor": "worker-1",
  "role": "application"
}
```

Claim first recovers expired leases for the project, then delegates to the normal guarded claim transition. The returned action is the bounded execution brief produced by the active frontier. `action_claimed` records host/workspace provenance without advancing semantic project revision.

## Complete

A completion envelope names the existing lease and one guarded outcome:

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "complete",
  "project_id": "first-project",
  "host": "codex",
  "lease_id": "lease-abc123",
  "role": "application",
  "outcome": {
    "type": "submit",
    "summary": "Increment implemented",
    "artifact_refs": ["projects/first-project/platform/result.txt"]
  }
}
```

The router verifies that project and role match the lease before performing the transition. Supported outcome types are:

- `release`
- `submit`
- `fail`
- `review`
- `advance`
- `commitment_fulfill`
- `exception_resolve`

Completion uses `scripts/lifecycle.py`, so local CLI and hosted execution share the same state mutation and post-transition telemetry semantics.

### Retry safety

A host may retry the same completion envelope after losing the response. Lattice searches the durable completion event stream by `lease_id` before requiring the ephemeral lease. If that lease already has a committed completion event, the adapter returns a replay acknowledgement with `replayed: true` and the original durable completion event instead of executing the transition again.

This makes ordinary network and process retries idempotent without introducing a completion queue. A replay must still match the project and role recorded on the original completion.

### Repository artifact reconciliation

For `submit`, any artifact reference inside `projects/<project-id>/...` is treated as a repository-local artifact that must already exist before the semantic submission transition. Missing or path-escaping project artifacts are rejected before mutation, and the lease remains active so the host can reconcile the files and retry.

Opaque or external artifact references are not interpreted as repository paths by this check. The host remains responsible for reconciling its isolated workspace into the repository before declaring project-local artifacts complete.

## External runtime events

Hosts may report only operational events that do not assert governed project truth:

- `workspace_created`
- `workspace_abandoned`
- `policy_checked`
- `worker_failed`
- `worker_timed_out`

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "event",
  "project_id": "first-project",
  "host": "codex",
  "workspace_id": "worktree-42",
  "event_type": "workspace_created",
  "entity_type": "workspace",
  "entity_id": "worktree-42",
  "payload": {}
}
```

Adapter-owned events such as `action_claimed`, lease recovery, hook failure, and completion telemetry cannot be forged through the external event operation.

## Inspect

Global inspection needs no project or host:

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "inspect"
}
```

Add `project_id` to scope the projection or `frontier_limit` to change the number of derived actions returned per project. Inspection does not mutate state.

## Recover

Global recovery also needs no artificial host or project identity:

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "recover"
}
```

With `project_id`, recovery is scoped to that project. Recovery removes expired leases, records durable operational evidence, and recomputes the frontier. An action reappears only if current durable state still makes it ready.

## Authority boundary

A host may inspect, claim, complete its leased work through guarded outcomes, report allowed runtime events, and request recovery. It may not directly insert or edit truths, records, conditions, reviews, milestones, commitments, or exceptions; bypass role/WIP guards; forge adapter-owned events; or treat lifecycle telemetry as project truth.

The lease remains ephemeral. Operational attempts and recovery events are durable because they are useful supervision evidence. Semantic project revision and event sequence remain separate so runtime observation cannot stale otherwise-current hosted work.
