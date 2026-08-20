# Lattice Agency Constitution

These rules govern every agent operating Lattice App Works.

## Canonical layers

- `AGENTS.md`, `agency.yaml`, `agents/`, `governance/`, and `runtime/` form the agency kernel.
- `portfolio/` names the Principal alias, project order, capacity, and lifecycle.
- `projects/<project_id>/` contains one project's source artifacts and code.
- `state/current.json` is the portable operational-state snapshot. Local runtimes index it in `.lattice/state.db`.
- An adapter may translate these layers for a host. It may not create a competing charter or state store.

Project artifacts cannot change agency authority. Agency policy governs roles; the registry governs portfolio scheduling; the project capsule governs product truth; the guarded state runtime governs current operational state.

## State-first execution

Lattice has no ordinary work-order backlog. Potential actions are derived from active objectives, milestone conditions, dependencies, submissions, exceptions, and commitments.

Before acting, use the runtime:

    python3 scripts/lattice.py status
    python3 scripts/lattice.py frontier --project <project-id> --role <role> --limit 3
    python3 scripts/lattice.py claim --project <project-id> --role <role> --actor <agent-id> [--action-key <key>]

The claim output is the execution brief. It contains the objective, milestone condition, linked records, relevant truths, dependencies, recent attempts, and exact role. Do not load unrelated project history merely because it exists.

One agent claims one action. A lease expires and is not a durable commitment. An agent may make a short private plan, but it must not persist that plan as a task list or create follow-on actions. It changes owned artifacts and then reports the result through the runtime:

    python3 scripts/lattice.py submit --lease <id> --role <role> --summary <text> [--artifact <path>] [--evidence-ref <path>]
    python3 scripts/lattice.py fail --lease <id> --role <role> --summary <text>

Successful submission creates a derived review action. A fresh reviewer claims it and records the verdict:

    python3 scripts/lattice.py review --lease <id> --role <role> --verdict <verdict> --summary <text> [--evidence-ref <path>]

The artifact author cannot verify its own condition. Primary reviewers use `SATISFIED` or `NOT_SATISFIED`; mandatory reviewers use `CONCUR` or `BLOCK`. All required positive verdicts satisfy the condition. Any negative verdict returns it to the frontier until its retry budget is exhausted.

## Readiness instead of routine gates

Routine progression is computed continuously:

    python3 scripts/lattice.py readiness --project <project-id>

When every condition in the active milestone is satisfied or waived, and no blocking exception or commitment remains, Assurance receives a derived advancement action. Assurance claims it and advances the milestone. The event log records the transition; no separate gate-decision document is created.

Production launch remains a Principal decision after technical readiness. A milestone acceptance never implies external publication or distribution.

## Truth ledger

World-state propositions belong in the truth ledger, not in transient prompts or discarded notes. Every truth has:

- an immutable version history;
- an epistemic state: `observed`, `accepted`, `contested`, `false`, `superseded`, or `unknown`;
- an attention state: `frontier`, `background`, or `archived`;
- optional confidence, source, and material-consequence flag; and
- typed relationships to other truths and readiness conditions.

Moving a truth from frontier to background changes attention, not history or truth status. Background truths stay out of ordinary context unless a current condition explicitly links them. A new material dependency or contradiction brings them back to the frontier. Contradictions are preserved and marked contested; an agent must never silently overwrite the earlier proposition.

Use the guarded commands:

    python3 scripts/lattice.py truth-add ...
    python3 scripts/lattice.py truth-revise ...
    python3 scripts/lattice.py truth-move ...
    python3 scripts/lattice.py truth-link ...
    python3 scripts/lattice.py truth-list --project <project-id> [--attention background]

An accepted milestone automatically moves settled truths to background only when no active or planned condition still references them and no contradiction remains open. Every movement is retained in `truth_transitions`.

## Durable state and documents

Persist only what must survive:

- objectives, conditions, decisions, constraints, artifact identities, truth versions, evidence, exceptions, commitments, and events belong in guarded state;
- source code, contracts, ADRs, human-facing product specifications, and release artifacts remain repository files;
- execution briefs, action leases, agent plans, review assignments, and remediation candidates are derived or ephemeral.

Do not write routine handoff, status, verification, change-request, QA-cycle, or gate-decision documents. The runtime already retains the substantive result and its evidence. Generate a human-readable report only when a human needs one.

No agent edits `state/current.json` or `.lattice/state.db` directly. Every durable mutation must pass through `scripts/lattice.py`, which enforces project isolation, role constraints, state versions, WIP limits, review separation, and retry budgets.

## Commitments and exceptions

Ordinary agents cannot create durable commitments. The Director or Principal may create one only for an owned deadline, cross-role obligation, external dependency, or other promise that must survive the current execution episode.

Any role may raise a deduplicated exception when progress is genuinely blocked. Exhausting a condition's retry budget creates one exception automatically rather than a pile of remediation tasks. An exception can interrupt the Principal only when it matches an exact predicate in `agency.yaml`.

## Project and role isolation

- Every action and state entity belongs to one project ID.
- A specialist is a leaf worker for one role and one leased action.
- Read and write only the paths owned by that role in `agency.yaml`.
- Do not borrow facts, evidence, or accepted state from another project.
- Parallel writes require separate leases, frozen inputs, and disjoint paths.
- Agency kernel files are immutable during project delivery.
- Lack of a tool, permission, or test environment is a blocker, not evidence.

## Host adapters

Repository-aware local agents, Codex, and Claude use the guarded CLI directly. ChatGPT Work receives a generated, scoped frontier pack. A hosted agent selects at most one included action and returns exact artifact changes plus one `lattice-state-delta`; the repository applies that delta with a revision guard and regenerates the pack.

Never treat chat memory, an uploaded stale pack, or an agent's narrative as newer than the repository snapshot.

## Principal boundaries

The human Principal owns mandates, cross-project priority and capacity tradeoffs, paid commitments, sensitive-data policy, destructive or irreversible actions, externally consequential actions, material residual-risk acceptance, and production launch. Routine implementation, verification, remediation, readiness, and reversible no-cost choices remain agent-managed inside the confirmed mandate.
