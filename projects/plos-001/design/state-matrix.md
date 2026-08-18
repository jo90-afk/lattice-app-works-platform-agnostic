# Release-One User-Visible State Matrix: Personal Life OS

**Revision:** 0.3  
**Status:** Owner draft  
**Owner:** Experience Lead — WO-006-R1  
**Last updated:** 2026-08-06  
**Verification and approval:** Quality verification and Gate 2 approval remain pending.

## Frozen basis

| Input | Frozen version/status | SHA-256 |
| --- | --- | --- |
| work/gate-decisions/GATE-1-principal.md | v1.0; ACCEPT | 8ade3617bb88123d1aededb0854718964b1b2e394ebfe23697f474178830f65b |
| product/acceptance-map.md | Gate 1 accepted v0.1 | 8b5fdb38cbe036f5ddeb4194b111cc85dc4eb4d39fae8ae3084da7db20c934d3 |
| design/journeys.md | revision 0.2; Quality-verified/Product-concurred | acd706dd5092e1aeabbbba267bcfd97e7d50b4ba07353b67208f95052f396019 |
| work/verifications/WO-004-R1-quality.md | SATISFIED/PASS | d50c9b136d5a06ca6b9629b7c5cae5bc7b519178fa90c2d425d9a03cc28c0bfa |
| work/reviews/WO-004-R1-product.md | CONCUR | 93d7dfaf5d19a6aae687653e1d16af1f0b1bb711632c6070801fda183336c09e |
| design/information-architecture.md | revision 0.4; Quality-verified/Product-concurred | d267b2b60f308939bad6fa0a03ce475790014f0fcb7f6babb4fe28fb145bd8b2 |
| work/verifications/WO-005-R3-quality.md | SATISFIED/PASS | df817434fe4e77cec36181a7b1c7dd904a498ea36609be25ec917603d2cefe51 |
| work/reviews/WO-005-R3-product.md | CONCUR | 112a7b840e323218bf0ef0e46974bcdfcdb2b9d382d2fe2bf42908885583515b |
| design/state-matrix.md | blocked revision 0.2 remediation baseline | bfd1efa86c5df8ba51804a070234deafb25dafb8c0823b9dec92ef65e3ea8a79 |
| work/handoffs/WO-006-C1-experience.md | revision 0.2 owner handoff | 09937ab8adb8d02a4c4d2b107f05daab1b0f8388d98c4b2beb693b6b1d6cd349 |
| work/verifications/WO-006-C1-quality.md | NOT_SATISFIED/BLOCK; F-001 | 38463428f927f7bc1a310c5f0d596bfb6acd8be85f9c9716e970f2b110d2b1ee |
| work/orders/WO-006-C1.md | complete current claim set | bca942616c5cef240c862482327ebcad5a731ac9d0d5da3546acfd527f38cd73 |
| work/legacy-2.0/orders/WO-006.md | preserved 13-criterion specification | a8eec843fa90e0005b7741e39108d45c8988d37647bd44878fb9b557109e81cc |

This matrix specifies observable behavior, not storage, detection, resumption, permission, notification, file, or platform mechanisms. Examples are synthetic. Ranges are inclusive. Text below is semantic message intent plus action labels only; exact wording, tone, variants, notification categories, triggers, and defaults remain with WO-007.

## Identifier and presentation contract

- Stable IDs use SM-{family}-{number}. Family numbers are never reused; retired IDs remain reserved and are named in the revision change record.
- Required columns are destination/flow, trigger, visible information/status, available actions, transition/exit, data or consequence effect, and exact J/R/AC trace.
- State classes are H happy/ready, E first-use/empty, L preparing/in-progress, O offline, S stale/outcome-unknown, F error/no-effect, P permission-denied, C conflict, X cancellation, I interrupted/re-entry, and D destructive/external or discard confirmation.
- Status and actions must be perceivable without relying only on color, motion, timing, or a notification. Use visible text semantics and a programmatic status name; detailed Android accessibility rules remain with WO-008.
- Missing owner, follow-up, close, attention, next move, or disposition is shown as **Needs a decision**. Release one has no AI, recommendation, confidence, score, inference, or generated conclusion.
- Preparing is never displayed as empty. Completed is shown only after the outcome is established. Error/no-effect states name what remains unchanged and offer **Retry** where safe plus a safe exit.
- Time, omission, Back, navigation, interruption, dismissal, or silence never resolves, reconsiders, releases, exports, restores, replaces, or deletes. Completed decisions stay visible; unfinished decisions stay unresolved.
- **Keep editing** and **Discard changes** are required when leaving would discard entered but uncompleted changes. Dismissal means keep editing; discard changes only after explicit confirmation.
- Offline core use exposes no sign-in, sync, network retry, Calendar/Keep access, AI processing, upload, remote analytics, telemetry, or later-connectivity action.

## Not-applicable reason legend

| Code | Behavior-based reason |
| --- | --- |
| NA-1 | No remote, shared, synchronized, or multi-user record exists; remote stale and multi-user conflict cannot arise. |
| NA-2 | The destination requests no platform, external-account, Calendar, Keep, or location permission. |
| NA-3 | The destination performs no cancellable or confirmable consequence and contains no uncompleted editor change. |
| NA-4 | The destination has no asynchronous consequence whose outcome could remain unknown after interruption. |
| NA-5 | True absence is not a valid result for this decision/status destination; absence is handled at its owning collection or pre-initiation state. |
| NA-6 | No destructive replacement or external movement occurs in this flow; ordinary completion needs no consequence confirmation. |
| NA-7 | No permission is involved in full deletion; denial must not be invented as a gate. |
| NA-8 | Export never replaces app-managed information, so no merge or replacement conflict exists. |
| NA-9 | Full deletion acts on one app-managed set; no shared-version conflict or merge is accepted. |

