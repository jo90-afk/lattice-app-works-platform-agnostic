# Build Validation — Lattice 0.0.4

## Structural validation

- Agency Kernel, Portfolio Registry, Project Capsule, and Operational State remain separate.
- 11 role prompts and 22 non-overlapping artifact write patterns are present.
- Obsolete routine process templates and active process-backlog directories are absent.
- SQLite schema, portable snapshot, host adapters, GitHub workflow, and privacy scan pass.
- ChatGPT Work pack matches the current kernel and project revision.
- Expertise catalog, role modules, platform aliases, capability manifests, and scoped export inclusion are validated.

## Behavioral validation

The standard-library unit suite covers:

- scoped context that excludes unlinked project records and background truths;
- action leasing and role WIP enforcement;
- owner submission followed by fresh independent review;
- mandatory-review concurrence;
- record and truth changes invalidating linked active conditions;
- bounded retry exhaustion producing one deduplicated exception;
- Director/Principal-only commitment creation;
- stale hosted-delta rejection;
- snapshot round-trip without ephemeral leases;
- contradiction reactivating background truths while preserving prior versions;
- attention movement preserving truth content versions and transition history;
- a single planned successor milestone and truth promotion upon activation; and
- clean seed initialization, project rename, hosted export regeneration, and validation.
- role expertise resolution, cross-platform aliasing, unknown-platform fallback, and platform-pack export scoping.

Reproduce:

    python3 scripts/lattice.py validate
    python3 -m unittest discover -s tests -v
