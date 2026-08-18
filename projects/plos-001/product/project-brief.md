# Project Brief: Personal Life OS

**Version:** 0.1  
**Principal:** Jude O’Neill  
**Product Lead:** Product Lead — WO-002  
**Status:** In review  
**Last updated:** 2026-08-05

## Product intent

Create a private, Android-first Personal Life OS for Jude O’Neill that reduces the mental overhead of personal planning by turning daily and weekly reflection, personal promises, delegated follow-ups, and personal-project drift into deliberate next decisions.

## Evidence classification

| Class | Release-one treatment |
| --- | --- |
| Confirmed facts | Jude is the sole Principal and release-one user; the product is personal, Android-first, local-first, and separate from work systems and work data; Google Calendar and Google Keep are existing tools. |
| Principal decisions | D-01 A through D-07 A select the cross-priority loop, coexistence without direct Calendar/Keep connection, minimal local planning records, user-controlled portability and deletion, no AI or remote sync, observable outcome signals with thresholds after baseline, and no additional known accessibility need. |
| Hypotheses | The selected loop will reduce mental overhead; limited promise/waiting and project context will be enough to address the second and third ranked jobs; manual coexistence with Calendar and Keep will remain tolerable. |
| Constraints | The selected loop is personal-only, operates without remote services, uses no paid dependency, creates no silent external action, and remains a single personal installation. Experience and technical mechanisms remain undecided. |

## Target users and context

- **Primary user:** Jude O’Neill only; Jude is also the sole Principal and human decision authority.
- **Situation or trigger:** Beginning or ending a day or week; making a personal promise; waiting for another person; or noticing that competing personal projects may be drifting.
- **Current workaround:** Google Calendar and Google Keep remain separate existing tools. Release one adds no direct connection; Jude selects the personal context worth entering. No observed-use baseline for the current workflow exists yet.
- **Important constraints:** Personal use only; no work behavior or work data; Android-first; local-first; the selected value loop must not require a network, account, backend, remote synchronization, or AI provider; broader distribution is not authorized.

## Jobs to be done

1. When beginning or ending a day or week, I want to decide what deserves attention and reflect on what actually happened, so I can keep my personal plans intentional instead of carrying them mentally.
2. When I make a personal promise or wait for someone else, I want to know who owns the next move and when I should revisit it, so I can keep personal promises without relying on memory.
3. When personal projects compete for attention, I want to notice drift early enough to decide what happens next, so I can advance, pause, or consciously release a project instead of silently neglecting it.

## Smallest coherent value loop

1. Jude records only the minimal personal context needed to make a near-term decision.
2. At the start of a day, Jude forms a deliberate personal intention about what deserves attention.
3. At the end of the day, Jude considers what happened and deliberately resolves or reconsiders the intention rather than letting it disappear by default.
4. During a weekly reflection, Jude sees only enough unresolved personal intention, promise/waiting, and personal-project context to identify who owns a next move, when a follow-up is due, and which project needs a next move or explicit disposition.
5. Jude leaves the reflection with clear changes in attention, follow-up, or project disposition. That decision state is the end-to-end value delivered by release one.

This loop does not require specialized personal-domain suites, direct Calendar or Keep access, AI, remote synchronization, or a network connection.

## Goals and outcome signals

| Goal | Observable signal | Baseline | Target | Review date |
| --- | --- | --- | --- | --- |
| G-01 — Make daily and weekly attention deliberate | The daily and weekly loop produces an explicit decision about what matters now and what changed after reflection. | Unknown; no real-use baseline exists. | Signal observed in real use; any numerical threshold waits for baseline evidence. | To be set after an initial real-use baseline. |
| G-02 — Reduce memory dependence for personal promises | Each reviewed open personal promise or waiting item has a clear owner and next follow-up. | Unknown; no real-use baseline exists. | Signal observed in real use; any numerical threshold waits for baseline evidence. | To be set after an initial real-use baseline. |
| G-03 — Prevent silent personal-project drift | Each reviewed active personal project has a credible next move or an explicit disposition decision. | Unknown; no real-use baseline exists. | Signal observed in real use; any numerical threshold waits for baseline evidence. | To be set after an initial real-use baseline. |
| G-04 — Remove more confusion than the product creates | Jude reports that maintaining the product feels less burdensome than the confusion removed. | Unknown; no real-use baseline exists. | Signal observed in real use; any numerical threshold waits for baseline evidence. | To be set after an initial real-use baseline. |

