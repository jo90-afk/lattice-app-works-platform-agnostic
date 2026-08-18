# Lattice 2.2 Portability Validation

**Validated scope:** agency/portfolio/project separation, 11 roles, 22 disjoint write domains, independent verification, Assurance gate authority, host adapter boundaries, and snapshot export integrity.

| Check | Expected result |
| --- | --- |
| Agency model | Persistent multi-project organization; no default product or platform |
| Canonical state | Kernel, portfolio registry, and isolated project capsules |
| Role map | Eleven canonical roles |
| Writable ownership | Twenty-two non-overlapping domains |
| Routine gates | Assurance approves routine progression from independent evidence |
| Principal boundary | Mandate, consequence exceptions, portfolio tradeoffs, and production launch |
| Local hosts | Use checked-out repository and AGENTS.md |
| Claude Code | CLAUDE.md imports AGENTS.md |
| ChatGPT Work | Uses a labelled, regenerated source snapshot |
| GitHub | Optional storage, review, and CI adapter |

## Portability invariants

- The Agency Kernel contains no live project ID, product mandate, platform default, integration rule, or project gate state.
- The Portfolio Registry carries project identity and scheduling state, but no product requirements.
- Each Project Capsule carries one project's state and no copied agency governance.
- A host adapter adds startup/export mechanics only. It cannot change governance.
- A hosted pack is validated against canonical files and must be regenerated after substantive source changes.
- Accepted project evidence survives an agency runtime upgrade.
