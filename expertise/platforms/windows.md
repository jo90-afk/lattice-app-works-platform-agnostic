# Windows Platform Pack

Use this pack for a declared Windows desktop/application target.

## Platform rules

- Choose the app technology from current Windows-supported options based on existing code, deployment, accessibility, performance, device integration, and support constraints; do not assume one framework fits every project.
- Follow current Windows design guidance for layout, commands, navigation, windows, system back behavior where present, input, notifications, typography, themes, high contrast, and fluent system surfaces.
- Support the declared combination of touch, mouse, keyboard, pen, controller, and accessibility technologies. Make keyboard access, focus, scaling, high contrast, and text behavior testable.
- Define app lifecycle, activation/deep links, multi-window behavior, settings/data locations, update, package identity, signing, installation, repair, and uninstall consequences.
- Minimize capabilities and brokered/system access. Preserve least privilege and explain any elevated or enterprise deployment requirement.
- Test supported Windows versions, architectures, display scaling, localization, and packaging/distribution paths.

## Evidence to add

Record Windows/framework/version/architecture matrix, input and accessibility results, lifecycle/activation checks, package/signing/install/update/uninstall evidence, and performance/resource behavior.

## Primary sources

- [Windows app development overview](https://learn.microsoft.com/en-us/windows/apps/get-started/) — first-party framework and app-platform choices, updated August 14, 2026 at verification.
- [Windows app design guidance](https://learn.microsoft.com/en-us/windows/apps/design/).