Roadmap timing and percentage claims are not release-one targets. Quality may define a later verification method only after Product obtains baseline evidence; Security and Quality retain their own acceptance responsibilities.

## Non-goals

The first release will not:

- provide specialized suites or workflows for People, Writing, Research, Maker/Collections, Life Maintenance, or other personal domains;
- support work behavior, work records, work links, work backups or exports, company context, meetings, 1:1s, employee or customer context, or any work-oriented profile;
- connect to, read from, import or copy from, monitor, or write to Google Calendar or Google Keep;
- include AI behavior, AI-provider processing, a backend, remote synchronization, remote analytics, or telemetry;
- solicit or support detailed health information, financial data, location data, detailed relationship dossiers, detailed journals, full manuscripts or essays, research claims or source archives, media archives, credentials, API keys, regulated data, or confidential company material;
- include voice recordings, share-sheet intake, deep links, or other app-to-app capture;
- communicate externally, make service-visible changes, modify a calendar, or take any silent external action;
- use streaks, shame, escalating pressure, or notification behavior Jude cannot configure or disable;
- depend on a paid service, license, API, storage provider, model, or other paid dependency;
- support multiple users, shared accounts, public release, or broader distribution; or
- select screens, navigation, components, schemas, APIs, file formats, frameworks, encryption mechanisms, environment topology, test methods, or launch mechanics.

## Proposed release scope

| Requirement ID | User-visible behavior | Priority | Acceptance summary |
| --- | --- | --- | --- |
| R-001 | Jude can record and revise the minimal personal planning context needed by the selected value loop. | Must | The supported context is limited to personal intentions or commitments, promise/waiting ownership and follow-up, personal-project title and next move or disposition, and short reflection or review decisions; completing the loop never requires a detailed personal archive or a prohibited data category. |
| R-002 | Jude can form a personal daily intention about what deserves attention. | Must | After beginning the daily loop, Jude can identify the personal commitment or commitments intentionally chosen for attention without requiring network access or an external account. |
| R-003 | Jude can deliberately close a daily intention. | Must | After the close, Jude can tell what happened and what was resolved or reconsidered; an unresolved intention does not disappear without a deliberate decision. |
| R-004 | Jude can distinguish a personal promise he owns from an item for which he is waiting on someone else. | Must | For each reviewed open promise or waiting item, Jude can identify who owns the next move and the next follow-up to revisit. No external message is sent. |
| R-005 | Jude can make a deliberate decision about a personal project that lacks a credible next move or intended attention. | Must | During reflection, Jude can identify a relevant personal project needing attention and give it a next move or an explicit disposition; no fixed state model, drift threshold, or work-in-progress limit is assumed. |
| R-006 | Jude can complete a weekly reflection across the three ranked jobs without entering a specialized domain workflow. | Must | The reflection surfaces only enough unresolved daily, promise/waiting, and personal-project context for Jude to leave with clear attention, follow-up, or disposition decisions. |
| R-007 | Jude can complete the selected value loop while Calendar and Keep remain separate and while the device has no network connection. | Must | Daily intention, daily close, weekly reflection, and their minimal supporting personal context remain usable without connecting to, reading, or writing either external system and without a network, backend, sync service, or AI provider. |
| R-008 | Jude can control or completely opt out of every release-one notification behavior that is offered. | Must | Any offered notification allows Jude to control its category, timing, quiet hours, frequency limits, and opt-out; no streak or escalating-pressure consequence is attached. Exact defaults and interaction behavior remain for Experience. |
| R-009 | Jude can explicitly initiate an export or backup and choose its destination. | Must | No app-managed personal data leaves the device until Jude initiates the action and selects a destination; the export or backup contains no work data. Format, protection, and destination handling remain undecided. |
| R-010 | Jude can explicitly initiate restoration of a user-chosen backup. | Must | A restore never silently replaces existing information; Jude is made aware of any destructive consequence and explicitly confirms it before that consequence occurs. Restore format and mechanism remain undecided. |
| R-011 | Jude can explicitly initiate full deletion of app-managed personal data. | Must | Full deletion occurs only after Jude deliberately initiates and confirms the destructive consequence; it is never automatic or silent. The deletion mechanism and later verification remain undecided. |

