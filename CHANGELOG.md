# Changelog

## 0.0.5

- Reframed Lattice around a durable, host-agnostic control plane rather than competing with coding-agent runtimes.
- Added the first host-neutral adapter boundary and stable control-plane read model.
- Added host/workspace-aware claims, durable lifecycle events, and audited expired-lease recovery.
- Routed the primary claim path through the control plane.
- Added deterministic, fail-closed lifecycle hooks.
- Kept operational lifecycle telemetry from advancing semantic project revisions, so host events do not stale valid hosted deltas.
- Added explicit event sequencing alongside semantic revision reporting in the control read model.
- Compensate failed post-claim hooks by releasing the lease and recording `hook_failed` plus `claim_aborted`, so no failed claim remains hidden in flight.
- Added the first dependency-free local control surface and `/api/state` projection.
- Removed legacy process-backlog artifacts and restored a clean neutral seed contract.
- Added release-version consistency checks so future PRs cannot land with stale README or seed metadata.

## 0.0.4

- Added a selectively loaded, primary-source-grounded expertise library for all 11 agent roles.
- Replaced the Android-only builder with a platform-neutral Application Engineer while preserving the 11-role and 22-write-domain model.
- Added open-ended project capability manifests and common Android, Apple, web, Windows, Linux, CLI, and cross-platform expertise packs.
- Added an expertise resolver that reports unknown platforms without rejecting them or loading the entire library.
- Included only action-relevant role and platform expertise in scoped ChatGPT Work exports.
- Added validation and regression coverage for expertise integrity, platform aliases, unknown-platform fallback, and export scoping.

## 0.0.3

- Replaced persistent work orders with a query-derived active frontier.
- Added guarded SQLite state, Git-friendly snapshots, expiring leases, WIP limits, and revision checks.
- Replaced routine gate documents with continuously evaluated milestone conditions.
- Added independent submissions and structured review verdicts.
- Added bounded retries with one deduplicated exception after exhaustion.
- Restricted durable commitments to the Director and Principal.
- Added a versioned truth ledger with frontier/background attention, contradiction preservation, consequence invalidation, and transition history.
- Rebuilt ChatGPT Work exports as scoped execution packs with one-operation hosted deltas.
- Preserved local, Codex, Claude Code, ChatGPT Work, and GitHub portability.

## 0.0.2

- Published the sanitized, platform-agnostic seed used as the migration base.
