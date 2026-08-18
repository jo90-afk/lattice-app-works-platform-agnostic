# Lattice: A Personalized Android Life-Management App

**Working product roadmap for Jude O’Neill**  
**Planning horizon:** 14 weeks for a part-time solo build (roughly 6–10 hours/week)  
**Product principle:** Turn attention into explicit commitments, then make reflection unavoidable but humane.

## 1. Product Definition

Lattice should be a private, local-first Android personal operating system. Its purpose is not to hold every fact in Jude’s life or compete with a calendar, project-management suite, CRM, manuscript editor, or note archive. Its job is to answer five questions quickly:

1. What matters now?
2. What have I explicitly promised—and to whom?
3. What am I waiting on?
4. Which meaningful projects are drifting?
5. What needs to change when I review the week honestly?

The app should feel like a clear desk at the beginning and end of the day. It should unify a complex life without flattening its domains into one undifferentiated task list.

### North-star behavior

Every morning, Jude selects no more than three meaningful commitments. Every evening, he closes the loop on them. Every week, he reviews his roles, promises, active projects, and neglected priorities before selecting the next week’s focus.

### Recommended working title

**Lattice** fits the product: a small set of structures supports many connected domains without forcing them into the same shape. The name also quietly echoes Jude’s mathematical and symbolic interests.

## 2. Personalization Map

The app should use shared underlying objects—areas, outcomes, projects, commitments, people, artifacts, signals, and reviews—while presenting different workflows for each part of life.

| Life domain | Personalized view | Behavior the app should support |
| --- | --- | --- |
| VP of Revenue Marketing transition | **Leadership Console** | Weekly executive outcomes, operating cadence, delegated follow-ups, decision log, 1:1 agendas, risks, and scorecards for Campaigns; Web & Regional Demand Generation; GDR; PR & Corporate Events; and Marketing Operations |
| Family and relationships | **People & Presence** | Remember important moments, plan intentional one-on-one time, capture promised follow-ups, and protect space for Connor, Rain, and Carter without turning relationships into performance scores |
| Theology, politics, and long-form essays | **Writing Desk** | Track thesis, outline, source notes, claims requiring support, revision passes, citations, publication status, and the moral purpose of a piece |
| Modular-forms and number-theory research | **Research Lab** | Track conjectures, definitions, lemmas, dependencies, exact-computation checks, reviewer issues, confidence, reproducibility evidence, and manuscript versions |
| Sigilize and software builds | **Maker Studio** | Manage milestones, bugs, decisions, tests, releases, and the next shippable slice for Sigilize, Android tools, the home-network dashboard, and other builds |
| D&D, fragrance, game tools, and other creative exploration | **Collections** | Use lightweight structured notebooks and reusable templates without promoting every curiosity into an active project |
| Personal administration and recurring care | **Life Maintenance** | Handle appointments, household routines, renewals, care schedules, and other obligations that should be reliable but should not dominate the home screen |

## 3. The Core System

### Core objects

| Object | Purpose | Key fields |
| --- | --- | --- |
| **Area** | A durable responsibility or interest | Name, type, privacy profile, review cadence |
| **Outcome** | A result that should become true | Success test, horizon, area, status, importance |
| **Project** | A finite body of work that produces an outcome | Type, outcome, next milestone, state, review date |
| **Commitment** | A promise or next action | Owner, recipient, due date, follow-up date, duration, energy, status |
| **Person** | Someone connected to promises or presence | Relationship, relevant follow-ups, important dates; sensitive notes discouraged |
| **Artifact** | A link to work stored elsewhere | URI, type, version label, project, short description |
| **Signal** | A metric or qualitative indicator | Definition, cadence, target or healthy range, latest observation |
| **Review** | A durable record of reflection and reprioritization | Period, answers, decisions, carried/dropped commitments |
| **Claim / Issue** | A specialized research or writing object | Statement, evidence, confidence, severity, resolution state |

### Shared states

Every project should be in exactly one state:

- **Active:** receives time this week.
- **Maintaining:** ongoing responsibility with a light recurring cadence.
- **Incubating:** important, but intentionally not receiving current effort.
- **Someday:** retained without an implied promise.
- **Archived:** complete, abandoned, or superseded.

This is the central defense against a sprawling app becoming a sprawling life. A project is not “active” merely because Jude cares about it.

