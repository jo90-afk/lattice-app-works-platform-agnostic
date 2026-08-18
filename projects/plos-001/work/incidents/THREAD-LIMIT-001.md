# Internal Scheduling Incident — THREAD-LIMIT-001

**Project ID:** `plos-001`  
**Project root:** `projects/plos-001`  
**Date:** 2026-08-06  
**Owner:** Portfolio Director  
**Status:** OPEN — retry at next fresh-thread opportunity  
**Principal exception:** No

## Event

After Quality returned `NOT_SATISFIED/BLOCK` on information-architecture revision 0.3 finding F-003, the Director prepared ready remediation order `work/orders/WO-005-R3.md` for a fresh Experience author.

Direct fresh-thread creation failed with the exact runtime result:

`collab spawn failed: agent thread limit reached`

The Director then reactivated completed leaf `/root/plos001_experience_wo004_r1` only as a relay and instructed it not to inspect or edit evidence. Its attempt to create a context-free child returned verbatim:

`BLOCKED: unable to spawn /root/plos001_experience_wo004_r1/plos001_experience_wo005_r3_fresh; spawn_agent returned agent thread limit reached. No files were inspected or modified and no specialist work was performed.`

## Integrity effect

- No WO-005-R3 author was activated.
- No file was modified after the failed delegations.
- `design/information-architecture.md` remains blocked revision 0.3 at SHA-256 `df3af327d514bfe61645cf684fc87e9c6025bd353af8a059b2654a582077f2a3`.
- F-003 remains open exactly as recorded in `work/verifications/WO-005-R2-quality.md`.
- WO-006-C1 and all downstream work remain blocked.
- Gate 2 remains open and Assurance is not activated.

## Recovery

When a fresh thread becomes available, delegate `work/orders/WO-005-R3.md` unchanged to a new Experience Lead leaf for project `plos-001`. Do not reuse a prior author, repeat intake, reopen Gate 1, or ask the Principal. After owner completion, use a fresh Quality retest, then a fresh Product mandatory review.