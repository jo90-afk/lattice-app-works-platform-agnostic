# Dependency-Ordered Delivery Plan — Personal Life OS for Android

**Plan version:** 1.5  
**Owner:** Director  
**Date:** 2026-08-05  
**Current gate:** Gate 1 — Intent  
**Current state:** Gate 1 evidence verified; awaiting Principal `ACCEPT` or `REJECT`

## Activation rule

This plan sequences future work; it does not approve product scope or activate a specialist. A work item becomes actionable only after the Director creates a complete `READY` work order with resolved dependencies and consequence boundaries. The Director must then explicitly delegate that order to a fresh matching specialist subagent.

Every specialist will receive only:

- the matching `agents/*.md` role brief;
- one ready work order;
- named, versioned inputs;
- directly relevant sources and paths; and
- an instruction that it is a leaf agent and may not switch roles or spawn agents.

Independent verification always uses a fresh thread. Returned handoffs, verifications, mandatory reviews, and gate decisions are recorded verbatim.

## Dependency sequence

| Sequence | Gate or stage | Planned owner | Planned evidence | Verification and approval | Activation condition |
| --- | --- | --- | --- | --- | --- |
| 0 | Bootstrap | Director | `work/bootstrap.md` v1.0 | Principal mandate confirmation received | Complete |
| 1 | Gate 0 — Intake | Director | `work/intake.md` v1.0 | Principal confirmed faithful intake on 2026-08-05 | Complete — `VERIFIED` |
| 2 | Gate 1 discovery | Product Lead | `product/discovery.md` revision 0.1 | Principal selected D-01 A through D-07 A and returned `SATISFIED` on 2026-08-05 | Complete — WO-001 `VERIFIED` |
| 3 | Gate 1 — Intent | Product Lead | `product/project-brief.md` v0.1 | Fresh Experience Lead returned `SATISFIED` on 2026-08-05 | Complete — WO-002 `VERIFIED` |
| 4 | Gate 1 — Intent | Product Lead | `product/acceptance-map.md` v0.1 | Fresh Experience Lead returned `SATISFIED` on 2026-08-06; Principal decision required | Evidence complete — WO-003 `VERIFIED`; Gate 1 awaiting approval |
| 5 | Gate 2 — Experience | Experience Lead | `design/journeys.md` | Fresh Quality Engineer verifies observable, testable behavior | Gate 1 accepted |
| 6 | Gate 2 — Experience | Experience Lead | `design/state-matrix.md` | Fresh Quality Engineer verifies state coverage | Journeys are versioned |
| 7 | Gate 2 — Experience | Experience Lead | `design/accessibility.md` | Fresh Quality Engineer verifies testability; Product Lead approves Gate 2 after all evidence | Journeys and states are versioned |
| 8 | Gate 3 — Architecture | Systems Architect | `architecture/system.md`, consequential ADRs, and identified versioned contracts through separate work orders | Fresh Security reviewer verifies design risk; Android reviews feasibility; Principal decides only material tradeoffs | Gate 2 accepted |
| 9 | Gate 4 — Test design | Quality Engineer | `quality/test-strategy.md`, `quality/traceability.md`, and acceptance-test specifications through separate work orders | Fresh Product Lead verifies requirement coverage; Security reviews risk coverage | Gate 3 verified, material decisions resolved, contracts frozen |
| 10 | Gate 5 — Implementation | Android Engineer | Thin vertical slice and Android unit evidence through disjoint, contract-bound work orders | Fresh Quality Engineer verifies each order; risk-based Security review | Gates 3 and 4 verified; relevant intent and design versions frozen |
| 11 | Optional Gate 5 components | Services or Intelligence Engineer | Only artifacts justified by newly accepted requirements | Quality verification and applicable Security review | Dormant unless change control and Principal approval activate the role |
| 12 | Gate 6 — Convergence | Quality, Security, and Release in their separate roles | Functional verdict, risk verdict, and operational evidence | All blocking findings resolved through new owner work orders | Implementation evidence complete |
| 13 | Gate 7 — Release | Release Engineer | Reproducible release packet and environment-promotion evidence | Fresh Quality verification, Security concurrence, then Principal launch decision | Gate 6 clear |
| 14 | Gate 8 — Learn | Product Lead coordinates domain signals | Outcome review and proposed changes | Any changed scope re-enters Gate 1 | Release and observation evidence available |

## Planned work-order decomposition

The identifiers below reserve sequence only. They are not ready work orders and must not be delegated yet.

| Planned ID | Owner | Single intended result | Dependency |
| --- | --- | --- | --- |
| WO-001 | Product Lead | Capture Principal decisions and ranked jobs in `product/discovery.md` | `VERIFIED` 2026-08-05 |
| WO-002 | Product Lead | Publish `product/project-brief.md` | `VERIFIED` 2026-08-05 |
| WO-003 | Product Lead | Publish `product/acceptance-map.md` | `VERIFIED` 2026-08-06; Gate 1 Principal decision pending |
| WO-004 | Experience Lead | Publish `design/journeys.md` | Gate 1 accepted |
| WO-005 | Experience Lead | Publish `design/state-matrix.md` | WO-004 verified |
| WO-006 | Experience Lead | Publish `design/accessibility.md` | WO-004 and WO-005 verified |
| WO-007+ | Systems Architect | One architecture, ADR, or contract artifact per ready order | Gate 2 accepted; exact set determined from approved intent and design |
| Later orders | Quality, Android, Release | One independently verifiable artifact or implementation slice per order | Their applicable upstream gates |

## Environment controls

### Development

- Broad, reversible Director coordination decisions are permitted.
- Only synthetic or non-sensitive data may be used before the applicable personal-data controls are approved.
- No real-world external effect, paid commitment, destructive action, or specialist-role substitution is permitted.

### Test

- Test work uses frozen, versioned inputs and approved fixtures.
- Promotion from development requires the relevant owner handoff and independent verification.
- A test environment is not treated as approval for production data or external integrations.

### Production

- No production promotion or launch occurs without Gate 7 evidence and the Principal’s explicit decision.
- Production data, integrations, and recovery behavior must match approved requirements, contracts, and security findings.

## Parallelism boundary

- Read-only independent reviews may run in parallel.
- Writes may run in parallel only when inputs are frozen and `agency.yaml` assigns disjoint paths.
- Services and Intelligence remain dormant.
- No implementation agent is active.

## Current next safe action

Jude O’Neill reviews the frozen Gate 1 decision packet and returns `ACCEPT GATE 1` or `REJECT GATE 1` with corrections. Gate 2 work orders remain blocked until an `ACCEPT` decision is recorded. No implementation specialist is active.

## Principal delegation in effect

`work/authority-delegations/AD-001.md` v1.0 authorizes minor, reversible development-process approvals by the Director. It does not alter domain ownership, assurance rules, or any retained Principal consequence boundary.