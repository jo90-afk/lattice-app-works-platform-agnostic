# Evaluation and autonomy evidence

Lattice 0.0.8 turns the roadmap's reliability claims into repeatable evidence contracts. The evaluation layer is deliberately separate from project truth: it measures how the control plane behaved, but evaluation output does not become authority for a project unless a governed project transition explicitly records it.

## Scenario registry

`evals/scenarios.json` is the canonical versioned registry of bounded evaluation scenarios. Version 1 covers every 0.0.8 roadmap class:

- greenfield feature delivery;
- cross-component refactoring;
- migration work;
- test and CI remediation;
- ambiguous requirements requiring escalation;
- contradictory new information;
- worker crash and lease expiry;
- verifier disagreement;
- concurrent artifact conflict; and
- multi-project capacity contention.

Each scenario names the metric signals it must exercise. The registry validator fails if a roadmap scenario disappears, if IDs are duplicated, or if the suite stops exercising one of the product-thesis metrics.

Validate the registry with:

```bash
python3 scripts/evaluation.py validate
```

## Result contract

One bounded run emits one `lattice-evaluation-result` version 1 object. A result identifies the scenario, run, and host, then records observed counts rather than a synthetic autonomy score.

Required counters are:

- `routine_transitions` and `routine_autonomous_transitions`;
- `accepted_changes` and `false_acceptances`;
- `escalations` and `unnecessary_escalations`;
- `worker_losses` and `recoveries_succeeded`;
- `state_divergence_incidents`;
- `verification_defects_presented` and `verification_catches`;
- `blocked_seconds_missing_information`; and
- `context_bytes`.

Every result also carries `state_fingerprint` and `acceptance_fingerprint`. These are intentionally host-neutral comparison values: the same scenario may run through different execution hosts, but equivalent runs should converge to equivalent durable state and acceptance semantics.

The harness rejects impossible relationships such as more false acceptances than accepted changes, more successful recoveries than worker losses, or more verification catches than defects presented.

## Summary metrics

Summaries correspond directly to the roadmap's autonomy metrics:

- **routine autonomy rate** — routine transitions completed without Principal intervention;
- **false acceptance rate** — accepted changes later identified as invalid inside the evaluation oracle;
- **unnecessary escalation rate** — escalations that the scenario oracle says did not require Principal authority;
- **recovery success rate** — worker-loss cases recovered without manual state reconstruction;
- **state divergence incidents** — count of incompatible accepted state outcomes;
- **verification catch rate** — seeded or known defects caught before acceptance;
- **blocked time for missing information** — elapsed seconds where progress correctly stopped for missing governed information; and
- **context bytes per accepted change** — bounded execution context volume normalized by accepted change.

A denominator that has not been exercised is reported as `null`, not zero. This prevents an untested behavior from appearing perfect.

Summarize one or more result files with:

```bash
python3 scripts/evaluation.py summarize evals/results/*.json
```

Result files may contain one object or an array of objects.

## Portability evidence

When the same scenario appears for more than one host, the summary compares `state_fingerprint` and `acceptance_fingerprint`. Any mismatch is reported under `portability.equivalence_violations`.

A host may use different workspaces, tools, models, or execution strategies. Lattice's claim is narrower: host-specific execution must not change the durable state meaning or acceptance semantics of the bounded scenario.

The initial 0.0.8 harness defines and tests this comparison contract. Later 0.0.8 slices will add executable scenario drivers, adversarial state cases, and host adapters that emit these results from real runs.

## Evidence discipline

Evaluation results are observations about the control plane, not project-state shortcuts. In particular:

- a high autonomy rate does not authorize broader agent permissions;
- an evaluation pass does not replace independent verification of project work;
- a portability fingerprint does not permit one host to bypass guarded transitions; and
- thresholds for public claims belong in an explicit release/evaluation policy, not hidden in presentation code.

0.0.8 exits only when reproducible scenarios show that durable state and independent verification reduce autonomy failures rather than merely adding ceremony.
