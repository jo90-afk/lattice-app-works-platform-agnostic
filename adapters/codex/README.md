# Codex adapter

Start Codex in the repository root. Root `AGENTS.md` is canonical.

Use the guarded runtime before reading broadly:

    python3 scripts/lattice.py status
    python3 scripts/lattice.py frontier --project <project-id> --role <role>
    python3 scripts/lattice.py claim --project <project-id> --role <role> --actor <agent-id>

Treat the claim output as the bounded task context. Use a fresh delegated context for review. Record outcomes through `submit`, `review`, `fail`, or `advance`; do not create process documents or a `.codex` policy fork.
