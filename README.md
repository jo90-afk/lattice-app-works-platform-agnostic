# Lattice App Works Seed

Lattice App Works is a pre-alpha, multi-project development agency. This repository is a clean seed: it contains the portable agency kernel, a neutral portfolio record, one uninitialized example project, host adapters, and no real person’s project history or seed data.

The repository is structured as three separate layers:

| Layer | Location | Owns |
| --- | --- | --- |
| Agency Kernel | AGENTS.md, agency.yaml, agents/, governance/, templates/ | Roles, authority, gates, ownership, and escalation |
| Portfolio Registry | portfolio/ | Principal alias, project IDs, priority, capacity, and scheduling |
| Project Capsule | projects/<project-id>/ | One project’s mandate, artifacts, evidence, delivery state, and release history |

The included example-001 capsule is illustrative only. It is not a confirmed mandate, an approved plan, or a real user’s data.

## Initialize the seed before using it

Choose a non-sensitive Principal alias, a stable project ID, and a project name. From the repository root, run:

    python3 scripts/lattice.py initialize --principal-alias "Repository Owner" --project-id first-project --project-name "First Project"

This replaces the neutral placeholders, renames the example capsule, creates a fresh ChatGPT Work source pack for that project, and marks the seed as initialized. Use an alias rather than a real name if the repository might become public.

Then confirm the fresh project mandate and begin ordinary Lattice work:

    python3 scripts/lattice.py validate
    python3 scripts/lattice.py status

## Use with an AI host

| Environment | Start |
| --- | --- |
| Local / any repository-aware agent | Read AGENTS.md at the repository root. |
| Codex | Start in the repository root; Codex reads AGENTS.md. |
| Claude Code | Start in the repository root; CLAUDE.md imports AGENTS.md. |
| ChatGPT Work | Set the generated Project instructions and upload the generated source pack in exports/chatgpt-work/<project-id>/. |

See adapters/ for the host-specific startup notes. The adapters do not alter governance; the repository remains the source of truth.

## GitHub initialization

After extracting this folder, create a private GitHub repository and push the initialized repository contents:

    git init -b main
    git add -A
    git commit -m "chore: initialize Lattice seed"
    git remote add origin https://github.com/<owner>/lattice-app-works.git
    git push -u origin main

If a phone Git client uses buttons instead of commands, initialize this extracted folder as a repository, stage every file, make the first commit, connect the empty private GitHub repository as origin, then push main.

## Seed-data privacy rule

Do not commit real names, contact information, calendars, notes, health data, financial data, addresses, credentials, tokens, or private source material to the seed. Put real project data only in a private project capsule after initialization.
