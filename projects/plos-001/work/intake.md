# Gate 0 Intake — Personal Life OS for Android

**Status:** VERIFIED  
**Record version:** 1.0  
**Author:** Director  
**Verifier:** Jude O’Neill, Principal  
**Date:** 2026-08-05  
**Verified:** 2026-08-05

## Named inputs

| Input | Version or revision | Role in intake |
| --- | --- | --- |
| `work/bootstrap.md` | 1.0, confirmed 2026-08-05 | Authoritative Principal mandate |
| `examples/personal-life-os/starter-brief.md` | Hosted pack revision supplied 2026-08-05 | Discovery seed only |
| Principal-provided refined roadmap | Discovery revision discussed 2026-08-05 | Supporting evidence; not approved requirements |
| `START-HERE.md` | Supplied as `START-HERE-1.md` on 2026-08-05 | Hosted operating instructions |

## Requested outcome

Create a private Android-first Personal Life OS for Jude that reduces the mental overhead of managing commitments, projects, routines, reflection, and meaningful interests.

The first three outcome priorities are:

1. Daily and weekly planning and reflection.
2. Keeping promises and delegated follow-ups.
3. Preventing project drift.

Gate 0 does not define the features or measures that will realize those outcomes. Product owns that work at Gate 1, and the Principal approves it.

## Known user and operating context

- Release one has one intended user: Jude O’Neill.
- Jude O’Neill is the sole Principal.
- This is a personal product, separate from work systems and work data.
- Google Calendar and Google Keep are existing systems with which the product must coexist.
- The mandate describes a hybrid layer. Direct integration, read/write behavior, and release-one boundaries remain to be decided at the appropriate gates.
- Release one is a personal installation. Public or broader distribution is not authorized.

## Confirmed constraints

### Product and data

- Android-first and local-first.
- The core daily loop must work offline.
- No release-one dependency on remote synchronization or AI.
- Locally permitted data includes names, important dates, family plans, reflections, and generic care reminders.
- Work content and work backups are excluded.
- Detailed health information, financial data, and location data are out of scope.
- Notifications must be user-configurable.
- Streaks and escalating-pressure mechanics are prohibited.

### Cost, timing, and distribution

- No paid service or dependency is pre-authorized.
- The stated 14-week schedule is a human-equivalent estimate, not agent elapsed time.
- Release one is for Jude’s personal installation only.

### Environment and autonomy

- Development, test, and production must be separate environments.
- In development, the Director may make broad, reversible process and experimentation decisions using synthetic or non-sensitive data and without real-world external effects.
- Domain work remains owned by its named specialist even in development.
- Test or production promotion is not covered by development autonomy.
- The Principal’s bounded delegation of minor development approvals is recorded in `work/authority-delegations/AD-001.md` v1.0. It does not expand Director authority across any consequence boundary or specialist domain.

## Principal-controlled consequence boundaries

The agency must return to Jude for an explicit decision before:

- spending money or adopting a paid dependency;
- collecting, syncing, sharing, or sending personal data to an AI provider;
- destructive deletion, migration, or import overwrite;
- external communication or another service-visible action;
- modifying Google Calendar or another external system;
- accepting residual privacy or security risk;
- promotion to production; or
- launch or broader distribution.

## Open decisions and owners

These are questions for later domain work, not gaps that the Director may fill.

| Decision | Recommendation owner | Decision owner | Earliest gate |
| --- | --- | --- | --- |
| Exact jobs to be done, smallest coherent release loop, goals, non-goals, and outcome signals | Product Lead | Principal | Gate 1 — Intent |
| Whether release one merely coexists with Google Calendar and Keep or directly integrates with either | Product Lead, with later Architecture feasibility | Principal for any personal-data or external-action consequence | Gate 1 — Intent |
| Backup, export, restore, and deletion experience, including whether personal data may leave the device | Product Lead; Architecture later defines the mechanism | Principal for data policy | Gate 1, then Gate 3 |
| Default notification categories, cadence, quiet-hour behavior, and controls within the mandate’s user-configurable boundary | Experience Lead | Product Lead within accepted intent; Principal if intent changes | Gate 2 — Experience |
| Any accessibility needs beyond baseline platform support | Product Lead elicits; Experience Lead specifies accepted needs | Principal | Gate 1, then Gate 2 |
| Technical definition and isolation of development, test, and production | Systems Architect | Principal only if a material cost, privacy, or irreversible tradeoff appears | Gate 3 — Architecture |
| Whether Services or Intelligence should ever activate | Product Lead must establish an approved product reason | Principal | Gate 1 or later change control |

## Dormant capabilities

- Services remains dormant because no backend or remote synchronization is approved.
- Intelligence remains dormant because no AI behavior is approved.
- Android implementation remains inactive until Gates 1 through 4 provide accepted and verified inputs.

## Gate 0 exit check

- [x] Principal identified.
- [x] Requested outcome identified without inventing requirements.
- [x] Known constraints recorded.
- [x] Open decisions named with owners.
- [x] Consequence boundaries recorded.
- [x] Principal confirms that this intake faithfully represents the mandate.

## Principal verification evidence

Principal response received 2026-08-05, recorded verbatim:

> Confirm gate 0 intake. Delegate minor approvals to directlr

The Director interprets `directlr` as `Director`. Gate 0 is `VERIFIED`; Gate 1 discovery may begin through a complete ready work order delegated to the Product Lead.