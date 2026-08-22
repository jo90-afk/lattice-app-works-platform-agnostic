# Changelog

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
