# Delivery Plan — Portfolio-Scoped Gate 2 Continuation

**Plan version:** 2.1.1  
**Date:** 2026-08-06  
**Owner:** Portfolio Director  
**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Current gate:** Gate 2 — Experience

## Preserved stage state

| Stage | State | Controlling evidence |
| --- | --- | --- |
| Bootstrap | `CONFIRMED` | `work/bootstrap.md` |
| Gate 0 — Intake | `VERIFIED` | `work/intake.md`, Principal verification |
| Gate 1 — Intent | `ACCEPTED` | Frozen Product hashes and `work/gate-decisions/GATE-1-accepted.md` |
| 2.1 capsule isolation | `COMPLETE` | `work/migrations/LATTICE-2.1-PORTFOLIO.md` |
| Activation reconciliation | `COMPLETE` | `work/migrations/LATTICE-2.1-ACTIVATION-RECONCILIATION.md` |

No completed intake, accepted gate, or Principal decision is reopened.

## Gate 2 dependency order

| Order | Work | Owner / reviewer | Output or record | Dependency | State |
| ---: | --- | --- | --- | --- | --- |
| 1 | WO-004 author + Quality | Experience / Quality | `design/journeys.md`; handoff; verification | Gate 1 | Imported complete evidence |
| 2 | WO-004-PR | Fresh Product reviewer | `work/reviews/WO-004-product.md` | Imported WO-004 evidence | `BLOCK`; closed by verified WO-004-R1 |
| 3 | WO-005 + WO-005-R1 author + Quality | Experience / Quality | `design/information-architecture.md`; remediation evidence | WO-004 | Imported complete evidence |
| 4 | WO-005-R1-PR | Fresh Product reviewer | `work/reviews/WO-005-R1-product.md` | Imported WO-005-R1 evidence | Preserved `CONCUR`; later invalidated by upstream revision |
| 5 | WO-004-R1 | Fresh Experience / Quality / Product | Journeys revision 0.2, verification, concurrence | Product F-01 | Complete — `VERIFIED` |
| 6 | WO-005-R2 | Fresh Experience / Quality | IA revision 0.3 and verification | WO-004-R1 | Quality `BLOCK` on F-003 only |
| 7 | WO-005-R3 | Fresh Experience author | IA revision 0.4 | F-003 | Complete — owner revision 0.4 |
| 8 | WO-005-R3-Q / PR | Fresh Quality / Product | Retest and concurrence | WO-005-R3 owner complete | Complete — `PASS` / `CONCUR` |
| 9 | WO-006-C1 + R1 | Fresh Experience author | Complete and remediate `design/state-matrix.md` | WO-005-R3 verified/concurred | Complete — revision 0.3 |
| 10 | WO-006-R1-Q / PR | Fresh Quality / Product | State-matrix verification and concurrence | WO-006-R1 owner complete | Complete — `PASS` / `CONCUR` |
| 11 | WO-007 + WO-007-R1 | Fresh Experience author | Complete `design/content.md` | WO-006 verified and concurred | Monolithic owner blocked/failed operationally; no source conflict |
| 11a | WO-007-R1A/R1B/R1C | Three fresh Experience authors; fresh Quality each | Disjoint coverage, core/consequence, and notification/boundary support specifications | WO-007-R1 unchanged candidate | `READY` in parallel |
| 11b | WO-007-R1D | Fresh Experience consolidator | `design/content.md` revision 0.2 | R1A/R1B/R1C independently verified | Planned |
| 11-ops | WO-007-OPS-RCA | Fresh Architecture / Quality | Third-cycle root cause and decisive write reproduction | Repeated zero-write Experience sessions | `BLOCKED` in current runtime before artifact; reissue after fresh session allocation |
| 12 | WO-007-Q / PR | Fresh Quality / Product | Verification and concurrence | WO-007 owner complete | Planned |
| 13 | WO-008 | Fresh Experience author | `design/accessibility.md` | WO-007 verified and concurred | Planned |
| 14 | WO-008-Q / PR | Fresh Quality / Product | Verification and concurrence | WO-008 owner complete | Planned |
| 15 | GATE-2-A | Fresh Assurance Governor | Gate decision record | Complete Gate 2 evidence; all primary verifications `SATISFIED`; all mandatory reviews `CONCUR` | Planned |

Routine findings enter the bounded owner-remediation and fresh-retest loop. A blocked order does not block an unrelated project; no other active project is currently registered.

## Later gates

| Gate | Owner | Activation condition |
| --- | --- | --- |
| Gate 3 — Architecture | Systems Architect | Gate 2 `ACCEPT` or `ACCEPT_WITH_DEBT` |
| Gate 4 — Test design | Quality Engineer | Gate 3 accepted, contracts and risk posture sufficiently frozen |
| Gate 5 — Implementation | Android Engineer | Gates 3–4 accepted; exact slice order ready |
| Gate 6 — Convergence | Quality / Security / Release | Integrated implementation evidence complete |
| Gate 7 — Release readiness | Release Engineer | Gate 6 accepted; reproducible environment evidence complete |
| Production launch | Principal | Gate 7 Assurance packet accepted; explicit Principal launch decision |
| Gate 8 — Learn | Product Lead | Release and observation evidence available |

Services and Intelligence remain dormant. Android, Architecture, Security, Release, and implementation work remain inactive until their dependencies are accepted.

## Concurrency and isolation

- Portfolio limit: three concurrent specialist threads.
- Current allocation before WO-007-R1 delegation: no specialist thread active.
- Every delegation names one project ID/root and supplies only its role brief, ready order, frozen inputs, and directly relevant paths.
- Read-only reviews may overlap; writes overlap only when paths are disjoint and inputs are frozen.

## Principal exceptions

The Director interrupts Jude only for the exact `agency.yaml` exception predicates. Routine review, remediation, gate approval, reversible no-cost detail, and test promotion remain agent-managed. No exception is pending.