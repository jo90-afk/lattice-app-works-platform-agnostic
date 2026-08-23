---
name: lattice-execution
description: Execute a claimed Lattice action using only its bounded context, selectively resolved expertise, owned artifacts, decisive validation, and the guarded completion path. Use when an agent host is performing work already claimed from a Lattice active frontier.
---

# Lattice execution

This skill teaches execution technique. It does not grant authority, select portfolio priority, alter readiness rules, or replace the repository's `AGENTS.md`, `agency.yaml`, current project state, or the claimed action.

## Start from the claim

Use the claimed action as the execution boundary. Preserve its `project_id`, `action_key`, `role`, target, semantic revision, linked records/truths, and acceptance context. Do not create a parallel task backlog or infer additional mandate from chat history.

If no action has been claimed, use the repository's guarded claim path or host-adapter `claim` operation before editing project deliverables.

## Load only relevant expertise

Resolve technique after the claim:

```bash
python3 scripts/lattice.py expertise --project <project-id> --role <role>
```

For Application work, pass only confirmed target platforms when a preview or unresolved-platform check is needed:

```bash
python3 scripts/lattice.py expertise \
  --project <project-id> --role application \
  --platform <platform>
```

Read the returned expertise paths. Treat them as technique and evidence guidance, never as permission to override the mandate, state, ownership boundaries, or verification requirements.

## Execute narrowly

1. Inspect the claimed context and the owned artifact paths for the role.
2. Read only additional project sources required by a linked dependency or contradiction.
3. Make the smallest coherent change that can satisfy the claimed condition or decision.
4. Preserve unrelated state and artifacts.
5. Run the smallest decisive checks that prove the changed behavior and any affected contract.
6. Record limitations or failed evidence rather than weakening acceptance criteria.

For an isolated host workspace, reconcile repository-local artifacts into the project capsule before reporting them in a hosted `submit` outcome.

## Complete through the guarded boundary

Repository-aware local execution may use the primary CLI completion commands. Hosts using the adapter should send a `complete` envelope to `scripts/host_adapter.py`.

Do not directly edit `state/current.json` or `.lattice/state.db`, forge lifecycle events, mark your own work verified, or treat a successful command as acceptance. Submission, independent verification, and Assurance acceptance remain separate transitions.

If the host loses the completion response, retry the identical completion envelope. Lattice will replay or reconcile the durable result when it can prove the original transition committed; it will reject stale or changed intent rather than guessing.
