# Verification Record: WO-003 — Experience Lead

**Record type:** PRIMARY VERIFICATION  
**Reviewer role:** Experience Lead — fresh independent verifier  
**Date:** 2026-08-06  
**Input handoff:** `work/handoffs/WO-003-product.md`  
**Frozen artifact:** `product/acceptance-map.md` v0.1

## Assigned question

Does `product/acceptance-map.md` give every frozen release-one requirement complete, unambiguous, user-observable acceptance coverage that Experience can design from without guessing or inheriting technical prescriptions?

## Evidence reproduced

| Inspection | Expected | Actual |
| --- | --- | --- |
| `product/acceptance-map.md` SHA-256 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | Exact match |
| `product/project-brief.md` SHA-256 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | Exact match |
| Source requirements | R-001 through R-011, each once and `Must` | 11 unique rows; exact behavior and priority preserved |
| Acceptance registry | Stable, unique, owned criteria | 32 unique registry entries; no duplicates, omissions, or orphans |
| Outcome anchors | JTBD-01–JTBD-03 and G-01–G-04 | All explicitly covered |
| Approval posture | Experience verification and Gate 1 approval pending | Explicitly pending; no prohibited readiness or approval claim |

The work order, frozen artifact, Product handoff, frozen project brief, and WO-002 Experience verification were read in full. No files were edited.

## Requirement and acceptance enumeration

| Requirement | Acceptance IDs | Trace anchors |
| --- | --- | --- |
| R-001 | AC-R001-01, AC-R001-02, AC-R001-03 | JTBD-01, JTBD-02, JTBD-03; G-01, G-02, G-03, G-04 |
| R-002 | AC-R002-01, AC-R002-02 | JTBD-01; G-01 |
| R-003 | AC-R003-01, AC-R003-02, AC-R003-03 | JTBD-01; G-01 |
| R-004 | AC-R004-01, AC-R004-02, AC-R004-03 | JTBD-02; G-02 |
| R-005 | AC-R005-01, AC-R005-02, AC-R005-03 | JTBD-03; G-03 |
| R-006 | AC-R006-01, AC-R006-02, AC-R006-03 | JTBD-01, JTBD-02, JTBD-03; G-01, G-02, G-03, G-04 |
| R-007 | AC-R007-01, AC-R007-02, AC-R007-03 | JTBD-01, JTBD-02, JTBD-03; G-01, G-02, G-03, G-04 |
| R-008 | AC-R008-01, AC-R008-02, AC-R008-03 | G-04 |
| R-009 | AC-R009-01, AC-R009-02, AC-R009-03 | G-04 |
| R-010 | AC-R010-01, AC-R010-02, AC-R010-03 | G-04 |
| R-011 | AC-R011-01, AC-R011-02, AC-R011-03 | G-04 |

Each acceptance ID appears once in the registry and is owned by its matching requirement. Reappearances in trace tables are references, not duplicate definitions.

## JTBD and goal enumeration

- JTBD-01: R-001, R-002, R-003, R-006, and R-007 criteria.
- JTBD-02: R-001, R-004, R-006, and R-007 criteria.
- JTBD-03: R-001, R-005, R-006, and R-007 criteria.
- G-01: R-001, R-002, R-003, R-006, and R-007 criteria.
- G-02: R-001, R-004, R-006, and R-007 criteria.
- G-03: R-001, R-005, R-006, and R-007 criteria.
- G-04: R-001 and R-006 through R-011 criteria.

This matches `JTBD and goal coverage`; no outcome anchor is orphaned. G-01 through G-04 remain qualitative pending real-use evidence, as stated immediately after that table.

## Boundary and deferred-owner enumeration

`Personal-data boundary trace` covers DI-01, DI-02, DI-03, DI-04, DI-05, DI-06, DI-07, DI-08, DI-09, DI-10, DI-11, DI-12, and DI-13.

`External, destructive, background, and paid-action trace` covers:

- local notifications;
- export or backup;
- destructive restore;
- full deletion;
- Calendar/Keep access or modification;
- other external communication or service-visible action;
- background monitoring, analytics, or telemetry;
- AI processing or action;
- remote synchronization, backend service, or remote copy;
- paid dependencies; and
- production promotion, launch, or broader distribution.

`Deferred decisions and owner boundaries` assigns:

- journeys, content, interaction states, notification defaults, and accessibility validation to Experience;
- mechanisms, interfaces, formats, protection, and destination handling to Architecture;
- test design, implementation, evidence, and measurement methods to Quality and builders;
- protective-control sufficiency and risk decisions to Security and the later risk owner;
- baselines and later numerical targets to Product with Quality input; and
- Gate 1, release, distribution, and consequential changes to the Principal and applicable gate owners.

No boundary or deferred-owner category is omitted or orphaned.

## WO-003 acceptance-criteria inspection

| Criterion | Result | Artifact evidence |
| --- | --- | --- |
| 1 | Met | Header metadata and `Frozen basis and interpretation` identify v0.1, pending review, and the exact source hash. |
| 2 | Met | `Requirement-to-acceptance map` contains R-001–R-011 exactly once, all `Must`, with behavior matching the frozen brief. |
| 3 | Met | Every requirement owns at least two unique criteria and has a JTBD or goal anchor. |
| 4 | Met | All 32 rows in `Acceptance-criterion registry` provide a condition, user action or trigger, and observable outcome. |
| 5 | Met | `Minimum acceptance semantics` defines minimal context, deliberate close, owner/follow-up, credible next move, and explicit disposition without selecting an interface or model. |
| 6 | Met | Positive core behavior is covered by R-001–R-007; offline behavior by AC-R002-02 and AC-R007-01–03; notification control by AC-R008-01–03; negative/non-action outcomes by AC-R003-03, AC-R009-01, AC-R010-03, and AC-R011-02–03; destructive confirmation by AC-R010-02 and AC-R011-01. |
| 7 | Met | Both boundary-trace sections cover personal-only data, prohibited categories, user-initiated portability, destructive controls, optional notifications, and no paid dependency. |
| 8 | Met | `JTBD and goal coverage` covers JTBD-01–JTBD-03 and G-01–G-04; all requirements and criteria are owned and traced. |
| 9 | Met | The statement following the outcome-coverage table explicitly keeps all baseline-dependent measures qualitative and sets no numerical or roadmap threshold. |
| 10 | Met | `Deferred decisions and owner boundaries` assigns every required matter to its correct later owner without choosing the solution. |
| 11 | Met | Header metadata and `Owner-side completeness statement` leave Experience verification and Principal Gate 1 approval pending and disclaim tests, security verdicts, readiness, promotion, and launch approval. |

## Findings

None. No material ambiguity, scope drift, duplicate, omission, orphan, experience prescription, or technical prescription was found. The behavioral and consequence constraints are inherited from the frozen brief; implementation and interaction choices remain deferred to their proper owners.

## Outcome

`SATISFIED`

The acceptance map provides complete and bounded Product semantics for all frozen release-one requirements. Experience can derive journeys and visible states without inventing Product intent, while retaining ownership of interaction behavior. This record does not claim Principal Gate 1 approval.