# Mandatory Product Review — WO-005-R3-PR

## Project ID/root

- **Project ID:** `plos-001`
- **Project root:** `/workspace/scratch/4b457a2fe6bb/projects/plos-001`
- **Reviewer role:** Product Lead, mandatory reviewer
- **Artifact:** `design/information-architecture.md`, revision 0.4
- **Date:** 2026-08-06

## Record type

**MANDATORY REVIEW**

## Assigned question

Does information-architecture revision 0.4 preserve accepted Gate 1 intent across all 11 requirements and 32 acceptance criteria, resolve the J-09/F-003 visibility gap, keep destination choice as the sole export authorization, and avoid weakening restore, deletion, data, offline, exclusion, priority, or deferred-owner boundaries?

## Environment/method

- Linux 6.18.35 x86_64 GNU/Linux
- GNU coreutils 9.4
- ripgrep 15.2.0
- Read-only review; no files modified.
- Method: complete work-order and frozen-input inspection, SHA-256 reproduction, exact identifier-set comparison, requirement-by-requirement and criterion-by-criterion semantic trace, six-state J-09 consequence walk, destination inventory check, and regression of protected Product boundaries.
- Automated checks reproduced 11 unique journey IDs, 11 unique requirement IDs, 32 unique acceptance IDs, zero R/AC symmetric difference against the accepted map, 11 `Must` priorities, and 20 unique expected IA destinations with no surplus or duplicate.
- This is a Product intent review only. It does not claim primary Quality verification or Gate acceptance.

## Input integrity

