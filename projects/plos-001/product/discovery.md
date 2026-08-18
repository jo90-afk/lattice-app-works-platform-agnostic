# Product Discovery Record and Principal Decision Interview

**Work order:** WO-001 — Product Discovery and Principal Decision Interview  
**Owner:** Product Lead  
**Principal and verifier:** Jude O’Neill  
**Revision:** 0.1  
**Date:** 2026-08-05  
**Status:** OWNER COMPLETE — AWAITING PRINCIPAL DECISIONS AND VERIFICATION  
**Next blocked artifact:** `product/project-brief.md`

## 1. Purpose and evidence discipline

This record ranks the user jobs established by the confirmed mandate, distinguishes confirmed facts from discovery proposals, and asks only the remaining Principal decisions needed before a versioned project brief can be drafted. It does not approve a feature, screen, requirement, architecture, contract, test, phase, schedule, or success threshold.

The labels used throughout are:

- **CONFIRMED** — stated in `work/bootstrap.md` v1.0 and/or the Principal-verified `work/intake.md` v1.0.
- **PROPOSAL / HYPOTHESIS** — supplied in the roadmap or starter brief as discovery evidence; not approved product behavior.
- **OPEN — PRINCIPAL** — a decision that materially affects intent, release scope, data use, autonomy, cost, or external action.
- **DEFERRED** — belongs to a later Product, Experience, Architecture, Quality, Security, or Release gate.
- **PROHIBITED** — conflicts with the confirmed mandate and cannot enter release one without explicit mandate change.

### Named evidence used

| Source | Version or revision | Evidentiary role |
| --- | --- | --- |
| `work/bootstrap.md` | v1.0, `CONFIRMED` 2026-08-05 | Authoritative Principal mandate and consequence boundaries |
| `work/intake.md` | v1.0, `VERIFIED` 2026-08-05 | Gate 0 outcomes, constraints, and open-decision ownership |
| `upload/Lattice_personal_android_app_roadmap-1.md` | Principal-provided discovery revision received 2026-08-05 | Proposed behaviors, domains, scope, measures, phases, and technical hypotheses only |
| `examples/personal-life-os/starter-brief.md`, hosted-pack revision | Canonical section at lines 1619–1669 of the supplied hosted pack | Original discovery hypothesis and unresolved-decision inventory only |

## 2. Confirmed Principal facts and constraints

| ID | Confirmed matter | Product consequence for this discovery |
| --- | --- | --- |
| CF-01 | The intended outcome is a private, Android-first Personal Life OS that reduces Jude’s mental overhead across commitments, projects, routines, reflection, and meaningful interests. | This is the product intent; the roadmap’s broader descriptions do not replace it. |
| CF-02 | Priority order is: (1) daily/weekly planning and reflection; (2) promises and delegated follow-ups; (3) project drift. | Jobs and candidate scope must preserve this order. |
| CF-03 | Jude O’Neill is the only intended release-one user and the sole Principal. Release one is a personal installation only. | Shared accounts, public distribution, and multi-user behavior are outside authorization. |
| CF-04 | The product is personal and must remain separate from work systems and work data. | All release-one jobs, examples, records, backups, and exports must be personal. |
| CF-05 | Google Calendar and Google Keep must coexist with the product; direct integration remains undecided. | “Hybrid” does not itself authorize reading, copying, or changing either system. |
| CF-06 | The product is local-first, and the core daily loop must work offline. | The smallest loop cannot require a network, account, backend, sync service, or AI provider. |
| CF-07 | Names, important dates, family plans, reflections, and generic care reminders may be stored locally. | These are the only expressly permitted personal-data examples; broader content remains subject to scope and data decisions below. |
| CF-08 | Work data and work backups are excluded. Detailed health information, financial data, and location data are out of scope. | These categories are prohibited in release one under the current mandate. |
| CF-09 | Notifications must be user-configurable. Streaks and escalating-pressure mechanics are prohibited. | Notification defaults are not decided here; the product may not use shame or artificial pressure. |
| CF-10 | Release one may not depend on remote synchronization or AI. | Optional release-one AI or sync is not implied and remains an explicit Principal question. |
| CF-11 | No paid service or dependency is pre-authorized. | Any paid dependency must return to the Principal before adoption. |
| CF-12 | The 14-week roadmap is a human-equivalent estimate, not an elapsed-time commitment for agents. | Roadmap phases and timing are not an approved delivery plan. |
| CF-13 | Development, test, and production must be separate environments. | The technical definition is deferred to Architecture; production promotion and launch remain Principal-controlled. |
| CF-14 | Personal-data movement, AI-provider use, destructive deletion/import overwrite, external communication or service-visible action, calendar modification, residual-risk acceptance, production promotion, and launch cross explicit consequence boundaries. | No such behavior is authorized by this discovery record. Development experiments may use only synthetic or non-sensitive data and create no real external effect. |

