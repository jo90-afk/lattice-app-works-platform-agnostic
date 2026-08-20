# Repository Setup

1. Extract or clone the seed.
2. Run `scripts/lattice.py initialize` with a non-sensitive Principal alias, stable project ID, and project name.
3. Confirm `projects/<id>/work/bootstrap.md`.
4. Add one active objective and milestone.
5. Add versioned records, material truths, and the minimum readiness conditions.
6. Run validation and inspect the derived frontier.
7. Commit the repository, including `state/current.json` but excluding `.lattice/`.

For a new project after initialization, run `python3 scripts/lattice.py project-create --project-id <id> --project-name <name>`. This creates a proposed capsule, registry entry, paused state record, and scoped hosted export. After mandate confirmation, activate it with `python3 scripts/lattice.py project-status --project <id> --status active`. Never reuse another project's state entities or evidence.

Before each commit:

    python3 scripts/lattice.py validate
    python3 -m unittest discover -s tests -v

Regenerate a ChatGPT Work pack only for the project and role that need hosted execution.
