# Lattice Expertise Library

This library supplies current professional guidance to an agent after it claims one active-frontier action. It is advisory context, not a second authority layer: the confirmed mandate, current project records and truths, `agency.yaml`, runtime policy, and the claimed condition always win.

## Selective loading

Resolve expertise for the claimed role and project:

    python3 scripts/lattice.py expertise --project <project-id> --role <role>

Load only the paths returned by that command. Every role receives one compact core module. The Application Engineer additionally receives only the platform packs selected in `projects/<project-id>/project/capabilities.json`. A caller may preview a proposed platform set with repeated `--platform` arguments.

Platform identifiers are open-ended. An unknown identifier does not make the project invalid or cause every available pack to load. The resolver reports it under `unresolved_platforms`; the Application Engineer then consults current first-party platform documentation for the claimed condition and records any consequential capability change as a sourced truth. Reusable guidance can later be added through agency maintenance.

## Source policy

- Prefer normative standards and first-party platform documentation.
- Treat drafts, previews, and vendor recommendations as guidance with an explicit maturity note.
- Recheck a source when the catalog verification date is older than the decision warrants or the platform/tool version has changed.
- Translate guidance into project-specific conditions and evidence; do not copy a framework's backlog, ceremony, or role model into Lattice.
- Never turn every recommendation into work. Apply only guidance material to the claimed condition, its risks, and its acceptance evidence.
- If new external evidence changes a consequential assumption, revise or add a truth-ledger entry rather than silently changing project behavior.

The catalog's `verified_on` date records the last cross-library review. Individual modules may cite a more specific edition or maturity state.
