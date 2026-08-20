# Mandatory Product Retest Record: WO-004-R1-PR

**Project ID:** `plos-001`  
**Reviewer role:** Product Lead  
**Gate:** Gate 2 — Experience  
**Date:** 2026-08-06  
**Artifact reviewed:** `design/journeys.md`, revision 0.2

## Assigned question

Does `design/journeys.md` revision 0.2 implement R-009 and AC-R009-01 through AC-R009-03 without an added prerequisite, while preserving every other accepted Gate 1 semantic and priority?

## Frozen-input integrity

| Input | Expected and reproduced SHA-256 | Result |
| --- | --- | --- |
| `product/project-brief.md` | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | Exact match |
| `product/acceptance-map.md` | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | Exact match |
| `work/reviews/WO-004-product.md` | `4e1e0a31974085ff8a4fdedd8b64216d71df7c458ca2fc4ce73348b5a7317330` | Exact match |
| `design/journeys.md` | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` | Exact match |
| `work/handoffs/WO-004-R1-experience.md` | `2f1ee31794e9eaadf694efe8c9a32d8a4525d43bf09d031266e25eceace429b9` | Exact match |

## R-009 and acceptance review

- **R-009:** J-09 begins only through Jude’s explicit initiation and lets Jude choose the destination (`design/journeys.md:248-255`). During destination selection, the eligible scope and external-copy consequence are visible (`design/journeys.md:256`). Completed destination choice is expressly the authorization for one attempt, with no additional mandatory in-app confirmation (`design/journeys.md:257,262`). Destination choice is therefore the final accepted authorization action; no second mandatory action remains.
- **AC-R009-01:** Before completed destination choice, leaving, cancellation, denied destination access, or interruption starts no attempt, creates no copy, moves no app-managed personal data off-device, and leaves app-managed information unchanged (`design/journeys.md:257,265-266`). This preserves the accepted initiation-and-destination boundary.
- **AC-R009-02:** After completed destination choice, the product directs the eligible copy only to the chosen destination and exposes in-progress status without premature success (`design/journeys.md:258`). It reports completed only when established, reports did-not-take-effect when no copy is established, and reports outcome unknown after an interruption when neither result can be established (`design/journeys.md:259,265-266`). The unknown state does not claim completion or no effect and does not silently repeat. Any retry after established no effect requires fresh initiation and destination choice (`design/journeys.md:260,265`), preserving deliberate authorization rather than adding a prerequisite to the accepted attempt.
- **AC-R009-03:** The eligible copy is limited to supported DI-01 through DI-05 data; DI-07 through DI-13, including work and prohibited data, are excluded (`design/journeys.md:256,267`). The action is non-recurring, is not synchronization, and cannot use an app-chosen remote destination (`design/journeys.md:256,262,267`).
- **Cancellation and interruption boundary:** Pre-choice interruption has guaranteed no effect; post-choice interruption may truthfully remain outcome unknown because authorization already occurred and an external copy may have been created. The journey identifies the chosen destination, avoids false status, and prohibits silent repetition (`design/journeys.md:265-266`). These states do not reintroduce confirmation or standing authorization.

The remediation directly resolves original finding F-01, whose sole defect was the extra confirmation after destination selection (`work/reviews/WO-004-product.md:50-71`). The owner handoff accurately describes that bounded correction (`work/handoffs/WO-004-R1-experience.md:8-19`).

## Regression of all other accepted semantics

| Scope | Evidence and result |
| --- | --- |
| Requirements and priorities | J-01 through J-11 remain mapped one-to-one to R-001 through R-011 (`design/journeys.md:44-58`). All 11 source requirements remain `Must` in the accepted map (`product/acceptance-map.md:33-45`); revision 0.2 introduces no alternate priority. |
| Acceptance ownership | All 32 criteria remain assigned to their original single owning journeys, including unchanged ownership outside R-009 (`design/journeys.md:318-355`). |
| R-001–R-006 | Minimal context, daily intention, deliberate close, promise/waiting ownership, project decisions, and the three-job weekly reflection preserve their accepted outcomes, cancellations, and exclusions (`design/journeys.md:60-196`). |
| R-007 | Core-loop operation remains available offline without account, backend, synchronization, AI, Calendar, or Keep, and later connectivity causes no silent upload or processing (`design/journeys.md:198-219`). |
| R-008 | Notifications remain conditional, fully configurable and optional, non-coercive, and unnecessary to complete the core loop (`design/journeys.md:221-244`). |
| R-010–R-011 | Restore replacement and full deletion retain explicit initiation, prior consequence disclosure, destructive confirmation, cancellation safety, and observable completion/no-effect behavior (`design/journeys.md:270-316`). |
| Data categories | DI-01 through DI-05 remain the only supported context; DI-06 exists only as Jude-initiated portability; DI-07 is not collected; DI-08 through DI-13 remain excluded or prohibited (`design/journeys.md:23-24,69-80,267`). |
| Integrations and external actions | Calendar and Keep remain separate; promise/waiting activity sends nothing; no sharing, service-visible action, telemetry, AI, backend, or remote synchronization is introduced (`design/journeys.md:25-29,137-149,183-219`). |
| Consequence rules | Time, omission, dismissal, failure, or journey exit cannot resolve, dispose, replace, or delete by itself; restore and deletion retain separate destructive confirmation (`design/journeys.md:28-29,38-41`). |
| Exclusions and release boundary | The artifact introduces no work use, specialized domain workflow, new data category, paid dependency, multi-user behavior, production promotion, launch, or broader distribution. |
| Deferred-owner boundaries | Navigation, state presentation, content, accessibility details, architecture mechanisms, and Quality verification remain assigned to their proper downstream owners without selecting those mechanisms (`design/journeys.md:374-383`). |

## Findings

No Product-semantic finding remains. Revision 0.2 implements the accepted portability behavior without another authorization action and preserves every other accepted Gate 1 semantic, priority, ownership boundary, and exclusion.

## Verdict

`CONCUR`