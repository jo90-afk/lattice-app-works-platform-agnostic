# Contributing

1. Preserve agency, portfolio, project, and operational-state boundaries.
2. Use the guarded CLI for durable state; never edit the snapshot or SQLite database directly.
3. Do not introduce work-order, handoff, verification, gate-decision, or status-document requirements for routine execution.
4. Keep actions derived, leases ephemeral, commitments rare, and exceptions deduplicated.
5. Preserve independent review and Principal consequence boundaries.
6. Add or update tests for every state transition or policy invariant.
7. Run `python3 scripts/lattice.py validate` and the unit suite before a pull request.

Never commit secrets, credentials, direct personal identifiers, or sensitive fixture data.
