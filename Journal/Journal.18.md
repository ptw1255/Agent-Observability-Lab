# Journal.18 — Hosted cost baseline and trace coverage

## What we did

We added `aol hosted-baseline`, then ran five hosted probes from one credentialed terminal session. Each run saved a raw trace and analysis. The command wrote a `summary.json` with minimum, mean, and maximum values for model calls, input tokens, output tokens, duration, and span count.

The key remained in the terminal session. The published artifacts contain trace metadata and response IDs, not the API key or prompt text.

## Concept to know

Cost anomaly detection needs a reference distribution. One 511-token response may be normal for a reasoning-capable model, while the same value may be unusual for a scripted local model. The baseline must match the model, prompt, runtime lane, and task shape.

## Why we are doing it

Journal.17 fixed a concrete false positive. This checkpoint replaces the removed threshold with evidence that could support a lane-specific hosted cost rule.

## Result at this checkpoint

The five-run hosted baseline is complete. Every run had one root span, one hosted model span, depth 1, one model call, no tool calls, and no analyzer findings.

Input tokens were constant at 33. Output tokens ranged from 360 to 504, with a mean of 449. Duration ranged from 4.1 to 7.4 seconds, with a mean of 6.1 seconds. The provider response metadata reported reasoning-token use on each run, which explains much of the output-token variation for this fixed prompt.

This is a narrow baseline for one model, one prompt, and one runtime shape. It is enough to show that the earlier 300-token deterministic threshold would have created false positives for normal hosted calls.

## Next step

Define a hosted cost-envelope rule from this baseline, then test it on a deliberately more expensive hosted prompt before using it as a finding or feedback signal.

## Work snapshot

```text
five hosted traces -> one model call and two spans each
output tokens      -> 360 to 504; mean 449
duration           -> 4.1 to 7.4 seconds; mean 6.1 seconds
baseline           -> ready for a narrow cost-envelope experiment
```

The notable result is stable execution shape with variable cost. The trace separates model-call count from token and latency variation, but it cannot fully separate provider reasoning behavior from network effects.

Artifacts: [local-v0-hosted-baseline](../data/published/local-v0-hosted-baseline/).
