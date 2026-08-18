# Work Order: WO-005-R2-PR — Fresh Mandatory Product Retest

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Status:** BLOCKED — revision 0.3 failed primary verification  
**Assigned role:** Product Lead, mandatory reviewer  
**Gate:** Gate 2 — Experience

## Assigned question

Does `design/information-architecture.md` revision 0.3 preserve accepted Gate 1 semantics and remove the added export prerequisite everywhere without weakening restore, full-deletion, or any other accepted boundary?

## Frozen inputs

| Path | Status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | verified/concurred revision 0.2 | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` |
| `work/reviews/WO-004-R1-product.md` | Fresh Product `CONCUR` | `93d7dfaf5d19a6aae687653e1d16af1f0b1bb711632c6070801fda183336c09e` |
| `design/information-architecture.md` | remediation revision 0.3 | `df3af327d514bfe61645cf684fc87e9c6025bd353af8a059b2654a582077f2a3` |
| `work/handoffs/WO-005-R2-experience.md` | owner handoff | `a220e1cc9b94738334a400ee4ee387791a9142f0239f0fd5de53f0dfb28c864b` |

## Review requirements

- Reproduce all hashes.
- Inspect R-009 and all AC-R009 criteria across the information model, movement rules, S-03, journey route, state entry, exact trace, and usability hypothesis.
- Confirm no second export authorization action remains and destination choice is deliberate with visible scope/consequence.
- Confirm restore replacement and full deletion still require distinct explicit confirmation.
- Regress all 11 requirements, 32 criteria, priorities, data categories, integration/offline rules, exclusions, and deferred-owner boundaries.
- Return a complete review record with exactly `CONCUR` or `BLOCK`.

## Boundaries

- Read only this order, `agency_kernel/agents/product.md`, and named inputs.
- Do not edit files, redesign the IA, contact the Principal, or inspect another project.
- Director records the response verbatim at `work/reviews/WO-005-R2-product.md`.