### Controlled interpretations, not new decisions

- “Promises and delegated follow-ups” is interpreted as **personal-only** because work data is categorically excluded.
- “Coexistence” means Calendar and Keep remain available as existing tools; it does not mean a direct connection.
- “No release-one dependency” does not answer whether optional AI or sync belongs in release one; that ambiguity is isolated in D-05.
- The roadmap cannot expand the confirmed mandate. Where it proposes work behavior or work data, the mandate controls.

## 3. Ranked observable jobs to be done

These are outcome statements, not feature or interface prescriptions.

| Rank / ID | Situation and job | Observable user outcome | Boundary |
| --- | --- | --- | --- |
| 1 — JTBD-01 | When beginning or ending a day or week, Jude needs to decide what deserves attention and reflect on what actually happened, so plans remain intentional rather than mentally carried. | Jude can identify the personal commitments that matter now, deliberately resolve or reconsider them, and leave a review with a clear change in attention. | Exact cadence, limits, prompts, duration, screens, reminders, and measures are not approved. |
| 2 — JTBD-02 | When Jude makes a personal promise or is waiting for someone else, he needs to retain who owns the next move and when to revisit it, so promises do not depend on memory. | Jude can distinguish his own open promise from a personal delegated/waiting item and can tell what follow-up is due next. | No employee, customer, company, or other work content may be used. Exact fields and workflow are not approved. |
| 3 — JTBD-03 | When personal projects compete for attention, Jude needs to notice drift early enough to decide, so meaningful projects are advanced, paused, or consciously released rather than silently neglected. | Jude can identify a personal project that lacks a credible next move or is no longer receiving intended attention and make an explicit disposition decision. | Drift rules, project states, WIP limits, indicators, and thresholds remain proposals. |

### Smallest coherent value-loop hypothesis

**H-01 — PROPOSAL / HYPOTHESIS:** A narrow release-one loop could let Jude form a personal daily intention, close that intention deliberately, and use a weekly reflection to reconsider open personal promises, waiting items, and drifting personal projects. This is the Product Lead’s recommended scope direction because it covers the three ranked jobs through one end-to-end loop without importing the roadmap’s domain-suite breadth. It is not approved unless the Principal selects D-01 option A.

## 4. Principal-provided proposals and hypotheses

The entire refined roadmap remains discovery evidence. The classifications below apply to **every** named object, rule, feature, screen, workflow, phase, exit criterion, technical component, test priority, timing claim, and success measure in the cited roadmap sections, including examples not repeated here.

