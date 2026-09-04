# Journal.28 — Research checkpoint and answer

## What we did

Reviewed the deterministic control results, the hosted baseline tool trace, two hosted calculator-failure traces, their path-oracle scores, the minimal outcome signal, and the outcome-aware feedback decision. This checkpoint separates direct observations from the stronger claims that would require more tasks, models, or real intervention runs.

The hosted evidence is deliberately small but concrete. A successful run produced the expected three-turn, three-tool execution graph with exact baseline-oracle agreement. Two runs then forced the first calculator invocation to fail. In both, telemetry identified the failed calculator boundary and showed that the model did not retry. In the later run, the root-level validator recorded a valid task outcome despite the missing retry. The post-run policy consequently returned `observe_only` rather than requesting unnecessary recovery.

## Concept to know

The project has tested **execution semantics**, not hidden reasoning. Execution semantics are facts that a runtime can legitimately observe at reusable boundaries: model invocations, tool requests, parentage, status, attempts, argument equivalence, tokens, latency, and a separately supplied outcome class. They are enough to reconstruct what the agent did in this experiment.

They do not reveal why the model made its choices, whether an unvalidated response was semantically sensible, or whether a tool call was philosophically necessary. Those claims require additional context or a separate evaluator. Keeping that boundary explicit is what makes the evidence defensible.

## Why we did it

The initial question was not whether traces are useful in the abstract. It was whether OpenTelemetry can reconstruct agent behavior well enough to identify inefficient or failed paths without manually instrumenting every business-logic step. The second question was whether observability can become a feedback signal.

A project checkpoint prevents the experiment from drifting into feature accumulation. It asks whether the collected evidence answers those questions at the intended scope and what one more experiment would genuinely add.

## Result at this checkpoint

### Answer to the execution-reconstruction question

**Qualified yes, for externally observable execution behavior.** The deterministic lane and the real hosted tool runs reconstruct the operation sequence, causal topology, tool failure, retry absence, attempt identity, latency, token use, and a provider-versus-tool cost split. The hosted failure trace made a missing recovery branch visible without adding spans inside option lookup or calculator logic.

The qualification is essential. OpenTelemetry did not reconstruct private reasoning or model intent. It also did not establish answer correctness by itself; the valid/invalid/unavailable class came from a small external task validator at the agent boundary. The result should therefore be read as: boundary telemetry is strong evidence about *how a run executed*, but not a substitute for semantic evaluation.

### Answer to the feedback-signal question

**Qualified yes, as a bounded post-run feedback signal.** The real trace contained a tool failure and no retry, yet the outcome was valid. The policy used both facts to choose `observe_only`. This is a concrete example of observability informing a proportionate next action rather than treating every anomaly as failure.

The policy is not yet an autonomous in-run controller. The outcome class arrives after completion, so the demonstrated action is suitable for a scheduler, retry queue, reliability alert, or review workflow. In-run intervention remains separately supported only for timely evidence such as repeated failures or retry budgets in the deterministic lane.

### What is proven, suggested, and open

| Status | Claim |
| --- | --- |
| Directly shown | Shared agent/model/tool spans reconstruct the observed hosted path and tool-parentage graph. |
| Directly shown | A failed tool span and absence of a retry are detectable without a fault label in telemetry. |
| Directly shown | A minimal outcome class prevents a tool error from being mistaken automatically for a failed task. |
| Suggested | Small boundary attributes—attempt number, logical operation ID, and argument fingerprint—materially improve diagnosis. |
| Open | Generalization across complex tasks, models, tools, and multi-agent runtimes. |
| Open | A real hosted invalid or unavailable outcome and a real automated intervention. |

One additional hosted invalid/unavailable-outcome scenario would exercise the `intervene_on_next_attempt` branch with real model behavior. It would strengthen the feedback-policy evidence, but it would not materially change the central conclusion above. It is best treated as an optional extension, not a prerequisite for the current result.

## Next step

Choose one of two valid directions:

1. Stop the first study here and turn this checkpoint into a concise final report.
2. Run one optional hosted scenario designed to yield an invalid or unavailable outcome, then test the intervention branch with real evidence.

## Work snapshot

```text
What telemetry reconstructed
  model turns, tool calls, parentage, failures, retry absence, cost envelope

What required one extra boundary signal
  whether the task outcome was valid

What feedback did in the real failure run
  tool failure + valid outcome -> observe only
```

The notable result is not that telemetry replaced reasoning evaluation. It did not. The result is that telemetry supplied reliable execution evidence, and a very small outcome signal turned that evidence into a safe, explainable feedback decision.
