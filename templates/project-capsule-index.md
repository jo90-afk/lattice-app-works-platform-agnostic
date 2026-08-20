# Project Capsule Index: [Project ID]

This source contains only the canonical state for one project. All virtual paths are rooted at `projects/[project-id]/`.

## Required sections

- `PROJECT.md`
- confirmed `work/bootstrap.md`
- operational state referenced by project ID in `state/current.json`
- current and background truth-ledger propositions
- submissions, reviews, and evidence represented in guarded state
- current domain artifacts and project-owned source needed for continuation

## Excluded sections

Do not duplicate `AGENTS.md`, `agency.yaml`, `agents/**`, `governance/**`, or `templates/**`. Those belong only to the Agency Kernel.

At checkpoint time, reconcile the project capsule and its matching state revision together. Never merge two full-state snapshots for the same project.
