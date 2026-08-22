# Local adapter

Any repository-aware agent can run Lattice with Python's standard library.

1. Read root `AGENTS.md`.
2. Run `python3 scripts/lattice.py status`.
3. Query and claim one frontier action for one project and role.
4. Resolve expertise with `python3 scripts/lattice.py expertise --project <project-id> --role <role>` and load only its returned paths.
5. Edit only owned paths.
6. Submit or review through the guarded CLI.
7. Run `python3 scripts/lattice.py validate` before commit.

The local SQLite index is created automatically. Durable state is exported to `state/current.json`; no agent edits either representation directly.
