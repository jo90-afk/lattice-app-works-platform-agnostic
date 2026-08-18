# Start Lattice in ChatGPT Work

Lattice has two supported operating modes. The local-project mode provides the strongest enforcement because ChatGPT Work can discover the repository instructions and named agent definitions directly.

## Mode A — Local project (recommended)

1. Extract this folder into the root of the app repository you want Lattice to manage.
2. Open the ChatGPT desktop app and add that folder as a local project. Make it the primary folder so `AGENTS.md`, `.codex/config.toml`, and `.codex/agents/` are discovered.
3. Start a new ChatGPT Work chat in the project. Select the permission mode appropriate to the work. A planning/bootstrap run can begin read-only; implementation will need workspace write access.
4. At non-Ultra intelligence levels, explicitly request subagents. The supplied activation prompts already do this.
5. Paste one prompt from `prompts/`.

The primary thread becomes the Director. It writes work orders and delegates each ready order to a named project agent. Three subagent threads may run concurrently, but the Director must keep writes sequential until inputs are frozen and owned paths are disjoint.

## Mode B — Hosted ChatGPT Project

A hosted ChatGPT Project can share uploaded files and project instructions, but it does not directly expose a folder on your computer. Project-scoped `.codex/agents/*.toml` files are a local Codex-client feature, so hosted mode uses ChatGPT Work's general subagents with the matching role briefs instead.

1. Create a ChatGPT Project in your company workspace.
2. Upload `Lattice_ChatGPT_Work_Hosted_Pack.md` as a project source.
3. Copy the `HOSTED-PROJECT-INSTRUCTIONS.md` section at the top of that pack into the project's instructions.
4. Start a Work chat inside the project and paste the activation prompt included near the end of the pack, or adapt it for another app.

In hosted mode, tell the Director to spawn a specialist subagent for each role and include that role's `agents/*.md` brief verbatim in the delegated task. Do not assume a named TOML agent was auto-loaded.

## What happens first

Lattice does not begin by coding. The Director conducts the Principal bootstrap, records the confirmed mandate, and produces Gate 0 intake. Product then owns the first domain artifact. Services and Intelligence remain dormant unless accepted requirements justify them.

## Useful commands to give the Director

- `Activate Lattice for this project. Use explicit subagent delegation.`
- `Resume Lattice from the recorded work and gate state. Do not infer missing approvals.`
- `Show me the current gate, decisions I own, active work orders, blockers, and next safe action.`
- `Run the assigned gate reviews with fresh verifier threads, wait for all required results, and record them verbatim.`

## Human approvals

The Principal remains the human decision owner for product intent, priorities, spending, personal-data policy, irreversible or externally visible actions, accepted residual risk, and launch. When the agency reaches one of those boundaries, ChatGPT Work must pause and ask rather than selecting a default.