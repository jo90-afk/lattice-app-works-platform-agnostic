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

## Executable scenarios

`scripts/evaluation_scenarios.py` runs bounded scenarios against a fresh temporary Lattice store and emits a validated result object. The initial production-path set is:

```bash
python3 scripts/evaluation_scenarios.py greenfield-feature-delivery
python3 scripts/evaluation_scenarios.py verifier-disagreement
python3 scripts/evaluation_scenarios.py worker-crash-and-lease-expiry
```

### Greenfield feature delivery

The runner creates a deterministic project/objective/milestone/condition, claims owner work through the atomic host boundary, submits the result, obtains a fresh Quality verdict, and advances through Assurance. The scenario passes only if the condition is satisfied and the milestone is accepted.

### Verifier disagreement

The owner submits a result explicitly seeded with an evaluation defect. Quality records `NOT_SATISFIED`. The scenario passes only if the condition and milestone remain unaccepted. The seeded defect contributes one presented defect and one verification catch to the evaluation metrics.

### Worker crash and lease expiry

The runner first acquires a real guarded lease. Its only direct state manipulation is evaluation fault injection: the lease expiry is moved into the past to model a vanished host without introducing a wall-clock sleep. Production recovery must detect the expired lease, audit recovery, return the same derived intent to the frontier, allow another worker to reclaim it, and carry it through independent verification and Assurance acceptance. The injected failure is not itself a production mutation path.

## Adversarial state and authority scenarios

`scripts/evaluation_adversarial_scenarios.py` adds scenarios where the correct result is often refusal, invalidation, or bounded scheduling rather than acceptance.

```bash
python3 scripts/evaluation_adversarial_scenarios.py ambiguous-requirements-escalation
python3 scripts/evaluation_adversarial_scenarios.py contradictory-new-information
python3 scripts/evaluation_adversarial_scenarios.py multi-project-capacity-contention
```

### Ambiguous requirements escalation

The Director records a real `principal_only` exception before any specialist condition is created. The evaluation runner makes the open interval measurable by moving only the exception timestamp backward; it does not create a special runtime state. The scenario passes only when the active frontier contains Principal work, a normal specialist worker receives no scheduler assignment, and the escalation remains necessary. This contributes one required escalation, zero unnecessary escalations, and observed blocked time for missing information.

### Contradictory new information

A condition is first satisfied through a normal owner submission and independent Quality verdict under an accepted truth. That truth is then treated as settled/background. A second material truth is added and linked with the production `contradicts` relation. The scenario passes only when Lattice reactivates and contests both propositions, clears the accepted truth version from the dependent condition, increments the condition state version, makes the condition no longer satisfied, keeps the milestone unaccepted, and derives new owner work. A coherent invalidation records zero state-divergence incidents; failure to invalidate records divergence.

### Multi-project capacity contention

Three active projects compete for three available Application workers under a temporary evaluation registry with portfolio capacity two and explicit order B → A → C. Planning must remain read-only. Dispatch must grant only B and A in the first wave. After those workers submit and release their lease capacity, a second derivation must admit C. The scenario passes only if all three projects progress to pending independent verification without creating a durable queue.

The evaluation registry used here is an evaluation input, not a replacement for the repository portfolio registry.

CI executes all six implemented scenarios as command-line runs, writes their result JSON, and feeds the aggregate back through `scripts/evaluation.py summarize` before the ordinary SQLite/Postgres regression suite runs.

## Semantic fingerprints

`scripts/evaluation_fingerprint.py` derives host-neutral fingerprints from canonical project meaning.

The full state fingerprint includes project/objective/milestone state, current records and truths, truth links, readiness conditions and their accepted inputs, submissions, reviews, evidence, commitments, and exceptions. Generated submission/review/evidence IDs, event IDs, lease IDs, timestamps, host identity, workspace identity, and lifecycle ordering are excluded.

The narrower acceptance fingerprint includes milestone status, condition status/version/attempt state, accepted record/truth versions, and independent review verdicts.

Evaluation scenarios use deterministic IDs for durable seeded entities. Generated runtime identities are intentionally not part of either fingerprint. A test runs the same greenfield scenario under different host labels and requires identical state and acceptance fingerprints.

This establishes the comparison mechanism; it does **not** yet claim that distinct external host adapters have been proven portable. Later 0.0.8 slices must run the same bounded scenario through genuinely different supported host paths.

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

The fingerprint and result contracts are executable. Distinct host-adapter evaluation remains explicit future 0.0.8 work rather than being inferred from a changed host label.

## Evidence discipline

Evaluation results are observations about the control plane, not project-state shortcuts. In particular:

- a high autonomy rate does not authorize broader agent permissions;
- an evaluation pass does not replace independent verification of project work;
- a portability fingerprint does not permit one host to bypass guarded transitions; and
- thresholds for public claims belong in an explicit release/evaluation policy, not hidden in presentation code.

0.0.8 exits only when reproducible scenarios show that durable state and independent verification reduce autonomy failures rather than merely adding ceremony.
