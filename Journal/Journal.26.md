# Journal.26 — Outcome-aware feedback decision

## What changed

Added a small post-run policy that consumes one analyzer report and emits a recommended action. It reads only two evidence classes: whether the analyzer found `tool_failure`, and the root-level `answer_validation` class. It does not read model text, prompts, injected-condition labels, or business-logic internals.

The policy has four outcomes:

- `no_action` when no tool failure was observed.
- `observe_only` when a tool failed but the task outcome is `valid`.
- `intervene_on_next_attempt` when a tool failed and the outcome is `invalid` or `unavailable`.
- `insufficient_evidence` when a tool failed but this trace lacks a recognized validation class.

We ran the policy over the real validated-failure trace from Journal.25. It returned `observe_only`, with the evidence `tool_failure = true` and `answer_validation = valid`. Three local tests cover the valid, unavailable, and missing-validation cases.

## Key concepts

This is a feedback decision, not an in-flight interruption. The answer-validation class becomes available only after the agent run ends, so the policy cannot go back in time and make the failed calculator succeed. It can determine what a runtime, scheduler, or human workflow should do next: retain the failure as an operational signal, request a new attempt, route for review, or take no action.

That timing constraint is useful rather than embarrassing. It keeps the claim precise. Runtime telemetry can inform a control loop, but the appropriate control point depends on when evidence becomes available. Some evidence, such as repeated tool errors, can support in-run action. Outcome validation supports post-run action.

## Why this checkpoint matters

The previous result made a policy choice necessary. The calculator failed, the model did not retry, and the final answer was nevertheless validated. A failure-only rule would have treated that run as something to interrupt or rerun. The outcome-aware rule instead recognizes that the task completed correctly while preserving the dependency failure for reliability analysis.

This is the first concrete answer to the project's follow-up question: observability can become a feedback signal when the policy is explicit about which evidence justifies which action. It should not turn every anomaly into an intervention.

## Result and significance

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

The result supports a restrained action. The system can aggregate or alert on calculator reliability without rerunning a task that met its contract. The policy is intentionally small and task-agnostic except for the source of the validation class.

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

## Significance

The policy converts two evidence fields into four explicit actions and correctly selects `observe_only` for the real hosted trace. Because validation arrives after completion, the demonstrated control point is the next attempt, retry queue, alert, or review workflow. This timing boundary prevents the project from presenting a post-run recommendation as a live recovery mechanism.

## Market thesis

The first commercial user for outcome-aware feedback is an AI operations team managing retries, review queues, and incident routing. That team needs decisions that name both the execution evidence and the outcome evidence. A product can earn trust by making `insufficient_evidence` a supported result instead of forcing an intervention from incomplete telemetry.
