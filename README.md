# Lattice App Works

Lattice App Works is a pre-alpha, autonomous, multi-project development agency. This repository is a portable operating system for that agency: it carries policy, portfolio state, project capsules, evidence, and host adapters without treating any AI product as the source of truth.

Repository posture: private by default. The current Personal Life OS capsule contains personal project material. Review every project capsule before making this repository public.

## What is portable

| Layer | Canonical location | Host-specific behavior |
| --- | --- | --- |
| Agency Kernel | AGENTS.md, agency.yaml, agents/, governance/, templates/ | None; it is platform-neutral |
| Portfolio Registry | portfolio/ | None; it controls identity, priority, and scheduling |
| Project Capsules | projects/<project-id>/ | None; each is isolated and carries its own state |
| Host adapters | adapters/ and CLAUDE.md | Thin launch and export guidance only |

The current portfolio contains Personal Life OS (plos-001). It is one project capsule, not Lattice's charter.

## Start here

Lattice is an agent operating system, not a web server. Run it by opening this repository with an AI agent that can read Markdown and work in the checked-out folder.

    python3 scripts/lattice.py validate
    python3 scripts/lattice.py status

Then follow the matching adapter:

| Environment | Use |
| --- | --- |
| Local / any agent | adapters/local/README.md |
| Codex | Open this repository as the project root; Codex discovers AGENTS.md. |
| Claude Code | Open this repository as the project root; CLAUDE.md imports AGENTS.md. |
| ChatGPT Work | Upload the current source pack from exports/chatgpt-work/plos-001/. |

## Current project state

The plos-001 capsule preserves its confirmed bootstrap, Gate 0 evidence, architecture decision AD-001, discovery and acceptance artifacts, work-order history, frozen Gate 1 hashes, the Principal's ACCEPT GATE 1, and the ready Gate 2 state. The portable runtime change does not alter those records.

## GitHub

GitHub is an optional review and CI host, not the agency runtime. After extracting this folder, create a private repository and push its contents.

    git init -b main
    git add -A
    git commit -m "chore: import Lattice App Works 2.2"
    git remote add origin https://github.com/<owner>/lattice-app-works.git
    git push -u origin main

For mobile-friendly upload steps and ongoing rules, read docs/REPOSITORY-SETUP.md.

## Design rules

- The kernel never assumes a product, platform, backend, integration, model feature, or default host.
- Project-specific decisions never become agency policy.
- Builders, verifiers, reviewers, and Assurance remain separate.
- Routine remediation is agent-managed; the Principal is engaged only at declared consequence boundaries and for production launch.
- Platform adapters must be replaceable and may not duplicate or override canonical governance.
