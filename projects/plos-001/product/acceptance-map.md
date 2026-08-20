# Acceptance Map: Personal Life OS

**Version:** 0.1  
**Review status:** Product owner draft; independent Experience verification pending  
**Gate:** Intent; Principal Gate 1 approval pending  
**Owner:** Product Lead — WO-003  
**Last updated:** 2026-08-06

## Frozen basis and interpretation

| Input | Frozen version/status | Owner-side integrity evidence | Use in this map |
| --- | --- | --- | --- |
| `product/project-brief.md` | v0.1, `In review`; independently verified by Experience on 2026-08-05 | SHA-256 `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` (exactly reproduced by Product) | Sole source of release-one requirements, jobs, goals, scope, data boundaries, constraints, and decisions |
| `work/verifications/WO-002-experience.md` | v1.0, `SATISFIED`, 2026-08-05 | Product read the complete verification record | Evidence that the frozen brief is behaviorally coherent and bounded; not verification of this map |

This map decomposes, but does not change, the 11 frozen `Must` requirements. Every criterion is cumulative within its source requirement. Its condition, action or trigger, and observable outcome are all part of acceptance. The criteria define Product semantics only: they do not prescribe a journey, screen, component, copy, gesture, interaction state, data field, schema, interface, file format, architecture, platform mechanism, or test implementation.

## Minimum acceptance semantics

| Term | Product meaning for acceptance |
| --- | --- |
| **Minimal personal planning context** | Only Jude-selected context needed to make a near-term decision in the selected loop: personal intentions or commitments; promise/waiting ownership and next follow-up; a personal-project title and next move or disposition; and short reflection or review decisions. Optional routine references, important dates, family plans, or generic care reminders may serve only as relevant context within that loop. Loop completion does not require a detailed archive, specialized domain record, or prohibited data category. |
| **Deliberate close** | A conscious end-of-day decision through which Jude can tell what happened to an intention and whether it was resolved or reconsidered. Time passing, omission, or disappearance is not a close. |
| **Clear owner and next follow-up** | Jude can unambiguously tell whether the next move belongs to Jude or another person and can identify the intended point at which Jude will revisit the item. No external contact or message is implied. |
| **Credible next move** | A next action that Jude judges concrete enough to understand how he intends to advance the personal project. Acceptance uses Jude's judgment and assumes no system score, elapsed-time threshold, or fixed work-in-progress rule. |
| **Explicit disposition** | A deliberate decision to pause or consciously release a personal project instead of leaving it without attention by default. It does not imply a fixed project-state model. |
| **Full deletion of app-managed personal data** | After Jude's explicit initiation and confirmation, personal data managed by the product is no longer available in the product. Copies previously created at a destination chosen by Jude remain outside app-managed data and under Jude's control. |

## Requirement-to-acceptance map

Acceptance criteria listed in a row inherit every JTBD and goal trace anchor in that row.

| Source requirement | Priority | Frozen user-visible behavior | Acceptance criteria | JTBD and goal trace anchors |
| --- | --- | --- | --- | --- |
| R-001 | Must | Jude can record and revise the minimal personal planning context needed by the selected value loop. | AC-R001-01 through AC-R001-03 | JTBD-01, JTBD-02, JTBD-03; G-01, G-02, G-03, G-04 |
| R-002 | Must | Jude can form a personal daily intention about what deserves attention. | AC-R002-01 through AC-R002-02 | JTBD-01; G-01 |
| R-003 | Must | Jude can deliberately close a daily intention. | AC-R003-01 through AC-R003-03 | JTBD-01; G-01 |
| R-004 | Must | Jude can distinguish a personal promise he owns from an item for which he is waiting on someone else. | AC-R004-01 through AC-R004-03 | JTBD-02; G-02 |
| R-005 | Must | Jude can make a deliberate decision about a personal project that lacks a credible next move or intended attention. | AC-R005-01 through AC-R005-03 | JTBD-03; G-03 |
| R-006 | Must | Jude can complete a weekly reflection across the three ranked jobs without entering a specialized domain workflow. | AC-R006-01 through AC-R006-03 | JTBD-01, JTBD-02, JTBD-03; G-01, G-02, G-03, G-04 |
| R-007 | Must | Jude can complete the selected value loop while Calendar and Keep remain separate and while the device has no network connection. | AC-R007-01 through AC-R007-03 | JTBD-01, JTBD-02, JTBD-03; G-01, G-02, G-03, G-04 |
| R-008 | Must | Jude can control or completely opt out of every release-one notification behavior that is offered. | AC-R008-01 through AC-R008-03 | G-04 |
| R-009 | Must | Jude can explicitly initiate an export or backup and choose its destination. | AC-R009-01 through AC-R009-03 | G-04 |
| R-010 | Must | Jude can explicitly initiate restoration of a user-chosen backup. | AC-R010-01 through AC-R010-03 | G-04 |
| R-011 | Must | Jude can explicitly initiate full deletion of app-managed personal data. | AC-R011-01 through AC-R011-03 | G-04 |

