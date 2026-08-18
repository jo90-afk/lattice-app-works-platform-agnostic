# Release-One Information Architecture: Personal Life OS

**Revision:** 0.4  
**Status:** Owner draft  
**Owner:** Experience Lead — WO-005-R3  
**Last updated:** 2026-08-06  
**Verification and approval:** Quality verification and Gate 2 approval remain pending.

## Remediation basis

| Input | Frozen version/status | SHA-256 |
| --- | --- | --- |
| `product/project-brief.md` | Gate 1 accepted v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | Gate 1 accepted v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |
| `design/journeys.md` | verified/concurred revision 0.2 | `acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019` |
| `work/verifications/WO-004-R1-quality.md` | Fresh Quality `SATISFIED`; `PASS` | `d50c9b136d5a06ca6b9629b7c5cae5bc7b519178fa90c2d425d9a03cc28c0bfa` |
| `work/reviews/WO-004-R1-product.md` | Fresh Product `CONCUR` | `93d7dfaf5d19a6aae687653e1d16af1f0b1bb711632c6070801fda183336c09e` |
| `design/information-architecture.md` | superseded revision 0.2 | `848e767cd60a83c8850bd12efc988430f5b62f530aaf38f07e1877eaa5a04dac` |
| `work/verifications/WO-005-R1-quality.md` | prior full regression basis; `SATISFIED`; `PASS` | `dca4ced0f958311294fc145a46e45cbfa22b659220d71bfe299ff0f8c62e6f42` |

This artifact defines user-facing organization, destinations, and movement among the verified release-one journeys. It does not change Product semantics or select screens, storage, schemas, APIs, file formats, services, platform components, or any other implementation mechanism. All examples, if used in later validation, must be synthetic.

## Revision 0.4 F-003 remediation record

- **F-003 — J-09/S-03:** When an authorized export's outcome is not yet established, S-03 keeps Jude's chosen destination visible alongside the uncertainty and possible completed/no-effect terminal outcomes. It asserts neither success nor no effect, never repeats the attempt, and permits a new attempt only after established no effect through fresh initiation and destination choice.
- **Preservation:** Destination choice remains the sole final export authorization action; no second export confirmation is introduced. Restore replacement and full deletion confirmations, the 20-destination inventory, all J/R/AC sets, and all non-F-003 declarations remain unchanged.

## Revision 0.3 downstream-remediation record

- **J-09/S-03:** Removed the additional mandatory export confirmation. During destination selection, Jude sees the eligible scope and external-copy consequence; deliberately completing destination choice authorizes exactly one attempt. Leaving, Back, cancellation, denial, or interruption before completed destination choice starts no attempt and creates no copy. After completed destination choice, status distinguishes in progress, completed, did not take effect, and outcome not yet established; no attempt repeats silently, and only established no effect permits a new attempt through fresh initiation and destination choice.
- **Preservation:** Restore replacement and full deletion retain their distinct consequence disclosure and explicit destructive confirmation. The existing 20 destinations, Today/Reflect/Context priority, DI-04/DI-05 routes, F-001/F-002 recovery behavior, and all non-J-09 traces and routes are unchanged.
- **Downstream requirement:** The existing `design/state-matrix.md` draft requires remediation against revision 0.3 before verification.

## Revision 0.2 change record

- **F-001:** Reconciled J-01 origins, collection routes, entry destinations, DI-04 ownership, and optional DI-05 eligibility into one route and trace without changing J-03 deliberate-close behavior.
- **F-002:** Added explicit re-entry to S-03 after interruption once export destination choice completed or export was in progress, and to S-04 or S-05 after interruption of a confirmed or in-progress destructive operation, with visible status and no silent repeat or assumed outcome.

No destination, requirement, acceptance criterion, journey, hierarchy, data category, consequence boundary, or deferred-owner boundary changed.

## Information model in Jude's language

Release one contains only the planning information needed for a near-term personal decision. The concepts below are not records, fields, identifiers, or storage entities.

| Concept | User purpose | Permitted personal-context boundary | Relationship to the loop |
| --- | --- | --- | --- |
| Commitment context | State a personal commitment and, when useful, its relevant date. | DI-01 only; no work content, Calendar/Keep content, or detailed archive. | May be selected into a daily intention or considered during weekly reflection. |
| Daily intention | Identify one or more personal commitments Jude deliberately chooses for attention. | A deliberate use of DI-01; the product does not rank, recommend, or infer the choice. | Begins on **Today** and remains identifiable until Jude deliberately closes or reconsiders it. |
| Daily close decision | Record enough short reflection to distinguish resolved, reconsidered, and still-unresolved intentions. | DI-04 linked to the applicable intention; not a journal. | Feeds the daily result and the attention portion of weekly reflection. Reconsidered and unresolved are not treated as resolved. |
| Promise or waiting item | Identify whether Jude or another person owns the next move and when Jude intends to revisit it. | DI-02 only; another person is represented by minimal owner/recipient context. No message or external action follows. | Can be reviewed directly from **Context** or within weekly reflection. |
| Personal project context | Name a personal project and capture Jude's next move, pause decision, or conscious release. | DI-03 only; no project archive, score, fixed state model, drift threshold, or work-in-progress rule. | Can be reviewed directly from **Context** or within weekly reflection. |
| Weekly reflection decision | Show what attention changed, which follow-up is next and who owns it, and which reviewed project received a next move or disposition. | Short DI-04 review decisions using only applicable DI-01 through DI-03 context. | Completes the cross-priority loop without requiring every category to contain an item. |
| Optional supporting reference | Supply a routine reference, important date, family plan, or generic care reminder only when Jude considers it relevant. | DI-05 only; optional, minimal, and never a specialized area or completion requirement. | May support an existing beginning, ending, attention, promise/waiting, project, or reflection decision through its applicable context-entry route; it is not an independent destination or workflow. |
| Export or backup copy | Give Jude a portable copy of supported personal context. | DI-06: a copy of eligible DI-01 through DI-05 only. During destination selection, eligible scope and the external-copy consequence are visible; deliberate completion of destination choice authorizes exactly one attempt without another mandatory in-app confirmation. | Exists outside app-managed data at Jude's chosen destination; it is not synchronization and is not removed by in-app full deletion. |

### Concept relationships

- **Today** organizes daily intention and deliberate close. It is the stable starting point and the primary daily route.
- **Reflect** gathers only applicable unresolved intentions, open promise/waiting items, and relevant personal projects, then presents a cross-category decision summary.
- **Context** is one supporting area with three groups: **Commitments & intentions**, **Promises & waiting**, and **Personal projects**. These groups remain supporting context, not specialized suites.
- An optional supporting reference appears only with the decision it informs; there is no separate routines, dates, family, care, people, journal, or domain destination.
- A completed decision updates the applicable concept. Skipped, cancelled, interrupted, or no-effect work remains unresolved or leaves the previously established context unchanged, as required by the verified journey.
- Export/backup may copy eligible context outward only through J-09. Restore may replace app-managed information only through J-10. Full deletion applies only through J-11 and does not reach a previously created external copy.

## Organization and navigation model

### Primary and global destinations

| Level | Destination | Role in release one |
| --- | --- | --- |
| Stable start and primary | **Today** | A normal app launch with no interrupted destination-authorized or in-progress export and no interrupted confirmed or in-progress restore or deletion lands here. It shows the current daily decision, a clear route to form an intention, a clear route to close applicable intentions, and a route to continue an incomplete daily close. |
| Primary | **Reflect** | Starts or continues the weekly cross-priority reflection and exposes its attention, promises/waiting, projects, and summary sequence. |
| Primary | **Context** | Holds the three minimal supporting context groups. It enables direct review without making promise/waiting or projects independent top-level suites. |
| Global secondary | **Settings & data** | A consistently named action from Today, Reflect, and Context. It leads to notification controls, export/backup, restore, and full deletion without promoting any of them as prompts. |

The persistent primary navigation contains **Today**, **Reflect**, and **Context**. **Settings & data** is available through the same labeled global action on each primary destination; it must not be an icon-only or gesture-only route. No account, network, Calendar/Keep connection, permission grant, setup wizard, or notification choice gates access to the primary destinations.

### Hierarchy

- **Today**
  - Form daily intention
  - Close day
- **Reflect**
  - Attention
  - Promises & waiting
  - Personal projects
  - Reflection summary
- **Context**
  - Commitments & intentions
    - Add or revise commitment context
  - Promises & waiting
    - Add, review, or revise an item
  - Personal projects
    - Add, review, or decide a project
- **Settings & data**
  - Notifications, if any notification behavior is offered
  - Export or backup
  - Restore
  - Delete all app data

### Movement and return rules

1. A normal launch opens **Today** unless a destination-authorized or in-progress export, or a confirmed or in-progress restore or deletion, requires the re-entry defined in rule 11. Switching among Today, Reflect, and Context does not imply completion, cancellation, resolution, or loss of any previously completed decision.
2. A nested destination always offers a visible route back to its parent. Android system Back follows the same hierarchy; from a primary destination it follows normal platform exit/background behavior.
3. Context entry opened from Today or Reflect returns to the exact originating daily or weekly stage after completion or cancellation. Context entry opened from Context returns to its originating group.
4. The owning primary destination exposes the applicable continuation route: **Today** for an incomplete daily close and **Reflect** for an incomplete weekly reflection. Re-entry returns to the first still-unresolved applicable decision; it does not claim that the overall flow completed. **Settings & data** exposes the owning consequence-operation status route defined in rule 11; that route reviews status and never restarts the operation.
5. Decisions already completed before an interruption remain visible. A new entry left incomplete is not made current; a cancelled revision or no-effect outcome preserves the previously established information. Exact draft handling is an Architecture decision and may not weaken these outcomes.
6. If navigation away would discard entered but uncompleted changes, Jude receives an explicit choice to keep editing or discard. Dismissal is not discard. Exact presentation and wording belong to WO-006 and WO-007.
7. A nested decision needed by weekly reflection returns to the reflection stage that requested it. Jude does not have to rediscover the weekly flow after closing an intention, reviewing a promise/waiting item, or deciding a project.
8. No destination is reached only through a notification. If an offered notification provides an in-product route, it opens an existing applicable start or continuation destination. Ignoring or dismissing it changes nothing.
9. Export, restore, and deletion remain inside **Settings & data** and never start from an automatic prompt. Export retains a safe exit before destination choice is completed; restore and deletion retain safe exits before their destructive confirmations.
10. Restore replacement and full deletion place consequence disclosure and explicit confirmation on the only route to the destructive effect. Back, dismissal, silence, cancellation, or loss of access returns without the destructive effect.
11. After interruption once export destination choice has completed or export is in progress, app re-entry returns to S-03 status. After interruption of a confirmed or in-progress restore or deletion, app re-entry returns to S-04 or S-05 status. If Jude reaches S-01 instead, a visible **Review export status**, **Review restore status**, or **Review deletion status** action returns to the same owning view. It identifies the operation and exposes **in progress**, **completed**, **did not take effect**, or **outcome not yet established**, together with the possible terminal outcomes. For an export whose outcome is not yet established, S-03 identifies Jude's chosen destination alongside the uncertainty and possible completed/no-effect terminal outcomes. Re-entry never repeats the operation, treats an unknown outcome as success or no effect, or conceals possible external movement, replacement, or deletion. For export, a new attempt is available only after established no effect and requires fresh initiation and completed destination choice; restore and deletion retries retain their original consequence disclosure and confirmation boundaries.

## Complete destination inventory

Ranges such as `AC-R003-01–03` are inclusive. A destination family includes only the named collection, detail, or flow stages described in its row; it does not imply an unlisted screen or technical component.