| Roadmap evidence | Examples | Current classification and applicable gate |
| --- | --- | --- |
| Product framing and accountability model (sections 1 and 3) | Five framing questions; “Rule of Three”; project states; next-move, waiting, rollover, WIP, and review rules | **PROPOSAL / HYPOTHESIS.** Useful evidence for later Product requirements after Gate 1 intent; none is approved behavior now. |
| Personalization map and specialized workflows (sections 2 and 5) | People, Writing, Research, Maker, Collections, and Life Maintenance concepts and templates | **PROPOSAL / HYPOTHESIS.** Broader than the smallest value loop and pending D-01/D-03 or later change control. |
| Work-oriented workflows (sections 2, 5A, 6 phase 3, 7, and 9) | Leadership Console, functional cards, 1:1 agendas, employee/delegation records, executive summaries, work privacy profiles or partitions | **PROHIBITED** under the personal/work separation. A “work-minimal” profile does not cure the conflict; work content and work backups are excluded. |
| Primary experience (section 4) | Five destinations; Today, Inbox, Plan, Areas, Studio, Review; capture controls; widgets; voice; morning/evening/weekly flows | Named screens, navigation, controls, and interaction detail are **DEFERRED to Experience** after accepted intent. Workflow content and time claims remain **Product hypotheses** pending Principal and Quality evidence. |
| Roadmap phases and MVP inventory (sections 6 and 7) | Phases 0–7; “must ship” list; specialized templates; search; app lock; reminders; integrations; personal pilot | **DISCOVERY EVIDENCE, not an approved release plan or requirements set.** D-01 determines release breadth. Any accepted work must later pass its applicable gates. |
| Technical direction (section 8) | Native Android tools, storage, background work, encryption/key handling, file access, package/module boundaries, sync-readiness, test priorities | **DEFERRED to Architecture, Security, Android, and Quality.** No technology, schema, interface, file format, or test design is selected here. |
| Privacy model (section 9) | Personal, work-minimal, and restricted/link-only profiles; separate work exports; biometric lock | Personal-data ideas are **hypotheses** pending D-03/D-04 and later Security/Architecture. All work profiles and work exports are **prohibited** under the confirmed mandate. |
| AI roadmap (section 10) | Classification, summaries, drift suggestions, collision detection, claim analysis, on-device preference, draft-only guardrails | **PROPOSAL / HYPOTHESIS.** No AI behavior or provider is approved; D-05 controls release-one intent, and any provider/data/cost consequence requires explicit approval. |
| Success measures and pilot gates (sections 6 phase 7 and 11) | Completion rates, review duration, promise/project percentages, rollover/WIP counts, capture timing, 10-of-14 and 80% thresholds, qualitative questions | **UNVALIDATED HYPOTHESES.** D-06 determines the outcome-evidence posture. Quality later defines verification; roadmap numbers are not accepted thresholds. |
| First-build sprint (section 13) | Inventory, paper screens, schema, formats, privacy rules, acceptance tests | **PROPOSED SEQUENCE ONLY.** Product, Experience, Architecture, Security, and Quality ownership still applies; no listed artifact or decision is authorized by the roadmap. |
| Working title and Android references (sections 1 and 12) | “Lattice” name and cited platform guidance | The name is a **non-blocking proposal**. References are background evidence only and do not approve technical direction. |

All claims that capture takes under ten seconds, morning planning under one minute, evening close two minutes, weekly review 12–15 minutes, activation under one minute, or similar workflow timing are hypotheses until approved and validated.

## 5. Personal-data and consequence classification

### 5.1 Candidate data categories

| ID | Category | Current classification | Release-one implication |
| --- | --- | --- | --- |
| DC-01 | Names, important dates, family plans, reflections, and generic care reminders | **CONFIRMED for local storage** | Personal-only; inclusion still follows the chosen release scope. |
| DC-02 | Personal commitment descriptions, owner/recipient context, due or follow-up dates, personal project titles/status, routine descriptions, and review decisions | **CANDIDATE — D-01/D-03** | These are plausible minimum records for the ranked jobs, but their exact breadth is not approved. |
| DC-03 | Sensitive relationship notes, detailed journals, full essays/manuscripts, research claims/source notes, media, or stored artifact content | **OPEN — D-03** | Not expressly approved. Detailed storage increases sensitivity and risks turning the product into a note/archive system. |
| DC-04 | Locally derived use patterns such as completion, rollover, review duration, capture timing, or project-attention history | **CANDIDATE — D-06** | May support outcome evidence if approved; no telemetry or remote analytics is authorized. |
| DC-05 | Calendar or Keep content, metadata, account identifiers, or copied items | **OPEN — D-02** | No access, import, copying, or write permission is currently authorized. Selected content would have to exclude work, location, detailed health, and financial data. |
| DC-06 | Backup/export payloads containing personal data | **OPEN — D-04** | Whether data may leave the device is a Principal decision. Backups may never include work data. |
| DC-07 | AI prompts, context entries, model outputs, or provider identifiers | **NOT AUTHORIZED — D-05** | No personal data may be sent to an AI provider without explicit Principal approval of categories and route. |
| DC-08 | Remotely synchronized records, account data, or server copies | **NOT AUTHORIZED — D-05** | No remote sync behavior is approved, and release one may not depend on it. |
| DC-09 | Any work content, including high-level company outcomes, meeting titles, 1:1 notes, employee or customer context, company links, and work backups/exports | **PROHIBITED** | Excluded even if labeled “minimal,” “neutral,” or “link-only.” |
| DC-10 | Detailed health information, financial data, or location data | **PROHIBITED** | Out of scope. Calendar ingestion must not accidentally import these categories. |
| DC-11 | Credentials, API keys, customer records, employee-performance notes, regulated data, or confidential company material | **PROHIBITED** | Outside the personal product and incompatible with the mandate. |
| DC-12 | Voice recordings, shared text/links from other apps, and other externally supplied capture content | **CANDIDATE ONLY** | Roadmap feature evidence; data source, retention, processing, and scope would require later Product/Data decisions before use. |

