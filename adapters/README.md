# Host Adapters

Adapters explain how a host consumes the canonical agency and guarded state. They do not redefine policy.

| Adapter | State access |
| --- | --- |
| `local/` | Direct CLI and local SQLite index |
| `codex/` | Root `AGENTS.md` plus direct CLI |
| `claude/` | `CLAUDE.md` imports root guidance plus direct CLI |
| `github/` | Root `AGENTS.md`, host-neutral project skill, and host-adapter envelopes |
| `chatgpt-work/` | Scoped frontier projection plus revisioned delta |

Reusable execution technique lives under `.agents/skills/`; adapter directories may explain host discovery and transport, but they must not copy the Agency Kernel into host-specific policy.

No adapter may select a default product, create a competing backlog, approve its own work, or promote a project-specific truth into agency policy.
