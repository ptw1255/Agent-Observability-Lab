# Journal.18 — Hosted cost baseline and trace coverage

## What we did

We added `aol hosted-baseline`, which runs a chosen number of hosted probes from one credentialed terminal session. It saves each raw trace and analysis, then writes a `summary.json` with minimum, mean, and maximum values for model calls, input tokens, output tokens, duration, and span count.

No additional hosted calls were made while building this command. The key remains outside the repository and is required only when the command is run locally.

## Concept to know

Cost anomaly detection needs a reference distribution. One 511-token response may be normal for a reasoning-capable model, while the same value may be unusual for a scripted local model. The baseline must match the model, prompt, runtime lane, and task shape.

## Why we are doing it

Journal.17 fixed a concrete false positive. This checkpoint replaces the removed threshold with evidence that could support a lane-specific hosted cost rule.

## Result at this checkpoint

The hosted baseline has not been collected. One successful hosted trace exists and validates the instrumentation contract; the new command makes the next collection repeatable.

## Next step

Run five probes in the same configured terminal session, inspect the summary, and decide whether a hosted cost detector is justified.

## Work snapshot

```text
hosted trace 1 -> 1 model call, 511 output tokens, 8.8 seconds
hosted trace N -> collect comparable measurements
baseline       -> define a hosted cost envelope
```

The notable question is whether variation comes from the model, the network, or the task. The trace records all three imperfectly, so the baseline must stay narrow.
