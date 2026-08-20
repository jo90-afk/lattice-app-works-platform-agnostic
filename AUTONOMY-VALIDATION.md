# Autonomy Validation — 0.0.3

Validated properties:

- 11 specialized roles and 22 disjoint artifact write domains;
- no routine work-order, handoff, verification, QA-cycle, change-request, gate-decision, or release-gate templates;
- guarded state mutations with project, role, version, and foreign-key checks;
- one active objective and milestone per project;
- configurable project WIP and one lease per role/project;
- independent reviewer enforcement and no owner self-verification;
- automatic readiness recomputation and Assurance-only milestone advancement;
- bounded retries and deduplicated exception promotion;
- Director/Principal-only durable commitment creation;
- truth version history separate from attention transitions;
- background truth omission from unlinked context;
- contradiction reactivation and linked-condition invalidation;
- portable snapshots excluding ephemeral leases;
- stale hosted-delta rejection; and
- sanitized neutral seed data.

Run `python3 scripts/lattice.py validate` and `python3 -m unittest discover -s tests -v` to reproduce structural and behavioral checks.
