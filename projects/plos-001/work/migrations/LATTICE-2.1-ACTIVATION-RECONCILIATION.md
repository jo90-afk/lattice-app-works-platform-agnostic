# Activation Reconciliation — Lattice 2.1 Portfolio

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Date:** 2026-08-06  
**Owner:** Portfolio Director  
**Status:** COMPLETE

## Purpose

Reconcile the uploaded 2.1 project capsule checkpoint with later, project-specific Gate 2 evidence already produced in the same Director run. This record imports evidence without replaying accepted intake, changing the mandate, or treating pre-activation status labels as 2.1 approval.

## Authoritative checkpoint inputs

| Source | SHA-256 | Role |
| --- | --- | --- |
| `Personal_Life_OS_Project_Capsule_plos-001_v2.1.0.md` | `326f2db0bea2538a7b0880869022fcb4f980c1c3d2a8b29ab6eee885ad870761` | Project manifest, accepted state, and original next order |
| `Lattice_Portfolio_Registry_v2.1.0.md` | `9bdfb96730a8e6470a09bb5e76201ad1b3f0a09b9a3a297af1a5c818c03deb4c` | Project identity, priority, and scheduling |
| Lattice App Works Agency Kernel v2.1.0 | `b21fab0a882e7b5fe74ca60655aced62903de502bf99f3e802645b6422925ba0` | Roles, gates, assurance, concurrency, and exceptions; unchanged |

## Preserved accepted state

- Confirmed mandate, verified Gate 0, and accepted Gate 1 remain closed.
- Principal: Jude O'Neill.
- Frozen Product artifacts remain byte-identical:
  - `product/project-brief.md` — `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b`
  - `product/acceptance-map.md` — `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3`
- `ACCEPT GATE 1` remains the controlling gate decision.
- No mandate, priority, data, spending, external-action, residual-risk, or launch decision changed.

## Imported Gate 2 evidence

| Work | Artifact/evidence | SHA-256 | Imported status under 2.1 |
| --- | --- | --- | --- |
| WO-004 | `design/journeys.md` revision 0.1 | `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200` | Owner complete; Quality `SATISFIED`; Product mandatory review pending |
| WO-004 | `work/handoffs/WO-004-experience.md` | `665a4942cdd3adac6f777b05a1a6896f59d6c4799c3d2bab0cf3aa5948d17b70` | Preserved verbatim |
| WO-004 | `work/verifications/WO-004-quality.md` | `996cab972151fab2ad64fd2405e4227a7aa9db2b4698ea2cf739615aac8cfef1` | Preserved verbatim |
| WO-005 | `design/information-architecture.md` revision 0.1 | `fe3c9ceafd4d2f77212698356ec3268b08ca5ab950e316621f430fbeea72e4ae` | Superseded failed evidence; findings F-001/F-002 preserved |
| WO-005-R1 | `design/information-architecture.md` revision 0.2 | `848e767cd60a83c8850bd12efc988430f5b62f530aaf38f07e1877eaa5a04dac` | Owner complete; fresh Quality `SATISFIED`; Product mandatory review pending |
| WO-005-R1 | `work/handoffs/WO-005-R1-experience.md` | `aae0264cf3aeda1649ef686b064d7a0838512dcf5dac555178074168f00efc82` | Preserved verbatim |
| WO-005-R1 | `work/verifications/WO-005-R1-quality.md` | `dca4ced0f958311294fc145a46e45cbfa22b659220d71bfe299ff0f8c62e6f42` | Preserved verbatim |
| WO-006 | `design/state-matrix.md` interrupted draft | `afb0ebe6a8c81e5cf4e9abfc3fca43b1cf73d944145e9bfa18097a40c2733028` | Draft only; no handoff, verification, review, or gate effect |

The original 2.0 work-order records are retained byte-for-byte under `work/legacy-2.0/orders/`. Their former status labels are historical assertions, not substitutes for 2.1 mandatory review or Assurance.

## Reconciliation decisions

1. Do not rerun WO-004 or WO-005 authorship or their completed Quality checks.
2. Route each imported, owner-complete artifact to a fresh Product mandatory-reviewer thread for Gate 1 intent traceability.
3. Route the interrupted state-matrix draft to a fresh Experience author through WO-006-C1; the author may preserve its bytes if complete or make only bounded corrections.
4. Use fresh Quality and Product threads after WO-006-C1 owner completion.
5. Gate 2 remains open. Product concurrence on imported evidence, the remaining Experience artifacts, Quality verification, and a fresh Assurance decision are still required.

No Principal exception predicate was triggered.