### 5.2 Actions, dependencies, and autonomy

| Consequence | Current classification | Required treatment |
| --- | --- | --- |
| Local notifications | **CONFIRMED only within user-configurable bounds** | Categories, defaults, timing, quiet hours, frequency, and opt-outs are deferred to Experience. No streak or pressure mechanics. |
| Direct reading from Google Calendar or Keep | **OPEN — D-02** | Principal selects release-one intent; Architecture later assesses feasibility and Security reviews data access. |
| Writing to Calendar, Keep, or another external system | **NOT AUTHORIZED — D-02** | No silent action is permitted. Even user-confirmed writes require explicit Principal intent and later gates. |
| Share-sheet intake, deep links, voice processing, or other app-to-app exchange | **ROADMAP PROPOSAL** | No direct interface is approved. Personal-data flow and external-effect boundaries must be classified before adoption. |
| Backup, export, restore, or sharing | **OPEN — D-04** | Principal decides whether personal data may leave the device. Mechanism, protection, format, and recovery flow are deferred. |
| Full deletion, migration, restore replacement, or import overwrite | **PRINCIPAL-CONTROLLED consequence** | No destructive operation may be automatic or silent. D-04 sets product policy; Experience and Architecture later define safe behavior. |
| Remote synchronization or backend service | **NOT AUTHORIZED — D-05** | No release-one dependency; any optional inclusion requires explicit data, cost, and scope decisions. Services remains dormant meanwhile. |
| AI behavior or AI-provider processing | **NOT AUTHORIZED — D-05** | Intelligence remains dormant. Suggestions, even if draft-only, require approved product purpose and data policy. |
| Paid service, license, API, storage, model, or other paid dependency | **NOT AUTHORIZED** | Any proposal returns to the Principal with cost and alternative before adoption. |
| Production promotion, launch, or broader distribution | **NOT AUTHORIZED** | Release one remains a personal installation; later promotion and launch require their own gates and Principal approval. |

## 6. Minimum Principal decision interview

Please answer in the compact form `D-01 A; D-02 A; ...` and add the requested detail only where an option asks for it. Selecting an option approves intent for the future brief; it does not approve a feature design or implementation.

### D-01 — Release-one value loop

**Prompt:** Which scope should define the smallest coherent release-one value loop?

- **A — Cross-priority loop (recommended):** personal daily intention and deliberate close, plus a weekly reflection that surfaces only enough personal promise/waiting and personal-project context to address JTBD-02 and JTBD-03; defer specialized domain suites.
- **B — Priority-one only:** daily and weekly planning/reflection; defer promises/waiting and project drift to a later release.
- **C — Broader personal suite:** option A plus release-one domain workflows for People, Writing, Research, Maker/Collections, and Life Maintenance. Work workflows remain prohibited.

**Tradeoff:** A covers all three ranked jobs through one loop; B is smaller but postpones confirmed priorities; C offers breadth at materially greater scope and maintenance cost.  
**Product Lead recommendation:** A.

### D-02 — Google Calendar and Google Keep

**Prompt:** What direct relationship, if any, should release one have with Calendar and Keep?