## Destination and state-class coverage

Every omitted class is listed with a reason code. “Applicable” points to exact matrix families below.

| Verified destination | Applicable classes / state families | Explicitly not applicable |
| --- | --- | --- |
| T-01 Today | H,E,L,O,F,I — COR, DAY | S,C: NA-1; P: NA-2; X,D: NA-3 |
| T-02 Form daily intention | H,E,L,O,F,X,I,D — COR, DAY | S,C: NA-1; P: NA-2 |
| T-03 Close day | H,E,L,O,F,X,I,D — COR, DAY | S,C: NA-1; P: NA-2 |
| R-01 Reflect | H,E,L,O,F,I — COR, REF | S,C: NA-1; P: NA-2; X,D: NA-3 |
| R-02 Reflection — Attention | H,E,L,O,F,X,I,D — COR, REF | S,C: NA-1; P: NA-2 |
| R-03 Reflection — Promises & waiting | H,E,L,O,F,X,I,D — COR, REF | S,C: NA-1; P: NA-2 |
| R-04 Reflection — Personal projects | H,E,L,O,F,X,I,D — COR, REF | S,C: NA-1; P: NA-2 |
| R-05 Reflection summary | H,E,L,O,F,I — COR, REF | S,C: NA-1; P: NA-2; X,D: NA-3 |
| C-01 Context | H,E,L,O,F — COR, CTX | S,C: NA-1; P: NA-2; X,I,D: NA-3 |
| C-02 Commitments & intentions | H,E,L,O,F — COR, CTX | S,C: NA-1; P: NA-2; X,I,D: NA-3 |
| C-03 Commitment entry/revision | H,E,L,O,F,X,I,D — COR, CTX | S,C: NA-1; P: NA-2 |
| C-04 Promises & waiting | H,E,L,O,F — COR, CTX | S,C: NA-1; P: NA-2; X,I,D: NA-3 |
| C-05 Promise/waiting entry/review | H,E,L,O,F,X,I,D — COR, CTX | S,C: NA-1; P: NA-2 |
| C-06 Personal projects | H,E,L,O,F — COR, CTX | S,C: NA-1; P: NA-2; X,I,D: NA-3 |
| C-07 Project entry/decision | H,E,L,O,F,X,I,D — COR, CTX | S,C: NA-1; P: NA-2 |
| S-01 Settings & data | H,O,I — NOT, EXP, RST, DEL, OFF | E,L,F: NA-5; S,C: NA-1; P: NA-2; X,D: NA-3 |
| S-02 Notifications, if offered | H,E,L,O,F,P,X,I — NOT, OFF | S,C: NA-1; D: NA-6 |
| S-03 Export or backup | H,E,L,O,S,F,P,X,I,D — EXP | C: NA-8 |
| S-04 Restore | H,E,L,O,S,F,P,C,X,I,D — RST, OFF | None |
| S-05 Delete all app data | H,E,L,O,S,F,X,I,D — DEL, OFF | P: NA-7; C: NA-9 |

## Cross-core operating states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-COR-01 | T-01–T-03, R-01–R-05, C-01–C-07 | Established information is being prepared | **Preparing current information**; not empty and no remote-service claim | **Back** where nested | Same owning destination when established; safe parent exit | Nothing changes while availability is unestablished | J-01–J-07; R-001–R-007; AC-R001-01–03, AC-R002-01–02, AC-R003-01–03, AC-R004-01–03, AC-R005-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-COR-02 | T-01–T-03, R-01–R-05, C-01–C-07 | Device has no network or external account | **Available offline**; Calendar and Keep remain separate | Every normal core action; **Back** | Same route and outcome as connected context | Completed local decision is available; no external action now or when connectivity returns | J-01–J-07; R-001–R-007; AC-R001-01–03, AC-R002-02, AC-R003-01–03, AC-R004-03, AC-R005-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-COR-03 | Any core completion/revision | Attempt did not take effect | **Did not take effect**; last established context/decision named as unchanged | **Retry**, **Back** | Retry same deliberate action or exact origin | New entry is not current; prior information or unresolved status remains | J-01–J-07; R-001–R-007; AC-R001-01, AC-R002-01–02, AC-R003-01–03, AC-R004-01–03, AC-R005-01–03, AC-R006-01–03, AC-R007-01 |
| SM-COR-04 | C-03, C-05, C-07; editable T-02, T-03, R-02–R-04 | Back/navigation would discard uncompleted changes | **Uncompleted changes would be discarded** | **Keep editing**, **Discard changes** | Dismiss/keep returns to editor; confirmed discard returns exact origin | Established information unchanged; incomplete new work not current | J-01–J-07; R-001–R-007; AC-R001-01, AC-R002-01, AC-R003-03, AC-R004-03, AC-R005-01, AC-R006-01–02, AC-R007-01 |
| SM-COR-05 | Same editable destinations | Jude cancels before completion | **Change cancelled; prior status remains** | **Return**, **Edit again** | Exact origin; source weekly/daily stage remains resumable | No new context/decision; previously completed decisions remain | J-01–J-07; R-001–R-007; AC-R001-01, AC-R002-01, AC-R003-03, AC-R004-03, AC-R005-01, AC-R006-01–02, AC-R007-01 |
| SM-COR-06 | T-01 or R-01 re-entry | Daily close or reflection was interrupted | **Continue incomplete close/reflection**; completed and first unresolved decision distinguished | **Continue**, **Review completed decisions** | First unresolved applicable stage; normal primary exit | No decision disappears or is inferred; completed decisions remain | J-03, J-06, J-07; R-003, R-006, R-007; AC-R003-01–03, AC-R006-01–03, AC-R007-01 |

