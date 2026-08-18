# Contributing to Lattice

Lattice changes are governed artifacts, not informal prompt edits.

1. Select exactly one governed scope: agency, portfolio, one project capsule, or new-project intake.
2. Do not mix unrelated project capsules in one change.
3. Respect the write domains in agency.yaml and role briefs in agents/.
4. Preserve independent verification, mandatory review, Assurance decisions, and Principal exception boundaries.
5. Run:

       python3 scripts/lattice.py validate

6. If the change affects a source used in ChatGPT Work, regenerate its hosted pack before committing.

Never put credentials, sensitive data, private prompts, or signing material in source, fixtures, handoffs, or project evidence.
