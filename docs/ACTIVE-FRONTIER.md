# Active Frontier Runtime

The active frontier is a query over current state, not a stored queue. It can contain five action kinds:

| Action | Appears when | Durable result |
| --- | --- | --- |
| `satisfy_condition` | An active condition is unknown or unmet and its dependencies pass | Submission with artifact and evidence references |
| `review_submission` | A pending submission needs a required independent verdict | Review evidence and updated condition state |
| `advance_milestone` | Every readiness predicate passes | Accepted milestone event |
| `resolve_exception` | A deduplicated block remains unresolved | Resolution and, when applicable, reset condition |
| `fulfill_commitment` | A genuine surviving obligation is open | Fulfilled commitment event |

## Context compilation

A condition action receives only:

- its objective and milestone;
- the condition and owner/verifier roles;
- explicitly linked requirements, constraints, decisions, contracts, risks, and artifact records;
- explicitly linked truths, even when they live in background attention;
- prerequisite condition status; and
- the three most recent submissions.

Unlinked project history is omitted. Review actions add only the submitted claim and artifact references. This is the main reasoning-token control surface.

## WIP and leases

The default project WIP is three leases and role WIP is one lease per project. Leases expire after 60 minutes unless configured otherwise. They are local coordination state and are excluded from Git snapshots. A candidate action that is never claimed leaves no residue.

## State-change behavior

Changing a linked input invalidates the condition and its active downstream dependents. Reverting or superseding an input causes obsolete candidate actions to disappear on the next query. An accepted past milestone remains historical; new change belongs in a new active milestone.

## Basic cycle

    python3 scripts/lattice.py frontier --project sample-001 --role architecture
    python3 scripts/lattice.py claim --project sample-001 --role architecture --actor architecture-1
    # edit owned files and run relevant checks
    python3 scripts/lattice.py submit --lease <lease-id> --role architecture \
      --summary "Contract updated and checked" --artifact projects/sample-001/contracts/api.yaml

The verifier repeats `frontier` and `claim` under its own role, then records a structured verdict.
