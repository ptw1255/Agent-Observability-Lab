# Journal.16 — Credentialed hosted trace capture

## What we will do

Run the hosted portability probe with a configured API key and capture one successful response. If an OTLP endpoint is available, send the same spans to it while retaining the local JSONL export.

## Concept to know

The hosted lane tests instrumentation and export behavior. It does not automatically provide a ground-truth task graph, so its first evaluation is field presence, parentage, status, usage reporting, and backend receipt.

## Why we are doing it

The deterministic lane answered the controlled inference question. A real model call tests whether the telemetry boundary survives external latency, provider response metadata, and a real network path.

## Result at this checkpoint

No credentialed call has been made. The current machine has no hosted API key or OTLP endpoint configured.

## Next step

Configure credentials outside the repository, run the probe once, inspect the trace, and record whether the expected root/model relationship and usage fields are present.

## Work snapshot

```text
configuration check -> passed
hosted API call     -> waiting for OPENAI_API_KEY
OTLP export         -> waiting for OTEL_EXPORTER_OTLP_ENDPOINT
```

The notable constraint is cost and privacy: the hosted lane remains opt-in and its credentials never belong in the repository.
