# Repository setup and GitHub upload

## Initialize before first use

Run the seed initializer before creating work orders or uploading a hosted source pack:

    python3 scripts/lattice.py initialize --principal-alias "Repository Owner" --project-id first-project --project-name "First Project"

Use a non-sensitive alias if you expect to publish the repository.

## Generic Git upload

After extraction and initialization, run these commands from the repository root:

    git init -b main
    git add -A
    git commit -m "chore: initialize Lattice seed"
    git remote add origin https://github.com/<owner>/lattice-app-works.git
    git push -u origin main

If your phone Git client provides buttons instead of commands, initialize this extracted folder as a repository, stage every file, make the first commit, add the empty private GitHub repository as origin, then push main.

## GitHub is an adapter

The .github/ directory offers issue forms, pull-request guidance, and a validation workflow. It does not run the agency. The canonical Lattice runtime remains repository files plus the host adapter you choose.

## Ongoing change discipline

- Use one branch per governed scope: agency/, portfolio/, project/<project-id>/, or intake/<project-id>.
- Run python3 scripts/lattice.py validate before committing.
- Refresh exports/chatgpt-work/<project-id>/ whenever a project, registry, or Kernel change needs to be used in ChatGPT Work.
- Restrict changes to Agency Kernel paths to Principal-authorized agency maintenance.
