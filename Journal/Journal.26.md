# Journal.26 — Outcome-aware feedback decision

## What we did

Added a small post-run policy that consumes one analyzer report and emits a recommended action. It reads only two evidence classes: whether the analyzer found `tool_failure`, and the root-level `answer_validation` class. It does not read model text, prompts, injected-condition labels, or business-logic internals.

The policy has four outcomes:

- `no_action` when no tool failure was observed.
- `observe_only` when a tool failed but the task outcome is `valid`.
- `intervene_on_next_attempt` when a tool failed and the outcome is `invalid` or `unavailable`.
- `insufficient_evidence` when a tool failed but this trace lacks a recognized validation class.

We ran the policy over the real validated-failure trace from Journal.25. It returned `observe_only`, with the evidence `tool_failure = true` and `answer_validation = valid`. Three local tests cover the valid, unavailable, and missing-validation cases.

## Concept to know

This is a feedback decision, not an in-flight interruption. The answer-validation class becomes available only after the agent run ends, so the policy cannot go back in time and make the failed calculator succeed. It can determine what a runtime, scheduler, or human workflow should do next: retain the failure as an operational signal, request a new attempt, route for review, or take no action.

That timing constraint is useful rather than embarrassing. It keeps the claim precise. Runtime telemetry can inform a control loop, but the appropriate control point depends on when evidence becomes available. Some evidence, such as repeated tool errors, can support in-run action. Outcome validation supports post-run action.

## Why we did it

The previous result made a policy choice necessary. The calculator failed, the model did not retry, and the final answer was nevertheless validated. A failure-only rule would have treated that run as something to interrupt or rerun. The outcome-aware rule instead recognizes that the task completed correctly while preserving the dependency failure for reliability analysis.

This is the first concrete answer to the project's follow-up question: observability can become a feedback signal when the policy is explicit about which evidence justifies which action. It should not turn every anomaly into an intervention.

## Result at this checkpoint

The real trace produced this decision:

```json
{
  "action": "observe_only",
  "evidence": {
    "tool_failure": true,
    "answer_validation": "valid"
  }
}
```

This is a meaningful result because it is both actionable and restrained. The system can aggregate or alert on calculator reliability without needlessly rerunning a task that met its contract. The policy is intentionally small and task-agnostic except for the source of the validation class.

## Next step

Create a local synthetic analysis report with `tool_failure` plus `invalid` or `unavailable` outcome, then record the policy's different recommendation. This will complete the decision table without requiring another paid hosted call. After that, assess whether the project has enough evidence to answer its two research questions or whether one more hosted scenario would add material value.

## Work snapshot

```text
tool failure + valid outcome        -> observe only
tool failure + invalid/unavailable  -> intervene on next attempt
tool failure + no validation signal -> insufficient evidence
no tool failure                     -> no action
```

The notable point is the conjunction. A tool error is important evidence, but it becomes a reason to intervene only when paired with evidence that the task did not complete validly.
