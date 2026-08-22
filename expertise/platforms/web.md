# Web Platform Pack

Use this pack for browser-delivered applications, including a progressive web application when explicitly required.

## Platform rules

- Build on semantic HTML and web standards with progressive enhancement. Core content and actions should survive reasonable variation in browser capability, input, viewport, network, and script execution when the product permits.
- Meet the project's declared WCAG 2.2 conformance target; use native elements first and WAI-ARIA patterns only when a native control cannot express the interaction.
- Define responsive behavior, zoom/reflow, keyboard and focus order, announcements, history/navigation, deep linking, loading, failure, offline, and update behavior.
- Establish performance budgets and measure user-visible field behavior. Core Web Vitals are signals, not the whole experience; retain device/network/population context.
- Treat service workers as a privileged programmable network layer: scope deliberately, version caches, handle update races, and provide a recovery path from corrupt or stale state.
- Harden browser boundaries with least-privilege permissions, output encoding, trusted dependency policy, safe cross-origin behavior, and an explicit content security policy where applicable.

## Evidence to add

Record supported browser/input/viewport matrix, automated and manual accessibility evidence, keyboard/assistive-technology checks, field/lab performance context, offline/update/cache cases, and security-header/cross-origin validation.

## Primary sources

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/).
- [Service Workers specification](https://www.w3.org/TR/service-workers/).
- [Web App Manifest](https://www.w3.org/TR/appmanifest/) — W3C Working Draft dated August 13, 2026 at verification; treat draft features accordingly.
- [Core Web Vitals](https://web.dev/articles/vitals) — first-party Chrome/web.dev performance guidance, used with broader user evidence.
