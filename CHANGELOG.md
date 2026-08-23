# Changelog

## 0.1.5

- Preserve milestone context after Assurance acceptance so Principal launch decisions remain attached to the exact accepted release milestone.
- Expose complete milestone history in the project read model and detail screen.
- Use the latest accepted milestone as the portfolio card context when a project has no active milestone.

## 0.1.4

- Active portfolio rendering now excludes inactive/seed/history projects so the project cards agree with the active-project summary and navigation counts.

## 0.1.3

- Rebuilt the human surface as a warm portfolio dashboard modeled on the public Lattice site rather than an operations console.
- Made projects the primary management unit with compact milestone progress and a live per-project agent status roster derived from leases, verification, frontier work, blocked conditions, and Assurance readiness.
- Moved evidence, consequence state, and deeper project information to a separate project-detail screen.
- Kept ordinary exceptions inside project management; the top-level human decision strip appears only for state already classified as Principal-only by governance.

## 0.1.2

- Removed Principal-owned actions from each project's `Next` list because the same authority boundary is already presented once, with context and controls, in `Your decisions`.
- Removed Principal-only exceptions from the duplicate project attention list while retaining the affected project's blocked/readiness state.
- Corrected singular/plural decision headline grammar discovered in the 0.1.1 visual sandbox.

## 0.1.1

- Rebuilt the browser control surface around the Principal's control loop instead of the state schema: human decisions first, then each project's current objective, work happening now, work ready next, attention required, and recent accepted changes.
- Made Principal-only exceptions and Principal-owned commitments directly actionable in the browser by claiming the exact currently advertised Principal action key and executing the existing guarded lifecycle rather than creating a second mutation path.
- Kept evidence, frontier truths, and consequence relationships available as drill-down inspection state instead of expanding them into the primary dashboard hierarchy.
- Added responsive action forms with explicit decision consequences and durable decision notes, while preserving `/api/state` as the machine-readable supervision projection.

## 0.1.0

- Started the public-beta release on the sanitized 0.0.8 control-plane baseline.
- Added a dependency-free, non-destructive `doctor` preflight with human and machine-readable output for Python support, repository layout, release metadata, canonical repository/state validation, local writeability, and configured backend readiness.
- Made Postgres preflight explicit only when `LATTICE_DATABASE_URL` is configured; SQLite remains the zero-dependency local default.
- Added one documented bootstrap path from sanitized clone through initialization, mandate confirmation, objective/readiness encoding, frontier claim, evidence submission, independent verification, Assurance acceptance, inspection, and recovery.
- Aligned public release metadata across `VERSION`, README, seed manifest, changelog, and the control-surface release identifier without changing `agency_version`, state schema, adapter protocol, or read-model version.
- Added portable migration status plus self-describing snapshot backup/restore tooling with explicit refusal when active local leases make rollback unsafe or when a shared Postgres store is authoritative.
- Added machine-readable capability negotiation that separates public release, Agency compatibility, state schema, host-adapter protocol, hosted-delta/read-model versions, backends, operations, and feature support.
- Added cross-platform fresh-seed CI on Python 3.10 for Ubuntu, Windows, and macOS using the same `doctor`, initialization, validation, project creation, and frontier commands documented for public users.
- Added public-beta guidance for repository privacy boundaries, stable 0.1 contracts, supported local environments, initialization reproducibility, and guarded rollback.

## 0.0.8

- Added a versioned evaluation scenario registry covering every 0.0.8 roadmap scenario class: greenfield delivery, cross-component refactoring, migration, CI remediation, ambiguous requirements, contradictory information, worker loss, verifier disagreement, concurrent artifact conflict, and multi-project contention.
- Added a dependency-free evaluation harness that validates versioned run results and computes routine autonomy, false acceptance, unnecessary escalation, recovery success, state divergence, verification catch rate, missing-information blocked time, and context volume per accepted change.
- Made unexercised metric denominators report as unknown rather than zero, preventing absent evidence from appearing as perfect reliability.
- Added host-neutral state and acceptance fingerprints plus cross-host equivalence reporting so portability is measured rather than assumed.
- Documented the separation between evaluation evidence and project authority: evaluation results observe control-plane behavior but do not bypass guarded project transitions.
- Added executable greenfield delivery, verifier-disagreement, and worker-loss/recovery scenarios that drive the production claim, submission, independent verification, recovery, and Assurance boundaries and emit validated evaluation results.
- Added semantic and acceptance fingerprints that exclude generated runtime identity, timestamps, leases, workspaces, hosts, and event ordering while retaining governed project meaning and evidence/verification outcomes.
- Added a CI gate that runs the executable scenarios, writes their result JSON, and aggregates the resulting autonomy evidence before the full SQLite/Postgres regression suite.
- Added an ambiguous-requirements scenario proving a Principal-only exception leaves no specialist scheduler assignment, measures blocked-information time, and records a necessary rather than unnecessary escalation.
- Added a contradictory-information scenario proving a newly linked material contradiction reactivates and contests truth, preserves the previously accepted truth version as historical provenance, invalidates current condition satisfaction, increments its state version, and re-derives owner work without accepting the milestone.
- Added a multi-project contention scenario proving a two-slot portfolio dispatches in recorded order, creates no durable queue, and admits the third project as capacity is released while all three progress toward independent verification.
- Made the executable evaluation aggregate fail closed when any scenario result reports `outcome: failed`; successful process execution alone cannot make a failed evaluation pass CI.
- Added a live-Postgres concurrent-artifact-conflict evaluation that races two hosted deltas prepared from one observed revision, requires one durable winner and one stale rejection, then independently verifies the surviving submission.
- Kept concurrency rejection separate from verification metrics: serialization proves zero accepted-state divergence, while Quality verification remains a distinct evidence event rather than inheriting a synthetic catch.
- Added a cross-component-refactor evaluation where Application and Services preserve one Architecture-owned contract and both require independent Quality verification before Assurance acceptance.
- Added a migration evaluation that proves a governed contract revision invalidates earlier satisfaction, preserves the old accepted version as provenance, and requires fresh verification against the new version before acceptance.
- Added a CI-remediation evaluation that exercises bounded failure, durable retry state, corrected resubmission, independent verification, and successful acceptance without premature escalation.
- Expanded the fail-closed CI evidence gate to all ten registered 0.0.8 roadmap scenarios, including the real multi-connection Postgres race, before the full regression suite.

