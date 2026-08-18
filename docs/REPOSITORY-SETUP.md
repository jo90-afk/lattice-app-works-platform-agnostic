# Repository setup and GitHub upload

## Keep it private first

The current plos-001 capsule contains personal project material. Create a private repository and review the capsule before changing visibility.

## Generic Git upload

After extracting this folder, run these commands from its root in any Git client or terminal:

    git init -b main
    git add -A
    git commit -m "chore: import Lattice App Works 2.2"
    git remote add origin https://github.com/<owner>/lattice-app-works.git
    git push -u origin main

If your phone Git client provides buttons instead of commands, the equivalent is: initialize this extracted folder as a repository, stage every file, make the first commit, add the empty private GitHub repository as origin, then push the main branch.

## GitHub is an adapter

The .github/ directory offers issue forms, pull-request guidance, and a validation workflow. It does not run the agency. The canonical Lattice runtime remains repository files plus the host adapter you choose.

## Ongoing change discipline

- Use one branch per governed scope: agency/, portfolio/, project/<project-id>/, or intake/<project-id>.
- Run python3 scripts/lattice.py validate before committing.
- Refresh exports/chatgpt-work/<project-id>/ whenever a project, registry, or Kernel change needs to be used in ChatGPT Work.
- Restrict changes to Agency Kernel paths to Principal-authorized agency maintenance.
