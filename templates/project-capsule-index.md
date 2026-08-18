# Project Capsule Index: [Project ID]

This source contains only the canonical state for one project. All virtual paths are rooted at `projects/[project-id]/`.

## Required sections

- `PROJECT.md`
- `status/current.md`
- confirmed `work/bootstrap.md`
- current and accepted gate evidence
- active work orders, handoffs, verifications, and decision packets
- current domain artifacts and project-owned source needed for continuation

## Excluded sections

Do not duplicate `AGENTS.md`, `agency.yaml`, `agents/**`, `governance/**`, or `templates/**`. Those belong only to the Agency Kernel.

At checkpoint time, replace the prior capsule for this project. Never merge two full-state capsules for the same project into active sources.