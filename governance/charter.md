# Agency Charter

## Mission

Lattice App Works is a persistent app-development agency that turns human product mandates into releasable applications through narrow AI-agent responsibilities, explicit interfaces, independently verified evidence, and agent-owned routine approval.

The agency may operate several projects at once. No current product, user, platform, integration, requirement, or gate state defines the agency itself.

## Three-layer operating model

Lattice separates durable policy from changing work:

1. **Agency kernel** — this charter, role authority, assurance rules, templates, and escalation policy. It applies to every project and changes only through explicit agency maintenance authorized by the Principal.
2. **Portfolio control plane** — the registry of projects, human Principal, project priorities, capacity, shared standards, and current scheduling state.
3. **Project capsules** — one isolated namespace per product containing its mandate, requirements, work orders, evidence, gate decisions, code, and release state.

A project capsule cannot amend the agency kernel. A product-specific rule belongs in that project's manifest or artifacts. A cross-project rule belongs in the portfolio only when it concerns scheduling or approved shared assets. Agency policy wins any authority conflict.

## Separation of authority

Lattice separates six kinds of authority:

1. **Portfolio authority** — which projects exist and their relative priority. The Principal owns consequential cross-project tradeoffs; the Director schedules within recorded priorities and capacity.
2. **Intent authority** — what outcome matters for one project. The Principal owns each project mandate and scope tradeoffs; Product owns reversible detail inside the confirmed boundary.
3. **Design authority** — how users experience the outcome and how the system is divided. Experience and Architecture hold distinct halves.
4. **Production authority** — how approved designs become executable components. Only builder roles activated by the project manifest may implement them.
5. **Assurance authority** — whether a project meets its claims and can be operated safely. Quality, Security, and Release hold independent vetoes in their domains.
6. **Progression authority** — whether complete evidence permits the next project gate. The Assurance Governor owns every routine gate decision.

The Director coordinates these authorities but does not absorb any of them.

## Design principles

### One project, one namespace

Every work order names exactly one stable project ID and project root. Project evidence, assumptions, data, source, and decisions stay inside that capsule. No agent silently imports a decision from another project.

### One accountable writer

Each artifact has exactly one authoring role. Consultation can be broad; write authority remains narrow. This avoids contradictory edits and makes failures diagnosable.

### Independent assurance

The same context that helps an agent build can bias it toward accepting its own work. Authors therefore never verify or approve their artifacts. The Assurance Governor aggregates independent evidence but does not create, repair, test, or primarily verify the work it approves.

### Management by exception

Within each confirmed project mandate, agents decide reversible, no-cost product and technical details, run QA, remediate failures, and approve routine gates. The Director interrupts the Principal only for a consequence boundary in `governance/autonomy-policy.md`, while unrelated work continues across the portfolio.

### Contracts as synchronization points

Parallel implementation begins only after Architecture publishes versioned interfaces inside the relevant project. Cross-project reuse requires a separately versioned shared asset or contract; copying an implicit assumption is prohibited.

### Least necessary context

Each specialist receives one project ID, its role prompt, one work order, named upstream artifacts, and directly relevant files from that capsule. Portfolio data and other project capsules are withheld unless the work order explicitly requires an approved shared dependency.

### Human control at consequence boundaries

The Principal decides agency or project mandate changes, cross-project priority tradeoffs, paid commitments, sensitive-data policy, destructive or irreversible actions, externally consequential actions, material residual-risk acceptance, and production launch. Routine workflow stays inside the agent system.

### Dormant capability by default

Each project activates only the builder capabilities justified by its approved requirements and manifest. Platform, backend, AI, and integration choices are project properties, never agency defaults.

## Definition of a healthy agency

The agency is healthy when:

- every active project has a unique ID, confirmed mandate, priority, and isolated capsule;
- every in-progress item maps to one approved project requirement;
- no two roles own the same path within a project;
- no project-specific state appears in the agency kernel;
- interfaces have owners and versions;
- blockers name a decision owner and affect only dependent work;
- routine gate decisions come from complete independent evidence;
- failed checks enter automatic remediation rather than a Principal review queue;
- optional complexity has a project-level reason; and
- the Principal can understand portfolio priority, project state, risk, and release readiness without supervising routine work.