## Daily intention and close states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-DAY-01 | T-01 | First use; no intention or commitment context | **No daily intention formed**; optional context is absent, not required | **Form intention**, primary navigation | T-02 or another primary destination | Nothing is created; no setup, permission, account, or connection gate | J-01,J-02,J-07; R-001,R-002,R-007; AC-R001-02–03, AC-R002-01–02, AC-R007-01–03 |
| SM-DAY-02 | T-01 | Current or earlier unresolved intention exists | Chosen commitments and each **Unresolved**, **Resolved**, or **Reconsidered** outcome | **Close**, **Continue close**, **Review context** | T-03, C-01, or primary route | Merely viewing/time passing changes nothing | J-02,J-03,J-07; R-002,R-003,R-007; AC-R002-01–02, AC-R003-01–03, AC-R007-01–03 |
| SM-DAY-03 | T-02 | No recorded commitments | **No commitment context recorded; intention can still be formed** | **Add minimal context**, **Cancel** | C-03 then exact return, or T-01 | Optional absence remains; no inferred commitment | J-01,J-02,J-07; R-001,R-002,R-007; AC-R001-01–03, AC-R002-01–02, AC-R007-01–03 |
| SM-DAY-04 | T-02 | Jude is choosing/reviewing commitments | Proposed choices shown as **Not yet complete** | **Choose**, **Review**, **Complete**, **Cancel** | Complete to T-01; cancel to T-01 | Only explicit completion forms intention; earlier unresolved intention remains accounted for | J-02,J-07; R-002,R-007; AC-R002-01–02, AC-R007-01–03 |
| SM-DAY-05 | T-01 | Intention formation completed | **Current daily intention** identifies every chosen commitment | **Close**, **Review context** | T-03 or C-01 | Current choice becomes available; no external commitment | J-02,J-07; R-002,R-007; AC-R002-01–02, AC-R007-01–03 |
| SM-DAY-06 | T-03 | No current or unresolved intention exists | **Nothing to close**; not a completed close | **Return to Today** | T-01 | No fabricated decision or reflection | J-03,J-07; R-003,R-007; AC-R003-01, AC-R003-03, AC-R007-01–03 |
| SM-DAY-07 | T-03 | One or more intentions lack a close decision | Each intention **Unresolved**; short reflection and choice incomplete | **Add what happened**, **Resolve**, **Reconsider**, **Leave unresolved** | Continue item, summary, or exact origin | Skipped/unfinished item remains identifiable as unresolved | J-01,J-03,J-07; R-001,R-003,R-007; AC-R001-01–03, AC-R003-01–03, AC-R007-01–03 |
| SM-DAY-08 | T-03 | Jude explicitly chooses resolved and completes | Intention plus **Resolved** and short “what happened” intent | **Review**, **Next intention**, **Summary** | Next unresolved item or close summary | Explicit close decision recorded; no inference or external action | J-03,J-07; R-003,R-007; AC-R003-01, AC-R007-01–03 |
| SM-DAY-09 | T-03 | Jude explicitly chooses reconsidered and completes | Intention plus **Reconsidered**; visibly unlike resolved and still accounted for | **Review**, **Next intention**, **Summary** | Next unresolved item or close summary | Reconsideration remains context for later attention; not resolution | J-03,J-07; R-003,R-007; AC-R003-01–02, AC-R007-01–03 |
| SM-DAY-10 | T-03 | Close reaches summary with mixed outcomes | Counts/list semantics for resolved, reconsidered, unresolved; **Close incomplete** if any unresolved | **Review item**, **Complete available decisions**, **Return** | T-01 or R-02 origin; continuation remains when needed | Completed decisions persist; unresolved never disappears through omission | J-03,J-06,J-07; R-003,R-006,R-007; AC-R003-01–03, AC-R006-01–02, AC-R007-01–03 |