## Data and autonomy inventory

### Personal-data categories

| Item | Why needed | Stored where | Retention/control | Principal decision needed? |
| --- | --- | --- | --- | --- |
| DI-01 — Personal intention and commitment descriptions and relevant dates | Supports daily intention, deliberate close, and weekly reflection. | On Jude’s Android device; mechanism deferred. | Jude controls the content; it may leave the device only through user-initiated export or backup and is subject to full deletion. | No; selected by D-01 A, D-03 A, and D-04 A. |
| DI-02 — Names or minimal owner/recipient context and next follow-up dates for personal promises or waiting | Identifies who owns the next move and when Jude should revisit it. | On Jude’s Android device; mechanism deferred. | Same user-controlled boundary as DI-01; no external communication is implied. | No; selected by D-03 A and bounded to personal use. |
| DI-03 — Personal-project titles, next moves, and disposition decisions | Lets Jude notice and deliberately address personal-project drift. | On Jude’s Android device; mechanism deferred. | Same user-controlled boundary as DI-01; no detailed project archive is required. | No; selected by D-01 A and D-03 A. |
| DI-04 — Short personal reflections and review decisions | Supports deliberate close and records the change in attention after reflection. | On Jude’s Android device; mechanism deferred. | Same user-controlled boundary as DI-01; full journals and detailed dossiers are excluded. | No; selected by D-03 A. |
| DI-05 — Minimal routine references, important dates, family plans, and generic care reminders | Permitted as selected personal context when relevant to the loop; no specialized domain workflow is implied. | On Jude’s Android device if Jude chooses to record them; mechanism deferred. | Same user-controlled boundary as DI-01. | No; permitted by the mandate and D-03 A, but not required for loop completion. |
| DI-06 — Backup or export copy of DI-01 through DI-05 | Gives Jude user-controlled portability and recovery. | Only at a destination Jude explicitly chooses; destination and format are deferred. | Created only on Jude’s initiation; no automatic sync; never contains work data. | No; selected by D-04 A. Protection and mechanism require later specialist work, not a new intent decision unless they alter policy. |
| DI-07 — Locally derived use patterns, such as completion, rollover, duration, timing, or attention history | Could support later baseline measurement, but is not required to deliver the selected loop or qualitative signals. | Not included in proposed release scope. | Any later collection requires Product change control and applicable privacy review; remote analytics remains excluded. | Yes, if later proposed as product-collected data. |
| DI-08 — Calendar or Keep content, metadata, account identifiers, or copied items | Not needed because release one coexists without a direct connection. | Not collected or stored. | No access, import, copy, monitoring, or write behavior. | Resolved: excluded by D-02 A. |
| DI-09 — Detailed relationship notes, detailed journals, full manuscripts or essays, research claims or source notes, media, archives, voice recordings, or externally supplied app-to-app capture | Not needed for the minimum loop and would broaden sensitivity and scope. | Not collected or stored as supported release-one categories. | Outside release-one behavior. | Resolved: excluded by D-03 A; later inclusion requires change control. |
| DI-10 — Work content or work backups/exports, including company, meeting, employee, customer, or confidential context | Prohibited by the personal/work boundary. | Not collected or stored. | Never included in supported records, backup, or export. | No; prohibited by the confirmed mandate. |
| DI-11 — Detailed health information, financial data, or location data | Prohibited under the confirmed mandate. | Not collected or stored. | Outside release-one behavior and all backups/exports. | No; prohibited by the confirmed mandate. |
| DI-12 — Credentials, API keys, regulated data, employee-performance notes, customer records, or confidential company material | Not part of the personal product and incompatible with its boundary. | Not collected or stored. | Outside release-one behavior and all backups/exports. | No; prohibited by the confirmed mandate. |
| DI-13 — AI prompts, model context or outputs, provider identifiers, remotely synchronized records, account data, or server copies | Not needed; AI and remote synchronization are excluded. | Not collected or stored by an AI provider or remote service. | No AI-provider transfer, backend copy, or remote synchronization. | Resolved: excluded by D-05 A. |

