# Verification Record: WO-004 — Quality Engineer

**Record type:** PRIMARY VERIFICATION  
**Reviewer role:** Quality Engineer  
**Date:** 2026-08-06  
**Input handoff:** `work/handoffs/WO-004-experience.md`

## Assigned question

Does `design/journeys.md` describe complete, observable, testable, and safely bounded end-to-end user behavior for every accepted release-one criterion, without changing Product intent or prescribing technical implementation?

## Evidence reproduced

Environment: `/workspace/scratch/4b457a2fe6bb`; Linux 6.18.35 x86_64; GNU coreutils 9.4; ripgrep 15.2.0; mawk 1.3.4; GNU sed 4.9.

| Command or inspection | Expected | Actual | Evidence location |
| --- | --- | --- | --- |
| `sha256sum design/journeys.md work/gate-decisions/GATE-1-principal.md product/project-brief.md product/acceptance-map.md` | Four assigned hashes match exactly | Exact matches: journeys `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200`; Gate 1 `8ade3617bb88123d1aededb0854718964b1b2e394ebfe23697f474178830f65b`; brief `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b`; acceptance map `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | Frozen files; metadata at `design/journeys.md:3-15` |
| Inspect handoff and artifact metadata | Revision 0.1, owner draft, frozen inputs, verification and Gate 2 pending | All present and consistent with the handoff | `work/handoffs/WO-004-experience.md:1-45`; `design/journeys.md:3-17` |
| `rg -n '^## J-[0-9]{2} —' design/journeys.md` | Eleven bounded journeys covering R-001 through R-011 | Eleven headings: J-01 through J-11, with all required daily, weekly, promise/waiting, project, offline, conditional-notification, export, restore, and deletion behavior | `design/journeys.md:44-58`, journey bodies `60-316` |
| Count required journey fields with `awk` | Each of 11 journeys has trigger, preconditions, goal, entry context, ordered interaction, decisions, outcome, recovery, relevant states, consequence boundary, and trace | Each field counted exactly 11 times | `design/journeys.md:60-316` |
| Compare acceptance registry with ownership table using sorted extraction and `comm -3` | 32 exact IDs, no omission or surplus | Registry count 32; ownership rows 32; unique IDs 32; set difference empty; duplicate/non-exact count 0 | `product/acceptance-map.md:47-82`; `design/journeys.md:318-355` |
| Inspect journey traces and owner prefixes | Every criterion appears once in journey traces and is owned by its corresponding journey | Trace unique count 32; non-exact count 0; no ownership-prefix mismatch | Journey trace lines `81, 103, 126, 149, 172, 196, 219, 244, 268, 292, 316` |
| WO-004 criteria 5–6: deliberate choice and offline behavior | Unresolved intentions persist; owner/revisit and Jude-decided project outcomes remain visible; core loop works offline without external dependencies or action | Required behavior and recovery are explicit; no score, threshold, inference, silent upload, Calendar/Keep access, backend, sync, telemetry, or AI dependency is introduced | `design/journeys.md:105-219` |
| WO-004 criterion 7: portability and destructive actions | User initiation/destination for export; consequence disclosure and confirmation for replacement/deletion; cancellation/no confirmation preserves information | Complete success, cancellation, permission-denied, unavailable, no-effect, and retry behavior is observable and safely bounded | `design/journeys.md:246-316` |
| WO-004 criterion 8: offered notifications | Category, timing, quiet hours, limits, dismissal, complete opt-out, and continued core-loop use without coercion | All controls and outcomes are present; permission denial and failed control changes preserve core-loop usability | `design/journeys.md:221-244` |
| WO-004 criterion 9: data boundaries | Only DI-01 through DI-06 permitted; prohibited categories, work data, and specialized archives excluded | Supported entry is bounded to DI-01–DI-05; DI-06 exists only as initiated export/backup; DI-07 is not collected and DI-08–DI-13 are excluded | `design/journeys.md:21-30, 60-81, 246-268` |
| WO-004 criteria 10–11: assumptions, deferrals, and implementation independence | Accepted behavior separated from hypotheses; later artifacts and change control identified; no technical implementation selected | Hypotheses are explicitly unproven, scope conflicts route to Product change control, and navigation/state/content/accessibility/architecture/Quality mechanisms remain deferred | `design/journeys.md:17, 357-387` |

Exact acceptance ownership reproduced:

- J-01: AC-R001-01, AC-R001-02, AC-R001-03
- J-02: AC-R002-01, AC-R002-02
- J-03: AC-R003-01, AC-R003-02, AC-R003-03
- J-04: AC-R004-01, AC-R004-02, AC-R004-03
- J-05: AC-R005-01, AC-R005-02, AC-R005-03
- J-06: AC-R006-01, AC-R006-02, AC-R006-03
- J-07: AC-R007-01, AC-R007-02, AC-R007-03
- J-08: AC-R008-01, AC-R008-02, AC-R008-03
- J-09: AC-R009-01, AC-R009-02, AC-R009-03
- J-10: AC-R010-01, AC-R010-02, AC-R010-03
- J-11: AC-R011-01, AC-R011-02, AC-R011-03

## Findings

- None.

## Outcome

`SATISFIED`

## Rationale and next action

Quality verdict: `PASS`.

All 11 WO-004 acceptance criteria and all 32 accepted Product criteria have complete, observable journey-level behavior with exact ownership, safe cancellation/recovery and consequence controls, preserved offline operation, and no detected Product-semantic drift or technical prescription.

No Experience Lead remediation is required. Return this record to the Director, who may record WO-004 as verified and advance the frozen artifact to dependent Experience work; Gate 2 approval remains pending.