## Weekly reflection states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-REF-01 | R-01→R-05 | All three categories are truly empty | Each category **No recorded context needing a decision**; no false completion | **Begin**, **Continue**, **Complete reflection** | Normal sequence then R-01 | Empty reflection may complete without creating records or specialized workflow | J-06,J-07; R-006,R-007; AC-R006-01–03, AC-R007-01–03 |
| SM-REF-02 | R-01 | Earlier reflection incomplete | **Reflection incomplete** and first unresolved category identified | **Continue**, **Review completed decisions** | First unresolved R-02–R-04 stage | Existing decisions unchanged; unfinished work remains | J-06,J-07; R-006,R-007; AC-R006-01–02, AC-R007-01 |
| SM-REF-03 | R-02 Attention | Applicable intentions/commitments are reviewed | Changed/continued attention; intentions remain labeled resolved, reconsidered, or unresolved; missing choice **Needs a decision** | **Close intention**, **Add context**, **Continue**, **Leave incomplete** | T-03/C-03 exact return, or R-03 | Only completed Jude choice changes attention/close context | J-01,J-03,J-06,J-07; R-001,R-003,R-006,R-007; AC-R001-01–03, AC-R003-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-REF-04 | R-03 Promises & waiting | Applicable open items are reviewed | Owner and next follow-up together; either missing value **Needs a decision** | **Review item**, **Set owner/follow-up**, **Continue**, **Leave incomplete** | C-05 exact return, or R-04 | No message, calendar change, share, or service-visible action | J-01,J-04,J-06,J-07; R-001,R-004,R-006,R-007; AC-R001-01–03, AC-R004-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-REF-05 | R-04 Personal projects | Applicable projects are reviewed | Jude-chosen relevance; next move/pause/release or **Needs a decision**; no score/state/threshold | **Decide project**, **Continue**, **Leave incomplete** | C-07 exact return, or R-05 | No inferred disposition or automatic release | J-01,J-05,J-06,J-07; R-001,R-005,R-006,R-007; AC-R001-01–03, AC-R005-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-REF-06 | R-05 | One or more applicable decisions unfinished | Category summary distinguishes empty, completed, and needs-decision; **Reflection incomplete** | **Return to category**, **Exit and continue later** | Owning stage or R-01 continuation | Completed decisions remain; unresolved/omitted decisions remain visible | J-06,J-07; R-006,R-007; AC-R006-01–03, AC-R007-01 |
| SM-REF-07 | R-05→R-01 | All applicable decisions reviewed and Jude completes | Summary: attention changes, owner/follow-up, and project next move/pause/release for each applicable category | **Complete reflection**, **Revise category** | R-01 after completion; revision to owner stage | Completion changes no skipped item and creates no specialized record | J-06,J-07; R-006,R-007; AC-R006-01–03, AC-R007-01–03 |
| SM-REF-08 | R-02–R-05 | Category unavailable or change no effect | **Could not establish/complete this category**; not empty; last established decisions named | **Retry**, **Exit incomplete** | Same stage or R-01 continuation | Prior/unfinished status remains; false summary/completion forbidden | J-06,J-07; R-006,R-007; AC-R006-01–03, AC-R007-01 |

## Context, promise/waiting, and project states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-CTX-01 | C-01,C-02,C-04,C-06 | A collection has no established items | True absence by group; optional context not required | **Add minimal context**, **Back** | Owning entry destination or parent | Nothing inferred or created; core loop remains completable | J-01,J-04,J-05,J-07; R-001,R-004,R-005,R-007; AC-R001-01–03, AC-R004-01–02, AC-R005-01, AC-R007-01–03 |
| SM-CTX-02 | C-02 | Commitment/intention context exists | Current minimal context and identifiable unresolved/resolved/reconsidered outcomes; no archive | **Add**, **Revise**, **Today** | C-03, T-01, or C-01 | Viewing changes nothing | J-01–J-03,J-07; R-001–R-003,R-007; AC-R001-01–03, AC-R002-01–02, AC-R003-01–03, AC-R007-01–03 |
| SM-CTX-03 | C-03 | Jude enters/revises DI-01 or relevant optional DI-05 | Eligible minimal context; optional support identified as optional; proposal **Not yet current** | **Complete**, **Cancel**, **Back** | Exact origin C-02/T-02/T-03/R-02 | Completion makes Jude-chosen context current; no prohibited category requested | J-01–J-03,J-06,J-07; R-001–R-003,R-006,R-007; AC-R001-01–03, AC-R002-01–02, AC-R003-01–03, AC-R006-01, AC-R006-03, AC-R007-01–03 |
| SM-CTX-04 | C-04 | Open promise/waiting items exist | Item, owner, and next follow-up together; omissions **Need a decision** | **Add**, **Review**, **Back** | C-05 or C-01 | Viewing sends nothing and changes no external service | J-01,J-04,J-07; R-001,R-004,R-007; AC-R001-01–02, AC-R004-01–03, AC-R007-01–03 |
| SM-CTX-05 | C-05 | New/revised promise or waiting item incomplete | Ownership choice and revisit point; missing owner/follow-up visible | **Choose Jude**, **Choose another person**, **Set follow-up**, **Complete**, **Cancel** | Exact C-04/R-03 origin | Only completion updates minimal context; no external communication | J-01,J-04,J-06,J-07; R-001,R-004,R-006,R-007; AC-R001-01–03, AC-R004-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-CTX-06 | C-05 | Both owner and follow-up completed | **Jude owns next move** or **Waiting on another person**, plus next follow-up | **Revise**, **Return** | Exact origin | Owner/follow-up preserved without message, share, or calendar change | J-04,J-06,J-07; R-004,R-006,R-007; AC-R004-01–03, AC-R006-01–02, AC-R007-01–03 |
| SM-CTX-07 | C-06 | Relevant projects exist | Title plus next move, pause, conscious release, or **Needs a decision**; no product score | **Add**, **Review/decide**, **Back** | C-07 or C-01 | Viewing/time passage never disposes a project | J-01,J-05,J-07; R-001,R-005,R-007; AC-R001-01–02, AC-R005-01–03, AC-R007-01–03 |
| SM-CTX-08 | C-07 | Project lacks a Jude-completed decision | Minimal title/context and **Needs a decision** | **Advance**, **Pause**, **Consciously release**, **Cancel** | Review proposed outcome or exact origin | Cancellation/no effect preserves prior context and need for decision | J-01,J-05,J-06,J-07; R-001,R-005,R-006,R-007; AC-R001-01–03, AC-R005-01–03, AC-R006-01–03, AC-R007-01–03 |
| SM-CTX-09 | C-07 | Jude chooses advance | Proposed next move; credibility is Jude's judgment, never scored | **Complete**, **Revise**, **Cancel** | Exact origin after completion | Completed next move becomes visible; no fixed state assigned | J-05,J-06,J-07; R-005,R-006,R-007; AC-R005-01–03, AC-R006-01–02, AC-R007-01–03 |
| SM-CTX-10 | C-07 | Jude chooses pause | Proposed explicit **Paused** disposition; not time-based | **Complete**, **Change choice**, **Cancel** | Exact origin after completion | Pause is recorded only on completion; project is not deleted | J-05,J-06,J-07; R-005,R-006,R-007; AC-R005-01, AC-R005-03, AC-R006-01–02, AC-R007-01–03 |
| SM-CTX-11 | C-07 | Jude chooses conscious release | Proposed explicit **Consciously released** disposition with consequence distinct from full deletion | **Complete**, **Change choice**, **Cancel** | Exact origin after completion | Release only after completion; not full data deletion | J-05,J-06,J-07; R-005,R-006,R-007; AC-R005-01, AC-R005-03, AC-R006-01–02, AC-R007-01–03 |

