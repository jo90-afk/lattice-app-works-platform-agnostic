# Work Order: WO-006-R1-PR — Fresh Mandatory Product Review of State Matrix

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Status:** VERIFIED — CONCUR  
**Assigned role:** Product Lead, mandatory reviewer  
**Gate:** Gate 2 — Experience

## Assigned question

Does `design/state-matrix.md` revision 0.3 preserve accepted Gate 1 semantics across all 11 requirements and 32 criteria—with no added, dropped, narrowed, reprioritized, or externally consequential behavior—while making the verified journeys and IA observable in all relevant states?

## Frozen inputs

| Path | Status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | verified/concurred revision 0.2 | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` |
| `design/information-architecture.md` | verified/concurred revision 0.4 | `d267b2b60f308939bad6fa0a03ce475790014f0fcb7f6babb4fe28fb145bd8b2` |
| `design/state-matrix.md` | Quality-verified revision 0.3 | `18b0d077c713328cc38c3ad2fb4a8463921f7c4e125c9ef816dbbec731134e06` |
| `work/handoffs/WO-006-R1-experience.md` | owner handoff | `1fc7c213493ae9f4aab335fa47c85f8da6b2081c3a1e1c5d7faf575882eb9233` |
| `work/verifications/WO-006-R1-quality.md` | fresh Quality `SATISFIED/PASS` | `cdb71ce0441b1f094f703f5d47b499307b0cad5dd2835d0e81acd4eb12fd95ca` |

## Review requirements

- Reproduce all seven hashes.
- Trace exactly R-001–R-011 and all 32 acceptance criteria through state ownership and critical transitions; report any omission, addition, semantic narrowing, priority change, or unapproved precondition.
- Confirm daily intention/close, weekly reflection, promise/waiting, project, offline core, and notification states preserve deliberate choice, unresolved status, user control, and non-coercion.
- Confirm export uses completed destination choice as the sole final authorization, unknown outcome retains the chosen destination, and no state silently repeats or assumes an outcome.
- Confirm restore replacement and full deletion retain separate explicit confirmations, safe cancellation/no-effect, truthful uncertainty, and fresh retry boundaries.
- Confirm the four new offline rows do not add network/account behavior, external action, new data, a paid/service dependency, or an implementation mechanism.
- Regress accepted data categories and exclusions, Calendar/Keep coexistence-only, offline release boundary, no AI/backend/sync/telemetry, one-user/personal-install scope, and content/accessibility/Architecture deferrals.
- Return a complete mandatory-review record with exactly `CONCUR` or `BLOCK`.

## Boundaries

- Read only this order, supplied Product role brief, and seven named project inputs.
- Read-only review; no artifact edits, requirement weakening, design authorship, other project/portfolio access, Principal contact, spawning, role switching, or Gate approval.
- Return the review to the Director; it will be recorded verbatim at `work/reviews/WO-006-R1-product.md`.

## Routing

- `CONCUR` makes the state matrix fully verified and opens the next Gate 2 Experience artifact.
- `BLOCK` routes the exact intent gap to Experience; ordinary remediation requires no Principal response.