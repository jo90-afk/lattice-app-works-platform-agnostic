# Local adapter

This adapter works with any local AI agent that can read Markdown and edit a checked-out repository.

1. Open the repository root.
2. Read AGENTS.md, agency.yaml, portfolio/registry.md, and portfolio/status.md.
3. Select one project and read only its manifest, current status, ready work order, and directly relevant inputs.
4. Use the applicable role brief in agents/.
5. Validate before handoff:

       python3 scripts/lattice.py validate

The local runtime supplies tools; Lattice supplies authority boundaries and durable records. A missing tool or permission is a blocker, not evidence.