## Acceptance-criterion registry

| Acceptance ID | Condition | User action or trigger | Observable outcome |
| --- | --- | --- | --- |
| AC-R001-01 | Jude has personal context relevant to a near-term decision in the selected value loop. | Jude records that context or revises context he previously recorded. | The current Jude-chosen context is available to Jude when he makes the associated daily or weekly decision. |
| AC-R001-02 | Jude undertakes any part of the daily or weekly loop. | Jude supplies only the context he considers necessary for that decision. | He can complete the loop using the supported minimal categories; a detailed personal archive, specialized domain record, or prohibited data category is never required. |
| AC-R001-03 | A routine reference, important date, family plan, or generic care reminder is relevant to a loop decision. | Jude chooses whether to include that minimal context. | It can inform the decision without becoming a required category or a specialized workflow. |
| AC-R002-01 | Jude is beginning a day and wants to decide what deserves attention. | Jude begins the daily loop and chooses one or more personal commitments for attention. | Jude can tell which commitment or commitments he intentionally chose for the day. |
| AC-R002-02 | The device has no network connection and Jude has no external account connected. | Jude forms the daily intention. | The intention can be formed and remains identifiable without network access, Calendar or Keep content, or an external account. |
| AC-R003-01 | A daily intention exists and Jude is ending or reviewing the day. | Jude deliberately closes the intention. | Jude can tell what happened and whether the intention was resolved or reconsidered. |
| AC-R003-02 | Jude chooses to reconsider rather than resolve an intention. | Jude makes that reconsideration decision. | The reconsideration is distinguishable from resolution and the intention remains accounted for. |
| AC-R003-03 | An intention is unresolved and Jude has made no close decision about it. | The day ends or Jude leaves the close incomplete. | The intention remains identifiable as unresolved; it does not disappear merely through time, omission, or an incomplete close. |
| AC-R004-01 | Jude reviews an open personal promise or waiting item. | Jude identifies whether it is his promise or an item awaiting another person's move. | Jude can tell who owns the next move. |
| AC-R004-02 | An open personal promise or waiting item has an identified owner. | Jude identifies the next point at which he intends to revisit it. | On review, Jude can tell both the owner of the next move and the next follow-up. |
| AC-R004-03 | Jude records, changes, or reviews owner or follow-up context. | Jude completes that in-product action. | No external message, calendar change, share, or other service-visible action occurs. |
| AC-R005-01 | During reflection, Jude notices a relevant personal project without a credible next move or intended attention. | Jude gives it a credible next move or makes an explicit disposition decision. | Jude can tell the resulting next move, pause decision, or conscious release decision. |
| AC-R005-02 | Jude elects to advance a relevant personal project. | Jude states the next move he judges concrete enough to act on. | He can understand what he intends to do next without a product-generated credibility score. |
| AC-R005-03 | No fixed project state, elapsed-time drift threshold, or work-in-progress limit exists. | Jude decides during reflection whether a personal project needs attention. | He can make the next-move or disposition decision without a fixed state model or numerical drift rule deciding for him. |
| AC-R006-01 | Jude begins a weekly reflection with any unresolved daily intention, open promise/waiting item, or relevant personal project. | Jude considers the minimal available context across the three ranked jobs. | He can identify what needs an attention, owner/follow-up, next-move, or disposition decision. |
| AC-R006-02 | Jude reaches the end of the weekly reflection. | Jude makes the relevant decisions surfaced by the reflection. | He can tell what attention changed, which follow-up is next, and which reviewed project received a next move or disposition, for each applicable category. |
| AC-R006-03 | Jude has no specialized domain record or detailed personal archive. | Jude completes the weekly reflection using only minimal planning context. | The weekly reflection remains completable across all three jobs without entering or maintaining a specialized domain workflow. |
| AC-R007-01 | The device has no network connection and no external account, backend, synchronization service, or AI provider is available. | Jude records or revises minimal context, forms or closes a daily intention, or completes the weekly reflection. | Every selected core-loop behavior remains usable and its resulting decision remains available to Jude. |
| AC-R007-02 | Google Calendar and Google Keep remain separate. | Jude completes the selected value loop using context he chooses to record. | Completion requires no connection to, read from, import or copy from, monitoring of, or write to Calendar or Keep. |
| AC-R007-03 | Jude performs a core-loop action while offline. | The action completes. | It produces no silent external action and does not depend on a backend, remote synchronization, remote analytics, telemetry, or AI processing. |
| AC-R008-01 | A release-one notification behavior is offered. | Jude reviews or changes its controls. | Jude can control its category, timing, quiet hours, and frequency limits, and can opt out of it completely. |
| AC-R008-02 | Jude opts out of an offered notification category or all offered notifications. | The opt-out takes effect. | Notifications in the opted-out scope cease, while the selected value loop remains completable without them. |
| AC-R008-03 | A notification is offered, changed, ignored, or disabled. | Jude chooses how or whether to respond. | No streak, shame, escalating pressure, or punitive consequence is created. |
| AC-R009-01 | App-managed personal data exists and Jude has not initiated export or backup and chosen a destination. | No portability action is taken, or Jude leaves it before choosing a destination. | No export or backup copy is created by the product and no app-managed personal data leaves the device. |
| AC-R009-02 | Jude wants an export or backup. | Jude explicitly initiates it and chooses its destination. | A copy containing only supported personal data is directed to the chosen destination, and Jude can tell whether the action completed or did not take effect. |
| AC-R009-03 | Jude initiates an export or backup. | The product determines the content eligible for that action. | Work data and every prohibited data category are absent; the action does not create automatic synchronization or an app-chosen remote copy. |
| AC-R010-01 | Jude has selected a backup he chose and wants to restore it. | Jude explicitly initiates restoration. | Jude can proceed with the restoration and can tell whether it completed or did not take effect, without any silent replacement. |
| AC-R010-02 | The initiated restoration could replace existing app-managed information. | Before replacement, Jude is made aware of the destructive consequence and explicitly confirms it. | Replacement can occur only after that confirmation. |
| AC-R010-03 | A restoration could replace existing information, but Jude cancels or does not confirm. | The restore attempt ends without confirmation. | Existing app-managed information is not replaced. |
| AC-R011-01 | Jude wants all app-managed personal data deleted. | Jude explicitly initiates full deletion, is made aware of the destructive consequence, and confirms it. | The app-managed personal data is no longer available in the product, and Jude can tell the deletion completed. |
| AC-R011-02 | Full deletion has been initiated but Jude cancels or does not confirm. | The deletion attempt ends without confirmation. | App-managed personal data remains available; no destructive consequence occurs. |
| AC-R011-03 | Jude has not both initiated and confirmed full deletion. | Normal use, time passage, notification behavior, restore, or another product event occurs. | Full deletion never occurs automatically or silently. |

