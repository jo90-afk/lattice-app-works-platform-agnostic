# Cross-Platform Implementation Pack

Load this pack when a shared application framework or explicit multi-platform sharing strategy is declared. Also load each actual target-platform pack.

## Platform rules

- Choose sharing boundaries from product behavior and platform semantics. Share domain rules, data contracts, and non-visual infrastructure where beneficial; keep platform adapters and divergent interactions explicit.
- Define which layer owns navigation, lifecycle, state, persistence, networking, rendering, accessibility, permissions, and native extensions. Prevent two state systems from silently competing.
- Preserve native accessibility semantics, input, windows/navigation, permissions, background work, localization, performance, and distribution behavior on every target.
- Budget bridge/interop cost, binary size, startup/runtime performance, memory, dependency/update risk, debugging, testability, and access to new platform capabilities.
- Pin framework/toolchain versions and track upstream compatibility. A framework upgrade that changes behavior is a consequential dependency truth, not routine background work.
- Test shared logic once at its boundary and platform behavior on every supported target. A pass on one target does not certify another.

## Evidence to add

Record the sharing decision and alternatives, ownership/layer diagram, target matrix, framework/toolchain versions, native-extension boundary, per-platform accessibility/lifecycle/performance tests, packaging evidence, and upgrade/exit strategy.

## Primary sources

- [Flutter architectural overview](https://docs.flutter.dev/resources/architectural-overview) — first-party framework architecture.
- [React Native architecture overview](https://reactnative.dev/architecture/overview) — first-party framework architecture.
- [Tauri security](https://v2.tauri.app/security/) and [capabilities](https://v2.tauri.app/security/capabilities/) — first-party desktop framework isolation and permission model.

Framework documentation explains its own mechanisms, not whether that framework is right for the project. Make that choice from project constraints and target-platform evidence.
