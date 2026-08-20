# Ownership Matrix

| Domain | Sole writer | Independent check | Durable representation |
| --- | --- | --- | --- |
| Portfolio identity and order | Director | Principal for retained tradeoffs | `portfolio/` plus state events |
| Project mandate and manifest | Director records Principal intent | Product checks fidelity | Project capsule and state records |
| Product behavior | Product | Experience and Quality as condition reviewers | Product files plus versioned records |
| Interaction design | Experience | Product and Quality | Design files plus conditions |
| Architecture and contracts | Architecture | Builders, Security, and Quality as relevant | Architecture files, ADRs, contracts |
| Client implementation | Activated client builder | Quality | Code, tests, submission, review evidence |
| Services implementation | Services | Quality and Security as relevant | Code, tests, submission, review evidence |
| AI behavior | Intelligence | Quality and Security as relevant | Model code, evals, submission, review evidence |
| Acceptance evidence | Quality | Product or Experience for test-design claims | Tests and structured evidence |
| Security evidence | Security | Assurance checks required presence; Principal accepts material risk | Security files and structured evidence |
| Release mechanics | Release | Quality and Security | Ops/infra artifacts and conditions |
| Milestone acceptance | Assurance | Runtime readiness predicates | Milestone event |
| Production launch | Principal | Not delegated | Principal authorization artifact/event |
| Operational state | Guarded runtime | Schema, revision, role, and WIP checks | SQLite plus `state/current.json` |
| Project truth ledger | Guarded runtime from role assertions | Contradictions and linked conditions expose disputes | Versioned truths and transitions |

Agents contribute across domains through condition inputs, truth links, submissions, and review evidence. They do not create shared process documents or edit another role's artifact.