### External, destructive, background, AI, and paid actions

| Action or dependency | Release-one classification | User control and Principal review |
| --- | --- | --- |
| Local notifications | Permitted only within the confirmed configurable boundary; not an external communication. | Jude controls categories, timing, quiet hours, frequency limits, and opt-outs. Defaults and experience remain deferred. |
| User-initiated export or backup | Required; personal data may leave the device only through this explicit action. | Approved in D-04 A. Jude chooses the destination; no automatic transfer occurs. |
| User-initiated restore with possible replacement | Required and potentially destructive. | Approved in D-04 A only with explicit initiation and confirmation; silent destructive replacement is prohibited. Safe experience and mechanism remain deferred. |
| Full deletion | Required and destructive. | Approved in D-04 A only with explicit initiation and confirmation; automatic or silent deletion is prohibited. |
| Direct Calendar/Keep read, import, copy, monitor, or write | Excluded. | D-02 A authorizes coexistence only. Any later direct access or external modification returns to the Principal and applicable gates. |
| Other external communication, sharing, or service-visible action | Excluded. | No message, share, calendar modification, or other external effect is authorized. Any proposal requires explicit Principal intent. |
| Background monitoring, remote analytics, or telemetry | Excluded. | No ongoing monitoring or remote measurement is authorized. Notification mechanisms remain an Architecture decision within R-008. |
| AI processing or AI-initiated action | Excluded; Intelligence remains dormant. | D-05 A authorizes neither AI nor provider data transfer. Any later proposal requires a product reason and explicit data, autonomy, and cost decisions. |
| Remote synchronization, backend service, or remote copy | Excluded; Services remains dormant. | D-05 A authorizes no remote sync or backend data movement. |
| Paid service, license, API, storage, model, or purchase | No paid dependency is authorized or required. | Any later spending proposal must return to Jude with cost and an alternative before adoption. |
| Production promotion, launch, or broader distribution | Outside release-one product intent authorization. | Personal installation only; later promotion, launch, or broader distribution requires its own gates and explicit Principal approval. |

## Constraints

- **Platform:** Android-first. No Android implementation mechanism is selected by this brief.
- **Offline expectations:** The selected value loop and its minimal supporting personal context operate without a network, external account, backend, remote synchronization, or AI provider.
- **Accessibility:** Baseline Android accessibility support is required. D-07 A records no additional known release-one need; this remains an assumption to validate in real use.
- **Privacy/security:** Personal-only minimal planning records; strict separation from work; no direct Calendar/Keep access; no detailed health, financial, or location data; no AI or remote service. Export, backup, restore, and full deletion are user-initiated. Protection, format, deletion, restore, and storage mechanisms remain for later specialists.
- **Autonomy and notifications:** No silent external or destructive action. Any offered notification behavior is configurable and optional. Streaks, shame, and escalating-pressure mechanics are prohibited.
- **Budget/paid services:** No spend or paid dependency is pre-authorized, and none is required by release-one intent.
- **Schedule:** No release date or elapsed-time commitment is approved. The roadmap’s 14-week figure is only a human-equivalent estimate. Baseline-dependent numerical outcome targets remain unset.
- **Distribution:** One personal installation for Jude only; no multi-user or public distribution.
- **Environments:** Development, test, and production must remain separate. Architecture owns their technical definition; test or production promotion is not authorized by this brief.

## Assumptions to validate

