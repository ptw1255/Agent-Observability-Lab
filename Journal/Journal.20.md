# Journal.20 — Hosted tool-calling execution topology

## What we will do

Add a small hosted-model task with read-only local tools. The model will receive a comparison prompt and tool schemas for option lookup and arithmetic. Capture model calls, tool calls, arguments, retries, and parentage from a real hosted execution.

## Concept to know

The hosted probes so far have one model span and no tool spans. They validate provider usage capture but do not test whether OpenTelemetry can reconstruct a real model-driven tool path. Tool calling adds the decision boundary where retries, duplication, and execution topology become observable.

## Why we are doing it

The deterministic lane demonstrated path reconstruction and feedback with controlled tools. The cost experiment demonstrated that hosted cost must be interpreted separately from topology. This step joins those threads with one real model-driven, read-only tool path.

## Result at this checkpoint

The hosted tool-calling adapter has not been implemented. It will require additional paid API calls and should use a small fixed budget.

## Next step

Define the two tool schemas, cap model turns, record normalized argument fingerprints, run one baseline task, and inspect the trace before adding failure injection or feedback.

## Work snapshot

```text
hosted model -> local option lookup -> hosted model -> local calculator -> answer
```

The notable question is whether the trace captures the model-to-tool boundary well enough to reconstruct what happened without recording private reasoning content.
