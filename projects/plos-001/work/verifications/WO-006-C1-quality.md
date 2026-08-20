# Verification Record — WO-006-C1-Q

**Artifact:** `design/state-matrix.md`, revision 0.2  
**Method:** Read-only hash reproduction, exact-set comparison, row-field inspection, state-class mapping, and bounded critical-path regression.  
**Verifier modifications:** None.

## Integrity

All nine frozen inputs matched exactly:

| Input | Reproduced SHA-256 |
| --- | --- |
| `product/acceptance-map.md` | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` |
| `work/verifications/WO-004-R1-quality.md` | `d50c9b136d5a06ca6b9629b7c5cae5bc7b519178fa90c2d425d9a03cc28c0bfa` |
| `design/information-architecture.md` | `d267b2b60f308939bad6fa0a03ce475790014f0fcb7f6babb4fe28fb145bd8b2` |
| `work/verifications/WO-005-R3-quality.md` | `df817434fe4e77cec36181a7b1c7dd904a498ea36609be25ec917603d2cefe51` |
| `design/state-matrix.md` | `bfd1efa86c5df8ba51804a070234deafb25dafb8c0823b9dec92ef65e3ea8a79` |
| `work/handoffs/WO-006-C1-experience.md` | `09937ab8adb8d02a4c4d2b107f05daab1b0f8388d98c4b2beb693b6b1d6cd349` |
| `work/orders/WO-006-C1.md` | `bca942616c5cef240c862482327ebcad5a731ac9d0d5da3546acfd527f38cd73` |
| `work/legacy-2.0/orders/WO-006.md` | `a8eec843fa90e0005b7741e39108d45c8988d37647bd44878fb9b557109e81cc` |

Revision 0.2 names the current journey and IA revisions and hashes.

## Exact coverage

- Destinations: 20 rows, 20 unique; missing/surplus/duplicates: none.
- Journeys: J-01–J-11, 11 unique; differences/duplicates: none.
- Requirements: R-001–R-011, 11 unique; differences/duplicates: none.
- Acceptance ownership: 32 mentions, 32 unique; differences/duplicates: none.
- Active state rows: 73; duplicate IDs: none.
- Required fields: all 73 rows contain all eight fields.
- State-class declarations: 220 total across 20 destinations × 11 classes—143 applicable and 77 not applicable.
- NA reasons: nine defined, eight used, zero undefined; `NA-4` is unused.

## Finding

**F-001 — Major, blocking: declared offline coverage lacks explicit state rows.**

The coverage table marks `O` applicable for all 20 destinations, including S-01, S-02, S-04, and S-05. The only active rows explicitly triggered by offline operation are:

- `SM-COR-02`, covering the 15 core destinations T-01–T-03, R-01–R-05, and C-01–C-07.
- `SM-EXP-04`, covering S-03 export.

No NOT, RST, or DEL row explicitly specifies offline behavior for S-02, S-04, or S-05, and no row supplies S-01’s declared offline state. The exact uncovered mapping is:

`S-01/O, S-02/O, S-04/O, S-05/O`

This contradicts the owner claim that every applicable state class is explicit and fails preserved WO-006 criterion 4 and current WO-006-C1 criteria 1 and 3. It leaves downstream implementation and testing to invent user-visible offline status, actions, transitions, and unchanged-consequence behavior.

No second concrete finding was reproduced in the bounded related regression. Export retains destination-choice-only authorization and chosen-destination visibility for unknown outcomes; restore and deletion retain distinct confirmations and safe cancellation/re-entry.

## Experience remediation boundary

Modify only `design/state-matrix.md` to provide explicit, fully fielded offline behavior for S-01, S-02, S-04, and S-05, consistent with verified journeys and IA. Preserve:

- no network/account/backend dependency;
- notification non-coercion and core-loop availability;
- export’s sole destination-choice authorization;
- restore and deletion’s distinct confirmations;
- safe unchanged-data/consequence behavior;
- Calendar/Keep separation, exclusions, no-cost scope, accessibility baseline, and Architecture mechanism deferral.

## Required retest

Re-run all 13 preserved and 13 current criteria, with targeted verification of:

- the complete 20-destination × 11-class mapping and every applicable-row/NA link;
- S-01/S-02/S-04/S-05 offline triggers, visible status, actions, exits, and consequence effects;
- all counts, fields, hashes, differences, and duplicates;
- notification offered/unoffered/control/permission/opt-out;
- export authorization and outcome-unknown behavior;
- restore/deletion confirmation, cancellation, no-effect, and re-entry;
- offline core, Calendar/Keep, exclusions, no-service/no-cost, accessibility, and deferral regressions.

## Outcome

`NOT_SATISFIED`

## Quality verdict

`BLOCK`