### Accountability rules

1. **Daily Rule of Three:** select up to three meaningful commitments, ideally spanning work, personal/family, and craft or reflection.
2. **One next move:** every active project must have one visible next action or a documented blocker.
3. **Explicit waiting:** delegated work belongs in a Waiting view with an owner and follow-up date—not among Jude’s own tasks.
4. **No silent rollover:** unfinished daily commitments must be completed, rescheduled with a reason, delegated, dropped, or returned to the project backlog.
5. **WIP limit:** begin with no more than three strategic outcomes and six discretionary active projects across all non-routine domains. Areas and work functions do not count as projects.
6. **Review before expansion:** activating a new discretionary project requires pausing, completing, or explicitly overriding the limit on another.
7. **No shame mechanics:** show patterns and broken promises clearly, but do not use punitive streaks, red-number anxiety, or synthetic urgency.

## 4. Primary Experience

### Navigation

Use five bottom-level destinations:

1. **Today** — daily commitments, schedule context, and quick capture
2. **Plan** — outcomes, projects, commitments, and Waiting
3. **Areas** — Leadership, People & Presence, Writing Desk, Research Lab, Maker Studio, Collections, Life Maintenance
4. **Studio** — notes, claims, issues, artifacts, and reusable project templates
5. **Review** — daily close, weekly review, and longer-horizon reflection

### Today screen

The first screen should contain only what helps Jude act:

- Today’s three commitments
- The current focus card
- Calendar context, shown but not duplicated
- Time-sensitive promises and delegated follow-ups
- A single quick-capture control
- A calm indication of which important area has received no attention recently

It should not open on analytics, an infinite backlog, or a stream of overdue items.

### Capture flow

Capture must take under ten seconds through:

- A persistent quick-capture action
- Android share-sheet intake for links or selected text
- A home-screen widget
- Optional voice-to-text

Every capture enters an Inbox. During triage, it becomes a commitment, note, artifact, project idea, delegated follow-up, or deletion. The app should never force full classification at capture time.

### Morning contract

The morning check-in should take under one minute:

1. Surface the calendar, due promises, and one neglected priority.
2. Ask: **“What must be true by tonight for today to count?”**
3. Let Jude select or create up to three commitments.
4. Ask for the first focus item.

### Evening close

The evening check-out should take two minutes:

1. Resolve each daily commitment: done, deliberately moved, delegated, dropped, or blocked.
2. Capture the reason for movement with one tap plus optional text.
3. Ask: **“What deserves to be remembered from today?”**
4. Clear any remaining Inbox items or explicitly defer triage.

### Weekly review

The weekly review should take 12–15 minutes:

- What became true this week?
- Which promises remain open?
- What am I waiting on, and when will I follow up?
- Where did I spend attention that I did not intend to spend?
- Which role or person received too little presence?
- Which project is pretending to be active?
- What should be completed, paused, or abandoned?
- What are next week’s three strategic outcomes?

The review ends by generating a concise weekly brief, not a score.

## 5. Specialized Workflows

### A. Leadership Console

Preconfigure five functional cards:

- Campaigns
- Web & Regional Demand Generation
- GDR
- PR & Corporate Events
- Marketing Operations

Each card should show:

- Current outcome and success test
- One or two leading indicators
- Current risk or decision needed
- Last and next 1:1
- Open commitments Jude made to the leader
- Delegated items and follow-up dates
- A short “coach, unblock, decide, or stay out” prompt

Leadership-specific tools:

- **Decision log:** decision, context, owner, date, review trigger, and reversibility
- **Delegation ledger:** desired outcome, owner, check-in date, guardrails, and completion evidence
- **1:1 agenda:** wins, blockers, decisions, development, commitments made by each person
- **Executive weekly summary:** outcomes, signals, risks, decisions, and asks
- **Transition accountability:** recurring check against whether Jude is operating at VP altitude or slipping back into individual-contributor rescue work

The app should track Jude’s promises and decisions, not become an unofficial employee-performance database.

### B. People & Presence

This view should be deliberately gentle. It may hold:

- Important dates and events
- Things Jude promised to do or ask about
- Ideas for intentional time together
- A private “last meaningful contact” cue
- Shared plans or practical responsibilities

