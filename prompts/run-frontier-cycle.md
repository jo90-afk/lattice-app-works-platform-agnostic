# Run One Autonomous Frontier Cycle

For project `[project_id]`, run `python3 scripts/lattice.py frontier --project [project_id] --limit 3` and select the highest-priority action allowed by current capacity.

Claim it under the exact role. Give the worker only its role prompt, claim context, and referenced sources. On an owner result, submit changed paths and evidence. On review, use a fresh context and the allowed verdict. On readiness, use a fresh Assurance context to advance. On failure, record it and allow the runtime to derive remediation or one deduplicated exception.

Do not create future tasks. Recompute the frontier after the durable result and continue only if capacity and the requested cycle budget permit.