## JTBD and goal coverage

The traces below demonstrate that every frozen job and goal has acceptance coverage. Requirement coverage is complete in the 11-row requirement map above, and every acceptance ID is owned by exactly one row there.

| Frozen outcome | Acceptance coverage |
| --- | --- |
| JTBD-01 — Decide attention and reflect on what happened | AC-R001-01–03, AC-R002-01–02, AC-R003-01–03, AC-R006-01–03, AC-R007-01–03 |
| JTBD-02 — Know owner and revisit point for promises/waiting | AC-R001-01–03, AC-R004-01–03, AC-R006-01–03, AC-R007-01–03 |
| JTBD-03 — Notice and decide personal-project drift | AC-R001-01–03, AC-R005-01–03, AC-R006-01–03, AC-R007-01–03 |
| G-01 — Make daily and weekly attention deliberate | AC-R001-01–03, AC-R002-01–02, AC-R003-01–03, AC-R006-01–03, AC-R007-01–03 |
| G-02 — Reduce memory dependence for personal promises | AC-R001-01–03, AC-R004-01–03, AC-R006-01–03, AC-R007-01–03 |
| G-03 — Prevent silent personal-project drift | AC-R001-01–03, AC-R005-01–03, AC-R006-01–03, AC-R007-01–03 |
| G-04 — Remove more confusion than the product creates | AC-R001-01–03, AC-R006-01–03, AC-R007-01–03, AC-R008-01–03, AC-R009-01–03, AC-R010-01–03, AC-R011-01–03 |

G-01 through G-04 remain qualitative outcome signals pending initial real-use evidence. This map sets no duration, frequency, percentage, performance, adoption, or roadmap-time threshold. A signal being observable in real use is the current Product target; any numerical target and review date require a later documented baseline and Product/Quality review.

## Inherited constraint and evidence posture

This section preserves cross-cutting context without creating another source requirement.