## Notification states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-NOT-01 | S-01 | No release-one notification behavior is offered | Notifications control is absent; no permission prompt or degraded-core message | Core settings actions; **Return** | S-01 or origin | No notification behavior; core loop unchanged | J-08; R-008; AC-R008-01–03 |
| SM-NOT-02 | S-02 | Offered controls' effective status is being established | **Preparing effective controls**; not falsely enabled/disabled | **Back** | S-01 or stay until established | Prior effective behavior unchanged | J-08; R-008; AC-R008-01 |
| SM-NOT-03 | S-02 | At least one category is offered and status established | Every category's effective on/off, timing, quiet hours, frequency limit; category and all opt-out | **Change**, **Disable category**, **Disable all**, **Back** | Review proposed change or S-01 | Viewing changes nothing; core loop never gated | J-08; R-008; AC-R008-01–03 |
| SM-NOT-04 | S-02 | Jude proposes a control change | Proposed versus currently effective controls clearly distinguished | **Apply change**, **Cancel** | Completed state or prior controls | No effect until completed; cancel preserves prior state | J-08; R-008; AC-R008-01, AC-R008-03 |
| SM-NOT-05 | S-02 | Control change completes | **Controls changed** and complete effective scope visible | **Done**, **Change again** | S-01 or controls | Only selected notification behavior changes; planning data unchanged | J-08; R-008; AC-R008-01–03 |
| SM-NOT-06 | S-02 | Control change fails/does not take effect | **Change did not take effect**; prior effective controls shown | **Retry**, **Cancel** | Proposed flow or S-01 | Prior controls remain effective; no coercive consequence | J-08; R-008; AC-R008-01, AC-R008-03 |
| SM-NOT-07 | S-02 | Platform permission denied/unavailable | **Notifications cannot arrive**; core loop remains available; no pressure | **Review controls**, **Return** | S-02 or S-01 | No notifications arrive; planning data and access unchanged | J-08; R-008; AC-R008-01–03 |
| SM-NOT-08 | Offered notification | A later-defined routine trigger occurs within effective controls and permission | Routine, non-urgent semantic intent; no streak, shame, escalation, or punitive status | **Open**, **Dismiss**, **Notification controls** | Existing applicable destination, end presentation, or S-02 | Presentation alone changes no planning data or consequence | J-08; R-008; AC-R008-03 |
| SM-NOT-09 | Offered notification | Trigger occurs during quiet hours or outside frequency limit | No interruption; no duplicate/escalation; any later presentation only if completed controls allow | None at trigger time | No route forced | No data/status change and no missed-action penalty | J-08; R-008; AC-R008-01, AC-R008-03 |
| SM-NOT-10 | Offered notification | Jude dismisses or ignores | Presentation ends; underlying item remains unchanged | Optional normal app routes later | No hidden inbox required; no completion inferred | No resolve/reconsider/disposition/export/restore/delete/external action | J-08; R-008; AC-R008-03 |
| SM-NOT-11 | S-02 | Category or all opt-out completes | Effective disabled scope visible; core routes explicitly remain available | **Done**, **Change controls** | S-01 or S-02 | Notifications in scope cease; no streak/shame/penalty | J-08; R-008; AC-R008-02–03 |

