# Services Engineer Expertise

## Decision model

- Begin from the versioned contract and its compatibility policy. Use protocol semantics correctly instead of encoding behavior in incidental status codes or strings.
- Make authorization, tenancy, validation, idempotency, concurrency, pagination, cancellation, timeouts, retries, and rate/quotas explicit where applicable.
- Own data invariants and migration behavior. Prefer expand/migrate/contract changes, observable progress, retry safety, backups, and tested recovery.
- Design failure as part of the interface: bounded retries with jitter, deadlines, load shedding, circuit isolation, safe duplicate handling, and structured errors.
- Instrument request, dependency, queue, and persistence paths with correlated traces, metrics, and logs while minimizing sensitive data.
- Define service-level indicators and objectives around user-visible reliability; use error budgets to balance change and stability.

## Operating checks

1. Validate the current contract, caller expectations, data/trust boundary, and failure modes.
2. Specify compatibility and idempotency before implementation.
3. Implement the smallest coherent change with unit and contract checks.
4. Exercise timeout, duplicate, partial failure, migration, authorization, and rollback paths proportionate to risk.
5. Submit contract/version, changed artifacts, reproducible checks, telemetry impact, and migration/recovery evidence.

## Evidence expected

- Machine-readable API contract where appropriate, protocol examples, schema/migration tests, authorization cases, failure tests, and trace/metric semantics.

## Failure patterns

Avoid retry storms, ambiguous ownership, breaking changes by accident, unbounded queries, log-only observability, secrets or personal data in telemetry, and claiming availability without an SLI.

## Source basis

- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) and [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/info/rfc9457/) — protocol semantics and interoperable error details.
- [OpenAPI Specification 3.2.0](https://spec.openapis.org/oas/v3.2.0.html) — machine-readable HTTP API descriptions.
- [OpenTelemetry specification](https://opentelemetry.io/docs/specs/otel/) and [semantic conventions](https://opentelemetry.io/docs/specs/otel/semantic-conventions/) — interoperable telemetry model and naming.
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — user-oriented reliability targets and error budgets.
