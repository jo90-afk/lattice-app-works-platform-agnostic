# Experience Lead Handoff — WO-004-R1

**Project:** `plos-001`  
**Artifact:** `design/journeys.md`  
**Revision:** 0.2  
**Final SHA-256:** `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019`

## Changes

- Resolved Product finding F-01 only.
- Removed the additional mandatory export/backup confirmation.
- Made completed destination choice—with supported-data scope and external-copy consequence visible—the authorization for one non-recurring attempt.
- Defined pre-destination cancellation, denial, or interruption as creating no copy, moving no data, and leaving app-managed information unchanged.
- Defined post-destination states as in progress, completed, did not take effect, or interrupted/outcome unknown.
- Prohibited silent repetition; a recovery attempt after established no effect requires fresh initiation and destination choice.
- Preserved user initiation, destination control, DI-01–DI-05-only scope, local-first behavior, and the no-sync/no-recurring-transfer boundary.
- Updated the R-009 ownership summaries and related usability hypothesis without changing acceptance ownership.
- Added the bounded revision 0.2/F-01 change record.
- J-01 through J-08 and J-10 through J-11 remain semantically unchanged.

## Checks performed

- Reproduced every frozen-input SHA-256 from WO-004-R1 before editing; all five matched exactly.
- Confirmed revision metadata now reports `0.2` and owner `Experience Lead — WO-004-R1`.
- Inspected the revised global consequence language and J-09 behavior.
- Reproduced 11 journey headings, J-01 through J-11.
- Reproduced 11 requirement trace lines, R-001 through R-011.
- Reproduced all 32 acceptance-ownership rows, AC-R001-01 through AC-R011-03, with their original owning journeys.
- Confirmed the revision record names both required downstream artifacts.
- Reproduced the final artifact hash above.

## Downstream impact

- `design/information-architecture.md` requires regression against destination-choice-as-authorization before use.
- The interrupted `design/state-matrix.md` requires remediation for revised pre-choice and post-choice J-09 states before use.

## Risks

- Interrupted/outcome-unknown presentation must not imply completion, established no effect, or permission for an automatic retry.
- Destination-selection design must keep scope and consequence visible without reintroducing another mandatory action.

## Open items

- Fresh Quality verification is required.
- Fresh mandatory Product review is required.
- Gate 2 remains open.
- No Principal exception or change request is identified.