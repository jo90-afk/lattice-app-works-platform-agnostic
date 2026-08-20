# Delivery Plan — Lattice 2.0 Continuation

**Plan version:** 2.0  
**Date:** 2026-08-06  
**Owner:** Director  
**Current gate:** Gate 2 — Experience

## Sequence

| Stage | Owner | Evidence | Verification and approval | State |
| --- | --- | --- | --- | --- |
| Bootstrap | Principal / Director record | `work/bootstrap.md` | Principal mandate confirmation | Complete |
| Gate 0 — Intake | Director | `work/intake.md` | Preserved Principal verification | Complete |
| Gate 1 — Intent | Product | Project brief and acceptance map | Experience verified; preserved Principal acceptance | Complete |
| Gate 2 — Experience | Experience | Journeys, state matrix, accessibility | Quality verifies; Product concurs; Assurance approves | Active |
| Gate 3 — Architecture | Architecture | System, ADRs, contracts | Security verifies; affected builders and Quality concur; Assurance approves | Blocked by Gate 2 |
| Gate 4 — Test design | Quality | Strategy, traceability, acceptance specifications | Product verifies; Experience and Security concur; Assurance approves | Blocked by Gate 3 |
| Gate 5 — Implementation | Android | Contract-bound Android slices and unit evidence | Fresh Quality verification; conditional Security review; Assurance approves | Blocked by Gates 3–4 |
| Gate 6 — Convergence | Quality / Security / Release | Functional, risk, and operational evidence | Assurance approves or remediates | Blocked by implementation |
| Gate 7 — Release readiness | Release | Reproducible build and release evidence | Quality verifies; Security concurs; Assurance certifies readiness | Blocked by convergence |
| Launch | Principal | Assurance-accepted readiness packet | Jude authorizes production launch | Blocked by Gate 7 |
| Gate 8 — Learn | Product | Outcome review | Quality verifies; Experience and Release concur; Assurance approves | Post-release |

## Gate 2 work-order plan

| Order | Owner | Output | Dependency | State |
| --- | --- | --- | --- | --- |
| WO-004 | Experience | `design/journeys.md` | Gate 1 accepted | `READY` |
| WO-005 | Experience | `design/state-matrix.md` | WO-004 verified | Planned |
| WO-006 | Experience | `design/accessibility.md` | WO-004 and WO-005 verified | Planned |

The Director creates WO-005 and WO-006 only when their named dependencies are satisfied. Failed evidence enters the bounded remediation loop automatically. Services and Intelligence remain dormant.