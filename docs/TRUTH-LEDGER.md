# Truth Ledger

The truth ledger preserves project-world propositions when they stop occupying active attention. It separates two questions that ordinary notes often collapse:

1. What is the current epistemic standing of the proposition?
2. Does the current objective need it in working context?

## Epistemic state

| State | Meaning |
| --- | --- |
| `observed` | Recorded observation not yet adopted as stable project truth |
| `accepted` | Current working proposition with adequate support |
| `contested` | A live contradiction or unresolved challenge exists |
| `false` | Evidence disindicates the proposition; history remains |
| `superseded` | A newer proposition has replaced its role without erasing it |
| `unknown` | Current evidence cannot determine it |

## Attention state

| State | Context behavior |
| --- | --- |
| `frontier` | Eligible for active reasoning and broad current-world queries |
| `background` | Retained and searchable; included only through explicit relevance |
| `archived` | Historical and excluded from ordinary context |

Moving a truth to background does not change its epistemic state or content version. The movement has its own transition record with actor, time, and reason. The ledger also retains every readiness condition and milestone that consumed the truth, including the truth version accepted by that condition.

## Reactivation

A background truth returns to frontier attention when an authorized role links it to an active readiness condition or when a contradiction is recorded. Contradictory propositions are both retained and marked contested. Resolving the contradiction requires an explicit revision such as `false`, `superseded`, or newly `accepted`—never deletion.

Changing the statement, status, confidence, source, or materiality creates a new immutable truth version and invalidates linked conditions in the active milestone. Attention movement alone does not invalidate accepted evidence.

## Settling into background

When Assurance accepts a milestone, the runtime moves a linked frontier truth to background only if:

- no active or planned condition still references it; and
- it has no recorded contradiction.

The truth remains available to later objectives. If a future condition links it, the runtime records its return to frontier attention.

## Commands

    python3 scripts/lattice.py truth-add --project sample-001 --key world.api-available \
      --statement "The upstream API is available in test" --epistemic-status observed \
      --attention frontier --confidence 0.8 --source-ref evidence/api-check.txt \
      --material --role quality

    python3 scripts/lattice.py truth-move --truth <id> --attention background \
      --reason "No current milestone depends on this proposition" --role director

    python3 scripts/lattice.py truth-list --project sample-001 --attention background
