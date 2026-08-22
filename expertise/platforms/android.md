# Android Platform Pack

Use this pack only when an Android-family target is declared.

## Platform rules

- Follow the current Android recommended layered architecture: a clearly defined data layer, repositories that expose application data, unidirectional data flow, lifecycle-aware UI state collection, and a domain layer only when it simplifies reused or complex business logic.
- Make state resilient to configuration change and process recreation. Keep durable state outside UI objects and save only the minimum restoration keys needed.
- Keep blocking work off the main thread. Use structured, lifecycle-aware asynchronous work; make cancellation and retry behavior explicit.
- Design networked data for intermittent connectivity when the requirement warrants it: establish a source of truth, define read/write conflict policy, queue/synchronize safely, and expose freshness or pending state.
- Support adaptive layouts and inputs across relevant window sizes, orientations, foldables, tablets, desktop modes, TV/automotive/wear form factors, keyboard, mouse, touch, and accessibility services as declared.
- Request the minimum permissions at point of need, preserve platform back/navigation behavior, and validate background-work and power constraints.

## Evidence to add

Record supported API/device/form-factor matrix, lifecycle/process-restoration checks, accessibility checks, baseline/profile or performance evidence where material, offline/synchronization cases, and signed/package validation required by the distribution path.

## Primary sources

- [Android architecture recommendations](https://developer.android.com/topic/architecture/recommendations) — first-party guidance, updated April 26, 2026 at library verification.
- [Guide to app architecture](https://developer.android.com/topic/architecture) and [offline-first data layer](https://developer.android.com/topic/architecture/data-layer/offline-first).
- [Core app quality](https://developer.android.com/docs/quality-guidelines/core-app-quality) and [adaptive app quality](https://developer.android.com/docs/quality-guidelines/adaptive-app-quality).
