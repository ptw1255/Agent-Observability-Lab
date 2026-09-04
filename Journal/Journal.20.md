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

The adapter is ready for one controlled run. Its local components are tested without credentials: the schemas expose only the two intended functions, option lookup reads only versioned fixtures, calculation produces a deterministic answer, and a simulated three-turn provider exchange verifies that tool spans are children of their requesting model turns. There is no hosted result yet, so we have not established that a real model will follow the intended sequence or that the resulting trace supports all planned inferences.

## Next step

Run the command once in the terminal that has `OPENAI_API_KEY`, then inspect `analysis.json` and `raw-trace.jsonl`. Confirm the number and order of model/tool spans before attempting failure injection or feedback.

## Work snapshot

```text
root agent span
  -> hosted model turn 1
       -> local option lookup (option A)
       -> local option lookup (option B)
  -> hosted model turn 2
       -> local calculator
  -> hosted model turn 3 -> final answer
```

The precise order may vary: the model can request both lookups in one turn or one at a time. What matters is that every observed tool request has a model-turn parent, a tool name, a stable fingerprint, and an outcome. That is the evidence we will test next: can it reconstruct the externally visible path without recording private reasoning content?