- **A — Coexist only (recommended):** no direct connection; Jude continues using both systems separately and enters only selected personal context into the app.
- **B — Read-only:** directly read selected personal data; state `Calendar`, `Keep`, or `both`, and name the categories allowed. No writes.
- **C — Read plus confirmed action:** option B plus named user-confirmed external changes; state the system and exact actions. Silent action remains prohibited.

**Tradeoff:** Direct access can reduce duplicate entry but expands permission, privacy, offline, feasibility, and accidental work/location-data risk.  
**Product Lead recommendation:** A for release one.

### D-03 — Breadth of locally stored personal content

**Prompt:** How much personal content may release one store locally?

- **A — Minimal planning records (recommended):** personal commitments/projects/routines, dates, people needed for personal promises, short reflection/review entries, family plans, and generic care reminders; exclude full manuscripts, detailed relationship dossiers, media, and source archives.
- **B — Detailed personal knowledge:** option A plus full personal notes, essays/research content, claims, sources, and stored artifact content.
- **C — Metadata/link-light:** keep commitments and short reflections, but represent broader personal projects mainly through titles, state, and links to their proper source systems.

All options continue to prohibit work, detailed health, financial, and location data.  
**Tradeoff:** More content may reduce tool switching but increases sensitivity, backup burden, and warehouse scope.  
**Product Lead recommendation:** A; later evidence can justify B selectively.

### D-04 — Portability, recovery, and deletion

**Prompt:** May release-one personal data leave the device through an explicit backup/export, and what ownership controls must exist?

- **A — User-controlled portability (recommended):** require user-initiated export/backup, restore, and full deletion. Data may leave the device only when Jude explicitly chooses a destination. No automatic sync or silent destructive replacement.
- **B — Device-contained:** require full deletion but no export, backup, or restore; no app-managed personal data leaves the device, and lost-device recovery is unavailable.

**Tradeoff:** A supports recovery and ownership but creates a controlled data-movement surface; B minimizes movement but accepts loss-of-device/data risk. Protection, format, destination handling, and restore mechanics remain later specialist decisions.  
**Product Lead recommendation:** A.

### D-05 — AI and remote synchronization

**Prompt:** Should release one include any optional AI or remote-sync behavior, despite not depending on either?

- **A — Exclude both (recommended):** keep Services and Intelligence dormant for release one; reconsider only through later change control.
- **B — Optional AI:** state whether processing must be on-device or may use an external provider, which DC-01–DC-04 categories may be used, and whether a paid proposal may be considered. AI may only draft or recommend; never silently mutate data or act externally.
- **C — Optional remote sync:** state which DC-01–DC-04 categories may leave the device, the permitted destination class, and whether a paid proposal may be considered.
- **D — Both:** provide all details required by B and C.

**Tradeoff:** Optional AI/sync may add convenience or recovery but materially increases data-use, cost, security, offline, and release scope.  
**Product Lead recommendation:** A.

### D-06 — Outcome evidence before a baseline exists

**Prompt:** How should the future project brief define success before Jude has a validated baseline?

- **A — Observable signals, thresholds after baseline (recommended):** judge whether the daily/weekly loop produces deliberate decisions; personal promises have a clear owner/next follow-up; active personal projects have a next move or explicit disposition; and maintaining the product feels less burdensome than the confusion removed. Set numerical pilot thresholds only after baseline evidence.
- **B — Adopt roadmap pilot numbers now:** use the proposed 10-of-14 daily closes, two weekly reviews within 15 minutes, 80% promise coverage, all active projects with a next action/blocker, sub-ten-second median capture, and zero data-loss/notification-critical defects.
- **C — Principal-specified:** provide different observable signals or thresholds.

**Tradeoff:** A remains testable without false precision; B is immediately quantitative but currently unvalidated; C can reflect a stronger Principal preference. Quality and Security still own verification and defect/risk verdicts.  
**Product Lead recommendation:** A.

### D-07 — Accessibility needs

**Prompt:** Is there a known release-one accessibility need beyond baseline Android accessibility support?

- **A — No additional known need at present.**
- **B — Yes:** identify the need in terms of vision/text, motor/input, hearing, cognitive/attention, or another concrete use constraint.
- **C — Unknown:** schedule a short Principal accessibility follow-up before Experience begins.

