# Apple Platform Pack

Use this pack for iOS, iPadOS, macOS, watchOS, tvOS, visionOS, or another declared Apple application target. Confirm guidance for each actual OS rather than assuming one Apple UI fits all.

## Platform rules

- Apply the current Human Interface Guidelines and system components for the target device, input, window, navigation, modality, spatial context, and accessibility behavior.
- Keep one explicit source of truth for application state. Respect scene/application lifecycle, background limits, state restoration, cancellation, and data protection when interrupted or terminated.
- Use platform concurrency and UI-isolation rules; keep blocking work away from the main UI executor/thread and make cancellation/ownership legible.
- Ask for the minimum privacy-sensitive capability at the moment its value is clear. Provide accurate purpose descriptions and degrade safely after denial or revocation.
- Use semantic accessibility APIs, support text sizing and alternate input/assistive technologies, avoid color-only or motion-only meaning, and test on declared platforms.
- Define supported OS/device versions, localization, storage/synchronization, entitlement, signing, packaging, and distribution behavior explicitly.

## Evidence to add

Record OS/device/input matrix, lifecycle and restoration tests, XCTest results, accessibility inspection plus assistive-technology checks, permission denial/revocation, performance/energy evidence where material, and signing/distribution constraints.

## Primary sources

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines) and [design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles) — first-party guidance; principles page updated June 8, 2026 at verification.
- [Apple privacy design guidance](https://developer.apple.com/design/human-interface-guidelines/privacy).
- [Apple Accessibility documentation](https://developer.apple.com/documentation/accessibility).
- [XCTest documentation](https://developer.apple.com/documentation/xctest).