## 0.0.7

- Started the human supervision release on the same canonical read model and state authority used by the runtime.
- Made the local control surface open the configured operational backend instead of always reading local SQLite, so shared Postgres deployments and human supervision cannot silently diverge.
- Added a supervision projection with portfolio summary, Principal-only decision count, recent accepted changes, backend identity, and operational telemetry without creating a second writable state model.
- Expanded the read-only browser surface to show portfolio-level activity, semantic/event revision identity, frontier truths, evidence, verification, exceptions, and runtime health signals.
- Enriched every Principal-only exception and Principal-owned commitment with the exact decision required, the authority rule that forced escalation, affected project/target state, available durable evidence, and only state-machine-supported choices with their consequences.
- Rendered decision-grade Principal cards while keeping the browser strictly read-only; resolve/fulfill actions still require the guarded runtime rather than an implicit UI mutation path.
- Added a derived project consequence graph over the active objective, linking records, truths, condition dependencies, submissions, reviews, evidence, exceptions, commitments, milestones, and currently derived actions without storing a second graph or plan.
- Rendered consequence relationships as an accessible source → relation → target view, so the control surface explains both why work exists and why accepted state is trusted without depending on a decorative spatial visualization.
- Added temporal supervision derived from existing timestamps and events: lease age/remaining authority, verification wait, exception age, blocked-condition age, completed action durations, retries, recovery counts, exception frequency, and verification failure rate.
- Exposed raw elapsed seconds and rates in `/api/state` while rendering human-readable ages in the browser; no synthetic health score or new trace state is introduced.
- Added a real-Postgres mixed-portfolio exit scenario proving one read-only supervision projection can simultaneously explain live leased work, accepted/evidenced change, blocked remediation, the exact Principal-only decision boundary, and operational history without reading project files or creating a UI mutation path.

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
- Made a live Postgres database authoritative after one-time empty-store bootstrap so a stale repository snapshot cannot silently rewind shared operational state.
- Made shared snapshot publication explicit with `scripts/shared_state_checkpoint.py`; ordinary Postgres worker mutations no longer require or rewrite a shared checkpoint file.
- Added a queue-free bounded scheduler that derives assignments from portfolio order, current frontier, available workers, and live portfolio/project/role capacity.
- Scheduler plans are read-only and Principal actions are never auto-scheduled; dispatch persists only leases granted through the existing atomic host-claim path and continues unrelated projects when one is blocked.
- Made canonical `agency.yaml` role write domains executable: repository-local submissions are rejected before mutation when the leasing role does not own the artifact path or the path crosses project boundaries.
- Made the bounded scheduler avoid concurrent same-project roles with overlapping canonical write domains instead of relying on separate leases as a social convention.
- Made truth revision compare-and-swap: the primary `truth-revise` command requires the exact observed truth version, and stale writers are rejected under the project write lock rather than overwriting a newer proposition.
- Serialized hosted-delta acceptance by rechecking `base_revision` inside the project write boundary immediately before semantic mutation; two deltas prepared from the same old revision cannot both commit even when they target different actions.
- Routed the primary CLI claim and hosted-delta paths through the 0.0.6 atomic implementations so legacy entrypoints cannot bypass concurrency semantics.
- Made Postgres global snapshot revision allocation atomic with `UPDATE ... RETURNING`, preserving distinct monotonic revisions when unrelated projects mutate concurrently under different project advisory locks.
- Made direct Postgres semantic mutations intrinsically acquire the canonical project advisory lock, so project status, objectives, milestones, records, truths, readiness conditions, commitments, and exceptions cannot bypass shared-writer serialization.
- Added a live Postgres same-record race proving concurrent direct writers become successive versions rather than duplicate-version failures or lost updates.
- Added an integrated live-Postgres exit scenario proving the queue-free scheduler can dispatch three projects and carry concurrent application, independent verification, and Assurance workers through to three coherent accepted milestones with no residual leases or frontier work.

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
