# Journal.17 — Hosted-lane detector calibration

## What we will do

Separate hosted model usage accounting from the deterministic excessive-path threshold. Preserve raw usage details, including reasoning-token subfields, while preventing a single hosted model call from being labeled excessive solely because its output-token count is high.

## Concept to know

A threshold trained on one model lane is not automatically portable to another. Hosted responses may include reasoning tokens, provider-specific usage fields, and latency that are absent from a scripted local model. The analyzer needs a lane-aware rule or a normalized cost signal.

## Why we are doing it

The first hosted trace validated the telemetry boundary and exposed a concrete false positive. Fixing that issue is necessary before using hosted traces to discuss inefficient execution paths.

## Result at this checkpoint

Calibration has not been implemented. The current trace remains useful as a captured portability case, but its excessive-path finding should be treated as invalid for the hosted probe.

## Next step

Add a hosted probe-specific analysis rule or lane metadata, test it against the captured trace and deterministic excessive-path controls, and document which findings remain comparable across lanes.

## Work snapshot

```text
root span
└─ hosted model call
   ├─ input tokens: 33
   ├─ output tokens: 511
   └─ reasoning tokens: 448
```

The notable point is the mismatch between raw cost and path shape: high hosted output usage does not by itself prove an excessive execution path.