| Assumption | Risk if false | Evidence needed | Owner |
| --- | --- | --- | --- |
| A-01 — A daily intention, deliberate close, and weekly reflection reduce more mental overhead than they add. | The core loop could become another maintenance burden and fail G-01 or G-04. | Observed use plus Jude’s comparison of burden and confusion before and after initial use. | Product Lead |
| A-02 — Limited promise/waiting and personal-project context inside the weekly reflection is enough to address JTBD-02 and JTBD-03 without specialized suites. | Promises may still be missed or projects may still drift, forcing a scope reconsideration. | Real examples showing whether Jude can identify owner/follow-up and next move/disposition without extra domain behavior. | Product Lead |
| A-03 — Manual coexistence with Calendar and Keep is acceptable. | Duplicate entry or tool switching could outweigh the privacy and scope benefit of no direct connection. | Real-use observation and Jude’s report of re-entry burden; any integration proposal would require change control. | Product Lead |
| A-04 — Minimal planning records are sufficient and do not need detailed journals, archives, or specialized content. | The loop may lack context, or it may pressure release one toward a sensitive personal-data warehouse. | Real-use examples of decisions that can and cannot be made from the selected minimal context. | Product Lead |
| A-05 — The qualitative signals in G-01 through G-04 can establish a useful baseline before numerical targets are set. | Product and Quality may lack enough evidence to define meaningful later thresholds. | A documented initial-use baseline and a later Product/Quality review of candidate measures. | Product Lead |
| A-06 — User-controlled export, backup, restore, and full deletion can be understandable without introducing unacceptable burden or accidental loss. | Ownership controls may confuse Jude or create destructive-data risk. | Experience journey evidence, Architecture feasibility, Security review, and later Quality verification. | Experience Lead |
| A-07 — User-configurable notifications can support the loop without pressure or noise. | Notifications may increase overhead, interrupt quiet time, or create coercive behavior. | Experience evidence covering categories, defaults, timing, quiet hours, limits, and opt-out in the accepted journeys. | Experience Lead |
| A-08 — Baseline Android accessibility support meets Jude’s current release-one needs. | An unrecognized vision, motor, hearing, or cognitive/attention need could block successful use. | Direct validation with Jude during Experience work and observation in real use. | Experience Lead |

## Principal decisions

The decisions below approve release-one intent for this brief. They do not approve experience design, architecture, implementation, verification results, security risk, production promotion, or launch.

| Decision | Options considered | Decision | Date |
| --- | --- | --- | --- |
| D-01 — Release-one value loop | A: cross-priority loop; B: priority-one only; C: broader personal suite | **A — Cross-priority loop:** daily intention and close plus weekly reflection with only enough personal promise/waiting and project context for all three ranked jobs. | 2026-08-05 |
| D-02 — Calendar and Keep | A: coexist only; B: read-only; C: read plus confirmed action | **A — Coexist only:** no direct connection; Jude enters selected personal context. | 2026-08-05 |
| D-03 — Local content breadth | A: minimal planning records; B: detailed personal knowledge; C: metadata/link-light | **A — Minimal planning records.** | 2026-08-05 |
| D-04 — Portability, recovery, deletion | A: user-controlled portability; B: device-contained | **A — User-controlled export/backup, restore, and full deletion; no automatic sync or silent destructive replacement.** | 2026-08-05 |
| D-05 — AI and remote sync | A: exclude both; B: optional AI; C: optional remote sync; D: both | **A — Exclude both; Services and Intelligence remain dormant.** | 2026-08-05 |
| D-06 — Outcome evidence | A: observable signals, thresholds after baseline; B: adopt roadmap numbers; C: Principal-specified | **A — Use observable signals and set numerical pilot thresholds only after baseline evidence.** | 2026-08-05 |
| D-07 — Accessibility | A: no additional known need; B: named need; C: unknown/follow-up | **A — No additional known release-one need beyond baseline Android accessibility support.** | 2026-08-05 |

## Approval

- **Product Lead recommendation:** Submit version 0.1 for independent Experience Lead verification against WO-002; retain the selected scope and consequence boundaries.
- **Experience verification:** Pending fresh Experience Lead review; no verification is claimed.
- **Principal decision:** D-01 A through D-07 A are recorded as frozen intent decisions from WO-001. Approval of this project brief is pending; no Principal approval of version 0.1 is claimed.