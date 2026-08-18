# Lattice App Works Portfolio Registry

**Agency version:** 2.1.0  
**Principal:** Jude O'Neill  
**Principal scope:** Sole human Principal for the agency and all currently registered projects  
**Updated:** 2026-08-06 — Gate 2 internal runtime-block checkpoint

## Scheduling policy

- Maximum concurrent specialist threads: 3 across the portfolio
- Order: Principal priority, then dependency readiness, then oldest ready work
- A blocked project does not stop unrelated ready work
- Cross-project priority changes require a Principal decision; routine scheduling inside this order is Director-owned

## Registered projects

| Project ID | Name | Lifecycle | Priority | Current gate | Current action | Capsule source |
| --- | --- | --- | --- | --- | --- | --- |
| `plos-001` | Personal Life OS | Active | 1 | Gate 2 — Experience | Internal runtime block; reissue WO-007-OPS-RCA after fresh session allocation | `Personal_Life_OS_Project_Capsule_plos-001_v2.1.0.md` |

## Portfolio decisions pending

None.

## Boundary

This registry owns identity, priority, capacity, and capsule routing only. Product mandates, platform choices, requirements, data rules, integrations, evidence, and release state belong in their respective project capsules. The registry cannot amend the Agency Kernel.