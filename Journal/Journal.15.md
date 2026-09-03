# Journal.15 — Hosted-model and OTLP integration lane

## What we will do

Run a small integration lane using one hosted model adapter and an OTLP-compatible observability backend, while retaining the deterministic lane as the scoring source of truth. Repeat only the smallest task and condition set needed to test portability of the telemetry contract.

## Concept to know

Portability has two parts: the runtime can export the expected telemetry fields, and the analyzer can interpret traces whose timing, model behavior, and topology vary. A hosted model may choose different tools or produce different token and latency distributions, so deterministic oracle scores cannot be transferred automatically.

## Why we are doing it

The local experiments establish what the project can infer under controlled execution. This lane tests whether the boundary instrumentation and evidence projections remain usable when model calls and export infrastructure are real.

## Result at this checkpoint

The integration lane has not been run. It requires configured model and observability credentials and separate cost and privacy handling.

## Next step

Choose one provider, define the smallest task adapter, confirm OTLP export, record the actual model and backend versions, and compare trace completeness and field coverage before attempting diagnosis scores.

## Work snapshot

```text
deterministic lane -> sealed oracle -> scored diagnosis
hosted lane        -> OTLP backend -> field/shape inspection first
```

The notable boundary is evaluation. The hosted lane can test instrumentation portability; it cannot inherit deterministic correctness labels without a separate task evaluator.
