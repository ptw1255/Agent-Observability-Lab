# Journal.19 — Hosted cost-envelope experiment

## What changed

We added `aol hosted-cost-probe` and ran it once. It made one higher-effort hosted request, captured the trace, and compared output tokens and duration with the saved five-run baseline using a 1.25× envelope. The result is written as `hosted_cost_envelope`, separate from analyzer findings.

The cost-stress request asks for five taxed invoice totals and a JSON result with `high` reasoning effort. It is intentionally one model call, so any envelope exceedance remains a cost observation instead of an execution-path diagnosis.

## Key concepts

A cost anomaly and an excessive execution path are different findings. A cost anomaly compares a model call with comparable calls in the same lane. An excessive path compares topology, repeated work, or abnormal depth. One can occur without the other.

## Why this checkpoint matters

The hosted baseline shows that a one-call model response naturally uses more than the deterministic token threshold. This experiment tests whether lane-specific cost evidence can be useful without collapsing it into a topology diagnosis.

## Result and significance

The cost-stress probe exceeded both baseline limits. It used 2,988 output tokens against a 630-token envelope and took 30.0 seconds against a 9.2-second envelope. The trace recorded 2,880 reasoning tokens.

Its execution shape stayed simple: one root span, one model span, depth 1, no tool calls, no errors, and no execution-path findings. This validates the separation between a cost anomaly and an excessive execution path. The observed cost is unusual for this narrow hosted baseline; the trace does not show an abnormal topology or prove that the model’s reasoning was wasteful.

## Next step

Design a hosted tool-calling experiment. It should let a real model choose or repeat read-only local tools so the project can compare hosted cost observations with observable execution topology.

## Work snapshot

```text
normal hosted probe -> 1 model call -> 360–504 output tokens
cost-stress probe   -> 1 model call -> 2,988 output tokens
cost observation    -> output and duration exceed envelope
path finding        -> none; topology is unchanged
```

The notable distinction is that both traces have the same topology. The experiment shows cost differs enough to warrant attention; it does not show that the model followed a bad path.

Artifacts: [local-v0-hosted-cost-probe](../data/published/local-v0-hosted-cost-probe/).

## Significance

The cost-stress request used 2,988 output tokens and 30.0 seconds, exceeding both 1.25× baseline envelopes while preserving the same one-model-call topology. Recording `hosted_cost_envelope` outside the path findings prevents the analyzer from inventing structural waste. The trace supports a cost anomaly and leaves the usefulness of the extra reasoning unresolved.

## Market thesis

Cost observability is a distinct vertical inside agent observability. Its target user needs to know whether spend changed because a call became larger or because the agent executed more steps. Keeping cost-envelope alerts separate from path diagnostics lets vendors route the first to FinOps and the second to reliability engineering.

## Supporting market detail

The stress run reaches 2,988 output tokens and 30.0 seconds against envelopes of 630 tokens and 9.2 seconds. Both the baseline and stress traces contain one model call at depth one, so their execution graphs are equivalent. The cost observation belongs in a FinOps or model-performance queue, while no path finding belongs in a retry or orchestration queue. This routing distinction prevents a reliability team from investigating a topology defect that the trace does not contain.

## Conclusion

The hosted stress test proves that cost anomalies and execution-path anomalies need separate findings and owners.
