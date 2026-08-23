# Lattice Roadmap

Lattice is not trying to win the coding-agent runtime race.

Agent runtimes are rapidly standardizing around parallel workers, subagents, reusable skills, lifecycle hooks, isolated workspaces, persistent sessions, and hosted execution. Those capabilities are valuable, but they are increasingly infrastructure supplied by the host.

Lattice's durable advantage is the layer above them: project truth, explicit authority, bounded autonomy, independent verification, exception routing, recovery, and a shared account of what is true now.

The roadmap therefore treats Codex, Copilot, Claude Code, local agents, and future runtimes as replaceable execution hosts. Lattice owns the control plane and state contract.

## Product thesis

A useful autonomous software organization needs more than agents that can do work. It needs a durable answer to five questions:

1. What is true now?
2. What outcome is currently being pursued?
3. What work is actually ready next?
4. Who is allowed to change which part of the system?
5. What evidence is sufficient to accept that change?

The existing 0.0.4 seed already contains the core primitives: active-frontier derivation, durable project records, a truth ledger, leases, independent verification, Assurance gates, isolated project capsules, scoped expertise, and guarded hosted deltas. The next releases turn those primitives into a reliable interoperable control plane.

## What Lattice will not build

The roadmap deliberately avoids duplicating capabilities that execution hosts already provide well.

- No proprietary foundation model or model router as a product requirement.
- No general-purpose coding sandbox merely to reproduce host worktrees or cloud environments.
- No large static backlog generated in advance from a project plan.
- No hidden conversational memory as a source of project truth.
- No role proliferation when a capability can be expressed as policy, expertise, a verifier, or a host adapter.
- No mandatory hosted service for the local-first core.

## 0.0.5 — Interoperable control plane

**Goal:** make the current state machine easy to drive from modern agent hosts without weakening its authority model.

### Host adapter contract

Define a small adapter boundary for execution hosts:

- receive a claimed Lattice action and its bounded context;
- create or attach an isolated execution workspace when the host supports one;
- stream or return lifecycle events;
- submit artifacts, evidence, and a structured completion result;
- never mutate durable Lattice state except through guarded operations.

Ship reference adapters or integration guides for the major host patterns already supported by the seed: repository-aware local agents, Codex, Claude Code, GitHub-hosted agents, and ChatGPT Work projections.

### Standard skills packaging

Convert reusable role expertise into host-neutral skill packages where practical, while keeping authority and state rules in the Agency Kernel. Skills should teach execution technique; they must not become a second policy system.

### Lifecycle hooks

Add deterministic hook points around:

- action claim;
- workspace creation;
- tool or command policy checks where the host exposes them;
- submission;
- verification request;
- verification verdict;
- milestone acceptance;
- exception creation;
- worker failure or timeout.

Hooks produce events and may enforce policy, but may not silently rewrite project truth.

### State observability

Add a human- and machine-readable inspection surface for:

- current project and objective;
- active milestone;
- frontier actions and why they are ready;
- claimed leases and actors;
- pending verification;
- exceptions requiring human attention;
- recently changed truths and records;
- evidence supporting accepted conditions.

The first implementation may remain CLI-first, but it must expose a stable read model that a UI can consume later.

### Recovery hardening

Make interruption an ordinary state transition rather than an exceptional manual repair task:

- expired lease detection;
- safe reclaim rules;
- idempotent submission checks;
- abandoned workspace recording;
- partial-artifact detection;
- deterministic frontier recomputation after recovery.

**Exit criterion:** an agent session can disappear at any point between claim and verification and the project can resume without reconstructing intent from chat history.

## 0.0.6 — Concurrent execution without state ambiguity

**Goal:** support real multi-worker operation while preserving one coherent project state.

### Shared transactional state adapter

Keep `state/current.json` as the portable snapshot contract, but introduce an operational adapter interface and a Postgres reference implementation for installations that require simultaneous remote writers.

SQLite remains the default local runtime.

### Concurrency semantics

Specify and test:

- project revision guards;
- lease ownership and renewal;
- artifact-level write ownership;
- conflicting truth updates;
- simultaneous verification attempts;
- milestone advancement races;
- stale worker rejection;
- serialized acceptance of hosted deltas.

### Workspace isolation

Treat worktrees, branches, containers, or host-native sandboxes as execution details behind a common workspace identity. Persist enough identity to associate every artifact and evidence item with the action that produced it.

### Bounded scheduler

Add a scheduler that derives work from the frontier and recorded portfolio capacity rather than creating a permanent work-order queue. It should:

- honor portfolio priority;
- respect project and role concurrency limits;
- avoid assigning mutually conflicting actions together;
- continue unrelated projects when one project is blocked;
- surface exceptions instead of repeatedly retrying consequential failures.

**Exit criterion:** multiple workers can operate across multiple projects concurrently without relying on social conventions to avoid collisions.

## 0.0.7 — Human control surface

**Goal:** make management by exception visible enough that a person can supervise the agency without reading its files.

Build a local-first control surface over the stable read model from 0.0.5.

### Portfolio view

Show:

- active projects in portfolio order;
- current objective and milestone for each;
- worker and verification activity;
- blocked conditions;
- exceptions needing the Principal;
- recent accepted changes.

### Project view

Show the project as a consequence graph rather than a document tree:

- durable truths and their attention state;
- records and decisions;
- conditions that define readiness;
- evidence attached to claims;
- actions currently derived from unmet conditions;
- completed and superseded state transitions.

### Human decision inbox

Provide one place for decisions that actually cross the human boundary. Every request must show:

- the exact decision required;
- why the agency cannot decide it under current authority;
- affected projects and state;
- available evidence;
- consequences of each supported choice.

### Operational telemetry

Track enough runtime information to improve the system without turning traces into project truth:

- action duration;
- retries and recoveries;
- verification failure rate;
- exception frequency;
- host/model used when available;
- token or execution cost when hosts expose it;
- frontier churn and blocked time.

**Exit criterion:** a Principal can understand what the agency is doing, what changed, and where intervention is required from the control surface alone.

## 0.0.8 — Evidence that autonomy works

**Status: complete.** The fail-closed CI evidence gate executes all ten registered roadmap scenarios, including the live multi-connection Postgres conflict case, before the ordinary regression suite. The aggregate currently demonstrates zero failed scenarios, zero false acceptances, zero state-divergence incidents, zero unnecessary escalations, successful worker-loss recovery, and successful seeded-defect verification catch behavior under the bounded evaluation suite.

**Goal:** move from plausible architecture to demonstrated operational reliability.

### Evaluation harness

Create repeatable scenarios for:

- greenfield feature delivery;
- refactoring across components;
- migration work;
- test and CI remediation;
- ambiguous requirements requiring escalation;
- contradictory new information;
- worker crash and lease expiry;
- verifier disagreement;
- concurrent artifact conflict;
- multi-project capacity contention.

### Autonomy metrics

Measure outcomes that correspond to the product thesis:

- percentage of routine transitions completed without Principal intervention;
- false acceptance rate;
- unnecessary escalation rate;
- recovery success after worker loss;
- state divergence incidents;
- verification catch rate;
- time spent blocked for missing information;
- context volume per accepted change.

### Portability matrix

Run the same bounded scenarios through multiple supported hosts. Host-specific features may improve execution, but the resulting Lattice state and acceptance semantics must remain equivalent.

The evaluation contract and host-neutral fingerprints are implemented. Cross-host equivalence is measured when the same scenario is run through more than one host; broader external-host matrix expansion remains ongoing evidence work rather than a blocker to the 0.0.8 control-plane reliability exit criterion.

### Adversarial state tests

Stress the control plane with stale deltas, contradictory truths, duplicated submissions, malicious or malformed evidence references, reordered events, and partial writes.

**Exit criterion: satisfied.** Reproducible executable scenarios now exercise recovery, invalidation, independent verification, bounded remediation, portfolio contention, stale shared-writer rejection, and acceptance. CI fails closed if any scenario reports a failed outcome.

## 0.1.0 — Public beta

**Goal:** make Lattice installable and understandable by someone who did not design it.

### Setup

- one documented bootstrap path from clone to first verified action;
- environment preflight and `doctor` command;
- migration tooling with rollback guidance;
- neutral starter project and sample state transitions;
- clear private/public repository guidance;
- reproducible local initialization on macOS, Windows, and Linux where the Python runtime is supported.

### Packaging

- stable snapshot and delta schema for the 0.1 line;
- documented adapter interface;
- host integration packages where ecosystem conventions justify them;
- standard skill packaging for reusable expertise;
- machine-readable version and capability negotiation.

### Documentation

Organize public documentation around the operating model rather than the repository tree:

1. install Lattice;
2. define a project mandate;
3. encode current truth and an objective;
4. derive and claim work;
5. submit evidence;
6. verify independently;
7. accept or escalate;
8. recover from interruption;
9. add another host or project.

### Public claims at 0.1.0

Lattice may claim that it provides a local-first, host-agnostic control plane for durable project state, frontier-derived work, bounded authority, independent verification, and exception-based human supervision.

It should still avoid claiming universal provider independence, production-grade consequential autonomy, or compatibility with every agent host until the portability and evaluation evidence supports those statements.

## After 0.1

Post-beta work should follow demonstrated bottlenecks rather than a predetermined feature ladder. Likely directions include:

- event-driven triggers from issue trackers, CI, monitoring, and deployment systems;
- richer policy-as-code around tools, environments, and release authority;
- optional remote coordinator service for distributed teams;
- pluggable artifact and evidence stores;
- cross-project truths and dependencies with explicit ownership boundaries;
- stronger provenance and signed acceptance records;
- organization-level policy overlays;
- a plugin ecosystem for hosts, expertise packs, verifiers, and external systems.

A hosted Lattice service is optional. The durable project contract should remain usable without one.

## Release discipline

Every release must preserve four invariants:

1. **State beats memory.** If a fact is important to future work, it must be represented in durable project state.
2. **Ready work is derived.** The frontier is computed from current objectives, conditions, truth, ownership, and evidence; it is not a document backlog that grows forever.
3. **Authority is explicit.** Completing work, verifying work, and accepting work are distinct events owned by distinct roles or policies.
4. **Hosts are replaceable.** A better agent runtime should make Lattice more capable, not obsolete its project model.

The success condition for this roadmap is not a larger autonomous-agent framework. It is a smaller, harder control plane that lets increasingly capable agents operate for longer periods without losing project truth, crossing human authority boundaries, or forcing a person to reconstruct what happened from conversation logs.
