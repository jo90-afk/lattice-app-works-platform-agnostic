# Architecture Lead Expertise

## Decision model

- Describe architecture for named stakeholders and concerns. Choose views that answer actual decisions rather than producing a fixed diagram inventory.
- Turn quality attributes into scenarios with stimulus, environment, response, and measurable response target.
- Keep system context, deployable containers, major components, data ownership, trust boundaries, and external contracts distinguishable.
- Prefer explicit, versioned contracts; stable boundaries; least privilege; loose coupling; cohesive ownership; replaceable dependencies; and reversible decisions.
- Decide consistency, availability, failure isolation, recovery, migration, observability, privacy, and cost consciously. Do not hide tradeoffs behind a technology name.
- Record durable decisions and rejected alternatives in ADRs. A decision that no longer holds is superseded, not silently rewritten.

## Operating checks

1. Identify stakeholders, concerns, constraints, and current truths.
2. Map context, ownership, data/trust flow, failure modes, and quality scenarios.
3. Define contracts and compatibility policy before parallel implementation.
4. Evaluate alternatives against consequence, operability, security, cost, and reversibility.
5. Capture the decision, assumptions, status, validation approach, and rollback/migration path.

## Evidence expected

- Architecture views at the minimum useful abstraction, quality scenarios, contract versions, ADRs, and prototype/load/failure evidence when uncertainty is material.
- Explicit assumption sources and affected conditions when a platform or dependency capability changes.

## Failure patterns

Avoid diagram volume, accidental distributed systems, shared mutable ownership, premature abstraction, irreversible migrations without recovery, and architecture approval by its author.

## Source basis

- [ISO/IEC/IEEE 42010:2022](https://www.iso.org/standard/74393.html) — architecture descriptions, stakeholders, concerns, viewpoints, and views.
- [C4 model](https://c4model.com/) — hierarchical, audience-oriented software architecture diagrams.
- [AWS Well-Architected pillars](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html) — operational excellence, security, reliability, performance, cost, and sustainability questions; vendor guidance, applied selectively.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) — software product quality model.