| Frozen input | Expected SHA-256 | Reproduced SHA-256 | Result |
| --- | --- | --- | --- |
| `product/project-brief.md` | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | Exact match |
| `product/acceptance-map.md` | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | Exact match |
| `design/journeys.md` | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` | Exact match |
| `work/reviews/WO-004-R1-product.md` | `93d7dfaf5d19a6aae687653e1d16af1f0b1bb711632c6070801fda183336c09e` | `93d7dfaf5d19a6aae687653e1d16af1f0b1bb711632c6070801fda183336c09e` | Exact match |
| `design/information-architecture.md` | `d267b2b60f308939bad6fa0a03ce475790014f0fcb7f6babb4fe28fb145bd8b2` | `d267b2b60f308939bad6fa0a03ce475790014f0fcb7f6babb4fe28fb145bd8b2` | Exact match |
| `work/handoffs/WO-005-R3-experience.md` | `b3c523bcdf47be3a1b91d48f8533b3ac7558376fb5798cf2e3d1a104b5cf502a` | `b3c523bcdf47be3a1b91d48f8533b3ac7558376fb5798cf2e3d1a104b5cf502a` | Exact match |
| `work/verifications/WO-005-R3-quality.md` | `df817434fe4e77cec36181a7b1c7dd904a498ea36609be25ec917603d2cefe51` | `df817434fe4e77cec36181a7b1c7dd904a498ea36609be25ec917603d2cefe51` | Exact match |

## Requirement/acceptance trace evidence

The IA’s exact trace contains J-01 through J-11, R-001 through R-011, and all 32 accepted IDs with no omission, surplus, duplicate, ownership change, or alternate priority (`design/information-architecture.md:186-202`).

| Requirement and criteria | IA preservation evidence | Result |
| --- | --- | --- |
| R-001; AC-R001-01–03 | DI-01 through DI-05 remain minimal Jude-chosen context; DI-05 remains optional and attached only to a relevant decision. Exact-origin entry and return routes preserve current context, cancelled revisions, and no-effect outcomes (`:43-54,61-63,105-109,121-135,146,190`). | Preserved |
| R-002; AC-R002-01–02 | Today/Form daily intention lets Jude choose and identify one or more commitments without ranking or inference; the same route remains available without network, account, Calendar, or Keep (`:48,71,76,121-122,147,164-167,191`). | Preserved |
| R-003; AC-R003-01–03 | Close day distinguishes resolved, reconsidered, and unresolved; incomplete, skipped, cancelled, or no-effect work remains unresolved and reachable (`:49,62,71,103-107,121,123,148,171,192`). | Preserved |
| R-004; AC-R004-01–03 | Promise/waiting routes expose owner and next follow-up together, preserve prior context after cancellation/no effect, and cause no external action (`:50,126,132-133,149,193`). | Preserved |
| R-005; AC-R005-01–03 | Personal-project routes retain Jude-chosen advance, pause, or conscious release, with no score, fixed state, drift threshold, or work-in-progress rule (`:51,127,134-135,150,194`). | Preserved |
| R-006; AC-R006-01–03 | Reflect retains attention, promises/waiting, projects, and summary across all three ranked jobs; empty categories remain valid and no specialized workflow or archive is introduced (`:52,59-61,72,83-87,124-128,151,195`). | Preserved |
| R-007; AC-R007-01–03 | T-01 through C-07 remain available through normal routes offline; there is no connectivity gate, account requirement, Calendar/Keep access, backend, synchronization, analytics, telemetry, AI, or later silent upload (`:76,152,164-171,196,202,229`). | Preserved |
| R-008; AC-R008-01–03 | If notifications are offered, S-02 exposes category, timing, quiet hours, frequency limits, category opt-out, and complete opt-out. Opt-out and permission denial leave the core loop usable; notifications remain routine, non-urgent, and non-coercive (`:137,153,179-184,197,234`). | Preserved |
| R-009; AC-R009-01–03 | S-03 requires explicit initiation and completed destination choice, limits eligibility to DI-01 through DI-05, excludes prohibited/work data, prohibits recurrence and synchronization, and exposes truthful completed/no-effect/unknown outcomes (`:54,111,113,138,154,171-175,198`). | Preserved |
| R-010; AC-R010-01–03 | S-04 keeps selected-backup restore distinct, discloses possible replacement, requires explicit confirmation before replacement, preserves information on cancellation/no confirmation, and exposes truthful status without silent retry (`:63,112-113,139,155,170,172,199`). | Preserved |
| R-011; AC-R011-01–03 | S-05 retains separate initiation, full-deletion consequence disclosure, distinct confirmation, safe cancellation, visible completion, no silent retry, and the rule that external user-created copies remain outside app-managed deletion (`:63,99,112-113,140,156,172,200`). | Preserved |

All 11 source requirements remain `Must`. The labels “primary” and “global secondary” describe navigation placement, not Product priority; every required consequence route remains consistently reachable from Today, Reflect, and Context.

## R-009/J-09 consequence review

| State or rule | Revision 0.4 behavior | Result |
| --- | --- | --- |
| Scope/consequence disclosure | During destination selection, Jude sees eligible DI-01–DI-05 scope, external-copy consequence, exclusions, non-sync behavior, and non-recurrence (`:54,138,154,172,198`). | Preserved |
| Final authorization | Deliberately completing destination choice authorizes exactly one attempt. S-03 expressly has no additional mandatory in-app confirmation (`:26,54,138,154,172,198,223`). | Preserved |
| Pre-choice exit | Leaving, Back, cancellation, denied access, or interruption before completed destination choice starts no attempt and creates no copy (`:111,138,154,171`). | Preserved |
| In progress | S-03 exposes progress without claiming completion (`:138,154,175`). | Preserved |
| Completed | Completion is identifiable only as an established result and identifies Jude’s chosen destination (`:154`). | Preserved |
| Did not take effect | No copy is claimed, and the operation is not silently repeated (`:154`). | Preserved |
| Interrupted/outcome unknown | Every operative declaration keeps Jude’s chosen destination visible alongside the uncertainty and possible completed/no-effect outcomes, asserts neither result, and does not repeat (`:113,138,154,171,175,198`). | F-003 resolved |
| Retry | A new attempt is available only after established no effect and requires fresh explicit initiation plus completed destination choice; prior choice is not standing authorization (`:113,138,154`). | Preserved |

The revision 0.3 text is historical provenance. Revision 0.4’s remediation record and all six operative unknown-outcome declarations carry the required chosen-destination visibility.

## Boundary regression

| Protected boundary | Review result |
| --- | --- |
| Restore versus deletion | Replacement confirmation remains owned by S-04; full-deletion confirmation remains distinct in S-05. Neither is collapsed into export authorization or into the other destructive action. |
| Data categories | DI-01 through DI-05 remain the only supported context; DI-06 remains only a Jude-initiated copy at a chosen destination; DI-07 remains uncollected; DI-08 through DI-13 remain excluded or prohibited (`:43-54,129-140,229`). |
| Calendar/Keep coexistence | No read, import, copy, monitoring, write, connection, or permission gate is introduced (`:47,76,152,196,202,229`). |
| Offline core | Daily intention, close, reflection, and supporting context use the normal routes offline and retain locally observable results; a particular export destination’s availability does not gate the core loop (`:152,164-171,196`). |
| Notifications | Every offered behavior remains configurable and optional, with quiet-hours and frequency control, complete opt-out, no core-loop dependency, and non-coercive treatment (`:137,153,179-184,234`). |
| Exclusions and no-cost/no-service scope | No work behavior/data, specialized domain suite, detailed archive, AI, backend, remote synchronization, analytics, telemetry, external communication, or paid dependency is introduced (`:21,229,236`). |
| Release boundary | No multi-user or broader-distribution concept is introduced; the artifact claims no implementation, promotion, launch, or distribution authorization (`:229,239`). |
| Priority | The exact 11-requirement set remains 11 `Must`; no Product priority is reduced or replaced by navigation prominence. |
| Deferred owners | Exhaustive state presentation remains with WO-006, content/notification details with WO-007, accessibility details with WO-008, technical mechanisms with Architecture, and verification evidence with Quality (`:160,175,204-211,231-237`). No schema, format, storage, environment topology, platform mechanism, or test method is selected by the IA. |
| Outcome/evidence posture | Validation remains qualitative and synthetic; no telemetry, remote analytics, numerical threshold, or real/prohibited personal data is added (`:214-225`). |

## Findings

None.

No requirement or criterion is omitted, added, weakened, reprioritized, or reassigned. No data, autonomy, external-action, destructive-action, offline, exclusion, release, cost, service, or deferred-owner boundary regresses.

## Outcome

CONCUR

## Rationale/next action

Revision 0.4 remains faithful to accepted Gate 1 intent across all 11 requirements and 32 acceptance criteria. It resolves J-09/F-003 by retaining the chosen destination in every operative outcome-unknown declaration, while destination choice remains the sole final authorization for one export attempt. Restore and deletion keep their separate explicit destructive confirmations, and all other protected boundaries remain intact.

The Director may record this mandatory review verbatim and route the project to WO-006-C1 remediation/resumption. This concurrence verifies Product-intent fidelity only; it does not approve Gate 2 or claim primary Quality verification, architecture readiness, implementation readiness, security acceptance, production promotion, launch, or broader distribution.