## Settings and data offline states — F-001 remediation

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-OFF-01 | S-01 Settings & data | S-01 is opened while the device has no network or external account | **Settings & data available offline**; Today, Reflect, and Context remain available; notification controls and full deletion remain reachable; export and restore identify availability of Jude-chosen destinations or backups only in their owning states, without implying connectivity or an account | **Notifications** if offered, **Export or backup**, **Restore**, **Delete all app data**, applicable **Review operation status**, **Return to origin** | S-02, S-03, S-04, S-05, or the exact primary origin; status review opens the owning view without starting or repeating an operation | Viewing or returning changes nothing; loss or return of connectivity starts no operation, account flow, upload, synchronization, or other external action | J-08–J-11; R-008–R-011; AC-R008-01–03, AC-R009-01–03, AC-R010-01–03, AC-R011-01–03 |
| SM-OFF-02 | S-02 Notifications, if offered | Jude reviews or changes offered notification controls while the device has no network or external account | **Notification controls available offline**; every last-established effective category, timing, quiet hours, frequency limit, category opt-out, and complete opt-out remains visible; offline makes no delivery claim and is not presented as permission denial | **Change**, **Apply change**, **Disable category**, **Disable all**, **Cancel**, **Back**; normal core routes remain available | Proposed change uses SM-NOT-04; established completion uses SM-NOT-05 or SM-NOT-11; no effect uses SM-NOT-06; permission denial uses SM-NOT-07 only when separately established; Back returns to S-01 | Viewing or cancellation preserves prior effective controls; only an established completed change affects selected notification behavior; planning data and core access remain unchanged, with no external communication, penalty, pressure, or inferred consent | J-08; R-008; AC-R008-01–03 |
| SM-OFF-03 | S-04 Restore | S-04 is opened, or an already confirmed restore is active, while the device has no network or external account | **Restore status available offline**; an available Jude-chosen backup can be selected and progress can continue, while an unavailable selection is identified as **Restore cannot proceed; not started**; possible replacement still shows current information, selected backup, and the explicit replacement consequence; after confirmation, any unestablished result is **Outcome not yet established** with completed/no-effect possibilities | Before confirmation: **Choose backup**, **Choose another backup**, applicable **Proceed with restore** or **Confirm replacement**, **Cancel**; after confirmation: **Review status**, **Return to settings**; a new attempt is available only after established no effect | Available selection with no existing information uses SM-RST-05; possible replacement uses SM-RST-06; explicit proceed/confirmation enters SM-RST-07; unavailable selection uses SM-RST-03, or SM-RST-04 only when access denial is separately established; post-confirmation uncertainty uses SM-RST-08; established outcomes use SM-RST-09 or SM-RST-10 | Selection, unavailability, and cancellation leave existing information unchanged; replacement requires the applicable explicit confirmation and an established completed outcome; unknown status asserts neither replacement nor no effect, and no attempt repeats silently | J-10; R-010; AC-R010-01–03 |
| SM-OFF-04 | S-05 Delete all app data | S-05 is opened, or confirmed deletion is active, while the device has no network or external account | **Full deletion available offline** with no connectivity, account, or permission gate; before confirmation, the full consequence and the fact that Jude-created external copies remain are visible; after confirmation, status is in progress, an established terminal result, or **Outcome not yet established** with completed/no-effect possibilities | Before confirmation: **Start full deletion**, **Confirm full deletion**, **Cancel**; after confirmation: **Review status**, **Return to settings**; a new attempt is available only after established no effect | Pre-initiation and disclosure use SM-DEL-01 and SM-DEL-03; cancellation/no confirmation uses SM-DEL-04; explicit confirmation enters SM-DEL-05; interruption or uncertainty uses SM-DEL-06; established outcomes use SM-DEL-07 or SM-DEL-08 | All app-managed personal data remains available until distinct explicit confirmation and established completion; cancellation/no confirmation leaves it unchanged; unknown status asserts neither deletion nor no effect; external copies remain and no attempt repeats silently | J-11; R-011; AC-R011-01–03 |

## Export or backup states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-EXP-01 | S-01→S-03 | Before explicit initiation | Export/backup purpose; no action underway | **Start export/backup**, **Cancel** | S-03 scope or S-01 | No copy and no data leaves device | J-09; R-009; AC-R009-01–03 |
| SM-EXP-02 | S-03 | No supported DI-01–DI-05 data eligible | **Nothing supported to copy** | **Return** | S-01 | No copy; prohibited/work data never added to make one | J-09; R-009; AC-R009-01, AC-R009-03 |
| SM-EXP-03 | S-03 | Initiated; destination choice not completed | Eligible supported scope, exclusions, non-sync and non-recurring behavior, external-copy consequence, and notice that completing destination choice authorizes one attempt | **Choose destination**, **Cancel** | Completed destination choice proceeds to SM-EXP-07; leaving, Back, cancellation, denial, or interruption returns safely with no attempt | No copy or data movement before completed destination choice; app-managed data remains unchanged | J-09; R-009; AC-R009-01–03 |
| SM-EXP-04 | S-03 | Chosen location unavailable offline | **Destination unavailable; export not started**; core loop unaffected | **Choose another destination**, **Cancel** | Selection or S-01 | App-managed data unchanged; no copy claimed | J-09; R-009; AC-R009-01–02 |
| SM-EXP-05 | S-03 | Destination access denied | **Access denied; export did not start** | **Choose another destination**, **Retry access**, **Cancel** | Selection or S-01 | No product-directed copy; app-managed data unchanged | J-09; R-009; AC-R009-01–02 |
| SM-EXP-07 | S-03 | Jude deliberately completes destination choice, authorizing one attempt | **Export/backup in progress** at the chosen destination; completion not claimed | **Review status** | Stay in owning status; interruption re-enters SM-EXP-08 | Chosen destination authorizes this attempt only; copy outcome not yet claimed; no automatic repeat | J-09; R-009; AC-R009-02–03 |
| SM-EXP-08 | App re-entry/S-01→S-03 | Destination-authorized/in-progress export interrupted; outcome unestablished | Operation and Jude-chosen destination identified; **Outcome not yet established**; completed and no-effect remain possible outcomes | **Review status**, **Return to settings** | S-03 status or S-01; never starts or repeats an attempt | Neither copy nor no-copy asserted; app-managed data remains unchanged; no repeat | J-09; R-009; AC-R009-01–03 |
| SM-EXP-09 | S-03 | Completion established | **Export/backup completed** and Jude-chosen destination identified | **Done** | S-01 | Supported-data copy exists at chosen destination; app data remains | J-09; R-009; AC-R009-02–03 |
| SM-EXP-10 | S-03 | No-effect outcome established | **Did not take effect**; no copy claimed | **Start a new attempt**, **Choose another destination**, **Done** | New attempt requires fresh initiation, disclosure, and completed destination choice; or return to S-01 | Prior choice is not standing authorization; app-managed data remains unchanged; no silent retry | J-09; R-009; AC-R009-01–03 |

