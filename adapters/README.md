# Host adapters

These are compatibility shims, not a second control plane.

| Adapter | Purpose |
| --- | --- |
| local/ | Steps for a generic local, repository-aware agent |
| codex/ | Codex startup guidance using root AGENTS.md |
| claude/ | Claude Code startup guidance using root CLAUDE.md |
| chatgpt-work/ | Snapshot generation and upload guidance |

All policy remains in the canonical Agency Kernel. No adapter may select a default project or platform, redefine a role, or approve a gate.
