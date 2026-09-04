# Journal.20 — Hosted tool-calling execution topology

## What changed

Built the hosted tool-calling adapter, but did not run it against the API. The adapter gives a hosted model exactly two read-only local capabilities: `lookup_option`, which returns a versioned option fixture and its delivered total, and `calculate_lower_cost`, which compares the two totals. The model receives their strict input schemas, requests tools through the Responses API, and the runtime returns each result using the call ID the model supplied.

The run is deliberately bounded. It allows at most six model turns, writes one raw JSONL trace and one telemetry-only analysis file, and records neither the API key, prompt text, nor response text in the trace. A normal successful run should use several turns, but the six-turn cap is the maximum paid-request exposure if the model behaves unexpectedly.

## Key concepts

The hosted probes so far have one model span and no tool spans. They validate provider usage capture but do not test whether OpenTelemetry can reconstruct a model-driven tool path. Tool calling adds the decision boundary where retries, duplicate requests, failed tools, and execution topology become observable.

A tool span is nested under the model span that requested it. This parent-child relationship does not claim that the model's private reasoning is visible. It records a narrower, defensible claim: the provider returned a particular function-call request, and the local runtime then executed a named tool with structured arguments. The trace keeps a normalized argument fingerprint, logical-operation ID, and attempt number instead of raw business payloads.

## Why this checkpoint matters

The deterministic lane demonstrated path reconstruction and feedback with controlled tools. The cost experiment demonstrated that hosted cost must be interpreted separately from topology. This step joins those threads with one real model-driven, read-only tool path.

## Result and significance

The real hosted run completed successfully. It produced seven spans: one root agent span, three hosted-model spans, two local lookup spans, and one calculator span. The first model turn requested both lookups, the second requested the calculator, and the third produced the final answer. Every tool span has the model turn that requested it as its parent. All three tools succeeded on their first attempt; there were no error spans and no analyzer findings.

The seven-span trace answers the hosted reconstruction question for one successful task. Runtime-level telemetry reconstructs which provider turns occurred, which tools the model selected, which fixtures they addressed, their order, their parentage, and whether they succeeded. The trace contains no evidence about hidden reasoning, and one successful path does not test hosted retry or redundancy detection.

The run took 10,092.240 ms. The three hosted model turns accounted for almost all elapsed time: roughly 4,167 ms, 4,442 ms, and 1,456 ms of provider latency. The local tools together took about 0.135 ms. The measurements assign almost all latency to the provider calls. Total recorded usage was 1,587 input tokens and 653 output tokens, including 512 recorded reasoning tokens. Input tokens grew from 141 to 542 to 904 because the stateless `store: false` loop explicitly carries prior function-call context forward.

## Next step

Define a compact hosted-path oracle for this successful task, then compare future hosted traces against it. That gives the next failure-mode experiment a clear reference: the expected three model turns, two lookups, one calculation, first-attempt success, and depth of two.

## Work snapshot

```text
invoke_agent hosted-tool-agent                     10,092.240 ms
  -> chat hosted-model, turn 1                     4,167.422 ms provider latency
       -> execute_tool local_lookup, option A      0.059 ms
       -> execute_tool local_lookup, option B      0.029 ms
  -> chat hosted-model, turn 2                     4,441.574 ms provider latency
       -> execute_tool calculator                  0.047 ms
  -> chat hosted-model, turn 3                     1,455.592 ms provider latency
```

The notable pattern is not merely that tools appear in the trace. The trace preserves the causal boundary: turn 1 caused both lookups, turn 2 caused calculation, and turn 3 closed the task. That is enough to distinguish this efficient path from a future retry, duplicate lookup, or extra model-turn path without recording private reasoning content.

## Significance

This is the first real model-selected tool graph in the study. The trace attributes both lookups to turn one, the calculator to turn two, and completion to turn three while showing that provider calls consumed almost all 10.1 seconds. Input growth from 141 to 542 to 904 tokens also exposes the cost of carrying stateless conversation context between turns.

## Market thesis

Teams operating customer-facing agents need to separate provider latency from local tool latency before assigning incident ownership. This trace gives an AI platform lead that split without storing model reasoning or business payloads. The same causal graph can support provider reviews, context-growth controls, and later failure diagnosis.
