# Changelog

## 0.0.6

- Made hosted action claims acquire SQLite's writer lock before frontier and WIP checks so lease acquisition is serialized at the durable control boundary.
- Added explicit host lease renewal with project, role, and actor ownership checks for long-running workers.
- Added a `renew` host-adapter operation while keeping lease renewal operational: it extends execution authority without advancing semantic project revision.
- Extracted a concurrency-critical state-backend transaction interface with SQLite and Postgres implementations.
- Added a deterministic project-scoped Postgres advisory-lock key so distributed writers can serialize one project's guarded writes without globally blocking unrelated projects.
- Kept Postgres driver selection outside the local-first core; shared deployments load `psycopg` only when explicitly configured.
- Routed leased release, submission, failure, verification, milestone acceptance, commitment fulfillment, and exception resolution through the same project-scoped backend write boundary.
- Recorded the selected state backend on lifecycle telemetry so supervision can distinguish local and shared-writer execution paths.
- Added adversarial multi-connection tests proving a shared verifier lease and Assurance lease produce one durable winner and reject stale second attempts.
- Verified that revising a condition input revokes the worker lease and returns a new versioned action to the frontier, so work based on superseded requirements cannot submit.
- Added a Postgres-backed constructor for the canonical `StateStore` semantics without forking the truth/frontier/verification model.
- Preserved the portable `state/current.json` contract across SQLite and Postgres with explicit backend-neutral ordering and Postgres event-sequence repair after snapshot import.
- Added `LATTICE_DATABASE_URL` shared-store construction and `scripts/shared_host_adapter.py` while keeping SQLite as the default local runtime.
- Added a real Postgres 17 CI service that runs the guarded claim -> submit -> independent review -> Assurance acceptance lifecycle and snapshot round trip on Postgres.

## 0.0.5

- Reframed Lattice around a durable, host-agnostic control plane rather than competing with coding-agent runtimes.
- Added the first host-neutral adapter boundary and stable control-plane read model.
- Added host/workspace-aware claims, durable lifecycle events, and audited expired-lease recovery.
- Routed the primary claim path through the control plane.
- Added deterministic, fail-closed lifecycle hooks.
- Kept operational lifecycle telemetry from advancing semantic project revisions, so host events do not stale valid hosted deltas.
- Added explicit event sequencing alongside semantic revision reporting in the control read model.
- Compensate failed post-claim hooks by releasing the lease and recording `hook_failed` plus `claim_aborted`, so no failed claim remains hidden in flight.
- Added post-transition lifecycle telemetry for release, submission, failure, verification, milestone acceptance, commitment fulfillment, and exception resolution.
- Made completion-hook failures auditable without rolling back already committed guarded state transitions.
- Added a Principal decision inbox derived only from `principal_only` exceptions and Principal-owned commitments.
- Added an executable, versioned host-adapter envelope router for claim, complete, event, inspect, and recover operations.
- Made host-adapter requirements operation-specific so global inspect/recover do not require invented project or host identities.
- Added cross-project and role guards for hosted completion envelopes.
- Made hosted completion retries idempotent by replaying the durable completion event for an already-completed lease.
- Reject missing or path-escaping repository-local project artifacts before a hosted submission mutates project state, preserving the lease for reconciliation and retry.
- Recover expired leases with their recorded host/workspace provenance and automatically record `workspace_abandoned` when the vanished host did not report abandonment itself.
- Bracket hosted completion with a durable `completion_started` marker and reconcile a missing final lifecycle event from the matching committed semantic transition after process loss.
- Reject changed completion intent and stale post-expiry replay rather than guessing after interruption.
- Added a host-neutral `lattice-execution` Agent Skill under `.agents/skills` so execution technique can be loaded selectively without becoming a second authority system.
- Added a GitHub hosted-agent adapter that uses canonical root `AGENTS.md`, the shared execution skill, and the same versioned host-adapter envelopes as other runtimes.
- Added the first dependency-free local control surface and `/api/state` projection.
- Exposed milestone readiness and the submission/review evidence chain directly in the control read model and local supervision surface.
- Removed legacy process-backlog artifacts and restored a clean neutral seed contract.
- Added release-version consistency checks so future PRs cannot land with stale README or seed metadata.

## 0.0.4

- Added a selectively loaded, primary-source-grounded expertise library for all 11 agent roles.
- Replaced the Android-only builder with a platform-neutral Application Engineer while preserving the 11-role and 22-write-domain model.
- Added open-ended project capability manifests and common Android, Apple, web, Windows, Linux, CLI, and cross-platform expertise packs.
- Added an expertise resolver that reports unknown platforms without rejecting them or loading the library.
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
