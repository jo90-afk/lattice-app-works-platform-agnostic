# Migrate Lattice to the 2.1 Portfolio Model

This migration separates durable agency governance from portfolio scheduling and project state. It does not invalidate any accepted project mandate, artifact, work order, evidence, gate decision, or Principal decision.

## Preserve every project

For each existing project, keep all:

- confirmed bootstrap mandates and Gate 0 decisions;
- product, design, architecture, contract, implementation, test, security, assurance, release, and environment artifacts;
- `work/` and `status/` records;
- accepted Principal decisions and authority delegations; and
- hashes or versions used by accepted gates.

Do not rerun intake or ask the Principal to reconfirm accepted gates solely because the namespace changed.

## Create the portfolio layer

1. Create `portfolio/registry.md` from `templates/portfolio-registry.md`.
2. Record the human Principal once in the registry.
3. Give every existing project a stable ID and priority.
4. Create `portfolio/status.md` containing only scheduling, capacity, and capsule freshness—not product requirements.

## Isolate project capsules

Move or virtually prefix each project's state under `projects/<project_id>/`. Add `PROJECT.md` from `templates/project-manifest.md`.

Paths inside existing artifacts may remain project-relative. The capsule index establishes their project root. Preserve bytes of frozen or hashed artifacts whenever possible; namespacing a hosted `Source:` heading does not require rewriting contents.

Do not copy these agency files into project capsules: `AGENTS.md`, `agency.yaml`, `.codex/**`, `agents/**`, `governance/**`, or `templates/**`. They belong once in the Agency Kernel.

## Hosted source migration

Replace a monolithic project pack with three separately replaceable source types:

- one stable Agency Kernel;
- one Portfolio Registry; and
- one current capsule per project.

Project updates replace only that project's capsule and, when scheduling state changes, the registry. Agency maintenance replaces only the kernel.

## Resume

Start a new Work turn with `prompts/activate-agency.md`. The Director validates the registry, preserves every project's accepted state, and continues ready work in portfolio order without reopening completed gates.