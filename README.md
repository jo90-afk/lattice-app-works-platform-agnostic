# Lattice App Works 0.0.3

Lattice is a platform-agnostic, multi-project AI software agency built around an active frontier rather than a task backlog. It stores durable project state, truth, evidence, commitments, and exceptions; it derives the next few executable actions only when an agent asks for them.

The repository is a sanitized seed. It contains no real person's data or project history.

## Architecture

| Layer | Location | Purpose |
| --- | --- | --- |
| Agency Kernel | `AGENTS.md`, `agency.yaml`, `agents/`, `governance/`, `runtime/` | Roles, authority, state rules, assurance, escalation |
| Portfolio | `portfolio/` | Principal alias, project identity, priority, capacity |
| Project Capsules | `projects/<project-id>/` | Product artifacts, code, tests, mandate, human-facing evidence |
| Operational State | `state/current.json` | Git-friendly objectives, conditions, truths, evidence, commitments, exceptions, events |
| Local Index | `.lattice/state.db` | SQLite indexes and expiring leases; generated and ignored by Git |

The runtime uses only Python's standard library and SQLite.

## Initialize the seed

Use Python 3.10 or newer. From the repository root:

    python3 scripts/lattice.py initialize \
      --principal-alias "Repository Owner" \
      --project-id first-project \
      --project-name "First Project"

Use an alias rather than a real name if the repository might become public. Initialization renames the neutral capsule, activates its state record, and regenerates its ChatGPT Work export.

Confirm the project mandate in `projects/first-project/work/bootstrap.md`. Then establish one bounded objective and active milestone:

    python3 scripts/lattice.py objective-add \
      --project first-project --id objective-001 \
      --title "Deliver the first usable increment" \
      --description "A bounded outcome inside the confirmed mandate" \
      --owner-role product

    python3 scripts/lattice.py milestone-add \
      --project first-project --objective objective-001 --id milestone-001 \
      --title "Increment is usable and verified" --ordinal 1 --activate

Record requirements, constraints, decisions, contracts, artifact identities, and risks with `record-put`. Record consequential world-state propositions with `truth-add`. Create only the readiness conditions needed to make the milestone true:

    python3 scripts/lattice.py condition-add \
      --project first-project --objective objective-001 --milestone milestone-001 \
      --key increment.builds --title "Increment builds reproducibly" \
      --description "The documented build succeeds and produces the expected artifact" \
      --owner-role release --verifier-role quality --role director

Check the installation and current state:

    python3 scripts/lattice.py validate
    python3 scripts/lattice.py status
    python3 scripts/lattice.py frontier --project first-project --limit 3

## Run an action

Claim one derived action:

    python3 scripts/lattice.py claim \
      --project first-project --role release --actor release-1

The returned context is the execution brief. After editing owned files and running checks:

    python3 scripts/lattice.py submit \
      --lease <lease-id> --role release \
      --summary "Build is reproducible" \
      --artifact projects/first-project/ops/build.md \
      --evidence-ref projects/first-project/quality/build-output.txt

A fresh verifier claims the resulting review action and records its verdict. When every condition passes, Assurance receives a milestone-advancement action.

## Add another project

Create a proposed, isolated capsule and state record:

    python3 scripts/lattice.py project-create \
      --project-id second-project \
      --project-name "Second Project"

Confirm its mandate and portfolio priority before activating an objective. The command does not modify the Agency Kernel or borrow state from another project.

    python3 scripts/lattice.py project-status \
      --project second-project --status active --role director

## Truth ledger

Truth status and attention are separate. A proposition can move from `frontier` to `background` while its versions, source, confidence, links, and transition reason remain intact. Background truths stay out of routine context unless a condition or contradiction makes them relevant again.

    python3 scripts/lattice.py truth-list --project first-project --attention background

See `docs/TRUTH-LEDGER.md`.

## Hosts

| Environment | Start |
| --- | --- |
| Local repository-aware agent | Read `AGENTS.md`, then use `scripts/lattice.py` |
| Codex | Open the repository root; root `AGENTS.md` is canonical |
| Claude Code | Open the repository root; `CLAUDE.md` imports `AGENTS.md` |
| ChatGPT Work | Generate and upload a scoped execution pack |

Generate a ChatGPT Work pack:

    python3 scripts/lattice.py export-chatgpt-work --project first-project --overwrite

Hosted results return one project-revision-guarded delta. Reconcile artifact files first, then apply it with `python3 scripts/lattice.py apply-delta --file <delta.json>`. Generated packs are disposable and ignored by Git.

## GitHub initialization

After initialization:

    git init -b main
    git add -A
    git commit -m "chore: initialize Lattice active-frontier seed"
    git remote add origin https://github.com/<owner>/lattice-app-works.git
    git push -u origin main

Use a private repository for real projects. Commit `state/current.json`; do not commit `.lattice/`.

## Privacy

Do not put credentials, tokens, direct personal identifiers, calendars, health data, financial data, addresses, or private source material in a public seed. Project truth can be sensitive even when it is structured. Use private capsules and appropriately protected repositories for real work.
