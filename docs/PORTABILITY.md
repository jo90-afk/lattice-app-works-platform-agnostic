# Portability contract

## Canonical rule

The repository is the only canonical state. It consists of an Agency Kernel, one Portfolio Registry, and isolated Project Capsules. Host adapters only explain how a host loads or exports that state; they never redefine roles, gates, write domains, Principal authority, or project state.

## Supported operation paths

| Path | How it loads Lattice | Persistence boundary |
| --- | --- | --- |
| Generic local agent | Open the repository root and read AGENTS.md | Checked-out repository |
| Codex | Start in the repository root | Current working tree and AGENTS.md |
| Claude Code | Start in the repository root | CLAUDE.md importing AGENTS.md, plus working tree |
| ChatGPT Work | Upload a generated source pack and set Project instructions | Uploaded sources are a replaceable snapshot |
| GitHub | Store, review, and validate the repository | Git history and repository files |

## Adapter constraints

- An adapter may add concise host startup instructions.
- An adapter may package canonical paths for a host that cannot read a repository.
- An adapter must declare whether its copies are snapshots.
- An adapter must not create a divergent policy source.
- An adapter must not select a default project, platform, integration, backend, or model behavior.

## Hosted snapshot rule

Regenerate the pack after substantive repository changes:

    python3 scripts/lattice.py export-chatgpt-work --project <project-id> --overwrite

The output keeps the Agency Kernel, Portfolio Registry, and selected Project Capsule separately labelled inside one uploadable source file. A hosted agent must return replaceable updates rather than silently treating its chat transcript as durable state.
