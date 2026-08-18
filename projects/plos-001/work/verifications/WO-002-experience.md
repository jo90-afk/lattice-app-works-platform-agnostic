# Verification Record: WO-002 — Experience Lead

**Record type:** PRIMARY VERIFICATION  
**Reviewer role:** Experience Lead — fresh independent verifier  
**Date:** 2026-08-05  
**Input handoff:** `work/handoffs/WO-002-product.md`  
**Frozen artifact:** `product/project-brief.md` v0.1, `In review`

## Assigned question

Does `product/project-brief.md` translate the confirmed mandate and D-01 A through D-07 A into a coherent, bounded, user-observable release-one intent that Experience can interpret without guessing, while avoiding experience or technical design?

## Evidence reproduced

| Inspection | Expected | Actual |
| --- | --- | --- |
| `sha256sum product/project-brief.md` | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` | Exact match |
| Proposed-scope requirement rows | Stable, unique identifiers with behavior, priority, and acceptance summary | 11 unique rows, R-001 through R-011; each has all required columns |
| Principal decision rows | D-01 A through D-07 A | All seven recorded |
| Approval inspection | No Experience or Principal approval of v0.1 claimed | Experience verification and Principal approval explicitly pending |

The artifact, handoff, work order, and all four authorized trace inputs were read in full. No files were edited.

## Section trace

| Project-brief section | Frozen basis |
| --- | --- |
| Product intent; target users and context | `work/bootstrap.md` “Raw product intent” and “Known users and context”; `work/intake.md` “Requested outcome” and “Known user and operating context” |
| Evidence classification | Confirmed mandate and intake constraints; `product/discovery.md` sections 1–2; D-01 through D-07 selections confirmed by `work/verifications/WO-001-principal.md` |
| Jobs to be done | Confirmed priority order and `product/discovery.md` section 3, JTBD-01 through JTBD-03 |
| Smallest coherent value loop | `product/discovery.md` H-01 and selected D-01 A |
| Goals and outcome signals | Selected D-06 A |
| Non-goals | Mandate and intake exclusions; discovery sections 4–5; selected D-01 A through D-05 A |
| Proposed release scope | Selected D-01 A through D-05 A plus confirmed offline, notification, personal/work, cost, and autonomy boundaries |
| Data and autonomy inventory | Discovery section 5 and selected D-02 A through D-05 A |
| Constraints | Confirmed bootstrap/intake constraints and selected D-05 A through D-07 A |
| Assumptions to validate | Discovery H-01, evidence limitations, and the selected decisions’ explicitly unresolved real-use questions |
| Principal decisions; approval | Discovery D-01 through D-07 and the verbatim Principal response in `work/verifications/WO-001-principal.md` |

## Acceptance-criteria inspection

| Criterion | Result | Artifact evidence |
| --- | --- | --- |
| 1 | Met | Header metadata; “Product intent”; “Target users and context” identify Jude O’Neill as sole Principal and user, version 0.1, and `In review` status. |
| 2 | Met | “Jobs to be done” preserves the confirmed 1–3 priority order and states observable outcomes without screens or mechanisms. |
| 3 | Met | “Smallest coherent value loop” and R-002 through R-006 define daily intention, deliberate close, and a bounded weekly reflection across all three jobs. |
| 4 | Met | “Goals and outcome signals,” G-01 through G-04, reproduces D-06 A; every baseline is unknown and every numerical threshold waits for real-use evidence. |
| 5 | Met | “Non-goals” explicitly covers specialized suites, work, Calendar/Keep connection, AI, remote sync, prohibited sensitive data, wider distribution, silent external action, pressure mechanics, and paid dependencies. |
| 6 | Met | “Proposed release scope” contains unique R-001 through R-011 rows with user-visible behavior, `Must` priority, and concise acceptance summaries. Experience and implementation choices are expressly deferred. |
| 7 | Met | R-007 and R-009 through R-011, together with both “Data and autonomy inventory” tables, implement coexistence-only, minimal local records, user-initiated portability, restore and deletion, and prohibit automatic sync or silent destructive replacement. |
| 8 | Met | “Constraints” records Android-first, offline/local operation, configurable optional notifications, baseline Android accessibility, separate environments, personal installation, and no pre-authorized spend. |
| 9 | Met | “Principal decisions” records D-01 A through D-07 A. “Assumptions to validate,” A-01 through A-08, isolates later non-material validation needs and owners. |
| 10 | Met | “Non-goals” rejects experience and technical prescriptions. “Approval” explicitly leaves Experience verification and Principal approval of v0.1 pending and claims no test, launch, or promotion decision. |

## Findings

None. No material ambiguity, scope expansion, ownership conflict, or accidental experience or technical prescription was found.

## Outcome

`SATISFIED`

## Rationale

The brief defines the release-one behavioral boundary and observable decisions precisely enough for Experience to derive journeys, states, content, notification behavior, and accessibility requirements without inventing product intent. It also leaves interaction details and technical mechanisms with their proper later owners. No gate approval is claimed.