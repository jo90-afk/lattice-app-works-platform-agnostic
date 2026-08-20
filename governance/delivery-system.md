# Active-Frontier Delivery System

## 1. Establish durable intent

The Principal confirms a project mandate. The Director registers the project, Product records one active objective, and authorized roles define the smallest set of conditions that would make the current milestone true. Conditions describe desired, verifiable states rather than implementation tasks.

## 2. Derive the frontier

The runtime exposes only conditions whose dependencies are satisfied, pending submissions needing independent review, ready milestones needing Assurance acceptance, unresolved exceptions, and real commitments. It ranks them by portfolio priority, severity, readiness, and age, then applies project and role WIP limits.

No candidate action is written to a backlog. Recomputing state can make an action appear or disappear without cleanup.

## 3. Lease and execute

An agent claims one action for a bounded period. The runtime compiles the smallest useful context from linked records, truths, dependencies, relevant artifact references, and recent failed attempts. The agent may edit only its owned paths.

A successful owner submission records changed artifact references and evidence, then removes the owner action. Review actions are derived from the submission. A failed attempt returns the condition to the frontier under a new state version.

## 4. Verify independently

The primary verifier and any mandatory reviewers act from fresh contexts. Their verdicts are stored as structured review evidence. All required positive verdicts satisfy a condition. A negative verdict rejects the submission and returns the condition to remediation.

The default retry budget is three. Exhaustion blocks the condition and creates one deduplicated exception. It does not generate another layer of remediation tasks.

## 5. Advance from predicates

Milestone readiness is true when it has at least one condition, every condition is satisfied or explicitly waived, and no blocking exception or commitment remains. Assurance claims the derived advancement action and records the milestone transition. A planned successor milestone activates automatically; otherwise the objective closes.

Production launch still requires the Principal because external distribution crosses a retained consequence boundary.

## 6. Maintain world state

Requirements and truth revisions invalidate only linked active conditions. Dependency invalidation propagates downstream. A truth can move from frontier attention to background attention after its work becomes settled; its statement, source, confidence, prior status, links, and movement history remain queryable.

When a background truth becomes relevant to an active condition, the runtime promotes it. A contradiction promotes both propositions and marks them contested. False or superseded propositions remain in history rather than disappearing.

## 7. Export across hosts

Local runtimes use SQLite and update `state/current.json` after each durable mutation. Git carries the snapshot and project artifacts. ChatGPT Work receives a scoped projection containing at most a few current actions and directly referenced sources, then returns a revision-guarded delta for reconciliation.