| Class | Frozen posture | Acceptance implication |
| --- | --- | --- |
| Facts | Jude is the sole Principal and release-one user; Calendar and Keep are existing, separate tools; no observed-use baseline exists. | Criteria address one personal installation and make no multi-user, integration, or baseline-performance claim. |
| Principal decisions | D-01 A through D-07 A select the cross-priority loop, coexistence-only, minimal records, user-controlled portability/deletion, no AI or remote sync, qualitative signals before thresholds, and no additional known accessibility need. | This map operationalizes those decisions but does not approve this artifact, experience, architecture, risk, implementation, or release. |
| Constraints | Android-first; personal-only and separate from work; local-first/offline core behavior; baseline Android accessibility support; no network/account/backend/AI requirement; no paid dependency; one personal installation; separated development, test, and production environments; no approved schedule. | Downstream work must preserve these constraints while Experience and Architecture select their respective details. No accessibility mechanism, environment topology, or timing target is selected here. |
| Hypotheses | A-01 through A-08 remain unproven, including loop value versus burden, sufficiency of minimal context, tolerability of Calendar/Keep coexistence, usefulness of qualitative baselines, understandable destructive controls, non-coercive notifications, and current accessibility fit. | Meeting these acceptance criteria does not prove real-use success. The named later evidence and owners in the frozen brief remain required. |

## Personal-data boundary trace

These are classifications inherited from the frozen brief, not new data or implementation decisions.

| Data category | Release-one classification and control | Acceptance trace | Principal review state |
| --- | --- | --- | --- |
| DI-01 — Personal intentions/commitments and relevant dates | Permitted minimal personal data; controlled by Jude; on-device except for explicit export/backup; subject to full deletion | AC-R001-01–02, AC-R002-01–02, AC-R003-01–03, AC-R007-01–03, AC-R009-01–03, AC-R011-01–03 | Decided; no further intent decision |
| DI-02 — Minimal owner/recipient context and next follow-up dates | Permitted only for personal promises/waiting; no external communication implied; same portability/deletion controls as DI-01 | AC-R001-01–02, AC-R004-01–03, AC-R007-01–03, AC-R009-01–03, AC-R011-01–03 | Decided; no further intent decision |
| DI-03 — Personal-project titles, next moves, and dispositions | Permitted minimal personal data; no detailed project archive required; same portability/deletion controls as DI-01 | AC-R001-01–02, AC-R005-01–03, AC-R007-01–03, AC-R009-01–03, AC-R011-01–03 | Decided; no further intent decision |
| DI-04 — Short reflections and review decisions | Permitted minimal personal data; full journals and detailed dossiers excluded; same portability/deletion controls as DI-01 | AC-R001-01–02, AC-R003-01–03, AC-R006-01–03, AC-R007-01–03, AC-R009-01–03, AC-R011-01–03 | Decided; no further intent decision |
| DI-05 — Minimal routine references, important dates, family plans, and generic care reminders | Permitted only when Jude chooses them as minimal context; never required and not a specialized workflow | AC-R001-03, AC-R006-03, AC-R007-01–03, AC-R009-01–03, AC-R011-01–03 | Decided; no further intent decision |
| DI-06 — Export/backup copy of DI-01 through DI-05 | Permitted only through Jude's explicit initiation and destination choice; no automatic synchronization; never includes work data | AC-R009-01–03, AC-R010-01–03 | Decided; format and protection deferred |
| DI-07 — Locally derived use patterns | Not collected in release one and not required for qualitative outcome signals | AC-R001-02, qualitative-measures statement above | Any later proposal returns to Product change control and applicable privacy review |
| DI-08 — Calendar/Keep content, metadata, account identifiers, or copied items | Excluded; no access, import, copy, monitoring, or write | AC-R002-02, AC-R007-02 | Exclusion decided; any later access requires Principal review and applicable gates |
| DI-09 — Detailed relationship notes, journals, manuscripts/essays, research/source archives, media, archives, voice, or app-to-app intake | Excluded as supported release-one data | AC-R001-02, AC-R006-03, AC-R009-03 | Exclusion decided; later inclusion requires change control |
| DI-10 — Work content and work backups/exports | Prohibited; never collected, stored, backed up, or exported | AC-R001-02, AC-R009-03 | Prohibition decided |
| DI-11 — Detailed health information, financial data, or location data | Prohibited; never collected or stored and absent from backups/exports | AC-R001-02, AC-R009-03 | Prohibition decided |
| DI-12 — Credentials, API keys, regulated data, employee/customer records, or confidential company material | Prohibited; never collected or stored and absent from backups/exports | AC-R001-02, AC-R009-03 | Prohibition decided |
| DI-13 — AI prompts/context/outputs, provider identifiers, remotely synchronized records, account data, or server copies | Excluded; no AI-provider transfer, backend copy, or remote synchronization | AC-R007-01–03, AC-R009-03 | Exclusion decided; any later proposal requires explicit data, autonomy, and cost decisions |

