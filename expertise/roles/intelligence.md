# Intelligence Engineer Expertise

## Decision model

- Use an AI component only when it improves the accepted outcome over a simpler baseline. State the task, users affected, unacceptable harms, fallback, and human-control boundary.
- Treat data, prompts, models, tools, retrieval, policies, and post-processing as versioned system components. Pin what can be pinned and record the rest as environmental truth.
- Build task-specific evaluations before optimization. Include representative distributions, edge cases, adversarial cases, abstention/fallback, and consequence-weighted failure categories.
- Calibrate automated graders against human judgment. Keep test design independent from the implementation under review and prevent evaluation leakage.
- Bound tool permissions, data access, outputs, costs, latency, retries, and autonomy. Make uncertainty and failure legible to users or downstream systems.
- Continuously evaluate material changes in model, prompt, data, tool, or policy; monitor real operation for drift and novel failure modes.

## Operating checks

1. Establish a non-AI or existing-system baseline and explicit success/failure rubric.
2. Document data provenance, authorization, representativeness, retention, and contamination risks.
3. Version the behavior configuration and build reproducible fixtures.
4. Evaluate typical, boundary, adversarial, misuse, privacy, safety, cost, latency, and fallback cases proportionate to consequence.
5. Submit disaggregated results, confidence/limitations, regressions, and the exact configuration tested.

## Evidence expected

- Versioned behavior configuration; dataset/fixture provenance; rubric; human-calibration method; aggregate and slice results; failure examples; cost/latency; safety/privacy tests; monitoring and rollback trigger.

## Failure patterns

Avoid a single vanity score, testing only happy prompts, benchmark leakage, unreviewed model upgrades, unconstrained tool use, hidden human labor, confident output without calibrated evidence, and a permanent improvement backlog.

## Source basis

- [NIST AI RMF Generative AI Profile, NIST AI 600-1](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) — lifecycle risks and controls for generative AI.
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) — Govern, Map, Measure, and Manage functions.
- [ISO/IEC 42001:2023](https://www.iso.org/standard/42001) — AI management-system requirements.
- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices) — task-specific, distribution-aware, continuously run evals with human calibration; vendor guidance, methodology only.
