# Reconcile GitHub project state

An active capsule can outlive its merged pull request. A release can be published
while its capsule still says publication is pending. An old open branch can have
no commits ahead of its current base. These are discrepancies in external facts;
they do not establish Lattice acceptance or authorize another publication.

The GitHub adapter compares explicit declarations with frozen GitHub GET
responses. `github-check` is read-only and works for connector-mode target
repositories without a local Lattice database. `github-reconcile` records those
observations in an initialized project's existing truth ledger. Both commands use
the same validation and report contract; neither makes GitHub writes.

## Select the declared facts

Use one repository-scoped contract, with only the pull requests and releases that
the current capsule actually relies on. Do not turn repository history into an
active work inventory. Read the authoritative capsule and source declarations
explicitly; this adapter does not guess state by matching words in Markdown.

```json
{
  "format": "lattice-github-tracking",
  "version": 1,
  "repository": "example/product",
  "declarations": [
    {
      "kind": "pull_request",
      "id": 7,
      "status": "active",
      "source_ref": "projects/product/PROJECT.md"
    },
    {
      "kind": "release",
      "id": "v0.1.0-rc.4",
      "status": "pending",
      "source_ref": "projects/product/PROJECT.md"
    }
  ]
}
```

Pull-request declarations support `active`, `merged`, `closed`, and `superseded`.
Release declarations support `pending`, `published`, and `superseded`.
`superseded` requires a nonempty `reason` recording the Director's disposition.
An open PR can be historical to the project while it remains open on GitHub; the
report retains both facts. Declared status cannot contain `accepted`, `ready`, or
publication authority. Those remain separate guarded project decisions.

## Capture evidence through the connector

Fetch each declared object through the connected GitHub tools. Use the full PR
endpoint rather than a list/issue response: `/pulls/{number}` must include the
boolean `merged`, merge identity, and frozen base/head SHAs. Releases use
`/releases/tags/{tag}`. A successful HTTP 200 response is required; missing,
forbidden, or unavailable evidence is unknown and fails the check.

For an open historical PR, optionally fetch
`/compare/{base_sha}...{head_sha}` using the exact SHAs from that PR response.
The comparison must identify that base and both SHAs in its canonical URL.
Zero commits ahead creates a `supersession_candidate`; it never closes the PR,
supersedes a declaration, proves equivalent behavior, or accepts a milestone.

For a stacked historical PR whose old base is no longer the integration target,
set optional `integration_branch: "main"` in the tracking contract and capture
`/branches/main` as well. Compare that branch's captured full commit SHA with the
PR's captured head SHA. The adapter requires the branch identity and commit URL
to match the declared repository; it records both the PR's original base and the
chosen integration base. It never silently assumes `main` is authoritative.

Wrap the unmodified response objects in this envelope:

```json
{
  "format": "lattice-github-observations",
  "version": 1,
  "repository": "example/product",
  "captured_at": "2026-09-04T19:00:00Z",
  "responses": [
    {
      "url": "https://api.github.com/repos/example/product/pulls/7",
      "status": 200,
      "data": { "...": "the complete GitHub GET response" }
    },
    {
      "url": "https://api.github.com/repos/example/product/releases/tags/v0.1.0-rc.4",
      "status": 200,
      "data": { "...": "the complete GitHub GET response" }
    }
  ]
}
```

The placeholder `data` objects above are explanatory, not executable fixtures.
Use the actual capture time, including its timezone. Captures older than 24 hours
or more than five minutes in the future fail closed. Source updates/publication
cannot postdate their capture. Exact API and object URLs bind the repository,
PR number, release tag, and optional comparison. Duplicate, unrequested,
cross-repository, malformed, or unsuccessful responses are rejected.

This boundary validates a trusted connector capture; it does not authenticate a
hand-authored JSON file or cryptographically attest GitHub. Keep captures with
their source workflow/connector provenance in the target's established evidence
location. Do not place tokens or request headers in them. A release's
`target_commitish` remains a GitHub ref, not proof of a deployed or installed SHA.

## Read-only check and CI

From a pinned Lattice checkout:

```bash
python3 scripts/lattice.py github-check \
  --declarations /path/to/target/declarations.json \
  --observations /path/to/target/observations.json
```

Exit codes are `0` for reconciled declarations, `1` for unresolved discrepancy,
and `2` for rejected or unavailable evidence. The JSON report identifies each
object's declared and observed states, source identity, facts, and attention.
It always declares `external_observation_only`, `acceptance_changed: false`,
and `publication_authorized: false`.

Use the same command in a target's CI after a read-only capture step. Produce
captures from trusted API/connector responses in that run; do not reuse a checked-in
snapshot as current remote evidence. The Lattice workflow executes deterministic
reconciliation regressions. Live target checks require their own current captures
and target repository permissions; Lattice's seed CI does not claim to inspect
every adopter's private repositories.

For connector-only capsules, correct the capsule in its bounded governed PR,
retain the prior declaration in Git history, and repeat this check against fresh
responses. Keep merged transport state, Quality evidence, Assurance acceptance,
and publication authorization distinct in the resulting capsule. No generated
report or secondary task ledger becomes authoritative state.

## Record observations through guarded state

For a project registered in the portable runtime, create or update the contract
with the existing Director-owned `record-put`. Pass the JSON above as its body;
use structured arguments rather than concatenating source text into a shell:

```python
import pathlib
import subprocess
import sys

subprocess.run([
    sys.executable, "scripts/lattice.py", "record-put",
    "--project", "product", "--key", "github.tracking", "--kind", "contract",
    "--title", "GitHub transport declarations",
    "--owner-role", "director", "--role", "director",
    "--source-ref", "projects/product/PROJECT.md",
    "--body", pathlib.Path("declarations.json").read_text(encoding="utf-8"),
], check=True)
```

Read the current project revision from `status` or `inspect`, then apply:

```bash
python3 scripts/lattice.py github-reconcile \
  --project product --role director --expected-revision 12 \
  --observations observations.json
```

The CLI's portable path uses SQLite, matching its other local state commands.
Shared hosts may call `reconcile_github_state` with their configured
`PostgresStateStore`; the same project transaction guard and truth semantics
apply. Checkpoint shared state deliberately through the existing checkpoint tool.

The adapter records one bounded `github.observed-state` truth with the exact
tracking-record ID/version, capture hash, sources, and report. Its epistemic
status is `contested` while a declared/observed discrepancy remains, and `observed`
once reconciled. This keeps unrelated milestone acceptance from backgrounding an
unresolved discrepancy. Its immutable truth versions and attention transitions
retain the former facts. It does not edit the tracking contract, conditions,
milestones, exceptions, or commitments to manufacture acceptance.

- Unresolved discrepancies remain on the truth frontier.
- Revising the Director's existing tracking contract records the disposition.
  Capture again; a reconciled observation can move to background.
- Superseded entries remain inspectable as history. Their unresolved siblings
  remain on the frontier. Removing a declaration is a versioned Director record
  revision; it cannot be caused by an absent response.
- Active or planned conditions linked to the observation truth retain frontier
  attention. A changed observation uses normal truth invalidation to require
  fresh verification; it cannot make those conditions satisfied.
- Exact accepted-capture retries are no-ops, even with the original revision.
  Changed observations require the current project revision and a newer capture.
  Regressing PR update times and repository reassignment are rejected.
- A manually contested or otherwise reclassified observation truth requires
  explicit resolution. The adapter cannot overwrite that status.

The neutral public seed remains unchanged. Store real project facts only in the
project's authorized state and repository.
