# Work Order: WO-[number] — [Deliverable]

**Project ID:** [Stable project ID]  
**Project root:** `projects/[project-id]`  
**Status:** NOT READY | READY | IN PROGRESS | BLOCKED | DONE BY OWNER | CHANGES REQUESTED | REMEDIATING | VERIFIED | ACCEPTED | AWAITING PRINCIPAL  
**Owner role:** [Exactly one role]  
**Verifier:** [Exactly one different agent role]  
**Mandatory reviewers:** [None, or named roles]  
**Gate:** [Intake | Intent | Experience | Architecture | Test design | Implementation | Convergence | Release readiness | Learn]  
**Priority:** [Critical | High | Normal | Low]

## Objective

One observable result, expressed without prescribing work outside the owner's domain.

## Non-goals

- Explicitly excluded work:

## Inputs

| Artifact | Version/revision | Why required |
| --- | --- | --- |
| | | |

## Output

- Exact owned path:
- Artifact type:

The output path must be inside the named project root, writable by the owner in `agency.yaml`, and writable by no other role.

## Acceptance criteria

1. A criterion the verifier can reproduce.

## Constraints

- Product:
- Design:
- Contract:
- Security/privacy:
- Performance/reliability:
- Tooling/environment:

## Dependencies

- Must be `VERIFIED` or `ACCEPTED` first:
- Work orders blocked by this output:

## Validation method

- Primary verification question:
- Verifier will run or inspect:
- Evidence to retain:

## Mandatory review questions

| Reviewer | Narrow review question | Evidence expected |
| --- | --- | --- |
| None, or role | | |

The Director cannot set `VERIFIED` until the primary verifier returns `SATISFIED` and every mandatory reviewer returns `CONCUR` in a recorded verification. Once verified, a fresh Assurance Governor thread decides routine gate progression.

## Allowed decisions

List choices the owner may make without escalation.

## Escalation triggers

- Requirement or contract change: route to the owning agent through change control
- Agency or project mandate change
- Cross-project priority or capacity tradeoff
- New paid commitment
- New or changed sensitive-data policy
- Destructive or irreversible action
- Externally visible person/service action
- Material residual-risk acceptance
- Mandate, priority, or release-scope tradeoff
- Production launch
- Any additional trigger must name its authority in `agency.yaml`

Routine defects, ownership routing, reversible no-cost choices, and gate approval are agent-managed and are not Principal escalation triggers.

## Director readiness check

- [ ] One owner
- [ ] One project ID and project root
- [ ] One independent verifier
- [ ] Mandatory reviewers named, if any
- [ ] Every reviewer has one narrow question
- [ ] Versioned inputs
- [ ] Owned output path
- [ ] No input or output from another project unless a versioned shared dependency is named
- [ ] Testable criteria
- [ ] Dependencies resolved
- [ ] Consequence boundaries decided
- [ ] Routine approver is Assurance Governor
- [ ] Any Principal escalation names an exact exception predicate