## External, destructive, background, and paid-action trace

| Action or dependency | Release-one classification and consequence control | Acceptance trace | Principal review state |
| --- | --- | --- | --- |
| Local notifications | Permitted only if offered within the configurable, optional, non-coercive boundary; not an external communication | AC-R008-01–03 | Boundary decided; defaults and interaction behavior deferred to Experience |
| Export or backup | Required, user-initiated external data movement to a user-chosen destination | AC-R009-01–03 | Approved boundary; mechanism and format deferred |
| Restore with possible replacement | Required and potentially destructive; explicit initiation, consequence awareness, and confirmation precede replacement | AC-R010-01–03 | Approved boundary; safe experience and mechanism deferred |
| Full deletion | Required and destructive; explicit initiation, consequence awareness, and confirmation precede deletion | AC-R011-01–03 | Approved boundary; experience, mechanism, and later verification deferred |
| Direct Calendar/Keep access or modification | Excluded, including read, import, copy, monitoring, and write | AC-R004-03, AC-R007-02 | Any later direct access or external change returns to the Principal and applicable gates |
| Other external communication, sharing, or service-visible action | Excluded; no message, share, calendar change, or other external effect | AC-R004-03, AC-R007-03 | Any later proposal requires explicit Principal intent |
| Background monitoring, remote analytics, or telemetry | Excluded | AC-R007-03 | Any later proposal requires change control; notification mechanism remains deferred |
| AI processing or AI-initiated action | Excluded | AC-R007-01, AC-R007-03 | Any later proposal requires explicit data, autonomy, and cost decisions |
| Remote synchronization, backend service, or remote copy | Excluded | AC-R007-01, AC-R007-03, AC-R009-03 | Any later proposal requires explicit Principal intent |
| Paid service, license, API, storage, model, or purchase | No paid dependency is authorized or required | All criteria are accepted without a paid dependency | Any later spend returns to Jude with cost and an alternative before adoption |
| Production promotion, launch, or broader distribution | Outside this acceptance map and current personal-installation authorization | None; no release acceptance is claimed | Requires its own gates and explicit Principal approval |

## Deferred decisions and owner boundaries

| Deferred matter | Later owner | Boundary retained here |
| --- | --- | --- |
| Journeys, navigation, screens, components, gestures, content copy, interaction states, notification defaults and exact interaction behavior, and validation of current accessibility needs | Experience | Must express the observable outcomes above without changing them; every offered notification remains configurable and optional |
| Persistence, storage, notification, offline, environment-separation, export, backup, restore, and deletion mechanisms; interfaces, formats, protection, and destination handling | Architecture | Must satisfy these outcomes without direct Calendar/Keep access, network-dependent core behavior, AI, remote sync, or paid dependency |
| Test design, test implementation, fixtures, execution evidence, and later measurement method | Quality and builders | Must verify the accepted observable semantics; numerical outcome thresholds wait for baseline evidence |
| Security findings, protective-control sufficiency, and any resulting risk decision | Security and the later designated risk owner | No security verdict or risk acceptance is made here |
| Baseline collection and any later numerical Product target | Product, with Quality input | G-01 through G-04 remain qualitative until real-use evidence exists |
| Gate 1 intent approval, production promotion, launch, distribution, and any consequential scope/data/autonomy/cost change | Principal and applicable later gate owners | None is approved by this map |

## Owner-side completeness statement

- Requirement inventory: 11 of 11 frozen requirements mapped once as source requirements; priorities remain 11 `Must` and no other priority appears.
- Acceptance inventory: 32 unique criteria, AC-R001-01 through AC-R011-03, each owned by one source requirement and carrying a condition, action or trigger, and observable outcome.
- Outcome inventory: JTBD-01 through JTBD-03 and G-01 through G-04 all have explicit acceptance coverage; no requirement or criterion is orphaned.
- Required scenario inventory: positive behavior, excluded/negative behavior, offline operation, notification control and opt-out, user-initiated portability, and confirmation before destructive restore or deletion are explicitly covered.
- Boundary inventory: DI-01 through DI-13 and every external, destructive, background, AI, remote, paid, and distribution classification from the frozen brief are traced without adding a category or action.

Independent Experience verification of this acceptance map and Principal Gate 1 approval are pending. This artifact claims no independent verification, gate acceptance, test result, security verdict, architecture or implementation readiness, production promotion, launch approval, or broader-distribution authorization.