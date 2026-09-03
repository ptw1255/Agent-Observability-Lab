# Learning and Interpretation Guide

## What this project should teach

The project measures where telemetry stops being raw operational data and becomes useful evidence about agent execution.

The learning path is:

1. Run a known task and record sealed ground truth.
2. Observe the run only at shared agent, model, and tool boundaries.
3. Reconstruct the operation sequence, topology, failures, and resource use from telemetry.
4. Compare the reconstruction with ground truth.
5. Repeat the analysis with progressively richer evidence profiles.
6. Decide which findings are accurate and timely enough to inform a runtime.

This separates three different questions:

- **What happened?** Calls, ordering, errors, retries, depth, latency, and tokens.
- **Was it abnormal?** Behavior relative to the same task's healthy baseline.
- **Why did the model choose it?** Generally not recoverable from operational telemetry.

## How to interpret the evidence profiles

| Outcome | What it would teach us |
| --- | --- |
| P0 performs well | Generic tracing is sufficient for much of the execution structure. |
| P1 materially improves on P0 | Standard GenAI attributes add meaningful diagnostic value. |
| P2 materially improves on P1 | A small boundary-level correlation contract is necessary. |
| Only direct failures are reliable | Telemetry supports reliability diagnosis better than inefficiency diagnosis. |
| P2 still performs poorly | Boundary telemetry is too coarse for the target behavior, or the behavior leaves insufficient observable evidence. |

The primary result should be a capability map, not a single yes/no score. A likely shape is:

| Question | Expected recoverability |
| --- | --- |
| Which operations occurred? | High |
| How were they connected? | High when trace context is preserved |
| Where did a tool fail? | High |
| Was it retried? | High with correlation evidence |
| Was work unusually expensive? | Baseline-relative inference |
| Was a repeated call unnecessary? | Candidate inference requiring context |
| Why did the model select an action? | Not recoverable |
| Was the final answer correct? | Requires a separate evaluator |

## Core definition record

| Variable | What it means / measures | Why it is important |
| --- | --- | --- |
| Run ID | Opaque identifier for one agent execution | Correlates spans without revealing the test condition. |
| Span | One timed operation, such as invoking a model or tool | Basic unit used to reconstruct execution. |
| Model call count | Number of model invocations in a run | Reveals repeated or unexpectedly long model interaction. |
| Tool call count | Number of tool invocations in a run | Supports workload, retry, and duplication analysis. |
| Latency | Duration of a span or complete run | Identifies slow operations and end-to-end impact. |
| Token usage | Model input and output tokens | Approximates model cost and execution expansion. |
| Status / error type | Success, failure, and failure category | Locates failures and distinguishes their causes. |
| Attempt number | Position of an attempt within one logical operation | Makes retry behavior directly correlatable. |
| Logical operation ID | Identifier shared by attempts serving the same intent | Separates retries from unrelated repeated calls. |
| Argument fingerprint | Non-reversible signature of normalized tool inputs | Detects repeated equivalent calls without exporting raw arguments. |
| Execution topology | Parent-child graph connecting spans | Shows causal structure, branching, and failure propagation. |
| Maximum depth | Longest parent-child chain in a run | Highlights runaway nesting or excessive delegation. |
| Critical-path latency | Duration of the slowest dependent execution path | Identifies operations that determine completion time. |
| Task outcome | Correct, incorrect, or failed result from a separate evaluator | Prevents operational success from being confused with answer correctness. |
| Tool failure | Tool error inferred from status or exception evidence | Tests whether telemetry can attribute a concrete failure. |
| Retry loop | Repeated failing attempts that consume the retry budget | Represents a common costly and potentially preventable failure mode. |
| Candidate redundant tool use | Equivalent successful calls with no observed new dependency | Flags possible waste while preserving uncertainty about necessity. |
| Excessive execution path | Depth, calls, tokens, or latency outside the healthy task envelope | Captures inefficient behavior without claiming access to hidden reasoning. |
| Reconstruction fidelity | Agreement between telemetry-derived structure and ground truth | Quantifies how much execution semantics telemetry recovered. |
| Baseline false positive | Healthy run incorrectly diagnosed as abnormal | Measures whether a detector is safe enough to trust. |

## From diagnosis to feedback

A useful runtime feedback signal must pass four tests:

```text
accurate diagnosis → timely detection → attributable cause → safe bounded action
```

A retry loop detected after a run is useful for debugging but not control. The same loop detected before another retry could support a bounded intervention. The follow-up study should therefore test recommendations first, then shadow mode, and only then interventions such as stopping after a retry or depth budget.

The final project should answer:

1. Which execution facts are recoverable?
2. What is the minimum telemetry required?
3. Which diagnoses remain uncertain or impossible?
4. Which signals, if any, are safe enough to influence future execution?
