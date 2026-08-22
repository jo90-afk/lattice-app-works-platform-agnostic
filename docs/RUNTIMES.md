# Runtime Guide

## Repository-aware runtimes

Local agents, Codex, and Claude Code share the same pattern: read root guidance, query the frontier, claim one lease, resolve the role's smallest expertise set, edit role-owned files, and record the result through the CLI. The local SQLite index is generated automatically from `state/current.json`.

Only one writable SQLite runtime should operate on a project snapshot at a time. Separate processes can safely read; simultaneous remote writers need a shared transactional database or serialized delta application.

## ChatGPT Work

ChatGPT Work receives a generated execution projection rather than the full state archive. A pack contains at most the requested frontier limit, linked context, relevant role prompts and expertise, project core files, and referenced artifacts. Application platform packs come only from the project's declared capabilities.

The hosted result must return one state delta. Applying the delta checks the base revision and recomputes the action before accepting it. Regenerate the pack after every accepted mutation.

## Database growth

SQLite is the default because it is local, portable, inspectable, and included with Python. Move the operational adapter to Postgres only when multiple simultaneous remote workers or durable server-side queues are actually required. Keep the snapshot contract and guarded operations stable so host migration does not change agency behavior.
