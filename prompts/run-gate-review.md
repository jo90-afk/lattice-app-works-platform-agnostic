# Autonomous Gate Cycle Prompt

Run the complete autonomous review cycle for project `[project_id]` at `projects/[project_id]`.

Act as the portfolio Director. Read only that project's applicable gate definition, work orders, handoffs, verification records, review findings, and current artifact versions. Identify exact owner handoffs, primary verification questions, mandatory reviewers, and evidence targets. Spawn fresh matching specialists for every independent check and wait for all results.

If evidence fails, record findings inside the capsule, issue remediation to the artifact owner, commission a fresh targeted retest plus affected regression, and continue unrelated portfolio work. Use the bounded cycles in `agency.yaml`; do not ask the Principal to manage QA.

When required evidence is complete, spawn a fresh Assurance Governor with `agents/assurance.md`, this project's gate records, and `templates/gate-decision.md`. Record its decision verbatim. Proceed on `ACCEPT` or valid `ACCEPT_WITH_DEBT`; loop on `REMEDIATE`; use `ESCALATE` only when it names an exact Principal exception predicate.