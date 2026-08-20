DONE BY OWNER

Status

WO-004 owner draft complete. Quality verification and Gate 2 approval remain pending.

Summary

Created the bounded release-one journey specification with 11 journeys covering daily intention, deliberate close, weekly reflection, promises/waiting, project decisions, offline use, conditional notification controls, export/backup, restore, and full deletion.

Artifacts

- `design/journeys.md`, revision 0.1
- SHA-256: `8a605a91960ee1cc943e1db6db4e5ae40e902093fc2f8ded51a8c9990868c200`
- 387 lines

Decisions

- Notifications remain conditional: J-08 applies only if notification behavior is offered.
- Weekly reflection covers the three ranked jobs without requiring every category to contain data.
- Export requires initiation, destination choice, and confirmation.
- Restore replacement and full deletion require consequence disclosure and explicit confirmation.
- No screens, navigation, persistence, formats, APIs, or technical mechanisms were selected.

Traceability

- R-001 through R-011 are represented by 11 journeys.
- All 32 criteria, AC-R001-01 through AC-R011-03, appear exactly once in the ownership table.
- Each journey specifies trigger, preconditions, goal, entry context, ordered interaction, decisions, completion, cancellation/recovery, relevant states, consequence boundary, and trace.

Validation

- All three frozen-input hashes matched WO-004 exactly.
- Counted 11 journey sections.
- Counted 32 unique AC ownership rows with no missing or duplicate identifier.
- Confirmed every required journey field appears 11 times.
- Confirmed `design/journeys.md` is the only file under `design/`.

Risks and Open Questions

No blocking issue or change request was identified. Real-use usability hypotheses remain explicitly unproven and are deferred to later Experience validation.

Next Actions

Quality Engineer independently verifies WO-004. If satisfied, the artifact can feed WO-005 through WO-008 and Gate 2 review.