# Project Manifest: [Project name]

**Project ID:** [stable-id]  
**Project root:** `projects/[stable-id]`  
**Lifecycle:** proposed / active / paused / released / retired  
**Principal:** [human name or registry reference]  
**Priority:** [portfolio rank]  
**Operational state:** `state/current.json` filtered by this project ID

## Mandate reference

- Confirmed mandate: `work/bootstrap.md`
- Confirmation date:
- Mandate version:

## Project-specific properties

- Target users:
- Platforms (keep synchronized with `project/capabilities.json`):
- Cross-platform strategy (`native`, `undecided`, or a named framework):
- Activated builder roles:
- Environments:
- Data classification:
- External services:
- Paid commitments already approved:
- Release boundary:

## Governance inheritance

This capsule inherits the Lattice App Works agency kernel. This manifest may narrow project behavior but cannot redefine agency roles, writable ownership, runtime state rules, assurance authority, or escalation predicates.

## Continuation

- Current objective and milestone: query `python3 scripts/lattice.py status`
- Active frontier: query `python3 scripts/lattice.py frontier --project [stable-id]`
- Background truths: query `python3 scripts/lattice.py truth-list --project [stable-id] --attention background`
- Role expertise: query `python3 scripts/lattice.py expertise --project [stable-id] --role [role]`
- Known internal blockers:
- Principal decisions pending:
