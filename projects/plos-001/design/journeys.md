# Release-One User Journeys: Personal Life OS

**Revision:** 0.2  
**Status:** Owner draft  
**Owner:** Experience Lead — WO-004-R1  
**Last updated:** 2026-08-06  
**Verification and approval:** Quality verification and Gate 2 approval remain pending.

## Frozen basis

| Input | Frozen version/status | SHA-256 |
| --- | --- | --- |
| `work/gate-decisions/GATE-1-principal.md` | v1.0; `ACCEPT` on 2026-08-06 | `8ade3617bb88123d1aededb0854718964b1b2e394ebfe23697f474178830f65b` |
| `product/project-brief.md` | v0.1 | `68097f79e003db0f4fa8d5b0ed547ae7a4d3a19fcf63d64b9677015698dbb76b` |
| `product/acceptance-map.md` | v0.1 | `8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3` |

This document translates the accepted Gate 1 intent into journey-level behavior. It does not select screens, navigation, components, copy, gestures, storage, interfaces, file formats, services, or test mechanisms. All examples are synthetic.

## Journey boundaries and conventions

### Accepted behavior

- Jude is the sole release-one user. Every journey is personal-only and separate from work systems and work data.
- The supported context is limited to DI-01 through DI-05. DI-06 exists only as a Jude-initiated export or backup copy. DI-07 is not collected. DI-08 through DI-13 are excluded or prohibited.
- Recording or reviewing a promise/waiting item never sends a message, changes a calendar, shares content, or causes another service-visible action.
- The core loop—minimal context, daily intention, daily close, and weekly reflection—works without a network, account, backend, synchronization service, AI provider, Calendar connection, or Keep connection.
- No AI behavior exists in release one. The product does not infer what matters, who owns a next move, whether a project move is credible, or what Jude should decide. User judgment and unresolved uncertainty remain visible rather than being replaced by a system conclusion.
- Time passage, omission, a dismissed notification, a failed action, or leaving a journey never resolves an intention, disposes a project, replaces information, or deletes information by itself.
- Export/backup is the only accepted user-visible movement of app-managed personal data off the device. Jude explicitly initiates it and deliberately completes destination choice after being shown the eligible scope and external-copy consequence; completed destination choice authorizes one attempt without an additional mandatory in-app confirmation. Restore replacement and full deletion require a separate explicit destructive confirmation.

### Journey-level status and recovery

These are behavioral obligations, not a detailed state matrix:

- **Empty:** Absence of optional context is stated as absence, not treated as an error or filled with inferred content. The core loop never requires a specialized record or prohibited category.
- **Preparing/loading:** Context that has not yet been established as available is not shown as an empty result. The product distinguishes preparation from an actual empty state.
- **Offline:** A lack of network or external account never blocks a core-loop action. Offline is not presented as a reason to sign in, connect Calendar or Keep, or wait for a remote service.
- **Error/no effect:** The product does not claim completion when an action did not take effect. It states that outcome, preserves the last established information, and offers retry or a safe exit where relevant.
- **Permission denied:** Core-loop journeys request no external-account or Calendar/Keep permission. If notification permission or access to a user-chosen export/backup location is unavailable, the affected optional action does not take effect and the core loop remains usable.
- **Stale/conflict:** Release one has no shared, remote, or synchronized record and therefore no accepted remote-stale or multi-user conflict journey. Potential replacement of existing information during restore is the relevant conflict and is resolved only by consequence disclosure and explicit confirmation; no merge behavior is implied.
- **Destructive confirmation for restore and full deletion:** Consequence disclosure precedes confirmation. Cancellation, dismissal, or lack of confirmation is not confirmation and leaves existing app-managed information unchanged.
- **Accessibility handoff:** Every decision and status named here must remain understandable with scalable text, meaningful labels, adequate target size and contrast, logical focus, non-color cues, and reduced motion. Exact specifications belong to the later accessibility artifact; no journey may rely only on color, motion, or a timed response.

## Journey inventory

| Journey | Purpose | Primary trace ownership |
| --- | --- | --- |
| J-01 | Record or revise minimal personal context | R-001 |
| J-02 | Form a daily intention | R-002 |
| J-03 | Deliberately close the day | R-003 |
| J-04 | Review a personal promise or waiting item | R-004 |
| J-05 | Decide a personal project's next move or disposition | R-005 |
| J-06 | Complete the weekly reflection across all three ranked jobs | R-006 |
| J-07 | Complete the core loop offline with Calendar and Keep separate | R-007 |
| J-08 | Control or completely opt out of offered notifications | R-008 |
| J-09 | Create a user-initiated export or backup | R-009 |
| J-10 | Restore a user-chosen backup | R-010 |
| J-11 | Fully delete app-managed personal data | R-011 |

## J-01 — Record or revise minimal personal context

**Trigger:** Jude encounters personal context relevant to a near-term daily or weekly decision, or chooses to revise context already recorded.  
**Preconditions:** None beyond personal use. Network access, an account, Calendar, Keep, a backend, synchronization, and AI are not preconditions.  
**User goal:** Keep only enough personal context to make the associated decision without building a detailed archive.  
**Entry context:** The action may begin while preparing a daily intention, closing the day, reviewing a promise/waiting item, deciding a project, or reflecting weekly.

**Ordered interaction**

1. Jude identifies the context he considers relevant to the near-term decision.
2. The product limits supported entry to a personal intention or commitment and relevant date; promise/waiting owner and next follow-up; personal-project title and next move or disposition; or a short reflection/review decision. A routine reference, important date, family plan, or generic care reminder may be included only when Jude chooses it as relevant minimal context.
3. The product does not request work information, Calendar/Keep content, a detailed journal or dossier, detailed health information, financial or location data, credentials, archives, AI context, or any other DI-08 through DI-13 category.
4. Jude records new context or reviews and revises existing context. The product presents the resulting current context without adding an inference.
5. Jude completes the action. The current Jude-chosen context becomes available for the associated daily or weekly decision.

**Decision points:** Jude decides whether any context is necessary, which supported minimum is relevant, whether optional DI-05 context helps, and whether to keep or revise what he entered. Optional context is never a completion requirement.

**Completion outcome:** Jude can identify the current context that will inform the associated decision.  
**Cancellation and recovery:** Leaving a new entry incomplete does not make it current. Cancelling a revision or receiving a no-effect outcome leaves the previously established context unchanged. Jude may retry without connecting an account or network.  
**Relevant states:** With no context, the product states that none is recorded and permits the applicable loop to continue or Jude to add minimal context. If established context cannot be presented, that condition is not represented as an empty result.  
**Consequence boundary:** No external read, write, message, share, calendar change, synchronization, analytics, telemetry, or AI processing occurs.  
**Trace:** R-001; AC-R001-01, AC-R001-02, AC-R001-03. Cross-cutting offline behavior is owned by J-07.

## J-02 — Form a daily intention

**Trigger:** Jude is beginning a day and wants to decide what deserves attention.  
**Preconditions:** No prior record, connection, or account is required.  
**User goal:** Make a deliberate choice about one or more personal commitments for the day.  
**Entry context:** Jude begins the daily loop directly or from current minimal personal context.

**Ordered interaction**

1. The product presents any current Jude-chosen commitments relevant to the daily decision. If none exist, it states that and allows Jude to supply only the minimal context needed through J-01.
2. Jude chooses one or more personal commitments for attention. The product does not rank, recommend, or infer the choice.
3. The product reflects the chosen commitment or commitments back as Jude's proposed daily intention.
4. Jude completes the choice. The product identifies the intention as the current deliberate choice for the day.

**Decision points:** Jude decides what, if anything, deserves attention and may leave before forming an intention. No product score, streak, urgency, or external schedule decides for him.

**Completion outcome:** Jude can tell exactly which commitment or commitments he intentionally chose.  
**Cancellation and recovery:** If Jude leaves before completing the choice, no new intention is claimed. Any earlier unresolved intention remains identifiable. If formation does not take effect, the product reports no effect and permits retry.  
**Relevant states:** Empty context does not block formation. Preparing existing context is distinct from no context. Offline formation follows J-07.  
**Consequence boundary:** The product neither reads from nor writes to Calendar or Keep and forms no external commitment.  
**Trace:** R-002; AC-R002-01, AC-R002-02.

## J-03 — Deliberately close the day

**Trigger:** Jude is ending or reviewing a day for which a daily intention exists.  
**Preconditions:** At least one current or unresolved daily intention is identifiable.  
**User goal:** Understand what happened and deliberately resolve or reconsider each intention instead of letting it disappear.  
**Entry context:** Jude begins the close from the daily loop or encounters an unresolved intention during weekly reflection.

**Ordered interaction**

1. The product presents each applicable intention and its current unresolved status.
2. For an intention Jude considers, he records only enough short reflection to tell what happened.
3. Jude deliberately chooses **resolved** or **reconsidered** for that intention. Reconsidered remains visibly distinct from resolved and remains accounted for as context requiring a later decision or attention.
4. The product presents a close summary that distinguishes resolved, reconsidered, and any still-unresolved intentions.
5. The close is represented as complete only for intentions with an explicit close decision. Any item Jude skipped or left incomplete remains identifiable as unresolved.

**Decision points:** Jude decides the outcome of each intention. The product does not resolve, roll over, or discard one based on time, omission, or inferred progress.

**Completion outcome:** Jude can tell what happened and which intentions were resolved or reconsidered.  
**Cancellation and recovery:** Leaving before a decision, cancelling, or encountering a no-effect outcome preserves the intention as unresolved. Completed decisions remain distinguishable from unfinished ones; an unfinished overall close is not represented as complete.  
**Relevant states:** If no intention exists, the product states that there is nothing to close and does not fabricate a completed close. If intended context is unavailable, it is not represented as an empty day. Offline close follows J-07.  
**Consequence boundary:** No notification, elapsed-time rule, AI inference, or external system closes an intention.  
**Trace:** R-003; AC-R003-01, AC-R003-02, AC-R003-03.

## J-04 — Review a personal promise or waiting item

**Trigger:** Jude records, changes, or reviews an open personal promise or an item awaiting someone else's move, including during weekly reflection.  
**Preconditions:** For review, an open item exists; for first entry, Jude has minimal personal context to record.  
**User goal:** Know unambiguously who owns the next move and when he intends to revisit the item.  
**Entry context:** The journey begins from minimal context entry or the promise/waiting portion of weekly reflection.

**Ordered interaction**

1. The product presents the minimal item context without contacting anyone.
2. Jude identifies ownership as either his own next move or another person's next move. If another person owns it, Jude supplies only the minimal owner/recipient context he needs.
3. Jude identifies the next point at which he intends to revisit the item.
4. The product presents the item with both owner and next follow-up visible together.
5. Jude completes the review or revision. An item missing either decision remains visibly in need of a decision rather than appearing complete.

**Decision points:** Jude determines ownership and the revisit point. A follow-up date is planning context; it does not itself send, schedule, share, or notify.

**Completion outcome:** Jude can tell both who owns the next move and when he intends to revisit it.  
**Cancellation and recovery:** Cancelling a new item does not create it. Cancelling a revision or receiving a no-effect outcome preserves the prior owner/follow-up context.  
**Relevant states:** With no open items, the product states that none are available and does not require Jude to create one. An inability to present existing items is not shown as an empty result.  
**Consequence boundary:** Recording, changing, or reviewing the item produces no message, calendar change, share, or other service-visible action.  
**Trace:** R-004; AC-R004-01, AC-R004-02, AC-R004-03.

## J-05 — Decide a personal project's next move or disposition

**Trigger:** During reflection, Jude judges that a relevant personal project lacks a credible next move or intended attention.  
**Preconditions:** Only a minimal personal-project title or equivalent Jude-chosen context is required.  
**User goal:** Advance, pause, or consciously release the project rather than silently neglect it.  
**Entry context:** The journey begins from project context or the project portion of weekly reflection.

**Ordered interaction**

1. The product presents relevant minimal project context without assigning a drift score, elapsed-time threshold, priority rank, state, or work-in-progress limit.
2. Jude decides whether this project needs attention.
3. Jude chooses one deliberate outcome: advance it with a next move, pause it, or consciously release it.
4. If advancing, Jude states the next move he judges concrete enough to understand how he intends to proceed. The product does not score or certify credibility.
5. The product presents the resulting next move, pause decision, or conscious release decision for Jude to review and complete.

**Decision points:** Relevance, need for attention, credibility, and disposition are all Jude's judgments. A conscious release is a recorded disposition, not full deletion of app-managed personal data.

**Completion outcome:** Jude can tell the resulting next move or explicit disposition.  
**Cancellation and recovery:** If Jude cancels or a change does not take effect, the prior context remains and the project remains identifiable as needing a decision where applicable. No disposition is inferred.  
**Relevant states:** If no relevant project exists, the product states that there is no applicable project decision and does not require a project archive. Offline use follows J-07.  
**Consequence boundary:** The product does not impose a project state model, numerical drift rule, score, or automatic release.  
**Trace:** R-005; AC-R005-01, AC-R005-02, AC-R005-03.

## J-06 — Complete the weekly reflection across all three ranked jobs

**Trigger:** Jude begins a weekly reflection.  
**Preconditions:** None. When available, unresolved daily intentions, open promise/waiting items, and relevant personal projects provide the minimal context.  
**User goal:** Leave with deliberate changes in attention, clear owner/follow-up decisions, and project next moves or dispositions for each applicable category.  
**Entry context:** Jude intentionally begins reflection; no notification, calendar event, or elapsed-time rule completes it automatically.

**Ordered interaction**

1. The product establishes the minimal current context across the three ranked jobs. A category with no context is stated as empty; unavailable context is not presented as empty.
2. **Attention:** Jude considers unresolved daily intentions and other minimal commitments, using J-03 where a close decision is needed, and identifies what deserves changed or continued attention.
3. **Promises/waiting:** Jude considers each open item he chooses to review and uses J-04 to establish owner and next follow-up.
4. **Projects:** Jude identifies which relevant projects need attention by his own judgment and uses J-05 to give each reviewed project a credible next move, pause, or conscious release.
5. The product presents a reflection summary showing, for every applicable category, what attention changed, which follow-up is next and who owns the move, and which reviewed project received a next move or disposition.
6. Jude completes the reflection after reviewing that summary. Items left without a required decision remain identifiable and the reflection is not represented as having resolved them.

**Decision points:** Jude decides which minimal context is relevant, what attention changes, which items to review, who owns a move, when to revisit, which projects need attention, and whether to advance, pause, or release them. The product does not require every category to contain an item.

**Completion outcome:** Jude can tell the resulting decision for every applicable category and can complete the reflection without a specialized domain record or detailed archive.  
**Cancellation and recovery:** Leaving early does not fabricate completion. Deliberate decisions already completed remain visible; unfinished items retain their prior or unresolved state. If a category cannot be presented, Jude can retry or leave the reflection incomplete rather than accepting a false empty result.  
**Relevant states:** With all categories empty, the product states that no recorded context needs a decision and permits completion without requiring new records. The reflection operates offline through J-07.  
**Consequence boundary:** Calendar and Keep remain separate. No communication, external action, AI recommendation, score, threshold, or specialized workflow is introduced.  
**Trace:** R-006; AC-R006-01, AC-R006-02, AC-R006-03.

## J-07 — Complete the core loop offline with Calendar and Keep separate

**Trigger:** Jude undertakes a core-loop action while the device has no network connection and no external account, backend, synchronization service, or AI provider is available.  
**Preconditions:** The Personal Life OS is available on Jude's device. No external connection is a precondition.  
**User goal:** Record or revise minimal context, form or close a daily intention, or complete weekly reflection with the same deliberate outcome while offline.  
**Entry context:** J-01, J-02, J-03, or J-06; promise/waiting and project decisions may occur as their supporting parts.

**Ordered interaction**

1. Jude begins the intended core-loop action.
2. The product makes clear that the action remains available offline and does not request sign-in, Calendar/Keep access, or a network-dependent alternative.
3. Jude supplies or reviews only context he chose to record in the Personal Life OS and completes the applicable decisions in J-01 through J-06.
4. The product makes the resulting current context or decision available to Jude and distinguishes completion from a no-effect outcome.
5. Later network availability causes no upload, synchronization, remote analytics, telemetry, AI processing, or other silent external action.

**Decision points:** Jude makes the same personal decisions as in the source journey. Connectivity does not change, rank, or complete them.

**Completion outcome:** The selected core-loop behavior completes and its result remains available without an external account or service.  
**Cancellation and recovery:** Normal cancellation behavior from the source journey applies. If an action does not take effect, the product does not blame an unavailable backend or require a connection; it states no effect and allows a local retry or safe exit.  
**Relevant states:** Offline is a supported operating context, not an error. Calendar/Keep separation is maintained even when a network later becomes available.  
**Consequence boundary:** No silent external action, backend, remote synchronization, remote analytics, telemetry, or AI processing occurs.  
**Trace:** R-007; AC-R007-01, AC-R007-02, AC-R007-03.

## J-08 — Control or completely opt out of offered notifications

**Applicability:** This journey applies only if release one offers one or more notification behaviors. It does not require that a notification be offered or decide exact defaults, categories, copy, or platform mechanism.  
**Trigger:** Jude reviews notification controls, changes them, receives an offered notification, or chooses to disable notifications.  
**Preconditions:** At least one release-one notification category is offered.  
**User goal:** Control the attention cost of every offered notification or opt out completely without losing the core loop.  
**Entry context:** Jude may enter from an offered notification or from its controls; no navigation structure is selected here.

**Ordered interaction**

1. The product identifies each offered category and its current effective status.
2. For every offered category, Jude can control whether it is enabled, its timing, quiet hours, and its frequency limit. Jude can also disable all offered notifications in one complete opt-out.
3. The product presents the proposed control state. Jude completes or cancels the change; only a completed change takes effect.
4. An offered notification is routine and non-urgent. It appears only within the completed controls. A notification due during quiet hours does not interrupt Jude; any later presentation, if any, remains within the selected frequency limit and is not duplicated or escalated.
5. Jude may act, ignore, or dismiss it. Ignoring or dismissing ends that presentation without changing planning data, creating a streak, applying shame, escalating pressure, or causing a punitive consequence.
6. When Jude opts out of a category or all notifications, the product shows the effective disabled scope and notifications in that scope cease. J-01 through J-07 remain completable.

**Decision points:** Jude controls category, timing, quiet hours, frequency limits, response, and complete opt-out. The product does not infer consent from use of the core loop.

**Completion outcome:** Jude can identify the effective controls; opted-out notifications cease while core behavior remains available.  
**Cancellation and recovery:** Cancelling a change preserves the prior effective controls. If a control change does not take effect, the product says so and continues to show the prior effective state.  
**Relevant states:** If platform notification permission is denied, the product states that notifications cannot arrive, treats them as unavailable, preserves full core-loop usability, and does not pressure Jude to re-enable them. Offline control causes no external communication.  
**Consequence boundary:** Notification interaction never resolves an intention, disposes a project, sends a message, deletes data, or creates an external action.  
**Trace:** R-008; AC-R008-01, AC-R008-02, AC-R008-03.

## J-09 — Create a user-initiated export or backup

**Trigger:** Jude wants a portable export or backup copy.  
**Preconditions:** Supported app-managed personal data may exist. No action begins automatically.  
**User goal:** Direct a copy containing only supported personal data to a destination he chooses and know whether it completed.  
**Entry context:** Jude deliberately enters the portability action; no schedule, notification, or background event initiates it.

**Ordered interaction**

1. Jude explicitly initiates export or backup.
2. As part of destination selection, the product makes visible that completing the choice will authorize one attempt to create a copy of supported DI-01 through DI-05 context outside app-managed data at the selected destination. It also makes visible that work and prohibited data are ineligible, the action is not synchronization, and it will not recur.
3. Jude either leaves, cancels, denies required destination access, or is interrupted before completing destination choice, in which case no attempt begins; or Jude deliberately completes destination choice with that scope and consequence context available. Completed destination choice authorizes the attempt without an additional mandatory in-app confirmation.
4. Once destination choice completes, the product may direct the eligible copy to that destination and shows **in progress** without claiming completion.
5. The product reports **completed** when it can establish that the copy was directed to the chosen destination, **did not take effect** when it can establish no copy was created, or **interrupted — outcome unknown** when it cannot establish either outcome. It identifies the chosen destination for completed and outcome-unknown results and never silently repeats the attempt.
6. A new attempt is available only after **did not take effect** is established. Jude starts that attempt through a new explicit initiation and completes destination choice again; the product never treats the earlier choice as standing authorization.

**Decision points:** Jude decides whether to begin and which destination to use. Completing destination choice after reviewing the visible scope and consequence authorizes one attempt. The product never chooses a remote destination or enables recurring transfer.

**Completion outcome:** A copy containing only supported personal data is directed to Jude's chosen destination, and Jude can tell it completed.  
**Cancellation and recovery:** Before destination choice completes, leaving, cancellation, denied destination access, or interruption creates no copy, moves no app-managed personal data off the device, and leaves app-managed information unchanged. After destination choice completes, interruption may leave the outcome unknown; the product states that uncertainty and the chosen destination without claiming completion or no effect, and it does not silently repeat. Only an established no-effect outcome makes a new attempt available, with fresh initiation and destination choice. Export never changes app-managed information.  
**Relevant states:** If no supported data is eligible, the product states that there is nothing to copy and creates none. If destination choice cannot complete because the destination is unavailable or access is denied, it reports that no attempt began. After destination choice completes, the observable attempt states are in progress, completed, did not take effect, and interrupted/outcome unknown. Availability of a particular destination offline is not assumed.  
**Consequence boundary:** The copy excludes DI-07 through DI-13, including work data, and creates neither automatic synchronization nor an app-chosen remote copy.  
**Trace:** R-009; AC-R009-01, AC-R009-02, AC-R009-03.

## J-10 — Restore a user-chosen backup

**Trigger:** Jude has selected a backup he chose and wants to restore it.  
**Preconditions:** A user-chosen backup is available to the product. Existing app-managed information may be present.  
**User goal:** Restore deliberately, understand any replacement consequence, and know whether the action completed.  
**Entry context:** Jude explicitly enters restoration; selection alone does not start replacement.

**Ordered interaction**

1. Jude explicitly initiates restoration of the selected backup.
2. The product establishes whether restoration can proceed and whether it could replace existing app-managed information. An unreadable, unavailable, or ineligible selection produces no replacement.
3. If replacement is possible, the product states plainly that existing app-managed information would be replaced and distinguishes the selected backup from the current information.
4. Jude explicitly confirms the replacement or cancels. Dismissal, navigation away, silence, or an unavailable confirmation is not consent.
5. Only after confirmation does restoration proceed. The product shows the action as in progress without representing replacement as complete.
6. The product reports **completed** only when restoration has taken effect; otherwise it reports **did not take effect** and does not claim replacement.

**Decision points:** Jude decides whether to initiate and whether to accept replacement after seeing the consequence. No merge, automatic restore, or silent conflict resolution is implied.

**Completion outcome:** Jude can tell that the chosen backup was restored. If existing information was replaced, that occurred only after explicit confirmation.  
**Cancellation and recovery:** Cancellation or lack of confirmation leaves existing app-managed information unchanged. An unavailable, unreadable, permission-denied, or no-effect attempt also leaves existing information unreplaced and permits a deliberate retry or different selection.  
**Relevant states:** With no existing information, Jude still explicitly proceeds, but no destructive replacement is claimed. The replacement conflict is never hidden behind a generic success. The action requires no account, backend, or automatic remote copy; access to a particular chosen location may be unavailable.  
**Consequence boundary:** Restore never silently replaces information and never initiates full deletion.  
**Trace:** R-010; AC-R010-01, AC-R010-02, AC-R010-03.

## J-11 — Fully delete app-managed personal data

**Trigger:** Jude wants all app-managed personal data deleted.  
**Preconditions:** None; deletion never starts from time passage, notification behavior, restore, ordinary use, or another product event.  
**User goal:** Deliberately remove all app-managed personal data and know when it is no longer available in the product.  
**Entry context:** Jude explicitly enters the full-deletion action; its consequence is kept distinct from deleting or changing one planning item.

**Ordered interaction**

1. Jude explicitly initiates full deletion.
2. The product explains that all app-managed personal data will no longer be available in the product. It also explains that export or backup copies previously created at Jude-chosen destinations are outside app-managed data and are not deleted by this action.
3. The product presents a distinct destructive confirmation after the consequence disclosure.
4. Jude explicitly confirms or cancels. Dismissal, leaving, silence, time passage, or any other event is not confirmation.
5. Only after confirmation does deletion proceed. The product shows an in-progress status and does not claim completion early.
6. The product reports completion only when app-managed personal data is no longer available in the product. If it cannot establish completion, it reports that deletion did not complete and does not silently continue later; any retry requires a new deliberate initiation and confirmation.

**Decision points:** Jude decides whether to initiate and, separately, whether to confirm after reading the consequence.

**Completion outcome:** App-managed personal data is no longer available in the product, and Jude can tell deletion completed.  
**Cancellation and recovery:** Cancelling or not confirming leaves app-managed personal data available and produces no destructive effect. A no-effect outcome is not retried automatically.  
**Relevant states:** If no app-managed personal data is available, the product states that condition rather than implying an additional deletion occurred. The action does not depend on a backend because release one manages no backend copy.  
**Consequence boundary:** Full deletion is never automatic or silent. Previously user-created copies remain under Jude's control at their chosen destinations.  
**Trace:** R-011; AC-R011-01, AC-R011-02, AC-R011-03.

