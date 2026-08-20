# Verification Record: WO-005 — Quality Engineer

**Record type:** PRIMARY VERIFICATION  
**Reviewer role:** Quality Engineer  
**Date:** 2026-08-06  
**Input handoff:** `work/handoffs/WO-005-experience.md`

## Assigned question

Does `design/information-architecture.md` provide a complete, minimal, and testably coherent organization and navigation path for every verified journey and accepted requirement, while preserving user control and avoiding scope or technical drift?

## Evidence reproduced

Environment: `/workspace/scratch/4b457a2fe6bb`; Linux 6.18.35 x86_64; GNU coreutils 9.4; ripgrep 15.2.0; GNU sed 4.9; mawk 1.3.4.

| Command or inspection | Expected | Actual | Evidence location |
| --- | --- | --- | --- |
| `sha256sum design/information-architecture.md` | `fe3c9ceafd4d2f77212698356ec3268b08ca5ab950e316621f430fbeea72e4ae` | Exact match | Frozen output |
| `sha256sum` on all five frozen inputs | All assigned hashes match | Gate 1 `8ade3617…f65b`; brief `68097f79…bb76b`; acceptance map `8b5fdb38…934d3`; journeys `8a605a91…c200`; WO-004 verification `996cab97…ef1`—all exact | Files named in `WO-005.md:21-29` |
| Inspect metadata | Revision 0.1, owner draft, exact frozen basis, Quality and Gate 2 pending | All present | `design/information-architecture.md:3-19` |
| Inspect conceptual model | Minimal user-language concepts covering DI-01–DI-06 without a technical model | Eight conceptual types, boundaries, and relationships present; no schema, field, API, persistence, or mechanism selected | `design/information-architecture.md:21-43` |
| `rg -n '^\| [TRCS]-[0-9]{2} '` and unique-count inspection | 20 unique destinations, each with purpose/information, actions, entry/exit, and trace | 20 unique rows: T-01–T-03, R-01–R-05, C-01–C-07, S-01–S-05. Required columns are populated, but route/trace contradictions remain in Finding F-001 | `design/information-architecture.md:94-119` |
| Extract unique J, R, and AC identifiers from the exact trace | J-01–J-11, R-001–R-011, all 32 acceptance IDs, no set difference | 11 journeys, 11 requirements, 32 acceptance IDs; set difference against the acceptance map is empty | `design/information-architecture.md:165-181`; `product/acceptance-map.md:47-82` |
| Semantic walk of J-01–J-11 | Each journey has coherent entry, completion, cancellation, and recovery | J-02–J-08 have coherent routes. J-01 has contradictory/incomplete routing and semantic trace. J-09–J-11 lack a defined re-entry route after interruption during confirmed/in-progress work | `design/information-architecture.md:81-92, 100-119, 121-154` |
| Inspect offline, first/returning use, error, permission, conflict, and destructive controls | Coherent entries with exhaustive presentation details deferred | Offline core routes, empty/returning entry, error/no-effect, permission denial, and consequence confirmation are defined; consequence-flow interruption remains incomplete | `design/information-architecture.md:137-154` |
| Inspect exclusions and deferred ownership | No scope/technical drift; WO-006, WO-007, WO-008, and Architecture boundaries explicit | Satisfied | `design/information-architecture.md:206-218` |

### WO-005 acceptance-criterion coverage

| Criterion | Result | Evidence |
| --- | --- | --- |
| 1 | Met | Metadata and frozen basis at lines 3-19 |
| 2 | Met | Concept model at lines 21-43 |
| 3 | Not met | Contradictory J-01 entry rules and missing consequence-flow interruption returns; F-001/F-002 |
| 4 | Not met | All 20 rows exist, but T-01/C-03 entry rules conflict and DI-04 support is not traced; F-001 |
| 5 | Not met | J-01 is not unambiguous; J-09–J-11 lack post-confirmation interruption recovery routes |
| 6 | Met | Today/Reflect primary loop and supporting Context structure at lines 38-40, 47-79 |
| 7 | Met | Discoverable S-01–S-05 routes and explicit consequence controls at lines 54, 91-92, 115-119, 151 |
| 8 | Not met | First, returning, and offline entry are covered, but incomplete-flow recovery is limited to Today/Reflect; F-002 |
| 9 | Not met | Identifier sets are complete, but J-01/R-001 semantic trace omits DI-04 and does not provide general DI-05 decision routes; F-001 |
| 10 | Met | Exclusions at lines 19, 56, 145-152, 204, 208 |
| 11 | Met | Exact WO-006/007/008 and Architecture deferrals at lines 139, 185, 210-216 |

