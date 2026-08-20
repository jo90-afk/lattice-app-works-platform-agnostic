# Host Adapters

Adapters explain how a host consumes the canonical agency and guarded state. They do not redefine policy.

| Adapter | State access |
| --- | --- |
| `local/` | Direct CLI and local SQLite index |
| `codex/` | Root `AGENTS.md` plus direct CLI |
| `claude/` | `CLAUDE.md` imports root guidance plus direct CLI |
| `chatgpt-work/` | Scoped frontier projection plus revisioned delta |

No adapter may select a default product, create a competing backlog, approve its own work, or promote a project-specific truth into agency policy.
