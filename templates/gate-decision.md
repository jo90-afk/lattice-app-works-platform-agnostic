# Gate Decision: [Gate] — [Project/version]

**Project ID:** [Stable project ID]  
**Project root:** `projects/[project-id]`  
**Approver:** Assurance Governor  
**Date:** YYYY-MM-DD  
**Gate evidence:** [Work order and verification-record references]
**Remediation cycle:** 0 | 1 | 2 | 3-DIAGNOSTIC

## Decision

Choose exactly one:

- `ACCEPT`
- `ACCEPT_WITH_DEBT`
- `REMEDIATE`
- `ESCALATE`

## Rationale

State whether complete independent evidence from this project permits progression inside its confirmed mandate. Identify every open finding and explain why the selected outcome follows `governance/autonomy-policy.md`.

## Conditions or scope boundary

- None, or list conditions that do not alter the verified artifact.
- For `ACCEPT_WITH_DEBT`, name each `MINOR`/`NOTE`, owner, due condition, bounded impact, and regression guard.
- For `REMEDIATE`, name the failed claim, artifact owner, retest evidence, and downstream work paused.
- For `ESCALATE`, name exactly one Principal exception predicate and the proposed decision packet.

If the desired condition would change requirements, design, contracts, implementation, or expected evidence, use `REMEDIATE` and initiate change control instead of accepting an unverified variant.

Return this decision to the Director; do not write directly into `work/gate-decisions/`.