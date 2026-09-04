# Journal.17 — Hosted-lane detector calibration

## What changed

We separated hosted usage accounting from the deterministic excessive-path threshold. The analyzer now identifies the runtime lane from the root span or the standard provider attribute. For the hosted lane, high output tokens remain a reported measurement but do not by themselves create `excessive_execution_path`.

The hosted probe now records the provider’s reasoning-token subfield when it is present in future Responses API usage records. The captured trace predates that field addition, so its published JSONL preserves the original evidence.

## Key concepts

A threshold trained on one model lane is not automatically portable to another. Hosted responses may include reasoning tokens, provider-specific usage fields, and latency that are absent from a scripted local model. The analyzer needs a lane-aware rule or a normalized cost signal.

## Why this checkpoint matters

The first hosted trace validated the telemetry boundary and exposed a concrete false positive. Fixing that issue is necessary before using hosted traces to discuss inefficient execution paths.

## Result and significance

The recalibrated analyzer reports no findings for the captured hosted trace. It retains the 33 input tokens, 511 output tokens, 8.8-second duration, one model call, and depth 1 as evidence for later cost analysis.

The deterministic excessive-path tests still pass. Their deep, multi-call paths remain findings because the structural thresholds are unchanged.

## Next step

Capture a second hosted trace or a hosted tool-calling run, then compare field coverage and define a hosted cost baseline before introducing any hosted cost anomaly detector.

## Work snapshot

```text
root span
└─ hosted model call
   ├─ input tokens: 33
   ├─ output tokens: 511
   └─ reasoning tokens: 448
```

The notable point is the mismatch between raw cost and path shape: high hosted output usage does not by itself prove an excessive execution path. The hosted trace has one model span and no repeated work.

## Significance

The recalibration removes the unsupported finding while preserving 33 input tokens, 511 output tokens, 448 reasoning tokens, 8.8 seconds, one model call, and depth one for later analysis. Deterministic excessive paths still trigger on structural expansion, so the change narrows only the hosted token rule. This is a concrete example of correcting a detector without deleting the evidence that exposed its error.

## Market thesis

The buyer for production agent monitoring needs low false-positive rates more than aggressive anomaly counts. Lane-aware calibration lets an AI platform team compare scripted tests, hosted models, and future providers without imposing one token threshold on all of them. A vendor can turn that capability into a model-onboarding check and a defensible alert policy.
