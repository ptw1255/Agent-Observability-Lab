# Journal.19 — Hosted cost-envelope experiment

## What we will do

Define a narrow hosted cost-envelope rule from the five-run baseline, then run one deliberately more expensive hosted prompt. Compare output tokens, reasoning-token usage, duration, and execution shape against the baseline without treating a normal one-call response as an execution-path failure.

## Concept to know

A cost anomaly and an excessive execution path are different findings. A cost anomaly compares a model call with comparable calls in the same lane. An excessive path compares topology, repeated work, or abnormal depth. One can occur without the other.

## Why we are doing it

The hosted baseline shows that a one-call model response naturally uses more than the deterministic token threshold. This experiment tests whether lane-specific cost evidence can be useful without collapsing it into a topology diagnosis.

## Result at this checkpoint

The hosted cost-envelope rule has not been implemented or tested.

## Next step

Choose a conservative envelope, capture one higher-effort hosted prompt, and report the result as a cost observation rather than a reasoning-path conclusion.

## Work snapshot

```text
normal hosted probe -> 1 model call -> 360–504 output tokens
higher-effort probe -> 1 model call -> compare cost with baseline
```

The notable distinction is that both traces can have the same topology. The experiment asks whether cost differs enough to warrant attention, not whether the model followed a bad path.