**Tradeoff:** Early knowledge changes experience scope and verification; guessing could miss a real need or invent one.  
**Product Lead recommendation:** None; the supplied evidence does not support an assumption.

## 7. Matters deliberately not asked again

- Platform, local-first posture, offline core loop, one-user personal installation, personal/work separation, excluded sensitive categories, user-configurable notifications, prohibition on shame mechanics, lack of pre-authorized spend, and consequence boundaries are already confirmed.
- Notification categories, default cadence, quiet-hour behavior, and controls belong to Experience after accepted intent; this record does not prescribe them.
- Navigation, screens, interactions, visual design, and notification defaults belong to Gate 2.
- Architecture, schema, APIs, integration mechanics, file formats, encryption mechanisms, environment isolation, and technology selection belong to Gate 3 and later reviews.
- Verification methods, test results, performance thresholds, defect severity, security acceptance, production promotion, and launch are outside this work order.

## 8. Concise decision log

| Log ID | Matter | Status | Basis / next owner |
| --- | --- | --- | --- |
| DL-01 | Product intent, sole user, and ranked jobs | **CONFIRMED** | Bootstrap v1.0 and Intake v1.0 |
| DL-02 | Personal-only scope and prohibited data categories | **CONFIRMED / PROHIBITED as listed** | Bootstrap v1.0 and Intake v1.0 |
| DL-03 | Local-first, offline core loop, no AI/sync dependency | **CONFIRMED** | Bootstrap v1.0 and Intake v1.0 |
| DL-04 | Smallest release loop | **OPEN — D-01** | Principal, Gate 1 |
| DL-05 | Calendar/Keep direct interaction | **OPEN — D-02** | Principal for intent/consequence; Architecture later for feasibility |
| DL-06 | Local personal-content breadth | **OPEN — D-03** | Principal, Gate 1 |
| DL-07 | Backup/export/restore/deletion policy and off-device movement | **OPEN — D-04** | Principal for data policy; Experience/Architecture/Security later |
| DL-08 | Optional AI or remote sync | **OPEN — D-05** | Principal; Services/Intelligence remain dormant |
| DL-09 | Outcome signals and threshold posture | **OPEN — D-06** | Principal for intent; Quality later for verification |
| DL-10 | Additional accessibility needs | **OPEN — D-07** | Principal, then Experience |
| DL-11 | Screens, navigation, interaction details, and notification defaults | **DEFERRED** | Experience, Gate 2 |
| DL-12 | Technology, schema, interfaces, formats, protection mechanisms, and environment implementation | **DEFERRED** | Architecture/Security, Gate 3 and later |
| DL-13 | Rule of Three, WIP limit, project states, object model, detailed domain templates, and precise workflow rules | **DEFERRED / UNAPPROVED** | Later Product requirements after project-brief intent; applicable gate review |
| DL-14 | Roadmap phases, 14-week timing, pilot protocol, and numerical gates | **UNAPPROVED HYPOTHESES** | Director/Quality only after accepted specialist inputs |
| DL-15 | Work-oriented features or data; detailed health, finance, or location data; silent external action; streak/escalating-pressure mechanics | **PROHIBITED** | Current mandate |
| DL-16 | Paid dependency, residual-risk acceptance, production promotion, launch, or broader distribution | **PRINCIPAL-CONTROLLED / NOT AUTHORIZED** | Later explicit Principal decision |

## 9. Readiness, assumptions, and limitations

`product/project-brief.md` remains blocked until Jude answers D-01 through D-07 and verifies whether this record is `SATISFIED` or `NOT_SATISFIED`. If an answer introduces work data, a prohibited data category, external AI/provider processing, remote sync, direct external writes, or paid dependency, Product must return with the smallest additional consequence decision rather than assume a default.

This discovery is based on Principal-provided documents, not observed use, baseline measurements, integration feasibility, security analysis, or tested workflows. The recommended loop and evidence posture are therefore hypotheses for Principal selection. No Experience, Architecture, Quality, Security, Android, Services, Intelligence, Release, or implementation work is activated by this record.
