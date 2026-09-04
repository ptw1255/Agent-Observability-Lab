# Journal.19 — Hosted cost-envelope experiment

## What we did

We added `aol hosted-cost-probe`. It makes one higher-effort hosted request, captures the trace, and compares output tokens and duration with the saved five-run baseline using a 1.25× envelope. The result is written as `hosted_cost_envelope`, separate from analyzer findings.

The cost-stress request asks for five taxed invoice totals and a JSON result with `high` reasoning effort. It is intentionally one model call, so any envelope exceedance remains a cost observation instead of an execution-path diagnosis.

## Concept to know

A cost anomaly and an excessive execution path are different findings. A cost anomaly compares a model call with comparable calls in the same lane. An excessive path compares topology, repeated work, or abnormal depth. One can occur without the other.

## Why we are doing it

The hosted baseline shows that a one-call model response naturally uses more than the deterministic token threshold. This experiment tests whether lane-specific cost evidence can be useful without collapsing it into a topology diagnosis.

## Result at this checkpoint

The rule and one-call probe are implemented but have not been run. Running it requires the same credentialed terminal session and incurs one API call.

## Next step

Run the one-call probe, inspect the cost observation, and report whether it exceeds the baseline envelope without calling it an inefficient path.

## Work snapshot

```text
normal hosted probe -> 1 model call -> 360–504 output tokens
higher-effort probe -> 1 model call -> compare cost with baseline
```

The notable distinction is that both traces can have the same topology. The experiment asks whether cost differs enough to warrant attention, not whether the model followed a bad path.
