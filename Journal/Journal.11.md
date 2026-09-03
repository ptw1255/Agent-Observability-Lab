# Journal.11 — Observability findings as a runtime feedback signal

## What we did

We implemented a bounded `RetryBudgetFeedback` policy and ran the invoice retry-loop task twice: once with feedback disabled and once with feedback enabled. The policy observes repeated failures for one logical operation and stops the loop after the second failure.

The policy is opt-in. When it intervenes, the runtime records `agent_observability_lab.feedback_action=stop_retry_loop` on the root span and preserves the failed task outcome.

## Concept to know

Detection and intervention are separate claims. A trace analyzer may correctly identify a retry loop, but that does not show that feeding the finding back into the runtime improves execution. Feedback can also create new failure modes, such as stopping too early or hiding a legitimate repeated call.

The feedback signal must include evidence, not only a label. This policy uses the logical operation and repeated failed tool attempts as its evidence. A production policy would also need a rule version, threshold, affected operation, and an audit record of the action.

## Why we did it

The matrix answers how much execution behavior can be reconstructed from telemetry in a controlled setting. This experiment tested whether that evidence can become an input to agent control logic without manually instrumenting every business branch.

## Result at this checkpoint

The disabled control made 3 failed tool calls and 4 model calls, producing 84 output tokens. The feedback-enabled run made 2 failed tool calls and 2 model calls, producing 44 output tokens. Both runs ended with root status `ERROR` and task outcome `failed`.

The enabled run reduced observed work by one failed tool attempt, two model calls, and 40 output tokens while preserving the explicit failure outcome. This is evidence that telemetry-derived feedback can change runtime behavior in this harness.

The result is bounded. The policy could stop a task that would have recovered on a later attempt. Because the intervention happened before the third attempt, the post-run analyzer reported two `tool_failure` findings but not `retry_loop`; the controller prevented the full loop from forming.

## Next step

Test the policy against transient recovery and legitimate multi-step work. The next checkpoint should measure whether feedback avoids excess work without suppressing a successful recovery.

## Work snapshot

The current evidence pipeline is:

```text
agent spans
  -> restricted evidence profile
  -> telemetry-only analyzer
  -> structured finding + evidence
  -> optional runtime feedback policy
```

The notable boundary is the arrow from finding to policy. Everything before it has been measured in the matrix. The next experiment must test whether the final arrow improves behavior without turning an imperfect detector into an unsafe controller.

Artifacts: [local-v0-feedback-retry-budget](../data/published/local-v0-feedback-retry-budget/).
