# Getting started

This is the supported 0.1.0 bootstrap path from a sanitized clone to one independently verified and accepted milestone. It uses the dependency-free SQLite runtime. Do not configure Postgres until the local flow is understood and working.

## 1. Preflight the repository

From the repository root, use Python 3.10 or newer:

```bash
python3 scripts/doctor.py
```

Every required check should report `OK`. For machine-readable diagnostics:

```bash
python3 scripts/doctor.py --json
```

`doctor` does not initialize a project or mutate durable Lattice state. Its temporary writeability probes are created and removed inside the ignored local runtime/state directories.

## 2. Initialize one project

Choose a repository-safe Principal alias and a lowercase project ID:

```bash
python3 scripts/lattice.py initialize \
  --principal-alias "Repository Owner" \
  --project-id first-project \
  --project-name "First Project"
```

Initialization replaces the neutral `example-001` capsule with `first-project`, updates the portfolio identity, activates the corresponding state record, and regenerates the scoped ChatGPT Work export.

If this repository may ever be public, do not put private identity, credentials, private source material, or sensitive project truth into it. Use a private repository for real work.

## 3. Confirm the mandate

Read and complete:

```text
projects/first-project/work/bootstrap.md
```

The mandate is the authority boundary for the project. Do not derive implementation work until scope, constraints, and the Principal's intended outcome are explicit enough to distinguish a valid result from an invalid one.

Re-run preflight after editing the mandate:

```bash
python3 scripts/doctor.py
```

## 4. Encode the first objective and milestone

Create one bounded objective:

```bash
python3 scripts/lattice.py objective-add \
  --project first-project \
  --id objective-001 \
  --title "Deliver the first usable increment" \
  --description "A bounded outcome inside the confirmed mandate" \
  --owner-role product
```

Create and activate its first milestone:

```bash
python3 scripts/lattice.py milestone-add \
  --project first-project \
  --objective objective-001 \
  --id milestone-001 \
  --title "Increment is usable and verified" \
  --ordinal 1 \
  --activate
```

## 5. Record current truth and readiness

Use `record-put` for requirements, constraints, decisions, contracts, artifact identities, and risks. Use `truth-add` for consequential propositions about the world whose revision should invalidate dependent work.

For a minimal first run, create one readiness condition:

```bash
python3 scripts/lattice.py condition-add \
  --project first-project \
  --objective objective-001 \
  --milestone milestone-001 \
  --id condition-001 \
  --key increment.builds \
  --title "Increment builds reproducibly" \
  --description "The documented build succeeds and produces the expected artifact" \
  --owner-role release \
  --verifier-role quality \
  --role director
```

Inspect what Lattice now derives rather than creating a separate task list:

```bash
python3 scripts/lattice.py frontier --project first-project --limit 3
```

## 6. Claim and execute the derived action

Claim the Release action:

```bash
python3 scripts/lattice.py claim \
  --project first-project \
  --role release \
  --actor release-1
```

The returned object contains the lease ID and bounded action context. Treat that context as the execution brief. Do only the claimed work and write only Release-owned paths.

After producing the artifact and evidence, submit them through the guarded lifecycle:

```bash
python3 scripts/lattice.py submit \
  --lease <release-lease-id> \
  --role release \
  --summary "Build is reproducible" \
  --artifact projects/first-project/ops/build.md \
  --evidence-ref projects/first-project/quality/build-output.txt
```

Submission makes the condition a verification candidate; it does not accept the work.

## 7. Verify independently

A fresh Quality actor asks for its frontier and claims the review action:

```bash
python3 scripts/lattice.py frontier --project first-project --role quality

python3 scripts/lattice.py claim \
  --project first-project \
  --role quality \
  --actor quality-1
```

After independently checking the submitted result and evidence:

```bash
python3 scripts/lattice.py review \
  --lease <quality-lease-id> \
  --role quality \
  --verdict SATISFIED \
  --summary "Independent build verification passed" \
  --evidence-ref projects/first-project/quality/verification.txt
```

If verification fails, use `NOT_SATISFIED`; Lattice re-derives remediation according to the condition's bounded retry policy rather than silently accepting the owner result.

## 8. Accept through Assurance

Once every active-milestone condition is satisfied, Assurance receives the acceptance action:

```bash
python3 scripts/lattice.py frontier --project first-project --role assurance

python3 scripts/lattice.py claim \
  --project first-project \
  --role assurance \
  --actor assurance-1
```

Accept the verified milestone:

```bash
python3 scripts/lattice.py advance \
  --lease <assurance-lease-id> \
  --role assurance \
  --summary "All readiness predicates are independently satisfied"
```

At this point the owner has done the work, a separate verifier has judged it, and Assurance has accepted the milestone. Those are three distinct authority events.

## 9. Inspect the resulting state

```bash
python3 scripts/lattice.py status
python3 scripts/lattice.py inspect --project first-project
python3 scripts/lattice.py principal-inbox --project first-project
```

You can also start the read-only human supervision surface:

```bash
python3 scripts/control_server.py
```

Then open `http://127.0.0.1:8765`.

## Recover from interruption

If a worker disappears, do not reconstruct the work from chat history. Expired leases and recorded host/workspace provenance are recoverable durable coordination state:

```bash
python3 scripts/lattice.py recover --project first-project
python3 scripts/lattice.py frontier --project first-project
```

The current frontier is re-derived from durable project state.

## Add another project or host

Create another isolated capsule with:

```bash
python3 scripts/lattice.py project-create \
  --project-id second-project \
  --project-name "Second Project"
```

For execution-host integration, keep `AGENTS.md` and the Lattice state engine authoritative. Host adapters may supply workspaces, tools, models, and lifecycle transport; they do not gain a second state or acceptance model. See `docs/HOST-ADAPTER.md` and `adapters/README.md`.
