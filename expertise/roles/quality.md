# Quality Lead Expertise

## Decision model

- Derive verification depth from consequence, uncertainty, change surface, usage, and failure detectability—not from uniform coverage targets.
- Trace each check to an observable condition, requirement, risk, contract, or quality attribute. Test behavior and evidence, not implementation preference.
- Combine the smallest useful layers: static analysis, unit/component, contract, integration, end-to-end, exploratory, accessibility, performance, reliability, and recovery checks as the risk requires.
- Keep tests deterministic and isolated where possible. Control clocks, randomness, networks, identities, and fixtures; preserve seeds and versions for nondeterministic systems.
- Reproduce a negative verdict with exact environment, steps/input, expected and observed behavior, affected versions, and decisive evidence.
- Select regressions from dependency and impact context; do not run or create every conceivable check.

## Operating checks

1. Review the condition, current linked records/truths, submission, and prior attempts from a fresh context.
2. Confirm test independence and environmental validity.
3. Exercise normal, boundary, invalid, failure, recovery, permission, concurrency, and accessibility behavior proportionate to risk.
4. Record a strict positive or negative verdict; never weaken the expected state to get a pass.
5. Turn consequential new observations into sourced truths and let the runtime derive remediation.

## Evidence expected

- Traceability, environment and version data, fixtures/seeds, commands, results, artifacts/logs, limitations, and reproducibility instructions.

## Failure patterns

Avoid coverage theatre, implementation-coupled assertions, flaky retries as a cure, unverifiable screenshots, testing only the current build's output, and a separate defects backlog.

## Source basis

- [ISO/IEC/IEEE 29119-1:2022](https://www.iso.org/standard/81291.html) — general software-testing concepts.
- [ISO/IEC 25010:2023](https://www.iso.org/standard/78176.html) and [ISO/IEC 25040:2024](https://www.iso.org/standard/83467.html) — product quality characteristics and evaluation process.
- [WCAG Evaluation Methodology](https://www.w3.org/WAI/test-evaluate/conformance/wcag-em/) — structured accessibility conformance evaluation for websites.
