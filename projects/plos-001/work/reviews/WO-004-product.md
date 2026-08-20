# Mandatory Product Review Record: WO-004-PR

**Project ID:** `plos-001`  
**Record type:** Gate 2 mandatory Product review  
**Reviewer role:** Product Lead  
**Date:** 2026-08-06  
**Artifact reviewed:** `design/journeys.md`, revision 0.1

## Assigned question

Does `design/journeys.md` revision 0.1 remain entirely inside the accepted Gate 1 intent and trace every frozen requirement and acceptance criterion without adding, dropping, narrowing, or reprioritizing scope?

## Evidence reproduced

| Frozen input | Expected SHA-256 | Reproduced SHA-256 | Result |
| --- | --- | --- | --- |
| `product/project-brief.md` | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | Exact match |
| `product/acceptance-map.md` | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` | Exact match |
| `design/journeys.md` | `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200` | `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200` | Exact match |
| `work/handoffs/WO-004-experience.md` | `665a4942cdd3adac6f777b05a1a6896f59d6c4799c3d2bab0cf3aa5948d17b70` | `665a4942cdd3adac6f777b05a1a6896f59d6c4799c3d2bab0cf3aa5948d17b70` | Exact match |
| `work/verifications/WO-004-quality.md` | `996cab972151fab2ad64fd2405e4227a7aa9db2b4698ea2cf739615aac8cfef1` | `996cab972151fab2ad64fd2405e4227a7aa9db2b4698ea2cf739615aac8cfef1` | Exact match |

## Requirement and acceptance review

| Requirement | Owning journey | Acceptance ownership | Product-semantic result |
| --- | --- | --- | --- |
| R-001 | J-01 | AC-R001-01–03 | Preserved |
| R-002 | J-02 | AC-R002-01–02 | Preserved |
| R-003 | J-03 | AC-R003-01–03 | Preserved |
| R-004 | J-04 | AC-R004-01–03 | Preserved |
| R-005 | J-05 | AC-R005-01–03 | Preserved |
| R-006 | J-06 | AC-R006-01–03 | Preserved |
| R-007 | J-07 | AC-R007-01–03 | Preserved |
| R-008 | J-08 | AC-R008-01–03 | Preserved |
| R-009 | J-09 | AC-R009-01–03 | All IDs present, but AC-R009-02 is narrowed |
| R-010 | J-10 | AC-R010-01–03 | Preserved |
| R-011 | J-11 | AC-R011-01–03 | Preserved |

The ownership table contains all 32 accepted IDs exactly once, with no missing, surplus, duplicate, or owner-prefix mismatch. The 11 frozen requirements remain represented one-to-one and are not reprioritized.

## Boundary review

- Data boundaries remain intact: DI-01 through DI-05 are the supported context, DI-06 exists only through initiated portability, DI-07 is not collected, and DI-08 through DI-13 remain excluded or prohibited (`design/journeys.md:23-29,69-81,255-267`).
- Offline and integration boundaries remain intact: J-07 preserves the core loop without network, account, backend, synchronization, AI, Calendar, or Keep access and prohibits later silent upload or processing (`design/journeys.md:198-219`).
- External-action boundaries remain intact for promises, waiting items, reflection, Calendar/Keep, sharing, telemetry, and AI (`design/journeys.md:137-149,183-196,207-218`).
- Notification behavior remains conditional, configurable, optional, non-coercive, and nonessential to the core loop (`design/journeys.md:221-244`).
- Restore replacement and full deletion retain explicit initiation, consequence disclosure, confirmation, cancellation safety, and observable completion/no-effect behavior (`design/journeys.md:270-316`).
- Specialized workflows, work data, remote services, paid dependencies, multi-user behavior, launch, and broader distribution are not introduced.

## Finding F-01 — Added export confirmation narrows AC-R009-02

The frozen Product semantics make initiation and destination choice the accepted user actions for export or backup:

- R-009 states that Jude can explicitly initiate export or backup and choose its destination (`product/project-brief.md:84`).
- AC-R009-01 prohibits creating or moving a copy before initiation and destination choice (`product/acceptance-map.md:74`).
- AC-R009-02 states that when Jude explicitly initiates the action and chooses its destination, the observable outcome is a supported-data copy directed to that destination with completed/no-effect status (`product/acceptance-map.md:75`).

Revision 0.1 adds a further mandatory condition:

- Its global boundary says export/backup requires “final confirmation” (`design/journeys.md:29`).
- J-09 requires a separate confirmation after destination selection and permits the copy attempt only after that confirmation (`design/journeys.md:258-260`).
- Cancellation at that added confirmation prevents the copy (`design/journeys.md:265`).
- The owner handoff records this as a deliberate decision (`work/handoffs/WO-004-experience.md:21`).

Consequently, a user who performs every action frozen in AC-R009-02—explicit initiation and destination choice—does not receive the accepted outcome unless an additional action is completed. This adds journey-level product behavior and narrows the accepted portability criterion. Exact interaction details were deferred to Experience, but Experience may not make a new action a prerequisite for an already-frozen acceptance outcome.

The Quality record’s structural trace findings remain valid, but exact ID presence does not resolve this semantic mismatch.

## Required remediation

Return J-09 to Experience for alignment with the frozen initiation-and-destination acceptance semantics. If a separate mandatory confirmation is to remain an acceptance condition, it requires Product change control before inclusion in the journey. Reproduce the revised artifact hash and repeat verification. No irreducible Principal exception is identified.

## Verdict

`BLOCK`