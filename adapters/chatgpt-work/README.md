# ChatGPT Work adapter

ChatGPT Work uses a scoped execution pack rather than the full repository.

    python3 scripts/lattice.py export-chatgpt-work --project <project-id> --overwrite

Optionally filter one role:

    python3 scripts/lattice.py export-chatgpt-work --project <project-id> --role quality --limit 1 --overwrite

In the ChatGPT Project:

1. Set `PROJECT-INSTRUCTIONS.md` as Project instructions.
2. Upload `Lattice_ChatGPT_Work_Pack_<project-id>.md`.
3. Ask Work to execute at most one action from the pack.
4. Reconcile its exact file changes into the repository.
5. Save its state delta and run `python3 scripts/lattice.py apply-delta --file <delta.json>`.
6. Regenerate the pack after the accepted mutation.

The export contains a bounded frontier and directly relevant sources, not the complete project archive. Its revision guard prevents an old hosted result from overwriting newer state.