### Journey and requirement trace result

| Journey / requirement | Route result |
| --- | --- |
| J-01 / R-001 | **Blocked:** contradictory entry declarations; DI-04 route/trace omitted; optional DI-05 is not eligible alongside promise/project decisions |
| J-02 / R-002 | T-01 → T-02 → T-01; completion, cancellation, no-effect, and offline outcomes covered |
| J-03 / R-003 | T-01 or R-02 → T-03 → origin; unresolved/cancelled work remains identifiable |
| J-04 / R-004 | C-01 → C-04 → C-05 or R-03 → C-05; completion and safe cancellation covered |
| J-05 / R-005 | C-01 → C-06 → C-07 or R-04 → C-07; no inferred disposition |
| J-06 / R-006 | R-01 → R-02 → R-03 → R-04 → R-05 → R-01; incomplete and empty-category behavior covered |
| J-07 / R-007 | Normal J-01–J-06 routes remain available offline without Calendar/Keep or remote dependencies |
| J-08 / R-008 | S-01 → S-02; control, opt-out, dismissal, denial, cancellation, and no-effect covered |
| J-09 / R-009 | Completion and pre-confirmation cancellation covered; **post-confirmation interruption re-entry unspecified** |
| J-10 / R-010 | Completion, cancellation, denial, and no-effect covered; **in-progress interruption re-entry unspecified** |
| J-11 / R-011 | Completion, cancellation, and new-attempt behavior covered; **in-progress interruption re-entry unspecified** |

## Findings

- **F-001 — Major: J-01/R-001 routing and trace are not testably coherent.**
  - `T-01` says it directly opens C-03 at `design/information-architecture.md:100`, while C-03 permits entry only from C-02, T-02, or R-02 at line 110.
  - J-01 says C-01 routes directly to C-03/C-05/C-07 at line 125, while C-01 opens only C-02/C-04/C-06 at line 108.
  - The verified J-01 permits context entry while closing the day and includes short reflection/review decisions (`design/journeys.md:65, 69-73`). T-03 owns DI-04 entry at IA line 102 but omits J-01/R-001, and the exact J-01 trace at line 169 names only C-03/C-05/C-07.
  - AC-R001-03 permits optional DI-05 context for a relevant loop decision (`product/acceptance-map.md:53`). The IA permits DI-05 only with C-03’s DI-01 context (line 110); C-05 is DI-02-only (line 112), and C-07 exposes only DI-03 actions (line 114). This leaves no explicit eligible route when DI-05 informs a promise/waiting or project decision.
  - User/test impact: downstream owners cannot derive one authoritative J-01 path or demonstrate complete R-001 context coverage without inventing navigation or narrowing accepted behavior.

- **F-002 — Major: interrupted consequence flows lack a defined re-entry route.**
  - Continuation rules name only incomplete daily close and weekly reflection at lines 86 and 150.
  - S-03–S-05 define cancellation, completion, and no-effect exits at lines 117-119, but do not define where Jude returns after interruption during confirmed/in-progress export, restore, or deletion.
  - J-09–J-11 route rows at lines 133-135 likewise omit this case. Line 154 requires status inside the owning flow but supplies no navigation route back to that flow.
  - User/test impact: after interruption, Quality cannot verify whether an export occurred, whether restore replaced information, or whether deletion completed without inventing recovery behavior. This is especially consequential for restore and deletion.

## Outcome

`NOT_SATISFIED`

Quality verdict: `BLOCK`.

## Rationale and next action

The artifact preserves the approved minimal scope, offline core loop, user-controlled notifications and data actions, exclusions, and deferred-owner boundaries. Its identifier inventories are complete. However, WO-005 requires semantic—not merely nominal—route completeness. The J-01 contradictions and missing DI-04/DI-05 trace prevent exact R-001 verification, while J-09–J-11 lack an unambiguous recovery route following interruption of a confirmed consequence operation.

Return F-001 and F-002 through the Director to the Experience Lead. After a revised artifact is frozen, Quality should rerun criteria 3–5, 8, and 9; all J-01 and J-09–J-11 route walks; the 20-destination inventory; and regression checks for criteria 1–2, 6–7, and 10–11.