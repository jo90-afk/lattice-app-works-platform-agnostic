# Runtime guide

## Local, Codex, and Claude Code

Use the repository directly. Begin at the root, read canonical guidance, select the project from portfolio/registry.md, and work only in the assigned project namespace.

    python3 scripts/lattice.py validate
    python3 scripts/lattice.py status

Codex reads repository AGENTS.md guidance when started at the project root. Claude Code reads CLAUDE.md; this repository imports the same AGENTS.md rather than maintaining a second policy file.

## ChatGPT Work

ChatGPT projects use uploaded sources and project instructions rather than direct access to an arbitrary local folder. Use the checked-in snapshot at exports/chatgpt-work/plos-001/, or regenerate it after changes. Upload the pack, set the project instructions, and treat the session as a working copy that must be reconciled back into the repository.

## Other agent hosts

If a host can read the repository, use AGENTS.md as its entry point. If it only accepts uploaded text, use the generated hosted pack as a snapshot and preserve the layer labels. Do not create host-specific policy copies.
