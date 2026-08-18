# Ownership and Handoff Matrix

All domain paths are relative to one named `projects/<project_id>/` root. The Director additionally owns `portfolio/**` scheduling and registry records. No domain role writes portfolio state, and no artifact owner writes into another project capsule.

| Domain | Sole writer | Required upstream inputs | Independent verifier | Handoff consumer |
| --- | --- | --- | --- | --- |
| Portfolio registry and scheduling status | Director | Principal priorities, project statuses | Principal only for retained priority/capacity decisions | Project Directors and status consumers |
| Project work orders and delivery status | Director | Confirmed project mandate, gates, handoffs | Artifact owner checks task accuracy | Agents assigned to that project |
| Requirements and acceptance map | Product | Principal intent, evidence | Experience | Experience, Architecture, Quality |
| Journeys and UI state specification | Experience | Approved requirements | Quality | Architecture, activated client builders |
| Architecture and shared contracts | Architecture | Requirements, design, constraints | Security; activated builders and Quality review | Builders, Quality, Assurance |
| Android client | Android | Design, contracts, ADRs | Quality; Security when relevant | Quality, Release, Assurance |
| Services and sync | Services | Contracts, ADRs | Quality; Security when relevant | Quality, Release, Assurance |
| AI behavior | Intelligence | Product policy, contracts, AI ADRs | Quality and Security | Activated integrators, Release, Assurance |
| Acceptance and end-to-end evidence | Quality | Requirements, design, contracts, handoffs | Product/Experience review authored test design | Release, Assurance |
| Threat model and risk verdict | Security | Data map, architecture, diffs, evidence | Independent evidence review by Assurance; Principal only for material residual risk | Architecture, builders, Release, Assurance |
| Build and operational readiness | Release | Verified components, gate verdicts | Quality and Security | Assurance |
| Routine gate decision | Assurance | Independent handoffs, verifications, and mandatory reviews | Director checks record completeness; no domain verdict is overridden | Director and all downstream roles |
| Production launch authorization | Principal | Assurance-accepted release packet | Not delegated | Release and Director |

## Boundary examples

- Product specifies “the user can export all personal data.” Experience specifies where the control lives and its states. Architecture specifies the export contract and data boundaries. Builders implement their components. Quality proves completeness. Security checks leakage and authorization. Release verifies the capability in the shipped build.
- Experience may specify an offline state but does not decide the synchronization algorithm. Architecture owns that choice and its contract.
- Quality may demonstrate that an API violates acceptance criteria but cannot edit the service or relax the criterion.
- Security may require remediation or document residual risk but cannot quietly patch and approve the same security-sensitive code.
- Assurance may approve progression but cannot write, repair, test, or primarily verify the artifact under decision.

## Shared-file rule

There are no shared writable files inside a project. When a cross-domain artifact is needed, Architecture owns interface truth, Product owns behavior truth, Assurance owns progression decisions, and the Director owns process records. Other agents contribute through review findings or change requests.

Cross-project reuse is not a shared writable shortcut. The Director must commission a versioned shared asset or contract with an explicit owner and consumers; projects pin a version and cannot mutate it privately.

## Data and migration decision chain

- Product owns which data use is permitted by the approved product intent.
- Architecture owns data classification, schemas, lifecycle, compatibility, and migration strategy.
- Activated data-owning builders implement migrations only inside their components and against the approved strategy.
- Security independently validates data and migration risk.
- Release owns migration execution, stop/recovery procedures, and evidence for the shipped artifact.
- Assurance approves technical progression when the migration stays reversible and inside accepted data policy.
- The Principal decides destructive or irreversible migrations and material changes to personal-data policy.