# Content Design — Revision 0.1

## 1 Metadata/frozen basis

Project: `plos-001`. Owner: Experience. Status: owner draft. This revision is bounded to the frozen sources named by `WO-007`; hashes and exact source inventory will be recorded after source inspection.

## 2 Voice and controlled vocabulary

Use calm, direct, non-judgmental language. Describe the present state, the available choice, and the consequence without urgency inflation, streak language, blame, or claims that an external action succeeded before its outcome is known.

## 3 Destination labels/help table (20 IDs)

The exact 20-destination label and help inventory is source-controlled and will be populated from the frozen routing inventory without adding destinations.

## 4 State content template table + exhaustive 77-state-to-template mapping

State copy uses a bounded template family: ready, empty, loading, offline, permission-required, validation-error, operation-in-progress, outcome-unknown, success, cancelled, and recoverable-error. The exhaustive mapping will be populated from the frozen 77-state inventory.

## 5 Core/error/offline/permission/cancel/result language

Core language states what is available now. Error language explains what was not completed and offers a safe next step. Offline language distinguishes locally available work from unavailable external operations. Permission language names the capability and why it is needed before requesting it. Cancellation language confirms that no requested consequence was completed. Result language distinguishes confirmed success, confirmed failure, and unknown outcome.

## 6 Export/restore/delete disclosure/action/confirmation matrix

Export uses destination choice as the initiating action and adds no separate confirmation. Restore and deletion retain distinct, explicit confirmations immediately before consequence. Unknown outcomes expose status and safe re-entry without silently repeating the operation.

## 7 Explicit notification applicability decision and full behavior/default/control matrix if offered

Notifications are applicable only where the frozen requirements make them user-configurable. They remain optional, off or conservative by default as specified by the source, respect user controls, and never use escalating pressure.

## 8 J/R/32 trace, exclusions, consistency and deferral audit

This artifact will trace all frozen journey IDs, requirement IDs, and 32 acceptance IDs without changing intent. It excludes implementation mechanisms, architecture, persistence design, analytics, AI, synchronization, work data, and final accessibility rules. Any unresolved mechanism remains deferred to its owning gate or specialist.