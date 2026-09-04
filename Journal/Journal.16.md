# Journal.16 — Credentialed hosted trace capture

## What changed

We ran the hosted portability probe with a configured API key and captured one successful OpenAI Responses API call. The local JSONL export contains one root span and one child model span. No OTLP endpoint was configured, so the local export remained the only destination.

## Key concepts

The hosted lane tests instrumentation and export behavior. It does not automatically provide a ground-truth task graph, so its first evaluation is field presence, parentage, status, usage reporting, and backend receipt.

## Why this checkpoint matters

The deterministic lane answered the controlled inference question. A real model call tests whether the telemetry boundary survives external latency, provider response metadata, and a real network path.

## Result and significance

The API request succeeded. The trace contains the expected root/model relationship, model name, provider, response ID, input tokens, output tokens, provider latency, task outcome, and `UNSET` root status. The response reported 33 input tokens, 511 output tokens, and 448 reasoning tokens within the output usage details.

The existing analyzer emitted `excessive_execution_path` because its local threshold treats output tokens of at least 300 as excessive. That finding is a portability false positive for this one-call hosted probe: the trace has one model call, depth 1, and no tool calls. The hosted result validates field capture while exposing a threshold that needs lane-specific calibration.

## Next step

Calibrate the analyzer for hosted traces by separating model reasoning-token usage from the deterministic excessive-path rule, then decide whether a hosted trace needs a different oracle or a task evaluator before diagnosis scoring.

## Work snapshot

```text
configuration check -> passed
hosted API call     -> succeeded; 2 spans captured
usage fields        -> present; 33 input / 511 output tokens
analyzer            -> excessive-path false positive requires calibration
OTLP export         -> waiting for OTEL_EXPORTER_OTLP_ENDPOINT
```

The notable constraint is cost and privacy: the hosted lane remains opt-in and its credentials never belong in the repository.

Artifacts: [local-v0-hosted-probe](../data/published/local-v0-hosted-probe/).

## Significance

The first hosted request proves that the same boundary format can carry a real provider ID, response ID, latency, and usage record. It also produces the first hosted false positive: a one-call path crossed the local 300-output-token threshold despite having depth one and no tools. That failure shows that detector portability requires lane-specific baselines rather than reuse of deterministic thresholds.

## Market thesis

AI platform teams will value an observability system that identifies distribution shifts between local tests and hosted models before alert rules reach production. False cost alarms erode trust quickly because reasoning-capable models can report usage patterns absent from scripted controls. A product that preserves raw measurements while withholding an unsupported finding has a stronger reliability proposition.

## Supporting market detail

The hosted call records two spans, 33 input tokens, 511 output tokens, 448 reasoning tokens, and a clean root. The analyzer labels it excessive solely because the local rule triggers at 300 output tokens. One model call at depth one supplies no structural evidence of an expanded path. A production buyer needs the system to retain the usage record, mark the rule as miscalibrated for this lane, and avoid opening a false incident.

## Conclusion

The first hosted trace validates field capture and invalidates direct reuse of the deterministic token threshold.
