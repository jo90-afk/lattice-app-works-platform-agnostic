# Work Order: WO-004-PR — Mandatory Product Review of User Journeys

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Status:** BLOCK — F-01 routed to remediation  
**Assigned role:** Product Lead, acting only as Gate 2 mandatory reviewer  
**Author artifact owner:** Experience Lead  
**Primary verifier:** Quality Engineer, already `SATISFIED`  
**Gate:** Gate 2 — Experience

## Assigned question

Does `design/journeys.md` revision 0.1 remain entirely inside the accepted Gate 1 intent and trace every frozen requirement and acceptance criterion without adding, dropping, narrowing, or reprioritizing scope?

## Frozen inputs

| Path | Status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | Owner complete revision 0.1 | `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200` |
| `work/handoffs/WO-004-experience.md` | Owner handoff | `665a4942cdd3adac6f777b05a1a6896f59d6c4799c3d2bab0cf3aa5948d17b70` |
| `work/verifications/WO-004-quality.md` | Quality `SATISFIED` | `996cab972151fab2ad64fd2405e4227a7aa9db2b4698ea2cf739615aac8cfef1` |

## Required review

- Reproduce every input hash.
- Inspect R-001 through R-011 and all 32 acceptance IDs against the journey inventory and exact ownership trace.
- Identify any added, omitted, narrowed, reprioritized, or contradictory product behavior with precise evidence.
- Confirm the accepted data, offline, integration, notification, consequence, and exclusion boundaries remain intact.
- Return one verdict: `CONCUR` or `BLOCK`, with the complete review record in the handoff.

## Boundaries

- Do not edit any project file or rewrite Experience or Quality evidence.
- Do not design journeys, architecture, tests, or implementation.
- Do not weaken an accepted criterion to concur.
- A routine finding returns to the Director for remediation. Escalate only if an exact Principal exception is irreducible.

## Completion

The Director records the returned review verbatim at `work/reviews/WO-004-product.md`. This review does not accept Gate 2.

## Delegation record

- Delegated: 2026-08-06
- Thread: fresh Product Lead mandatory reviewer `/root/plos001_product_review_wo004`
- Scope: project `plos-001` only