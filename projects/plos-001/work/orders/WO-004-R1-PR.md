# Work Order: WO-004-R1-PR — Fresh Mandatory Product Retest

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Status:** CONCUR  
**Assigned role:** Product Lead, mandatory reviewer  
**Artifact owner:** Experience Lead  
**Gate:** Gate 2 — Experience

## Assigned question

Does `design/journeys.md` revision 0.2 implement R-009 and AC-R009-01 through AC-R009-03 without an added prerequisite, while preserving every other accepted Gate 1 semantic and priority?

## Frozen inputs

| Path | Status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `work/reviews/WO-004-product.md` | Original Product `BLOCK` F-01 | `4e1e0a31974085ff8a4fdedd8b64216d71df7c458ca2fc4ce73348b5a7317330` |
| `design/journeys.md` | Remediation revision 0.2 | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` |
| `work/handoffs/WO-004-R1-experience.md` | Owner handoff | `2f1ee31794e9eaadf694efe8c9a32d8a4525d43bf09d031266e25eceace429b9` |

## Review requirements

- Reproduce every input hash.
- Inspect R-009 and all three AC-R009 criteria step-by-step, including cancellation and interruption boundaries.
- Confirm destination choice is the final accepted authorization action and that no second mandatory action remains.
- Regress all other requirements, priorities, acceptance ownership, data categories, integrations, offline behavior, consequence rules, exclusions, and deferred-owner boundaries.
- Return a complete review record with exactly one verdict: `CONCUR` or `BLOCK`.

## Boundaries

- Read only this order, `agency_kernel/agents/product.md`, and the named project inputs.
- Do not edit any project file or rewrite Experience/Quality evidence.
- Do not weaken accepted semantics or contact the Principal.
- The Director records the response verbatim at `work/reviews/WO-004-R1-product.md`.

## Delegation record

- Delegated: 2026-08-06
- Thread: `/root/plos001_product_wo004_r1`
- Scope: project `plos-001` only