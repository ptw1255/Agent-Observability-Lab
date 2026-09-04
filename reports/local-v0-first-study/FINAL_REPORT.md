# Agent Observability Lab — First Study Report

## Scope

This first study asks two related questions:

1. Can OpenTelemetry reconstruct enough of an AI agent's execution behavior to identify inefficient or failed paths without tracing every business-logic step?
2. Can that observability become a feedback signal for an agent runtime?

The study combines a deterministic control lane with a small real hosted-model lane. Local JSONL traces are the canonical evidence; hosted providers and any backend remain secondary integration surfaces. The scope is intentionally narrow: one fixture-backed comparison task, read-only local tools, one hosted model, bounded turn budgets, and a separate task-outcome validator.

## Evidence collected

| Evidence set | Observed result | What it establishes |
| --- | --- | --- |
| Deterministic 75-run matrix | Five conditions across three tasks and five repetitions | Controlled reconstruction and detector behavior across baseline, failure, retry, duplication, and excessive-path conditions. |
| Hosted baseline tool path | 3 model turns, 3 tool calls, 7 spans; exact structural oracle match | Shared model/tool spans reconstruct a real hosted tool topology. |
| Hosted calculator failure | Calculator error, no retry, but validated final outcome | A tool failure is not automatically a task failure. |
| Hosted lookup outage | 6 model turns, 12 failed lookups, safety cap reached | Repeated logical-operation failures and a terminating cost/path expansion are observable. |
| Outcome-aware policy | `observe_only` after valid outcome; `intervene_on_next_attempt` after terminated run | Telemetry plus a minimal independent outcome class can support proportionate post-run feedback. |

Published artifacts are under [`data/published`](../../data/published/). The human-readable sequence is recorded in [`Journal`](../../Journal/).

## Results from the real hosted runs

| Run | Model turns | Tool calls | Key evidence | Outcome / decision |
| --- | ---: | ---: | --- | --- |
| [Successful tool path](../../data/published/local-v0-hosted-tool-probe-attempt-02/analysis.json) | 3 | 3 | Two lookups, calculator, final model turn; exact baseline graph | Successful structural baseline |
| [Calculator failure](../../data/published/local-v0-hosted-tool-probe-attempt-04-validated-failure/analysis.json) | 3 | 3 | One calculator error; no retry | `answer_validation = valid`; `observe_only` |
| [Lookup outage](../../data/published/local-v0-hosted-tool-probe-attempt-05-lookup-outage/analysis.json) | 6 | 12 | Six failed attempts for each logical lookup; retry loop; cap termination | Failed/unvalidated terminal run; `intervene_on_next_attempt` |

The lookup outage consumed 4,268 input tokens, 873 output tokens, and 17,559.951 ms before the six-turn cap stopped it. The trace made clear that time was overwhelmingly provider-bound, while the local tool failures themselves were near-instant. This is the operational distinction the project needed: the expensive behavior was repeated provider reasoning around a failed dependency, not slow tool execution.

## How to read the hosted comparison

The comparison is meaningful because the same task, model boundary, and local tools were held fixed while the availability of one dependency changed. Read it as a decision guide, not as a leaderboard for the model:

```text
healthy path:        3 model turns + 3 tool calls -> task completes

one tool failure:    3 model turns + 3 tool calls -> task still validates
                      meaning: retain the failure for reliability analysis,
                      but do not force unnecessary recovery

dependency outage:   6 model turns + 12 tool calls -> safety cap stops the run
                      meaning: repeated work is consuming provider time and
                      tokens without progress; intervene before another attempt
```

The bars compare scenarios **within each metric only**. A full-width bar means “largest observed value in this column,” not that tool calls, model turns, and seconds share one scale. The most important visual contrast is therefore the outage's expansion relative to the healthy path: model turns doubled, tool calls quadrupled, and the run ended without a validated result.

The calculator-failure run is the equally important counterexample. Its tool failed, but the path did not expand and the answer was validated. That prevents the misleading rule “any tool failure means the agent failed.” The visualization earns its place in the report because it makes this contrast visible before the reader reaches the policy details.

## Answer to research question 1

**Qualified yes—OpenTelemetry can reconstruct externally observable execution semantics well enough to identify important inefficient and failed paths at reusable agent/model/tool boundaries.**

The traces recovered:

- model and tool operation sequence;
- parent-child execution topology;
- tool status and error category;
- logical operation identity, argument equivalence, and attempt count;
- retry absence and repeated retry behavior;
- model-turn expansion, token usage, and provider latency;
- terminal root status and task outcome class.

No spans were placed inside the lookup or calculator business logic. The minimal boundary contract—especially logical-operation ID, attempt number, and argument fingerprint—made retries and repeated equivalent requests attributable.

The qualification matters. Telemetry did **not** recover private reasoning, intent, or the semantic quality of model output. The root-level answer-validation class came from a separate task evaluator. For production work, that signal could come from a workflow assertion, downstream state transition, unit test, human approval, or another trusted evaluator.

## Answer to research question 2

**Qualified yes—observability can act as a safe feedback signal when action is tied to both execution evidence and task outcome.**

The two real hosted failure branches demonstrate why the policy must be proportionate:

```text
tool failure + validated outcome                 -> observe only
repeated tool failure + terminal failed outcome  -> intervene on next attempt
```

The first branch prevents needless recovery after a correct result. The second branch supports a bounded next action such as backoff, alternative data source, review, or deferred retry rather than replaying the same unavailable dependency.

This study demonstrated a **post-run** feedback decision. The six-turn cap was a preconfigured runtime safety boundary, not an analyzer-driven in-flight intervention. The deterministic lane separately demonstrates in-run retry-budget control. A future hosted study should test a shadow-mode, evidence-driven retry budget before enabling live dynamic intervention.

## What is established vs. still open

| Established in this study | Still open |
| --- | --- |
| Path reconstruction for a real hosted model/tool loop | Generalization to complex, long-horizon, or multi-agent workloads |
| Detection of real tool errors, retry loops, and cap termination | Detection quality across models and providers |
| Clear provider-versus-tool latency and token cost split | Robust cost thresholds under realistic workload variance |
| A valid outcome can override a naive failure-only policy | A real hosted invalid final response that ends naturally |
| A terminated failure path can justify next-attempt intervention | Safe online intervention using telemetry before completion |

## Conclusion

The first study supports a practical boundary: use OpenTelemetry as machine-readable evidence of how an agent executed, not as a transcript of why it reasoned as it did. At shared runtime boundaries, that evidence is sufficient to reconstruct meaningful operational behavior and to support explainable, bounded feedback decisions when paired with an independent outcome signal.

The next study should not simply add more traces. It should test whether the same compact telemetry contract remains useful across more realistic tasks and whether a hosted runtime can use timely evidence in shadow mode to prevent a repeated-failure path before the turn cap is reached.