It should not grade relationships, assign affection scores, or reward interaction streaks. Connor, Rain, and Carter are people to be present to, not accounts to service.

### C. Writing Desk

Each writing project should support:

- Purpose and intended audience
- One-sentence thesis
- Outline and section status
- Claims that need evidence
- Source and citation links
- Revision passes: structure, logic, evidence, voice, line edit, publication
- Questions or objections to address
- Version snapshots and publication destinations

For Jude’s theological and political writing, add a pre-publication prompt: **“Is the language clear, sourced, morally answerable to the people affected, and recognizably mine?”**

### D. Research Lab

Each mathematical research project should support:

- Definitions and invented terms
- Claim dependency tree
- Status: intuition, computational evidence, proof sketch, proved, independently verified, disputed
- Exact checks, scripts, bounds, and reproducibility notes
- Reviewer issues by severity and status
- Distinction between mathematical correctness, scope, wording, and publication readiness
- Version snapshot with the claims that changed

For the odd-support-filtration manuscript, a project template should include theorem inventory, coefficient/matrix verification, Sturm-bound certification, terminology definitions, application-scope claims, reviewer defects, and Lean-formalization candidates.

### E. Maker Studio and Collections

Use one flexible project template for software and another for open-ended exploration.

**Software template:** problem, user, next shippable slice, milestone, issue, test, decision, release, retrospective.

**Creative experiment template:** question, constraints, references, iterations, result, what to try next.

This supports Sigilize, network tools, Android projects, the Overwatch hero picker, D&D modules, and fragrance experiments without hard-coding a separate app feature for each interest.

## 6. Roadmap

### Phase 0 — Product Contract (2–3 days)

**Goal:** Freeze the problem before writing app code.

Deliverables:

- One-page product contract using the five core questions in Section 1
- Confirmed MVP and explicit Not Now list
- Initial privacy/data-classification policy
- Five paper or low-fidelity screen sketches
- A seed dataset containing current areas, five leadership functions, and 8–12 representative projects

Exit criteria:

- Every proposed MVP feature supports a daily or weekly behavior.
- No feature exists merely to warehouse information.

### Phase 1 — Local-First Foundation (Weeks 1–2)

**Goal:** Produce an app that can already replace a basic personal task list.

Build:

- Kotlin/Jetpack Compose app shell
- Today, Inbox, Plan, Areas, and Settings screens
- Areas, outcomes, projects, commitments, and basic notes
- Fast capture and triage
- Search and filters
- Local database, migrations, seed data, and JSON export/import
- Dark theme, dynamic type, accessibility labels, and tablet-safe layouts

Exit criteria:

- Capture takes under ten seconds.
- The app works fully in airplane mode.
- Export → delete test data → import restores an equivalent dataset.
- A schema migration test protects existing data.

### Phase 2 — Accountability Engine (Weeks 3–4)

**Goal:** Make the app meaningfully different from a task manager.

Build:

- Morning contract and Daily Rule of Three
- Focus mode and quick completion
- Evening close with explicit rollover reasons
- Weekly review and generated weekly brief
- Waiting/delegation view
- WIP-limit warnings
- Quiet reminders and a home-screen widget
- Drift indicators: repeated rollover, neglected area, blocked project, and missing next action

Exit criteria:

- Jude completes five morning/evening cycles and one weekly review using only the app.
- The app can distinguish “I failed to do this” from “I consciously changed the plan.”
- Notifications remain useful with no more than three default reminder classes.

### Phase 3 — Leadership Console (Weeks 5–6)

**Goal:** Support the VP transition and create visible operating discipline.

Build:

- Five preconfigured functional scorecards
- Leadership outcome, risk, signal, and decision views
- Delegation ledger
- 1:1 agenda and commitment capture
- “VP altitude” weekly reflection
- Executive weekly-summary export to Markdown
- Work/personal privacy partition and biometric lock option

Exit criteria:

- A real weekly leadership review can be run from the app.
- Every commitment made in a 1:1 can appear in either Jude’s actions or Waiting.
- The exported brief can be safely edited and used in the company’s approved environment.

### Phase 4 — Writing Desk and Research Lab (Weeks 7–9)

**Goal:** Support serious intellectual work without trying to replace specialist editors.

Build:

- Writing and mathematical-research project templates
- Claims, sources, issues, and artifact links
- Revision-pass workflow
- Claim-confidence and verification state
- Reviewer issue board
- Version snapshot and change summary
- Markdown export for project state and unresolved issues

Exit criteria:

- One essay and the modular-forms manuscript can each be represented without awkward task abuse.
- A reviewer issue can be traced to a claim, artifact/version, resolution, and verification step.
- The app stores links and project state while the actual manuscript remains in its proper authoring environment.

### Phase 5 — People, Life Maintenance, and Studio Templates (Week 10)

**Goal:** Extend the system beyond work while preserving humane boundaries.

Build:

- People & Presence view
- Important dates, promised follow-ups, and intentional-time prompts
- Life-maintenance routines
- Software-build and creative-experiment templates
- Collections for inactive interests and reference material

Exit criteria:

- Family reminders feel supportive in a one-week trial, not transactional.
- A new idea can be captured into Collections without becoming an active project.
- A technical or creative project can be activated from a template in under one minute.

### Phase 6 — Integrations, Security, and Polish (Weeks 11–12)

**Goal:** Make the app dependable enough for daily use.

Build:

- Read-only calendar overlay
- Android share target and deep links
- Encrypted backup through a user-selected document location
- Biometric app lock and automatic lock timeout
- Notification reliability and reboot testing
- Import/export versioning and recovery flow
- Performance, accessibility, and battery-use review
- First-run setup that preloads only the domains Jude chooses

Exit criteria:

- No network connection is required for core use.
- A lost-device scenario has a documented recovery path.
- Reminder behavior survives reboot and delayed execution.
- Work data follows the classification rules below.

### Phase 7 — Personal Pilot and Release (Weeks 13–14)

**Goal:** Prove that Lattice improves behavior rather than merely adding another system to maintain.

Pilot protocol:

- Use Lattice as the sole daily-commitment and weekly-review system for 14 days.
- Keep calendars and source documents in their existing systems.
- Log friction immediately through the app’s own Inbox.
- Make only one product change per day during the pilot.

Release gate:

- At least 10 of 14 daily closes completed
- Both weekly reviews completed in 15 minutes or less
- At least 80% of explicit promises have an owner and next date
- No active project lacks a next action or documented blocker
- Capture median below ten seconds
- Zero data-loss or notification-critical defects

## 7. MVP Scope

### Must ship

- Inbox and rapid capture
- Areas, outcomes, projects, commitments, and Waiting
- Daily Rule of Three
- Morning contract and evening close
- Weekly review and brief
- Leadership function cards and delegation ledger
- Writing, research, software, and creative templates
- Search, local backup, export/import, app lock, and quiet reminders

### Explicitly not in the MVP

- A general-purpose AI chat interface
- Automatic email or Slack ingestion
- Two-way calendar editing
- Full manuscript editing or citation management
- Full CRM, OKR, habit, finance, health, or household-management suites
- Shared family accounts
- Social features or public profiles
- Gamified streak pressure
- Direct storage of customer records, employee-performance notes, credentials, or regulated company data

## 8. Technical Direction

Use a native, offline-first Android architecture:

- **Language/UI:** Kotlin and Jetpack Compose
- **Structure:** Single-activity app with clear UI and data layers; add a domain/use-case layer only when shared business rules justify it
- **Local source of truth:** Room over SQLite
- **Reactive state:** Kotlin coroutines and Flow exposed through ViewModels
- **Preferences:** DataStore
- **Persistent background work:** WorkManager for reminders, maintenance, and backup jobs that do not require exact-to-the-minute alarms
- **Security:** Android Keystore-backed encryption keys, biometric gate, and least-privilege access
- **Files:** Android Storage Access Framework for explicit backup/export locations
- **Sync:** None in the MVP; design stable IDs and change timestamps so encrypted sync can be added later

This direction follows current Android guidance: Compose is the recommended modern UI toolkit; official architecture guidance recommends distinct UI and data layers; offline-first apps should use a local data source as the source of truth; Room is recommended over direct SQLite APIs; WorkManager persists scheduled background work across reboots; and Android Keystore keeps cryptographic key material harder to extract. See the official Android references in Section 12.

### Suggested package boundaries

