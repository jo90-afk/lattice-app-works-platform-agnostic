# Delivery System

Every gate belongs to one project capsule. In this document, paths such as `work/`, `product/`, and `design/` are relative to `projects/<project_id>/`. A gate decision, review, or accepted artifact from one project has no authority in another.

Portfolio scheduling is orthogonal to project gates: the Director may advance several projects within the concurrency limit, but each project's evidence and progression remain independent.

## Bootstrap — one-time Principal mandate

Before domain work begins, the human Principal issues or confirms `templates/bootstrap-mandate.md`. The Director records it as `projects/<project_id>/work/bootstrap.md`. This is a one-time authorization for that project and is repeated only when its mandate would change.

A previously confirmed bootstrap remains valid after upgrading Lattice. Do not ask the Principal to reconfirm Gate 0 merely because the agency runtime or approval model changed.

The mandate authorizes agents to decide reversible, no-cost detail inside its scope. It does not authorize the Director to create a domain artifact or any agent to cross a Principal consequence boundary.

## Gate 0 — Intake

**Author:** Director  
**Verifier:** Product Lead  
**Approver:** Assurance Governor  
**Output:** `work/intake.md`

**Exit condition:** the requested outcome, known constraints, open decisions, environment boundaries, and Principal are faithfully traced to the confirmed mandate. Any genuine Principal-owned exception is isolated in a decision packet; it does not block unrelated intake work.

Product verifies traceability, not whether it personally agrees with the mandate. Assurance accepts Intake without asking the Principal when it is inside the confirmed mandate.

## Gate 1 — Intent

**Author:** Product Lead  
**Verifier:** Experience Lead  
**Mandatory reviewer:** Quality, for acceptance testability  
**Approver:** Assurance Governor

Required evidence:

- a versioned project brief;
- target users and jobs to be done;
- explicit goals and non-goals;
- smallest coherent release boundary;
- measurable outcome signals;
- requirement-to-acceptance mapping; and
- data and external-action assumptions classified against the exception policy.

Experience verifies that requirements are understandable as user behavior. Quality verifies that each claim can be observed. Assurance approves intent detail that remains inside the confirmed mandate. A mandate, priority, or release-scope tradeoff goes to the Principal as one narrow decision.

## Gate 2 — Experience

**Author:** Experience Lead  
**Verifier:** Quality Engineer  
**Mandatory reviewer:** Product, for intent traceability  
**Approver:** Assurance Governor

Required evidence:

- end-to-end journeys;
- information architecture;
- screen and component states, including empty, loading, offline, error, permission-denied, and destructive-confirmation states;
- content and notification behavior;
- accessibility requirements; and
- traceability to accepted criteria.

Quality verifies observability and testability. Product verifies scope fidelity. Assurance approves the gate from those independent records.

## Gate 3 — Architecture and contracts

**Author:** Systems Architect  
**Verifier:** Security  
**Mandatory reviewers:** Every affected builder for feasibility; Quality for verifiability  
**Approver:** Assurance Governor

Required evidence:

- system context and component boundaries;
- data classification and lifecycle;
- versioned API, event, storage, and model contracts;
- ADRs for consequential choices;
- failure, offline, migration, and rollback behavior;
- threat-model input; and
- a thin vertical-slice plan.

Builders review feasibility without rewriting contracts. Security owns the design-risk verification. Quality confirms that non-functional claims can be proven. Assurance approves reversible, no-cost architecture inside accepted data boundaries. A new paid dependency, data-policy change, destructive migration, or material residual risk creates a Principal decision packet.

Parallel production work begins only after Security returns `SATISFIED`, all affected builders return `CONCUR`, Quality concurs on verifiability, Assurance returns `ACCEPT` or valid `ACCEPT_WITH_DEBT`, and contract versions are frozen.

## Gate 4 — Test design

**Author:** Quality Engineer  
**Verifier:** Product Lead, for requirement coverage  
**Mandatory reviewers:** Experience for state coverage; Security for risk coverage  
**Approver:** Assurance Governor

Acceptance and end-to-end tests are designed from accepted behavior before implementation is certified. Builders own component unit tests; Quality owns cross-component and user-level evidence.

Because Quality authors the test design, Quality cannot approve this gate. Product, Experience, and Security independently review coverage; Assurance aggregates their evidence and approves progression.