| ID and destination | User purpose and eligible information | Principal actions | Entry and exit routes | Journey and requirement trace |
| --- | --- | --- | --- | --- |
| T-01 **Today** | See the current daily intention, unresolved close work, and applicable completed daily decisions. DI-01 and linked short DI-04 decisions only. | Form an intention; close applicable intentions; continue an incomplete close; use primary navigation to open Context; open Settings & data. | Normal launch when no consequence-operation re-entry is due, or primary navigation. Opens T-02, T-03, or S-01; primary navigation reaches C-01. Returns here after daily completion/cancellation. | J-01, J-02, J-03, J-07; R-001 (`AC-R001-01–03`), R-002 (`AC-R002-01–02`), R-003 (`AC-R003-01–03`), R-007 (`AC-R007-01–03`). |
| T-02 **Form daily intention** | Choose one or more personal commitments for today's attention using DI-01 and optional relevant DI-05 context. | Review current context; add or revise minimum DI-01 or optional DI-05 context through C-03; choose; review the proposed choice; complete or cancel. | From T-01; C-03 returns here. Completion, cancellation, or no effect returns to T-01. | J-01, J-02, J-07; R-001 (`AC-R001-01–03`), R-002 (`AC-R002-01–02`), R-007 (`AC-R007-01–03`). |
| T-03 **Close day** | Consider each applicable intention and distinguish resolved, reconsidered, and unresolved using short DI-04 context, with optional relevant DI-05 support. | Review intention; record or revise the short reflection; optionally enter C-03 for relevant DI-05 support; choose resolved or reconsidered; review close summary; complete, cancel, or leave unresolved. | From T-01 or R-02; C-03 returns here. Returns to its origin after completion/cancellation; T-01 and R-01 retain continuation routes while work remains. | J-01, J-03, J-06, J-07; R-001 (`AC-R001-01–03`), R-003 (`AC-R003-01–03`), R-006 (`AC-R006-01–02`), R-007 (`AC-R007-01–03`). |
| R-01 **Reflect** | Start or continue a weekly reflection across applicable attention, promises/waiting, and project context; show whether a reflection is incomplete without fabricating completion. | Start; continue; review a completed reflection summary; open Settings & data. | Primary navigation or an applicable offered notification. Opens R-02; completion returns here. | J-01, J-06, J-07; R-001 (`AC-R001-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| R-02 **Reflection — Attention** | Review unresolved intentions and minimal commitments; record or revise changed or continued attention as short DI-04 context. DI-01 and optional relevant DI-05 support remain eligible. | Review; record or revise the short attention decision; enter T-03 when a close decision is needed; enter C-03 for DI-01 or relevant DI-05 context; continue or leave incomplete. | From R-01; T-03 or C-03 returns here; proceeds to R-03; exit returns to R-01 with continuation available. | J-01, J-03, J-06, J-07; R-001 (`AC-R001-01–03`), R-003 (`AC-R003-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| R-03 **Reflection — Promises & waiting** | Review applicable open DI-02 items and record or revise the applicable short DI-04 review decision without inference; optional relevant DI-05 support is eligible through C-05. | Review item; enter C-05 to establish or revise owner, revisit point, or relevant DI-05 support; record the short review decision; continue or leave incomplete. | From R-02; C-05 returns here; proceeds to R-04; exit returns to R-01 with continuation available. | J-01, J-04, J-06, J-07; R-001 (`AC-R001-01–03`), R-004 (`AC-R004-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| R-04 **Reflection — Personal projects** | Review applicable DI-03 project context and record or revise the applicable short DI-04 review decision; optional relevant DI-05 support is eligible through C-07. | Decide which project needs attention; enter C-07 for its decision or relevant DI-05 support; record the short review decision; continue or leave incomplete. | From R-03; C-07 returns here; proceeds to R-05; exit returns to R-01 with continuation available. | J-01, J-05, J-06, J-07; R-001 (`AC-R001-01–03`), R-005 (`AC-R005-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| R-05 **Reflection summary** | Show, for each applicable category, the completed short DI-04 attention, ownership/follow-up, and project review decisions; empty categories remain explicit. | Review current results; return to the owning stage to revise a short review decision; complete reflection. | From R-04. Completion returns to R-01; returning to a stage follows R-02 through R-04 without losing completed decisions. | J-01, J-06, J-07; R-001 (`AC-R001-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| C-01 **Context** | Find the three minimal supporting groups without entering a specialized suite. Only DI-01 through DI-05 may appear. | Open commitments & intentions, promises & waiting, or personal projects; open Settings & data. | Primary navigation. Opens C-02, C-04, C-06, or S-01; each group returns here. | J-01, J-04, J-05, J-07; R-001 (`AC-R001-01–03`), R-004 (`AC-R004-01–03`), R-005 (`AC-R005-01–03`), R-007 (`AC-R007-01–03`). |
| C-02 **Commitments & intentions** | Review current DI-01 commitment context and identifiable daily intention outcomes; no detailed history or archive. | Add minimum context; open current context to revise; return to Today. | From C-01. Opens C-03; returns to C-01 or moves to T-01 by explicit choice. | J-01, J-02, J-03, J-07; R-001 (`AC-R001-01–03`), R-002 (`AC-R002-01–02`), R-003 (`AC-R003-01–03`), R-007 (`AC-R007-01–03`). |
| C-03 **Commitment context entry/revision** | Record or revise only the DI-01 context, or optional relevant DI-05 support, needed by the originating beginning, ending, or reflection decision. | Enter or revise eligible minimum context; review the proposed context; complete; cancel; retry after no effect. | From C-02, T-02, T-03, or R-02. Returns to the exact origin; a cancelled revision leaves prior context unchanged. | J-01, J-02, J-03, J-06, J-07; R-001 (`AC-R001-01–03`), R-002 (`AC-R002-01–02`), R-003 (`AC-R003-01–03`), R-006 (`AC-R006-01`, `AC-R006-03`), R-007 (`AC-R007-01–03`). |
| C-04 **Promises & waiting** | Review open DI-02 items with owner and next follow-up visible together; state true absence without requiring creation. | Add an item; open an item; return to reflection when applicable. | From C-01. Opens C-05; returns to C-01. | J-01, J-04, J-07; R-001 (`AC-R001-01–02`), R-004 (`AC-R004-01–03`), R-007 (`AC-R007-01–03`). |
| C-05 **Promise/waiting entry or review** | Establish or revise minimal DI-02 item context, next-move ownership, Jude's revisit point, and optional DI-05 support only when relevant to that decision. | Choose Jude or another person as owner; add minimal owner context if needed; choose next follow-up; optionally add or revise relevant DI-05 support; complete, cancel, or retry. | From C-04 or R-03. Returns to exact origin; cancellation/no effect preserves prior information and produces no external action. | J-01, J-04, J-06, J-07; R-001 (`AC-R001-01–03`), R-004 (`AC-R004-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| C-06 **Personal projects** | Review minimal DI-03 project titles and their current next move or explicit disposition; state true absence without requiring an archive. | Add minimal project context; open a project decision; return to reflection when applicable. | From C-01. Opens C-07; returns to C-01. | J-01, J-05, J-07; R-001 (`AC-R001-01–02`), R-005 (`AC-R005-01–03`), R-007 (`AC-R007-01–03`). |
| C-07 **Project entry or decision** | Add minimum DI-03 context or let Jude advance with a credible next move, pause, or consciously release; optional DI-05 support is eligible only when relevant to that decision. | Add or revise title; optionally add or revise relevant DI-05 support; choose outcome; state next move if advancing; review; complete, cancel, or retry. | From C-06 or R-04. Returns to exact origin; cancellation/no effect leaves prior context and any need for decision visible. | J-01, J-05, J-06, J-07; R-001 (`AC-R001-01–03`), R-005 (`AC-R005-01–03`), R-006 (`AC-R006-01–03`), R-007 (`AC-R007-01–03`). |
| S-01 **Settings & data** | Find optional attention controls and user-controlled portability, recovery, and full deletion without coercive promotion, and re-enter the owning status view after interruption of a destination-authorized or in-progress export or a confirmed or in-progress restore or deletion. No planning-content editor appears here. | Open notifications, export/backup, restore, or full deletion; review an applicable interrupted operation's status without restarting it; return to origin. | Same labeled global action from T-01, R-01, and C-01. Opens S-02 through S-05. When an interrupted consequence operation applies, its visible review action opens the owning S-03, S-04, or S-05 status view. Otherwise returns to the primary origin. | J-08, J-09, J-10, J-11; R-008 (`AC-R008-01–03`), R-009 (`AC-R009-01–03`), R-010 (`AC-R010-01–03`), R-011 (`AC-R011-01–03`). |
| S-02 **Notifications** | Identify and control every offered notification category, including complete opt-out. No notification behavior is required by this IA. | Review effective state; control category, timing, quiet hours, and frequency limit; disable a category or all; complete or cancel a change. | From S-01 and, if offered, a notification's settings action. Returns to its origin; failed change preserves and shows prior effective controls. | J-08; R-008 (`AC-R008-01–03`). |
| S-03 **Export or backup** | Explicitly direct an eligible DI-06 copy to Jude's chosen destination and review its status after interruption; when the outcome is not yet established, keep that chosen destination visible without repeating or assuming external movement. | Initiate; during destination selection review eligible scope and the external-copy consequence; deliberately complete destination choice to authorize exactly one attempt; leave, go Back, cancel, deny access, or be interrupted before completing the choice without starting an attempt; observe progress/result; after interruption review established or not-yet-established status and possible terminal outcomes; start a new attempt only after established no effect through fresh initiation and destination choice. | From S-01 for a new attempt. Before completed destination choice, leaving, Back, cancellation, denied access, or interruption returns safely with no attempt and no copy. After destination choice completes, interruption or app re-entry returns here directly or through S-01 **Review export status** without restarting. Completion, did-not-take-effect, or outcome-not-yet-established status remains visible before explicit return to S-01. | J-09; R-009 (`AC-R009-01–03`). |
| S-04 **Restore** | Explicitly restore a user-chosen backup, with replacement conflict, result, and post-interruption status made visible without repeating or assuming replacement. | Initiate; choose backup; review eligibility and possible replacement; explicitly proceed or confirm replacement; cancel; observe progress/result; after interruption review established or not-yet-established status and possible terminal outcomes; retry deliberately after no effect. | From S-01 for a new attempt. After interruption during confirmed/in-progress restore, app re-entry or S-01 **Review restore status** returns here without restarting. Cancellation/no confirmation returns to S-01 unchanged. Completion remains visible and offers an explicit route to T-01. | J-10; R-010 (`AC-R010-01–03`). |
| S-05 **Delete all app data** | Remove all app-managed personal data only after separate initiation, consequence disclosure, and destructive confirmation; clarify that external copies remain and expose post-interruption status without repeating or assuming deletion. | Initiate; review consequence; explicitly confirm or cancel; observe progress/result; after interruption review established or not-yet-established status and possible terminal outcomes; initiate a newly confirmed attempt only after no effect. | From S-01 for a new attempt. After interruption during confirmed/in-progress deletion, app re-entry or S-01 **Review deletion status** returns here without restarting. Cancellation/no confirmation returns to S-01 unchanged. Completion remains visible and offers an explicit route to the now-empty T-01. | J-11; R-011 (`AC-R011-01–03`). |

## Journey routes and recovery

| Journey | Unambiguous route | Completion exit | Cancellation, interruption, or recovery |
| --- | --- | --- | --- |
| J-01 | Daily beginning: T-01 → T-02 → C-03 → T-02. Daily ending: T-01 or R-02 → T-03, with short DI-04 recorded or revised in T-03 and DI-01/optional relevant DI-05 entered through T-03 → C-03 → T-03. Weekly attention: R-01 → R-02, with short DI-04 recorded or revised in R-02 and DI-01/optional relevant DI-05 entered through R-02 → C-03 → R-02. Promise/waiting: C-01 → C-04 → C-05 → C-04, or R-03 → C-05 → R-03. Project: C-01 → C-06 → C-07 → C-06, or R-04 → C-07 → R-04. Direct Context commitment entry is C-01 → C-02 → C-03 → C-02. R-03 and R-04 record or revise their applicable short DI-04 review decisions; R-05 presents them and returns revisions to the owning stage. | Current Jude-chosen DI-01 through DI-05 context appears at the originating daily or weekly decision. DI-05 is optional in C-03, C-05, or C-07 only when relevant to that origin. | Incomplete new entry is not current; cancelled revision/no effect preserves prior context; retry or safe exit returns to the exact origin. A cancelled or unfinished DI-04 decision remains prior or unresolved as required by J-03 and J-06. |
| J-02 | T-01 → T-02 → T-01 | T-01 identifies the deliberate daily intention. | Leaving/cancelling creates no new intention; no effect is stated; any earlier unresolved intention remains identifiable. |
| J-03 | T-01 or R-02 → T-03 → same origin | Origin distinguishes resolved, reconsidered, and still-unresolved intentions. | Skipped/cancelled/no-effect items remain unresolved; Today or Reflect exposes continuation. |
| J-04 | C-01 → C-04 → C-05 → C-04, or R-03 → C-05 → R-03 | Owner and next follow-up appear together at the origin. | New item is not created on cancellation; prior context survives cancelled/no-effect revision; no external action occurs. |
| J-05 | C-01 → C-06 → C-07 → C-06, or R-04 → C-07 → R-04 | Next move, pause, or conscious release appears at the origin. | Cancellation/no effect preserves prior context and the visible need for a decision; no disposition is inferred. |
| J-06 | R-01 → R-02 → R-03 → R-04 → R-05 → R-01 | R-05 shows every applicable result, then R-01 identifies completion. | Exit returns to R-01 with continuation; completed decisions remain visible and unfinished decisions remain unresolved. Empty categories do not create detours. |
| J-07 | T-01, R-01, or C-01 → the same J-01 through J-06 route used online | Same destination and decision outcome as the source journey. | No connectivity gate or offline-only destination exists; local retry or safe exit is offered after no effect. Later connectivity triggers nothing. |
| J-08 | S-01 → S-02 → S-01; or offered notification → existing applicable destination or S-02 | Effective controls are identifiable; opted-out scope ceases while core routes remain available. | Cancellation/no effect preserves prior controls. Dismissal ends only that presentation. Permission denial leaves S-02 and all core routes available. |
| J-09 | New attempt: S-01 → S-03 initiation → destination selection with eligible scope and external-copy consequence visible → deliberately completed destination choice authorizing exactly one attempt → progress/result. Re-entry after interruption once destination choice completed or export was in progress: app re-entry → S-03 status, or S-01 → **Review export status** → S-03 status; neither route restarts export. | Completed identifies Jude's chosen destination, then returns to S-01 by explicit action. **Did not take effect** claims no copy. | Before completed destination choice, leaving, Back, cancellation, denial, or interruption starts no attempt and creates no copy. After completed destination choice, S-03 shows in progress, completed, did not take effect, or outcome not yet established. For outcome not yet established, it identifies Jude's chosen destination and names completed/no-effect as possible terminal outcomes. Unknown status asserts neither that a copy exists nor that none exists; no repeat occurs. A new attempt is available only after established no effect and requires fresh initiation and destination choice. |
| J-10 | New attempt: S-01 → S-04 initiation/selection → replacement consequence → explicit confirmation → progress/result. Re-entry after interruption during confirmed/in-progress restore: app re-entry → S-04 status, or S-01 → **Review restore status** → S-04 status; neither route restarts restore. | Completed remains visible; Jude may explicitly continue to T-01. **Did not take effect** leaves existing information unreplaced. | Before confirmation, cancellation, dismissal, denial, or unreadable selection leaves existing information unreplaced. After confirmation, S-04 shows in progress, completed, did not take effect, or outcome not yet established and names completed/no-effect as possible terminal outcomes. Unknown status assumes neither replacement nor no effect; retry is deliberate only after no effect and requires the original consequence review and confirmation. |
| J-11 | New attempt: S-01 → S-05 initiation → consequence disclosure → distinct confirmation → progress/result. Re-entry after interruption during confirmed/in-progress deletion: app re-entry → S-05 status, or S-01 → **Review deletion status** → S-05 status; neither route restarts deletion. | Completed remains visible; Jude may explicitly continue to empty T-01. **Did not take effect** does not claim deletion. | Before confirmation, cancellation/lack of confirmation leaves data available. After confirmation, S-05 shows in progress, completed, did not take effect, or outcome not yet established and names completed/no-effect as possible terminal outcomes. Unknown status assumes neither deletion nor no effect. A no-effect attempt stops; every retry requires new initiation, consequence disclosure, and confirmation. |

## Route-level state entry and system status

This section identifies where a state enters navigation; WO-006 owns exhaustive visible-state specifications.

| Operating context | Navigation obligation |
| --- | --- |
| First use or empty use | Open T-01 with direct access to T-02 and primary navigation; do not force setup, context creation, notification consent, an account, or a connection. R-01 can complete with truly empty categories, and C-01 exposes its empty groups without treating absence as error. |
| Returning use | With no interrupted destination-authorized/in-progress export or confirmed/in-progress restore or deletion, T-01 identifies the current intention and any unfinished close; R-01 identifies an unfinished weekly reflection; C-02, C-04, and C-06 expose established supporting context. Consequence-operation re-entry follows the owning S-03, S-04, or S-05 route below. |
| Preparing/loading | Keep Jude in the owning destination and distinguish preparation from a true empty result. Do not route to onboarding, sign-in, Calendar/Keep, or a remote-retry destination. |
| Offline | Keep T-01 through C-07 available through their normal routes. Offline is supported context, not an error destination. A particular Jude-chosen export/backup location may be unavailable without blocking the core loop. |
| Error or no effect | Remain in or return to the owning destination, state that completion did not occur, preserve the last established information, and offer a deliberate retry or safe exit. |
| Permission denied | Notification denial is explained in S-02; chosen-location denial is explained in S-03 or S-04. Neither redirects to a permission loop or blocks Today, Reflect, or Context. |
| Stale or conflict | There is no remote, shared, or multi-user stale state. The only release-one replacement conflict is contained in S-04 and requires consequence disclosure plus explicit confirmation; no merge route is implied. |
| Incomplete or interrupted | T-01 or R-01 owns the visible continuation route for daily or weekly work. Completed decisions remain visible, unfinished items remain unresolved, and re-entry starts at the first unresolved applicable decision rather than a hidden draft destination. Before export destination choice completes, leaving, Back, cancellation, denial, or interruption starts no attempt and creates no copy. After destination choice completes, an interrupted export re-enters S-03; interrupted confirmed/in-progress restore or deletion re-enters S-04 or S-05. S-01 exposes the same visible review routes. Each owning view shows in progress, completed, did not take effect, or outcome not yet established and never silently restarts or assumes the consequence. For an export outcome not yet established, S-03 also keeps Jude's chosen destination visible. |
| Destructive confirmation | S-04 owns replacement confirmation and S-05 owns full-deletion confirmation. Both preserve a visible safe exit; dismissal and Back are not confirmation. S-03 has no additional mandatory in-app confirmation: eligible scope and external-copy consequence are visible during destination selection, and deliberately completing destination choice authorizes exactly one attempt. |
| AI or inferred uncertainty | No AI destination, recommendation, confidence, or generated conclusion exists. Missing owner, follow-up, close, attention, next move, or disposition remains visibly **needs a decision** instead of being inferred. |

Every operation with a consequence exposes its current system status—ready for Jude's decision, in progress, completed, did not take effect, or outcome not yet established—within its owning flow. An outcome-not-yet-established presentation names the possible completed/no-effect terminal outcomes and makes no consequence claim; for export, it also identifies Jude's chosen destination. Status must not depend only on color, motion, a timed presentation, or a notification. Exact components and language remain deferred.

## Notification navigation contract

- Release one is not required to offer a notification. If any are offered, every category is routine and non-urgent.
- S-02 is the single discoverable control destination for category, timing, quiet hours, frequency limits, category opt-out, and complete opt-out. Exact categories, defaults, trigger rules, and wording belong to WO-007.
- A notification due during quiet hours does not interrupt Jude. Any later presentation, if offered, must remain within Jude's completed frequency control and must not duplicate or escalate pressure.
- Opening an offered notification routes only to an existing applicable start or continuation destination. It does not create a hidden notification inbox or a second route to the same planning information.
- Ignoring or dismissing a notification ends that presentation only. It never resolves, reconsiders, disposes, exports, restores, deletes, sends, shares, or changes planning information.
- Opt-out and platform permission denial leave Today, Reflect, Context, and every core-loop action available. The product does not pressure Jude to re-enable notifications.

## Exact journey and requirement traceability

| Journey | Owning destination/action | Exact Product trace |
| --- | --- | --- |
| J-01 | T-01 → T-02 → C-03 for beginning context; T-01/R-02 → T-03 for short DI-04 close context and T-03 → C-03 for DI-01/optional DI-05 support; R-02 through R-04 record/revise short DI-04 review decisions and R-05 presents them; C-01 → C-02 → C-03, C-01 → C-04 → C-05, and C-01 → C-06 → C-07 for direct Context entry; R-03 → C-05 and R-04 → C-07 for nested reflection context. C-03, C-05, and C-07 each admit optional DI-05 only when relevant and return to the exact origin. | R-001; `AC-R001-01`, `AC-R001-02`, `AC-R001-03` |
| J-02 | T-01 **Form intention** → T-02 choose/review/complete | R-002; `AC-R002-01`, `AC-R002-02` |
| J-03 | T-01 or R-02 **Close** → T-03 resolve/reconsider/review | R-003; `AC-R003-01`, `AC-R003-02`, `AC-R003-03` |
| J-04 | C-04 or R-03 → C-05 choose owner and next follow-up | R-004; `AC-R004-01`, `AC-R004-02`, `AC-R004-03` |
| J-05 | C-06 or R-04 → C-07 advance, pause, or consciously release | R-005; `AC-R005-01`, `AC-R005-02`, `AC-R005-03` |
| J-06 | R-01 → R-02 attention → R-03 promises/waiting → R-04 projects → R-05 summary | R-006; `AC-R006-01`, `AC-R006-02`, `AC-R006-03` |
| J-07 | Normal T-01 through C-07 routes remain available offline; no connectivity route or external action | R-007; `AC-R007-01`, `AC-R007-02`, `AC-R007-03` |
| J-08 | S-01 → S-02 control, dismiss, category opt-out, or complete opt-out | R-008; `AC-R008-01`, `AC-R008-02`, `AC-R008-03` |
| J-09 | S-01 → S-03 initiate; during destination selection show eligible scope and external-copy consequence; deliberately completed destination choice authorizes exactly one attempt; observe result; after post-choice/in-progress interruption, app re-entry or S-01 review returns to S-03 status, identifying Jude's chosen destination when the outcome is not yet established, without repeat or assumed outcome | R-009; `AC-R009-01`, `AC-R009-02`, `AC-R009-03` |
| J-10 | S-01 → S-04 initiate, select, disclose replacement, confirm, observe result; after confirmed/in-progress interruption, app re-entry or S-01 review returns to S-04 status without repeat or assumed replacement | R-010; `AC-R010-01`, `AC-R010-02`, `AC-R010-03` |
| J-11 | S-01 → S-05 initiate, disclose consequence, separately confirm, observe result; after confirmed/in-progress interruption, app re-entry or S-01 review returns to S-05 status without repeat or assumed deletion | R-011; `AC-R011-01`, `AC-R011-02`, `AC-R011-03` |

All J-01 through J-11 and all R-001 through R-011 have an entry, completion exit, cancellation/no-effect route, and recovery route. No accepted journey depends on an unlisted destination, notification, network, account, Calendar, or Keep.

## Navigation accessibility constraints

WO-008 owns the detailed accessibility specification. This IA requires that it preserve the following route structure:

- Every destination and action has a meaningful visible and programmatic name; global Settings & data and destructive actions are not icon-only.
- All routes work with Android system Back and without a swipe-only, drag-only, motion-only, color-only, or timed interaction.
- Focus order follows the information hierarchy and returns to the originating control after a nested cancellation or no-effect outcome.
- Scalable text, meaningful labels, adequate target size and contrast, non-color status cues, and reduced-motion behavior must not remove, obscure, or reorder a decision or consequence.
- Resolved, reconsidered, unresolved, needs-decision, in-progress, completed, and no-effect meanings remain distinguishable without color alone.

## Usability hypotheses and later validation

| Hypothesis | Synthetic task evidence to seek |
| --- | --- |
| IA-UH-01 — Today is a reliable starting point without hiding weekly work. | Jude can start an intention, resume an incomplete close, and find Reflect from a normal launch without prompting. |
| IA-UH-02 — One Context area keeps supporting information findable without feeling like separate suites. | Jude can find and revise a synthetic promise/waiting item and project, then return to the originating weekly stage. |
| IA-UH-03 — Weekly stage order makes all three ranked jobs understandable while allowing empty categories. | Jude completes mixed and all-empty synthetic reflections and can explain each applicable result. |
| IA-UH-04 — Settings & data is discoverable without coercive promotion. | Jude can find full notification opt-out, export/backup, restore, and deletion from each primary destination without encountering an unsolicited prompt. |
| IA-UH-05 — Interruption recovery preserves orientation and consequence awareness. | Jude leaves and resumes synthetic daily/weekly work, cancels entered changes, and predicts which decisions remain current. |
| IA-UH-06 — Portability and destructive routes remain distinct. | During destination selection for synthetic export, Jude correctly identifies the eligible scope and external-copy consequence and understands that deliberately completing the destination choice authorizes exactly one attempt without another mandatory in-app confirmation. Before confirming synthetic restore and deletion tasks, Jude correctly identifies what may be replaced, what is removed, and what external copies remain. |

Later task-based validation observes findability, orientation, consequence comprehension, and maintenance burden qualitatively. It adds no telemetry, remote analytics, numerical threshold, work data, prohibited category, or real personal content.

## Exclusions and owner boundaries

This structure contains no work content or behavior; direct Calendar/Keep read, import, copy, monitoring, or write; specialized personal-domain module; detailed archive; AI; backend; remote synchronization; analytics; telemetry; external communication; paid dependency; multiple users; or broader-distribution concept. DI-07 is not collected, DI-08 through DI-13 remain excluded or prohibited, and no route silently sends, shares, uploads, restores, replaces, or deletes.

| Deferred artifact or owner | Deferred decision | Binding IA constraint |
| --- | --- | --- |
| WO-006 — detailed state matrix | The existing `design/state-matrix.md` draft requires downstream remediation against revision 0.3 before verification; it then owns exhaustive happy, empty, preparing/loading, offline, stale, error, permission-denied, conflict, confirmation, progress, completion, and no-effect presentations. | Implement the owning destinations and route outcomes above without false empty, false completion, dead ends, or silent consequence. |
| WO-007 — content and notification behavior | Exact labels, explanations, confirmations, notification categories, triggers, defaults, timing language, quiet behavior, frequency language, and result wording | Preserve deliberate choice, routine/non-urgent treatment, complete opt-out, visible status, non-coercion, and consequence clarity. |
| WO-008 — accessibility | Detailed Android semantics, text scaling, focus, target, contrast, non-color, and reduced-motion behavior | Every named destination, status, decision, safe exit, and consequence remains perceivable and operable. |
| Architecture | Persistence, storage, offline, notification, export, backup, restore, deletion, format, protection, destination, interface, and platform mechanisms | Satisfy the routes without account/backend/AI/remote sync/paid dependency, direct Calendar/Keep access, or a new data category; do not infer a storage model from the conceptual relationships. |
| Quality | Verification design and evidence | Observe every entry, completion, cancellation, interruption, no-effect, permission, offline, opt-out, and destructive-confirmation route named here. |

No scope conflict or change request was identified. This revision claims no Quality verification, Gate 2 approval, architecture readiness, security verdict, implementation readiness, production promotion, launch approval, or broader-distribution authorization.