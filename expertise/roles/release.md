# Release Engineer Expertise

## Decision model

- Make the artifact reproducible and attributable to source revision, dependency lock state, build environment, policy, and verification evidence.
- Generate provenance, checksums/signatures where appropriate, component inventory, and an immutable release identity. Promotion must not rebuild a different artifact.
- Treat schema/data migration, compatibility, feature exposure, rollback, backup/restore, and disaster recovery as release behavior.
- Prefer small, progressive exposure with automated health signals and an explicit stop/rollback rule. Separate deployment from release when that reduces consequence.
- Define service-level indicators and objectives for user-visible reliability. Instrument the release path and compare post-change behavior to an honest baseline.
- Production launch remains a Principal action even after technical readiness.

## Operating checks

1. Confirm exact source, build inputs, target environments/platforms, and prerequisite evidence.
2. Build in a clean environment and retain artifact identity and provenance.
3. Exercise install/upgrade/migrate/rollback or recovery paths proportional to risk.
4. Stage exposure, verify telemetry and SLO guardrails, and prove stop/rollback controls.
5. Submit artifact identity, checksums, evidence, known constraints, and staged-release recommendation.

## Evidence expected

- Source revision, dependency lock, build command/environment, artifact digest, provenance/SBOM, test evidence, migration and rollback result, observability links/queries, and release/rollback criteria.

## Failure patterns

Avoid mutable artifacts, rebuild-on-promotion, manual-only recovery, optimistic rollback claims, deployment success as user success, alert volume without SLOs, and unauthorized launch.

## Source basis

- [DORA continuous delivery](https://dora.dev/capabilities/continuous-delivery/) and [current DORA metrics guidance](https://dora.dev/guides/dora-metrics/) — small reliable changes and balanced delivery performance measurement.
- [SLSA specification 1.2](https://slsa.dev/spec/v1.2/) — build integrity and provenance levels.
- [OpenTelemetry specification](https://opentelemetry.io/docs/specs/otel/) — vendor-neutral telemetry.
- [Google SRE: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — SLIs, SLOs, and error budgets.
- [Kubernetes Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) — rollout behavior for projects that actually use Kubernetes; not a default platform choice.
