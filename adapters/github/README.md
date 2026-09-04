# GitHub hosted-agent adapter

GitHub Copilot cloud agent can work in a Lattice repository without becoming a separate source of project truth.

GitHub supports root `AGENTS.md` agent instructions and project Agent Skills. Lattice therefore keeps the Agency Kernel in the existing root `AGENTS.md` and exposes execution technique through `.agents/skills/lattice-execution/SKILL.md`. Do not duplicate the kernel into `.github/copilot-instructions.md` merely to support this host.

## Host boundary

Treat the GitHub agent as a replaceable execution host:

1. inspect or claim through the Lattice host-adapter envelope contract;
2. associate the claim with the agent's branch/workspace identity when one is available;
3. use the `/lattice-execution` skill or allow the agent to load it when relevant;
4. resolve only the role/platform expertise named by the claimed work;
5. edit only role-owned project artifacts;
6. run decisive validation in the workspace;
7. reconcile repository-local artifacts before hosted submission;
8. complete through the same `scripts/host_adapter.py` contract used by other hosts;
9. leave independent verification and milestone acceptance to the roles already defined by Lattice.

## Claim envelope

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "claim",
  "project_id": "first-project",
  "host": "github-copilot-cloud-agent",
  "workspace_id": "branch-or-agent-workspace-id",
  "actor": "github-agent-1",
  "role": "application"
}
```

Pass it to:

```bash
python3 scripts/host_adapter.py --file claim.json
```

The returned action is the execution brief. Do not replace it with a GitHub issue checklist or agent-generated work plan as durable project state.

## Completion

A successful implementation still requires a guarded completion envelope. For example:

```json
{
  "format": "lattice-host-adapter",
  "version": 1,
  "operation": "complete",
  "project_id": "first-project",
  "host": "github-copilot-cloud-agent",
  "lease_id": "lease-abc123",
  "role": "application",
  "outcome": {
    "type": "submit",
    "summary": "Implemented the claimed increment",
    "artifact_refs": [
      "projects/first-project/platform/result.txt"
    ]
  }
}
```

If GitHub retries after a lost response, send the identical envelope. Lattice's recovery layer either replays the committed result, reconciles it from durable semantic state, or rejects stale intent and requires a fresh claim.

## Pull requests and reviews

A GitHub pull request is transport and collaboration evidence, not Lattice acceptance. A merged branch does not by itself satisfy a readiness condition. When a PR URL, check run, or review is useful evidence, record or reference it through the normal submission/review transition rather than turning GitHub status into an implicit gate.

Copilot code review may use repository skills when relevant, but Lattice's verifier role and required verdict remain the acceptance authority for the project condition.

## Reconcile external state

Use the shared [GitHub reconciliation contract](../../docs/GITHUB-RECONCILIATION.md)
when a capsule's active PR or release declaration may have outlived the external
state. `scripts/lattice.py github-check` validates fresh repository-scoped GET
captures without opening a state store. The Director can record the same report
with `github-reconcile`, using the existing contract record, truth versions,
project revision guard, and attention transitions. A zero-ahead open branch is a
supersession candidate requiring a scoped Director disposition; transport state
never substitutes for independent verification or publication authorization.