## Restore states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-RST-01 | S-01→S-04 | Before explicit initiation/selection | Restore purpose; selection alone will not replace information | **Start restore**, **Cancel** | Selection or S-01 | Existing app-managed information unchanged | J-10; R-010; AC-R010-01–03 |
| SM-RST-02 | S-04 | Chosen backup is being assessed | **Preparing selected backup status**; not empty/success | **Cancel** | Stay or S-01 | No replacement | J-10; R-010; AC-R010-01 |
| SM-RST-03 | S-04 | Selection unavailable, unreadable, or ineligible | **Restore cannot proceed; did not take effect** | **Choose another backup**, **Cancel** | Selection or S-01 | Existing information unreplaced | J-10; R-010; AC-R010-01, AC-R010-03 |
| SM-RST-04 | S-04 | Chosen-location access denied | **Access denied; restore did not start** | **Retry access**, **Choose another backup**, **Cancel** | Selection or S-01 | Existing information unreplaced; core loop available | J-10; R-010; AC-R010-01, AC-R010-03 |
| SM-RST-05 | S-04 | Eligible backup; no existing app information | Selected backup and **No existing information to replace**; explicit proceed still required | **Proceed with restore**, **Cancel** | Progress or S-01 | Cancel changes nothing; no destructive replacement claimed | J-10; R-010; AC-R010-01, AC-R010-03 |
| SM-RST-06 | S-04 | Eligible backup could replace existing information | Current information versus selected backup; explicit replacement consequence | **Confirm replacement**, **Cancel** | Progress only on explicit confirmation; else S-01 | Back/dismiss/silence/cancel leaves existing information unreplaced; no merge | J-10; R-010; AC-R010-01–03 |
| SM-RST-07 | S-04 | Proceed/confirmation accepted | **Restore in progress**; replacement not yet claimed | **Review status** | Owning status; interruption re-enters SM-RST-08 | Existing/replacement outcome not yet claimed; no repeat | J-10; R-010; AC-R010-01–02 |
| SM-RST-08 | App re-entry/S-01→S-04 | Confirmed/in-progress restore interrupted; outcome unestablished | Operation/backup identified; **Outcome not yet established**; possible completed/no-effect outcomes | **Review status**, **Return to settings** | S-04 or S-01; never restarts restore | Neither replacement nor no-effect asserted; retry unavailable | J-10; R-010; AC-R010-01–03 |
| SM-RST-09 | S-04 | Completion established | **Restore completed**; replacement consequence remains explicit if applicable | **Continue to Today**, **Done** | T-01 or S-01 | Chosen backup restored; any replacement followed confirmation | J-10; R-010; AC-R010-01–02 |
| SM-RST-10 | S-04 | No-effect outcome established | **Restore did not take effect**; existing information unreplaced | **Start a new attempt**, **Choose another backup**, **Done** | New attempt repeats selection/disclosure/confirmation or S-01 | Existing information unchanged; no silent retry | J-10; R-010; AC-R010-01–03 |

## Full deletion states

| State ID | Destination / flow | Trigger | Visible intent or status | Actions | Transition / exit | Data or consequence effect | Exact trace |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SM-DEL-01 | S-01→S-05 | Before explicit initiation | Full deletion purpose; ordinary use/time/notification/restore cannot start it | **Start full deletion**, **Cancel** | Disclosure or S-01 | All app-managed data remains | J-11; R-011; AC-R011-01–03 |
| SM-DEL-02 | S-05 | No app-managed personal data is available | **No app-managed data to delete**; not a new deletion success | **Return** | S-01 or empty T-01 | No additional deletion; external copies unaffected | J-11; R-011; AC-R011-01, AC-R011-03 |
| SM-DEL-03 | S-05 | Explicit initiation; before confirmation | All app-managed personal data will become unavailable; prior Jude-created copies remain outside; destructive consequence | **Confirm full deletion**, **Cancel** | Progress only on distinct explicit confirm; else S-01 | Back/dismiss/silence/time/cancel leaves all data available | J-11; R-011; AC-R011-01–03 |
| SM-DEL-04 | S-05 | Jude cancels or does not confirm | **Deletion cancelled/not confirmed; data remains available** | **Done** | S-01 | No destructive effect and no later silent continuation | J-11; R-011; AC-R011-02–03 |
| SM-DEL-05 | S-05 | Explicit confirmation accepted | **Deletion in progress**; completion not claimed | **Review status** | Owning status; interruption re-enters SM-DEL-06 | Availability outcome not yet claimed; no repeat | J-11; R-011; AC-R011-01 |
| SM-DEL-06 | App re-entry/S-01→S-05 | Confirmed/in-progress deletion interrupted; outcome unestablished | Operation identified; **Outcome not yet established**; possible completed/no-effect outcomes | **Review status**, **Return to settings** | S-05 or S-01; no new attempt/repeat | Neither deletion nor unchanged-data claim; retry unavailable | J-11; R-011; AC-R011-01–03 |
| SM-DEL-07 | S-05 | Completion established | **Full deletion completed**; app-managed personal data unavailable; external copies unaffected | **Continue to Today** | Empty T-01 | App-managed personal data removed from product only | J-11; R-011; AC-R011-01 |
| SM-DEL-08 | S-05 | No-effect outcome established | **Deletion did not complete**; data remains available | **Start a new deletion attempt**, **Done** | New attempt requires fresh initiation, disclosure, confirmation; or S-01 | No silent retry; app-managed data remains available | J-11; R-011; AC-R011-01–03 |

## State-family, journey, and destination map

