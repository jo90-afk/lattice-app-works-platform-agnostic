# Work Order: WO-005-R3-PR — Fresh Mandatory Product Retest

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Status:** VERIFIED — CONCUR  
**Assigned role:** Product Lead, mandatory reviewer  
**Gate:** Gate 2 — Experience

## Assigned question

Does `design/information-architecture.md` revision 0.4 preserve accepted Gate 1 intent across all 11 requirements and 32 acceptance criteria, resolve the J-09/F-003 visibility gap, keep destination choice as the sole export authorization, and avoid weakening restore, deletion, data, offline, exclusion, priority, or deferred-owner boundaries?

## Frozen inputs

| Path | Status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | verified/concurred revision 0.2 | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` |
| `work/reviews/WO-004-R1-product.md` | fresh Product `CONCUR` | `93d7dfaf5d19a6aae687653e1d16af1f0b1bb711632c6070801fda183336c09e` |
| `design/information-architecture.md` | Quality-verified revision 0.4 | `d267b2b60f308939bad6fa0a03ce475790014f0fcb7f6babb4fe28fb145bd8b2` |
| `work/handoffs/WO-005-R3-experience.md` | owner handoff | `b3c523bcdf47be3a1b91d48f8533b3ac7558376fb5798cf2e3d1a104b5cf502a` |
| `work/verifications/WO-005-R3-quality.md` | fresh Quality `SATISFIED/PASS` | `df817434fe4e77cec36181a7b1c7dd904a498ea36609be25ec917603d2cefe51` |

## Review requirements

- Reproduce every frozen hash.
- Trace all 11 requirements and all 32 acceptance criteria through the IA exact trace and route declarations; report any omission, addition, weakened criterion, or priority change.
- Inspect R-009 and AC-R009-01 through AC-R009-03 across scope/consequence disclosure, destination choice, progress, completed, no-effect, interrupted/outcome-unknown, and retry behavior.
- Confirm the chosen destination remains visible for outcome-unknown export without asserting success or no effect.
- Confirm destination choice remains the sole final export authorization and no added confirmation prerequisite exists.
- Confirm restore replacement and full deletion retain their distinct explicit confirmations.
- Regress accepted data categories, Calendar/Keep coexistence-only rule, offline core, notification control, exclusions, no-cost/no-service scope, release boundary, and Experience/Architecture deferrals.
- Return a complete mandatory-review record with exactly `CONCUR` or `BLOCK`.

## Boundaries

- Read only this order, the supplied Lattice 2.1 Product role brief, and named inputs.
- Do not edit files, redesign the IA, weaken requirements, contact the Principal, spawn agents, switch roles, or inspect another project.
- Return the review to the Director; the Director records it verbatim at `work/reviews/WO-005-R3-product.md`.

## Dependency and routing

- Depends on WO-005-R3-Q `SATISFIED/PASS` at the frozen revision 0.4 hash.
- `CONCUR` verifies the IA artifact and opens WO-006-C1 remediation/resumption.
- `BLOCK` routes the exact failed intent claim to Experience; no Principal response is required unless an exact exception predicate is identified.