## Acceptance ownership trace

Each accepted criterion has exactly one owning journey below. Cross-references elsewhere do not change ownership.

| Acceptance criterion | Owning journey | Journey-level observable behavior |
| --- | --- | --- |
| AC-R001-01 | J-01 | Current Jude-chosen context is available for its daily or weekly decision. |
| AC-R001-02 | J-01 | Only supported minimal categories are needed; no archive, specialized record, or prohibited category is required. |
| AC-R001-03 | J-01 | Optional routine/date/family/generic-care context may inform a decision without becoming required or specialized. |
| AC-R002-01 | J-02 | Jude chooses and can identify one or more daily commitments for attention. |
| AC-R002-02 | J-02 | The daily intention forms and remains identifiable without network, account, Calendar, or Keep. |
| AC-R003-01 | J-03 | Deliberate close shows what happened and resolved versus reconsidered. |
| AC-R003-02 | J-03 | Reconsideration is distinguishable and remains accounted for. |
| AC-R003-03 | J-03 | An intention without a close decision remains unresolved despite time, omission, or incomplete close. |
| AC-R004-01 | J-04 | Jude can tell whether he or another person owns the next move. |
| AC-R004-02 | J-04 | Owner and next follow-up are visible together on review. |
| AC-R004-03 | J-04 | Recording, changing, or reviewing owner/follow-up context creates no external action. |
| AC-R005-01 | J-05 | A relevant project receives a Jude-chosen next move, pause, or conscious release. |
| AC-R005-02 | J-05 | Jude states the next move he judges credible without a product score. |
| AC-R005-03 | J-05 | No fixed state, drift threshold, or work-in-progress rule decides for Jude. |
| AC-R006-01 | J-06 | Weekly reflection exposes applicable decisions across attention, promises/waiting, and projects. |
| AC-R006-02 | J-06 | The final summary makes each applicable attention, follow-up, and project result identifiable. |
| AC-R006-03 | J-06 | The reflection completes from minimal context without a specialized workflow or archive. |
| AC-R007-01 | J-07 | Every selected core behavior remains usable and its result available offline without external services or AI. |
| AC-R007-02 | J-07 | Calendar and Keep remain separate; no access, import, copy, monitoring, or write is required. |
| AC-R007-03 | J-07 | Offline completion produces no silent external action or remote dependency. |
| AC-R008-01 | J-08 | Every offered category exposes category, timing, quiet-hours, frequency-limit, and complete-opt-out control. |
| AC-R008-02 | J-08 | Opted-out notifications cease while the core loop remains completable. |
| AC-R008-03 | J-08 | Acting, ignoring, dismissing, changing, or disabling creates no coercive or punitive consequence. |
| AC-R009-01 | J-09 | Without Jude's initiation and completed destination choice, no copy is created or data moved. |
| AC-R009-02 | J-09 | Completed destination choice authorizes one attempt to direct a supported-data copy only to Jude's chosen destination, with observable completed, no-effect, or outcome-unknown status and no silent repeat. |
| AC-R009-03 | J-09 | Work and prohibited data are absent; no automatic sync or app-chosen remote copy is created. |
| AC-R010-01 | J-10 | Jude initiates restoration of his selected backup and sees completed/no-effect status without silent replacement. |
| AC-R010-02 | J-10 | Replacement consequence is disclosed and explicitly confirmed before replacement. |
| AC-R010-03 | J-10 | Cancellation or lack of confirmation leaves existing information unreplaced. |
| AC-R011-01 | J-11 | Initiation, consequence disclosure, and confirmation precede full deletion; completion is visible. |
| AC-R011-02 | J-11 | Cancellation or lack of confirmation leaves app-managed personal data available. |
| AC-R011-03 | J-11 | No ordinary event, time passage, notification, or restore can initiate or complete deletion automatically. |

## Experience assumptions and usability hypotheses

The following are hypotheses, not accepted Product behavior or numerical targets:

