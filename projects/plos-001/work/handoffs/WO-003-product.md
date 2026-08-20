## Canonical handoff — WO-003

**Status:** Complete; pending independent verification

**Artifact:** `product/acceptance-map.md` v0.1  
**SHA-256:** `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3`

### Frozen inputs

- `product/project-brief.md` v0.1 — SHA-256 exactly reproduced as `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b`
- `work/verifications/WO-002-experience.md` v1.0 — `SATISFIED`, 2026-08-05; locally reproduced SHA-256 `ae87c4ccaa3b0fc16ed62cc5e77eec1304f5b6513a1722953a6976645c4b32a1`

### Product decisions

- Adopted stable IDs `AC-R###-##`.
- Defined the five required ambiguous terms without selecting experience or technical mechanisms.
- Preserved all personal-data, autonomy, offline, destructive-action, paid-dependency, and external-action boundaries.
- Kept all baseline-dependent measures qualitative.
- Assigned unresolved design, architecture, testing, risk, and release matters to their later owners.

### Assumptions

No new assumptions were introduced. Frozen assumptions A-01 through A-08 remain unresolved pending their named real-use or specialist evidence.

### Owner-side validation evidence

- Requirements: 11/11 mapped exactly once, R-001 through R-011; all retain `Must`.
- Acceptance criteria: 32/32 unique and structurally complete.

  - R-001: 3
  - R-002: 2
  - R-003 through R-011: 3 each

- Every criterion includes a condition, user action or trigger, and observable outcome; zero empty acceptance fields.
- JTBD coverage: JTBD-01, JTBD-02, and JTBD-03 all covered.
- Goal coverage: G-01 through G-04 all covered.
- Boundary coverage: DI-01 through DI-13 and all 11 frozen external/destructive/background/paid classifications traced.
- Positive, negative, offline, notification-control, opt-out, export/backup, restore-confirmation, and deletion-confirmation outcomes are explicit.

### Risks and limitations

This is Product owner-side validation only. It claims no independent verification, Gate 1 acceptance, test result, security verdict, architecture or implementation readiness, production promotion, or launch approval. Notification defaults, interaction states, mechanisms, formats, test implementation, numerical thresholds, risk decisions, and release decisions remain deferred.

**Verification request:** Assign a fresh Experience Lead to independently reproduce the artifact hash and verify WO-003’s primary question: whether every frozen requirement has complete, unambiguous, user-observable acceptance coverage without scope drift or design/architecture prescription.