- `core/model`
- `core/database`
- `core/security`
- `core/designsystem`
- `feature/today`
- `feature/plan`
- `feature/areas`
- `feature/leadership`
- `feature/studio`
- `feature/review`
- `feature/settings`

Start with packages in one application module. Split Gradle modules only when build time, ownership, or test isolation creates a real need.

### Testing priorities

1. Data migrations and backup/import round trips
2. Accountability rules and WIP-limit behavior
3. Date, recurrence, and time-zone behavior
4. Notification scheduling and reboot recovery
5. Work/personal privacy partition
6. Core Compose navigation and accessibility
7. Exported Markdown correctness

## 9. Privacy and Work-Personal Firewall

The app should assign every area one of three profiles:

| Profile | Suitable data | Rule |
| --- | --- | --- |
| **Personal** | Family plans, personal projects, reflections, routines | Encrypted locally; included in user-controlled backup |
| **Work—minimal** | High-level outcomes, generic reminders, meeting titles, Jude’s own commitments | Store only what company policy permits; exclude confidential detail from personal backups when needed |
| **Restricted / link-only** | Customer information, sensitive metrics, employee matters, contracts, credentials, regulated or confidential documents | Do not store content; keep only a neutral reminder or approved link in the proper work environment |

Specific safeguards:

- Default Leadership Console notes to “Work—minimal.”
- Offer a separate export for work content.
- Never send work content to a personal cloud or external AI service by default.
- Do not store passwords, API keys, customer records, or sensitive direct-report assessments.
- Require explicit confirmation before changing an area’s privacy profile.

## 10. AI Roadmap—Only After the Core Works

AI should reduce clerical work, not become the operating system.

### Valuable later capabilities

- Turn a messy Inbox capture into suggested outcomes, actions, or notes
- Draft a weekly executive brief from selected work-safe entries
- Detect repeated rollover and propose a smaller next action
- Identify collisions among active projects and calendar capacity
- Summarize changes between research or manuscript snapshots
- Suggest which claims lack linked evidence
- Prepare a reviewer-response checklist

### Guardrails

- AI suggestions are drafts, never silent mutations.
- Show which entries were used to generate an answer.
- Keep Personal and Work contexts separate.
- Prefer on-device processing for private classification and summarization when practical.
- Require an approved enterprise route before processing company data externally.

## 11. Product Success Measures

Avoid vanity metrics such as total tasks created. Measure whether the app makes commitments more honest and attention more intentional.

### Weekly measures

- Daily close completion rate
- Weekly review completion and duration
- Percentage of explicit promises with an owner and next date
- Percentage of active projects with a next action or blocker
- Repeated-rollover count
- Number of active projects over the WIP limit
- Median capture time
- Number of projects deliberately paused, completed, or abandoned

### Qualitative questions

- Did the app make a neglected responsibility visible soon enough to act?
- Did it help Jude operate at VP altitude?
- Did it preserve time for family and meaningful intellectual or creative work?
- Did the review create a real decision?
- Did maintaining the app take less effort than the confusion it removed?

## 12. Official Android References

- [Recommendations for Android architecture](https://developer.android.com/topic/architecture/recommendations)
- [Build an offline-first app](https://developer.android.com/topic/architecture/data-layer/offline-first)
- [Save data locally with Room](https://developer.android.com/training/data-storage/room)
- [Schedule persistent work with WorkManager](https://developer.android.com/develop/background-work/background-tasks/persistent)
- [Android Keystore system](https://developer.android.com/privacy-and-security/keystore)

## 13. The First Build Sprint

The best next move is a three-day design sprint before scaffolding the application:

### Day 1: Inventory and cut

- List all current areas and projects.
- Classify every project as Active, Maintaining, Incubating, Someday, or Archived.
- Select representative seed data.
- Write the MVP Not Now list.

### Day 2: Paper prototype

- Sketch Today, Inbox, Plan, Leadership Console, and Weekly Review.
- Run one real morning plan and evening close on paper.
- Remove every field not used in the test.

### Day 3: Technical contract

- Freeze the initial Room schema.
- Define export JSON and Markdown formats.
- Define privacy profiles and backup rules.
- Write acceptance tests for capture, daily close, weekly review, migration, and restore.

Only then begin Phase 1. The app’s first valuable artifact is not its code; it is a precise agreement about what Jude will do differently because the app exists.