| Hypothesis | Journey evidence to seek later |
| --- | --- |
| UH-01 — Minimal context is sufficient without inviting a sensitive archive. | In a synthetic daily and weekly walkthrough, Jude can decide without asking for unsupported categories. |
| UH-02 — Resolved, reconsidered, and unresolved are distinguishable without adding maintenance burden. | Jude can explain the state of each synthetic daily intention after completing, cancelling, and partially leaving a close. |
| UH-03 — Owner plus next follow-up is enough to reduce memory dependence. | Jude can identify both for synthetic promise and waiting examples and does not expect an external message to be sent. |
| UH-04 — Jude can make project decisions without a score or fixed state model. | With synthetic project examples, Jude can advance, pause, or consciously release and explain the result. |
| UH-05 — The weekly sequence produces clarity across all three jobs without becoming a suite. | Jude reaches the summary and can state each applicable change, including an empty category. |
| UH-06 — Optional notifications can remain low-pressure. | Jude can configure quiet behavior, frequency limits, dismissal, category opt-out, and complete opt-out without expecting a penalty. |
| UH-07 — Export scope and consequence are understandable when choosing a destination, and restore and deletion consequences are understandable before confirmation. | Jude predicts correctly what stays on-device, what may leave, what destination choice authorizes, what replacement means, and what user-created copies full deletion does not remove. |
| UH-08 — Offline and no-account operation is trustworthy and baseline Android accessibility is sufficient. | Jude completes synthetic core tasks offline and can perceive status and decisions with relevant Android accessibility settings. |

Later Experience validation should use task-based walkthroughs with Jude and synthetic examples only: form and abandon a daily intention; resolve, reconsider, and leave an intention unresolved; review personal-promise and waiting examples; complete weekly reflection with mixed and empty categories; decide project advance/pause/release; dismiss and opt out of offered notifications; cancel export before destination choice and complete export by choosing a destination; cancel and confirm restore; and cancel and confirm full deletion. Observe comprehension, decision confidence, burden, and mistaken expectations qualitatively. Do not add telemetry, remote analytics, numerical thresholds, or prohibited personal data. Any finding that requires Calendar/Keep access, work data, AI, remote synchronization, new data categories, external communication, or changed consequence boundaries requires Product change control rather than journey expansion.

## Deferred dependencies

| Deferred artifact or owner | Decision still required | Boundary supplied by this document |
| --- | --- | --- |
| Information architecture/navigation | Entry points, organization, and movement among journeys | All 11 journeys and their safe exits must remain reachable without changing semantics. |
| Detailed state matrix | Exact happy, empty, preparing, offline, error, permission, conflict, confirmation, and completion presentations | The journey-level outcome and no-effect rules above are mandatory. |
| Content and notification content | Exact labels, explanations, confirmations, and notification wording | Content must preserve deliberate choice, visible status, non-coercion, and consequence clarity. |
| Accessibility specification | Detailed Android semantics, focus, scaling, target, contrast, non-color, and reduced-motion requirements | Every named status, choice, and consequence must remain perceivable and operable. |
| Architecture | Persistence, storage, offline, notification, export, restore, deletion, format, protection, destination, and environment mechanisms | Mechanisms must satisfy these behaviors without account/backend/AI/remote sync/paid dependency or direct Calendar/Keep access. |
| Quality | Verification design and evidence | Every completion, cancellation, no-effect, opt-out, offline, and destructive-confirmation outcome is externally observable to the user. |

## Revision change record

| Revision | Finding | Bounded change | Downstream impact before use |
| --- | --- | --- | --- |
| 0.2 | Product F-01 | Removed the additional mandatory in-app confirmation from J-09. Jude's completed destination choice, made with eligible scope and external-copy consequence visible, now authorizes one non-recurring attempt. The journey distinguishes pre-choice cancellation, denial, or interruption from post-choice in-progress, completed, established-no-effect, and interrupted/outcome-unknown behavior; it prohibits silent repeat and requires fresh initiation plus destination choice for a new attempt after established no effect. J-01 through J-08 and J-10 through J-11, all requirement priorities, and all acceptance ownership remain unchanged. | `design/information-architecture.md` requires regression against destination-choice-as-authorization before use. The interrupted `design/state-matrix.md` requires remediation for the revised pre-choice and post-choice J-09 states before use. |

## Owner statement

This revision introduces no change request and claims no Quality verification, Gate 2 approval, architecture readiness, security verdict, implementation readiness, production promotion, launch approval, or broader-distribution authorization.