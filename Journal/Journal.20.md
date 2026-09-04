# Journal.20 — Hosted tool-calling execution topology

## What we did

Built the hosted tool-calling adapter, but did not run it against the API. The adapter gives a hosted model exactly two read-only local capabilities: `lookup_option`, which returns a versioned option fixture and its delivered total, and `calculate_lower_cost`, which compares the two totals. The model receives their strict input schemas, requests tools through the Responses API, and the runtime returns each result using the call ID the model supplied.

The run is deliberately bounded. It allows at most six model turns, writes one raw JSONL trace and one telemetry-only analysis file, and records neither the API key, prompt text, nor response text in the trace. A normal successful run should use several turns, but the six-turn cap is the maximum paid-request exposure if the model behaves unexpectedly.

## Concept to know

The hosted probes so far have one model span and no tool spans. They validate provider usage capture but do not test whether OpenTelemetry can reconstruct a model-driven tool path. Tool calling adds the decision boundary where retries, duplicate requests, failed tools, and execution topology become observable.

A tool span is nested under the model span that requested it. This parent-child relationship does not claim that the model's private reasoning is visible. It records a narrower, defensible claim: the provider returned a particular function-call request, and the local runtime then executed a named tool with structured arguments. The trace keeps a normalized argument fingerprint, logical-operation ID, and attempt number instead of raw business payloads.

## Why we are doing it

The deterministic lane demonstrated path reconstruction and feedback with controlled tools. The cost experiment demonstrated that hosted cost must be interpreted separately from topology. This step joins those threads with one real model-driven, read-only tool path.

## Result at this checkpoint

The real hosted run completed successfully. It produced seven spans: one root agent span, three hosted-model spans, two local lookup spans, and one calculator span. The first model turn requested both lookups, the second requested the calculator, and the third produced the final answer. Every tool span has the model turn that requested it as its parent. All three tools succeeded on their first attempt; there were no error spans and no analyzer findings.

This is meaningful evidence for a narrow version of the research question. Without manually tracing each line of option-lookup or arithmetic logic, the runtime-level telemetry reconstructs the externally visible execution path: which provider turns occurred, which tools the model selected, which fixtures they addressed, their order, their parentage, and whether they succeeded. It does not reveal whether the model's hidden reasoning was sound, nor does one successful path establish that retry or redundancy detectors work with a hosted model.

The run took 10,092.240 ms. The three hosted model turns accounted for almost all elapsed time: roughly 4,167 ms, 4,442 ms, and 1,456 ms of provider latency. The local tools together took about 0.135 ms. Telemetry therefore makes the cost split visible: this path's time was provider-bound, not tool-bound. Total recorded usage was 1,587 input tokens and 653 output tokens, including 512 recorded reasoning tokens. Input tokens grew from 141 to 542 to 904 because the stateless `store: false` loop explicitly carries prior function-call context forward.

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
