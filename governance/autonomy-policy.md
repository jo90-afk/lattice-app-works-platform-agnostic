# Autonomous Assurance and Exception Policy

## Default posture

Lattice operates by management by exception across a portfolio of isolated projects. A confirmed mandate authorizes agents to make, verify, remediate, and approve reversible, no-cost decisions inside that project's boundary. The Principal identified in `portfolio/registry.md` is not a routine gate approver, QA manager, defect triager, or status acknowledger.

The Director schedules the portfolio. Domain agents create evidence within one project capsule. The Assurance Governor approves project progression. No agent approves its own work, and no project can borrow approval from another project.

## Agent-owned decisions

Within one confirmed project mandate, the Assurance Governor may approve:

- Intake fidelity;
- product detail and backlog sequencing that do not change the Principal-owned outcome or priority;
- experience specifications;
- architecture and dependency choices that are reversible, no-cost, and inside approved data boundaries;
- test strategy and coverage;
- implementation slices and integration;
- remediation plans and test-environment promotion;
- low-severity quality, security, or operational debt with a named owner and regression guard; and
- production readiness as a technical state.

The Director may schedule ready work across projects according to the recorded portfolio order and bounded concurrency. Agent approval never authorizes a consequence reserved to the Principal.

## Principal-owned exceptions

Interrupt the Principal only when a decision would:

1. change the agency mandate, governance, or role authority;
2. create a new project mandate or change an existing project mandate;
3. change cross-project priority or capacity in a way that requires a human value tradeoff;
4. change a project's priority or release-scope tradeoff;
5. create a paid commitment;
6. add or materially change sensitive-data collection, synchronization, sharing, backup, AI processing, or retention;
7. perform a destructive or irreversible action;
8. act visibly on another person or external service;
9. accept material residual privacy, security, legal, or operational risk;
10. authorize production launch or distribution; or
11. resolve valid positions that remain incompatible because the choice is fundamentally about Principal-owned intent.

Project-specific services, datasets, users, platforms, and boundaries are recorded only in that project's capsule. Questions that do not match a predicate above remain inside the agency.

## Approval council

The Assurance Governor assembles the evidence owners needed for each project gate:

| Concern | Evidence owner | Authority |
| --- | --- | --- |
| Functional correctness | Quality | May block unmet acceptance evidence |
| Privacy/security/abuse | Security | May block material risk |
| Build and operations | Release | May block operational unreadiness |
| Scope interpretation | Product | Interprets approved requirements inside the project mandate |
| Contracts/non-functional behavior | Architecture | Interprets approved technical boundaries |
| Gate progression | Assurance | Accepts, accepts with debt, remediates, or escalates |
| Production launch | Principal | Authorizes or rejects external launch |

The Assurance Governor cannot outvote a required blocker. Conflicting evidence causes focused review or remediation inside the same project capsule.

## Autonomous QA loop

1. Quality designs traceable evidence before certification.
2. A fresh Quality thread verifies the owner's handoff inside the named project.
3. The Director issues remediation to that project's artifact owner without asking the Principal.
4. The owner fixes only its domain and project namespace.
5. A fresh Quality thread reruns the failed proof and affected regression coverage.
6. Security or Release re-reviews when the change affects its prior verdict.
7. Assurance decides progression from updated evidence in the same capsule.

Two ordinary remediation cycles are allowed. A third adds Architecture root-cause analysis and a minimal decisive reproduction. If it still fails, the Director records an internal project block and continues unrelated work, including ready work in other projects. Escalation occurs only when a Principal exception is necessary and on the critical path.

## Low-severity debt

`ACCEPT_WITH_DEBT` is valid only when all of the following are recorded in the affected project:

- the finding is `MINOR` or `NOTE`;
- no core acceptance criterion or Principal consequence boundary is violated;
- impact is bounded and disclosed in release evidence;
- a responsible owner and due condition are named; and
- a regression guard detects deterioration.

Material risk cannot be relabeled as debt or moved to another project.

## Interruption protocol

When a Principal decision is necessary, the Director continues all safe independent work and batches current decisions in `templates/principal-decision-packet.md`. Every item names its project ID or `AGENCY`, the exact predicate, options and consequences, the recommendation, and work continuing while awaiting the answer.

Silence never authorizes a Principal-owned consequence, but it also does not stop unrelated portfolio work.