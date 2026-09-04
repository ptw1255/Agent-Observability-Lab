# Journal.27 — Outcome-aware decision table

## What changed

Completed the feedback decision table with four local, explicitly synthetic policy cases. Each case is a minimal analyzer-report shape, not a generated model trace and not a claim about hosted-model behavior. The published artifact labels itself `synthetic: true` so it cannot be confused with the observed hosted runs.

The table confirms these actions:

- No tool failure and a valid outcome: `no_action`.
- Tool failure and a valid outcome: `observe_only`.
- Tool failure and an unavailable outcome: `intervene_on_next_attempt`.
- Tool failure with no validation signal: `insufficient_evidence`.

The real hosted run from Journal.25 occupies the second row. It is observed evidence, not a synthetic example: a failed calculator and a validated answer produced `observe_only`. The unavailable-outcome row tests the contrasting policy behavior locally without implying that a hosted model produced it.

## Key concepts

A decision table is a policy contract. It makes the relationship between evidence and action reviewable before an automated system acts. That is especially important for agent runtimes, where an error log can be tempting but insufficient grounds for retrying, stopping, or escalating work.

The synthetic rows test policy determinism: given the same analyzer report, the system recommends the same action. They provide no evidence about model behavior. The observed traces answer the separate question of whether the runtime emits the evidence the policy needs.

## Why this checkpoint matters

The project has now demonstrated both halves of a feedback loop:

1. Runtime telemetry reconstructs a hosted model/tool path and detects a failed tool boundary.
2. A transparent policy combines that evidence with a minimal task outcome to recommend a proportionate next action.

Completing the decision table prevents the project from overclaiming. We have observed the valid-outcome branch in a real hosted run. We have not observed the unavailable or invalid branch from a real hosted model, so those remain policy-tested examples rather than experimental findings.

## Result and significance

The feedback policy is locally complete for its stated scope. Its behavior is deterministic, documented, and covered by 40 tests. The real hosted trace validates the most important restraint case: a tool failure does not automatically trigger recovery when the task outcome is valid.

This is enough to answer the follow-up question conditionally: observability can become a feedback signal when the runtime has both trustworthy execution evidence and a trustworthy outcome signal, and when the policy distinguishes observation from intervention. Telemetry alone is not a sufficient judge of answer correctness.

## Next step

Perform a project checkpoint: consolidate the evidence, state the answer to both research questions, identify what is proven versus suggested, and decide whether one additional hosted invalid/unavailable-outcome scenario would materially change the conclusion.

## Work snapshot

```text
observed hosted evidence
  tool failure + valid outcome -> observe only

synthetic policy coverage
  tool failure + unavailable outcome -> intervene on next attempt
  tool failure + no outcome signal   -> insufficient evidence
```

The notable boundary is clear: the real run proves that the telemetry and outcome signal can drive a restrained decision. The synthetic rows prove only that the decision logic is defined for the remaining cases.

## Significance

The decision table makes policy behavior reviewable before automation: the same input always produces the same recommendation across 40 tests. It also labels synthetic rows so they cannot be cited as observed model behavior. This distinction preserves the evidence chain and identifies the one missing live branch—failed dependency plus unavailable outcome.

## Market thesis

Enterprise governance teams will value a versioned decision table because it exposes when an agent system observes, retries, escalates, or declines to act. The table can become an approval artifact for runtime controls and a regression test after policy changes. Its commercial value comes from auditability and predictable action, not from the number of automated decisions.
