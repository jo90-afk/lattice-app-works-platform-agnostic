# Work Order: WO-005-R1-PR — Mandatory Product Review of Information Architecture

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Status:** CONCUR — reviewed revision later invalidated by upstream WO-004 block  
**Assigned role:** Product Lead, acting only as Gate 2 mandatory reviewer  
**Author artifact owner:** Experience Lead  
**Primary verifier:** Quality Engineer, already `SATISFIED` after remediation  
**Gate:** Gate 2 — Experience

## Assigned question

Does `design/information-architecture.md` revision 0.2 preserve the accepted Gate 1 intent and the verified journey semantics, with complete traceability and no added, dropped, narrowed, or reprioritized product scope?

## Frozen inputs

| Path | Status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | Owner complete revision 0.1 | `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200` |
| `design/information-architecture.md` | Remediated revision 0.2 | `848e767cd60a83c8850bd12efc988430f5b62f530aaf38f07e1877eaa5a04dac` |
| `work/handoffs/WO-005-R1-experience.md` | Remediation handoff | `aae0264cf3aeda1649ef686b064d7a0838512dcf5dac555178074168f00efc82` |
| `work/verifications/WO-005-R1-quality.md` | Fresh Quality `SATISFIED` | `dca4ced0f958311294fc145a46e45cbfa22b659220d71bfe299ff0f8c62e6f42` |

## Required review

- Reproduce every input hash.
- Trace J-01 through J-11, R-001 through R-011, and all 32 acceptance IDs through the destination model.
- Confirm F-001/F-002 remediation did not change Product intent.
- Check that the 20-destination model keeps daily/weekly reflection primary and promise/waiting and project context minimal.
- Confirm accepted data, offline, integration, consequence, and exclusion boundaries remain intact.
- Return one verdict: `CONCUR` or `BLOCK`, with the complete review record in the handoff.

## Boundaries

- Do not edit any project file or rewrite Experience or Quality evidence.
- Do not redesign navigation, architecture, tests, or implementation.
- Do not weaken an accepted criterion to concur.
- A routine finding returns to the Director for remediation. Escalate only if an exact Principal exception is irreducible.

## Completion

The Director records the returned review verbatim at `work/reviews/WO-005-R1-product.md`. This review does not accept Gate 2.

## Delegation record

- Delegated: 2026-08-06
- Thread: fresh Product Lead mandatory reviewer `/root/plos001_product_review_wo005_r1`
- Scope: project `plos-001` only