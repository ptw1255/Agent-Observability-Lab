# Journal.18 — Hosted cost baseline and trace coverage

## What we will do

Capture a small set of hosted probe runs and compare their model usage, latency, span shape, and provider fields. Use the resulting distribution to define a hosted cost baseline without borrowing deterministic token thresholds.

## Concept to know

Cost anomaly detection needs a reference distribution. One 511-token response may be normal for a reasoning-capable model, while the same value may be unusual for a scripted local model. The baseline must match the model, prompt, runtime lane, and task shape.

## Why we are doing it

Journal.17 fixed a concrete false positive. This checkpoint replaces the removed threshold with evidence that could support a lane-specific hosted cost rule.

## Result at this checkpoint

The hosted baseline has not been collected. One successful hosted trace exists and validates the instrumentation contract.

## Next step

Run several probes in the same configured terminal session, summarize field coverage and variation, and decide whether a hosted cost detector is justified.

## Work snapshot

```text
hosted trace 1 -> 1 model call, 511 output tokens, 8.8 seconds
hosted trace N -> collect comparable measurements
baseline       -> define a hosted cost envelope
```

The notable question is whether variation comes from the model, the network, or the task. The trace records all three imperfectly, so the baseline must stay narrow.
