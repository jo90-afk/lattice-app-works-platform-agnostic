# Migrate an Existing Lattice Repository to 0.0.4

Preserve existing code, product artifacts, confirmed mandates, decisions, evidence, and release history. Archive prior process records before removing them from active context.

Map only current operational state:

| Prior representation | 0.0.4 representation |
| --- | --- |
| Current project outcome | Active objective |
| Current delivery stage | Active milestone |
| Required completed claim | Readiness condition |
| Requirement, constraint, ADR, contract | Versioned record plus original artifact |
| Consequential proposition | Truth-ledger entry |
| Current independent proof | Evidence/submission/review |
| External deadline or promise | Commitment |
| Unresolved blocker | Deduplicated exception |
| Completed or speculative work order | Do not import as active state |

For a 0.0.3 repository, rename the `android` role to `application`, migrate its owned code from `platform/android/**` into the appropriate child of `platform/**`, and migrate role-unit tests to `tests/application-unit/**`. Change any active state rows that still name the `android` role before adopting the 0.0.4 runtime policy.

Add `project/capabilities.json` to each capsule. Declare actual application targets in `application_platforms` and use an open platform identifier when no bundled pack exists. Set `cross_platform_strategy` to `native`, `undecided`, or the selected framework. Do not activate platforms just because the expertise library contains them.

The expertise library is kernel guidance. Load it through `python3 scripts/lattice.py expertise`; do not copy its recommendations into a project backlog or treat cited standards as accepted project truth without project-specific evidence.

After import, compare the derived frontier with work that is genuinely executable now. If it produces actions merely because an old ticket existed, the migration imported administration rather than project state.
