# Runtime guide

## Local, Codex, and Claude Code

Use the repository directly. Begin at the root, read canonical guidance, select a project from portfolio/registry.md, and work only in the assigned project namespace.

    python3 scripts/lattice.py validate
    python3 scripts/lattice.py status

Codex reads repository AGENTS.md guidance when started at the project root. Claude Code reads CLAUDE.md; this repository imports the same AGENTS.md rather than maintaining a second policy file.

## ChatGPT Work

ChatGPT Projects use uploaded sources and Project instructions rather than direct access to a local folder. After seed initialization, use the matching export under exports/chatgpt-work/<project-id>/. Upload the pack, set the Project instructions, and reconcile exact file changes back into the repository.

## Other agent hosts

If a host can read the repository, use AGENTS.md as its entry point. If it only accepts uploaded text, use a generated hosted pack as a snapshot and preserve the layer labels. Do not create host-specific policy copies.
