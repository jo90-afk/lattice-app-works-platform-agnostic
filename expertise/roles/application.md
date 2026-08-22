# Application Engineer Expertise

## Decision model

- Treat the target as a declared capability set, not as Android by default. A project may target native mobile, desktop, web, terminal, embedded, console, spatial, or a future platform identifier.
- Load only the selected platform packs. For an unresolved platform, consult current first-party documentation for the claimed condition and retain the source/version used.
- Preserve platform-native conventions for navigation, lifecycle, windowing, input, permissions, accessibility, distribution, and system integration.
- Separate domain behavior, application state, platform adapters, persistence, and remote integration so lifecycle and failure behavior can be tested.
- Design for interruption, restoration, cancellation, partial data, concurrency, offline behavior, network changes, and version skew when applicable.
- Share code only where semantics are truly shared. Do not force every platform into the lowest common interaction model.

## Operating checks

1. Read `project/capabilities.json` and resolve expertise after claiming the action.
2. Confirm supported OS/browser/runtime versions, form factors, input modes, accessibility, distribution, and performance budgets.
3. Map observable UI and lifecycle states to owned application state and service contracts.
4. Minimize requested capabilities and permissions; explain them at the point of need.
5. Test platform-native behavior plus affected shared-domain behavior using the smallest decisive suite.
6. Submit exact artifacts, platform/runtime matrix, evidence, limitations, and known compatibility boundaries.

## Evidence expected

- Declared target matrix; architecture/state boundaries; permission and data behavior; accessibility checks; lifecycle/restoration tests; performance evidence; packaging/distribution constraints.
- First-party sources for unresolved platforms and a sourced truth revision when a consequential capability differs from the project record.

## Failure patterns

Avoid one-platform assumptions, blind code sharing, framework-default architecture, UI screenshots as functional proof, unbounded version support, main-thread blocking, hidden background work, and self-certification.

## Source basis

- Platform packs in `expertise/platforms/` hold current first-party guidance for common ecosystems.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) supplies cross-platform product-quality characteristics.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) supplies a strong accessibility baseline where its success criteria apply; native platform accessibility guidance remains authoritative for native behavior.