## Gate 5 — Parallel implementation

**Authors:** Activated builders only  
**Primary verifier:** Quality Engineer  
**Mandatory reviewer:** Security when the change affects data, permissions, dependencies, migration, external actions, AI tooling, or a prior security claim  
**Approver:** Assurance Governor

The Director issues separate work orders only to builder roles activated by the project manifest. Each work order references the same frozen contract version and has a disjoint project-owned output path.

Rules:

- builders do not edit shared contracts;
- an interface mismatch produces a change request;
- builders provide owner-side tests and a handoff;
- integration happens through contracts, never through unrecorded assumptions;
- Quality verifies each slice with a fresh thread; and
- Assurance accepts the slice or sends it into automatic remediation.

## Gate 6 — Convergence

**Functional verdict:** Quality Engineer  
**Risk verdict:** Security & Privacy Reviewer  
**Operational evidence:** Release Engineer  
**Approver:** Assurance Governor

Quality runs acceptance, end-to-end, regression, accessibility-behavior, and relevant performance checks. Security performs risk-based design and implementation review. Release verifies the integrated build and environment. Reviewers do not patch the code they certify.

Severity policy:

- `BLOCKER`: unsafe, data-loss, security-critical, or core acceptance failure; progression prohibited.
- `MAJOR`: important requirement or reliability failure; automatic remediation required. Product may narrow scope only inside the confirmed mandate, followed by full re-verification.
- `MINOR`: bounded defect with documented impact; Assurance may accept it as debt only under `governance/autonomy-policy.md`.
- `NOTE`: improvement with no current acceptance impact; may become tracked debt.

### Automatic remediation

1. Quality or another required reviewer returns reproducible evidence.
2. The Director records it and issues a remediation work order to the artifact owner.
3. The owner fixes only its domain.
4. A fresh verifier thread reruns the smallest decisive proof plus affected regression coverage.
5. Security or Release re-reviews if the fix affects its earlier verdict.
6. Assurance reassesses the gate.

Two ordinary cycles are automatic. A third cycle adds Architecture root-cause review and a minimal decisive reproduction. If the third cycle fails, record an internal block, continue unblocked work, and interrupt the Principal only when the remaining choice matches an exception predicate and is critical to progress.

## Gate 7 — Release Readiness

**Author:** Release Engineer  
**Verifier:** Quality  
**Mandatory reviewer:** Security  
**Approver:** Assurance Governor  
**Production launch authorizer:** Principal

Release evidence includes a reproducible build, signed-artifact procedure without exposed secrets, version and migration plan, rollback or recovery plan, monitoring and crash visibility, data export/deletion behavior where applicable, known limitations, and final gate verdicts.

Quality must return `SATISFIED` and Security must return `CONCUR`. Assurance then returns `ACCEPT`, `ACCEPT_WITH_DEBT`, `REMEDIATE`, or `ESCALATE` for technical release readiness. Only after Assurance accepts readiness does the Director send the Principal one launch packet. The Principal authorizes the external launch; the Principal does not redo QA or review every gate.

## Gate 8 — Learn

**Author:** Product Lead  
**Verifier:** Quality  
**Mandatory reviewers:** Experience and Release  
**Approver:** Assurance Governor

Product defines outcome review; Release supplies operational signals; Quality supplies defect signals; Experience supplies usability findings. Assurance may approve backlog and product-detail adjustments inside the existing mandate. A proposed mandate, priority, paid-service, data-policy, external-action, or material-risk change follows the exception policy.

## Change-control path

1. The discovering agent returns a proposed change request using `templates/change-request.md`; the Director records it verbatim in `work/change-requests/` and assigns its identifier.
2. The current artifact owner assesses impact and recommends the smallest change.
3. The domain owner decides changes inside the confirmed mandate. Assurance verifies that decision authority and downstream evidence are complete.
4. If the change matches a Principal exception, the Director creates a batched decision packet. Unrelated work continues.
5. If accepted, the artifact owner publishes a new version and identifies invalidated downstream work.
6. The Director cancels, pauses, or reissues affected work orders and commissions fresh verification.

Domain disagreement receives one focused re-review and, if necessary, Architecture or Product adjudication inside their authority. The Principal is not an internal tie-breaker unless the unresolved choice is fundamentally about Principal-owned intent.