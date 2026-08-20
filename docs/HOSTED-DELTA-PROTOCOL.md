# Hosted State Delta Protocol

ChatGPT Work cannot share a live local SQLite transaction. Lattice therefore exports a revisioned, scoped frontier projection. The hosted agent selects at most one supplied action and returns one delta after producing the exact repository-file changes.

```json
{
  "format": "lattice-state-delta",
  "schema_version": 1,
  "base_revision": 12,
  "project_id": "sample-001",
  "action_key": "condition:condition-001:satisfy:v2",
  "role": "architecture",
  "actor": "chatgpt-work",
  "outcome": {
    "type": "submit",
    "summary": "Updated the contract and retained validation output.",
    "artifact_refs": ["projects/sample-001/contracts/api.yaml"],
    "evidence_ref": "projects/sample-001/quality/api-validation.txt"
  }
}
```

Apply it only after reconciling its artifact changes:

    python3 scripts/lattice.py apply-delta --file returned-delta.json

The command rejects a stale project revision, unknown action key, wrong role, invalid verdict, or action that has disappeared from the frontier. Revisions are project-scoped, so an unrelated project's mutation does not invalidate this packet. A delta contains exactly one outcome, so partial multi-action reconciliation cannot corrupt state. Regenerate and re-upload the execution pack after each accepted delta.