| State family | Verified destinations | Supported journeys | Requirements |
| --- | --- | --- | --- |
| SM-COR-* | T-01–T-03, R-01–R-05, C-01–C-07 | J-01–J-07 | R-001–R-007 |
| SM-DAY-* | T-01–T-03 | J-01,J-02,J-03,J-06,J-07 | R-001,R-002,R-003,R-006,R-007 |
| SM-REF-* | R-01–R-05 plus nested T-03,C-03,C-05,C-07 | J-01,J-03,J-04,J-05,J-06,J-07 | R-001,R-003,R-004,R-005,R-006,R-007 |
| SM-CTX-* | C-01–C-07 plus exact T-02,T-03,R-02–R-04 origins | J-01–J-07 | R-001–R-007 |
| SM-NOT-* | S-01,S-02 and offered presentation routes | J-08 | R-008 |
| SM-OFF-* | S-01,S-02,S-04,S-05 | J-08–J-11 | R-008–R-011 |
| SM-EXP-* | S-01,S-03 | J-09 | R-009 |
| SM-RST-* | S-01,S-04 | J-10 | R-010 |
| SM-DEL-* | S-01,S-05 | J-11 | R-011 |

## Exact acceptance ownership trace

This table, not repeated coverage references in state rows, owns each of the 32 criteria exactly once.

| Acceptance owner | Exact acceptance IDs | Owning journey | Primary state families / destinations |
| --- | --- | --- | --- |
| R-001 | AC-R001-01, AC-R001-02, AC-R001-03 | J-01 | COR, DAY, REF, CTX / T-01–T-03, R-02–R-05, C-01–C-07 |
| R-002 | AC-R002-01, AC-R002-02 | J-02 | DAY, CTX, COR / T-01,T-02,C-02,C-03 |
| R-003 | AC-R003-01, AC-R003-02, AC-R003-03 | J-03 | DAY, REF, CTX, COR / T-01,T-03,R-02,R-05,C-02,C-03 |
| R-004 | AC-R004-01, AC-R004-02, AC-R004-03 | J-04 | CTX, REF, COR / C-04,C-05,R-03 |
| R-005 | AC-R005-01, AC-R005-02, AC-R005-03 | J-05 | CTX, REF, COR / C-06,C-07,R-04 |
| R-006 | AC-R006-01, AC-R006-02, AC-R006-03 | J-06 | REF, DAY, CTX, COR / R-01–R-05,T-03,C-03,C-05,C-07 |
| R-007 | AC-R007-01, AC-R007-02, AC-R007-03 | J-07 | COR plus DAY, REF, CTX / T-01–T-03,R-01–R-05,C-01–C-07 |
| R-008 | AC-R008-01, AC-R008-02, AC-R008-03 | J-08 | NOT / S-01,S-02,offered presentation route |
| R-009 | AC-R009-01, AC-R009-02, AC-R009-03 | J-09 | EXP / S-01,S-03 |
| R-010 | AC-R010-01, AC-R010-02, AC-R010-03 | J-10 | RST / S-01,S-04 |
| R-011 | AC-R011-01, AC-R011-02, AC-R011-03 | J-11 | DEL / S-01,S-05 |

## Deferred-owner and scope boundary

| Deferred owner/artifact | Decision not made here | Binding observable constraint |
| --- | --- | --- |
| WO-007 content | Final labels, wording, tone, variants, notification categories/triggers/defaults | Preserve every semantic intent, action distinction, non-coercive outcome, quiet/frequency control, and consequence disclosure above. |
| WO-008 accessibility | Exact scalable-text, labels, targets, contrast, focus, non-color, and reduced-motion specifications | Every status, choice, safe exit, and consequence remains perceivable and operable under current Android conventions. |
| Architecture | Persistence/detection, storage, offline, notification, destination access, export/backup, restore, deletion, format, protection, and platform mechanisms | Implement these observable states without network-dependent core use, Calendar/Keep access, AI, backend, remote sync, telemetry, silent repeat, or assumed outcome. |
| Quality | Test design, fixtures, execution, and verification evidence | Observe each state/transition and unchanged-data guarantee without treating this owner draft as verification. |

## Revision change record

| Revision | Basis | Bounded change | Preserved behavior |
| --- | --- | --- | --- |
| 0.3 | WO-006-R1 remediation of Quality F-001 against blocked revision 0.2 | Added only four fully fielded SM-OFF rows and their directly necessary coverage/family references for S-01/O, S-02/O, S-04/O, and S-05/O; updated current revision provenance. | All revision 0.2 rows and semantics remain unchanged. Export destination choice remains the sole final authorization for one attempt; restore replacement and full deletion retain distinct confirmations and safe recovery; notification control remains non-coercive; core use remains available without a network, account, backend, Calendar/Keep access, or external service. |
| 0.2 | Verified journeys revision 0.2 and information architecture revision 0.4 | Updated the frozen basis; made deliberately completed destination choice the sole final authorization for one export attempt; retired and reserved SM-EXP-06; reconciled SM-EXP-03, SM-EXP-07, SM-EXP-08, and SM-EXP-10; and kept the Jude-chosen destination visible with an outcome-not-yet-established export. | All non-export state rows remain unchanged. Export never repeats silently or asserts an unknown outcome. Restore replacement and full deletion retain their distinct consequence disclosures and explicit confirmations. |

This revision adds no work data, specialized domain, archive, network dependency, Calendar/Keep access, AI, backend, sync, analytics, telemetry, external communication, paid dependency, product score, fixed project model, drift threshold, inferred disposition, automatic consequence, or broader distribution. It claims no Quality verification, Gate 2 approval, architecture readiness, security verdict, implementation readiness, promotion, launch, or distribution authorization.