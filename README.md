# Lattice App Works 0.1.3

Lattice is a platform-agnostic, multi-project AI software agency built around an active frontier rather than a task backlog. It stores durable project state, truth, evidence, commitments, and exceptions; it derives the next few executable actions only when an agent asks for them.

The repository is a sanitized seed. It contains no real person's data or project history.

## Public-beta bootstrap

Use Python 3.10 or newer. The supported first-run path is deliberately linear:

1. clone or copy the sanitized repository;
2. run the non-destructive environment preflight;
3. initialize the neutral seed with one project identity;
4. confirm that project's mandate;
5. encode one objective, active milestone, and only the readiness conditions needed for it;
6. derive and claim work from the frontier;
7. submit artifacts and evidence;
8. verify with a fresh role;
9. let Assurance accept the milestone or route an exception.

From the repository root, start with:

    python3 scripts/lattice.py doctor

For automation or troubleshooting:

    python3 scripts/lattice.py doctor --json

`doctor` checks the Python runtime, required repository layout, release metadata, canonical repository/state validation, local runtime writeability, and the configured state backend. SQLite is the dependency-free default. If `LATTICE_DATABASE_URL` is set, `doctor` also requires `psycopg` and verifies Postgres connectivity without mutating Lattice state.

Then initialize the seed:

    python3 scripts/lattice.py initialize \
      --principal-alias "Repository Owner" \
      --project-id first-project \
      --project-name "First Project"

Continue with [Initialize the seed](#initialize-the-seed) below, or follow the single end-to-end walkthrough in [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md). Public/private repository boundaries, stable 0.1 contracts, cross-platform bootstrap support, and rollback guidance are collected in [`docs/PUBLIC-BETA.md`](docs/PUBLIC-BETA.md).

## Architecture

| Layer | Location | Purpose |
| --- | --- | --- |
| Agency Kernel | `AGENTS.md`, `agency.yaml`, `agents/`, `governance/`, `runtime/` | Roles, authority, state rules, assurance, escalation |
| Expertise Library | `expertise/` | Selectively loaded role playbooks and project-declared application platform packs |
| Portfolio | `portfolio/` | Principal alias, project identity, priority, capacity |
| Project Capsules | `projects/<project-id>/` | Product artifacts, code, tests, mandate, human-facing evidence |
| Portable State | `state/current.json` | Git-friendly snapshot of objectives, conditions, truths, evidence, commitments, exceptions, events |
| Local Runtime | `.lattice/state.db` | SQLite operational state and expiring leases; generated and ignored by Git |
| Shared Runtime | Postgres via `LATTICE_DATABASE_URL` | Optional simultaneous remote writers with project-scoped concurrency semantics |

SQLite remains the dependency-free local default. Shared deployments may install `psycopg` and use Postgres without changing the portable snapshot contract.

## Human control surface

Run the local human control surface:

    python3 scripts/control_server.py

Open `http://127.0.0.1:8765`. The browser is organized around the Principal's actual control loop rather than the database shape: decisions that require human authority first; each project's current objective and milestone; work happening now; work ready next; exceptions and blocked conditions that need attention; then accepted changes and system health.

Principal-only exceptions and Principal-owned commitments can be completed directly in the browser. The UI does not create a separate authority system: it claims the exact currently advertised Principal action key and executes the same guarded lifecycle used by the CLI, preserving lease checks, durable state transitions, lifecycle telemetry, and project history. Detailed evidence and consequence state remain inspectable on demand instead of occupying the primary dashboard hierarchy. Machine-readable supervision state is available at `/api/state`.

## Evaluation harness

0.0.8 established a fail-closed evidence suite for testing whether durable state, bounded authority, recovery, and independent verification actually reduce autonomy failures.

Validate the canonical scenario registry:

    python3 scripts/evaluation.py validate

Summarize one or more versioned run-result files:

    python3 scripts/evaluation.py summarize evals/results/*.json

CI executes all ten roadmap scenario classes, including a live multi-connection Postgres conflict case, before the ordinary regression suite. Metrics include routine autonomy, false acceptance, unnecessary escalation, recovery success, state divergence, verification catch rate, missing-information blocked time, context volume per accepted change, and cross-host state/acceptance equivalence. An unexercised denominator is reported as unknown rather than as a perfect score.

See [`docs/EVALUATION.md`](docs/EVALUATION.md).

## Roadmap

The public roadmap treats agent runtimes as replaceable execution hosts and focuses Lattice on the durable control plane above them: project truth, authority, frontier derivation, verification, recovery, and human exception handling.

See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Select expertise and platforms

Every role has a researched core expertise module. Application delivery is no longer an Android-only role: the platform list is an open set in `projects/<project-id>/project/capabilities.json`. Common Android, Apple, web, Windows, Linux, CLI, and cross-platform packs ship with the seed; an unknown platform remains valid and triggers focused first-party research rather than loading the whole library.

After claiming an action, resolve exactly what to load:

    python3 scripts/lattice.py expertise \
      --project first-project --role application

Preview a proposed target without changing project state:

    python3 scripts/lattice.py expertise \
      --project first-project --role application \
      --platform ios --platform web --platform linux

Keep `application_platforms` and `cross_platform_strategy` synchronized with the confirmed project manifest. Expertise guides the claimed work but never overrides the mandate, current records and truths, or role boundaries.

## Initialize the seed

Run `python3 scripts/lattice.py doctor` before initialization. Then, from the repository root:

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

A fresh verifier claims the resulting review action and records its verdict. When every condition passes, Assurance receives a milestone-advancement action. The complete command sequence is in `docs/GETTING-STARTED.md`.

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

Use a private repository for real projects. Commit `state/current.json`; do not commit `.lattice/`. See `docs/PUBLIC-BETA.md` before adding sensitive project state.

## Privacy

Do not put credentials, tokens, direct personal identifiers, calendars, health data, financial data, addresses, or private source material in a public seed. Project truth can be sensitive even when it is structured. Use private capsules and appropriately protected repositories for real work.
