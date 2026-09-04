# Journal.15 — Hosted-model and OTLP integration lane

## What changed

We added a hosted portability probe that sends one invoice prompt to the OpenAI Responses endpoint, records a root span and model span in the same JSONL format, and optionally exports the spans to the endpoint in `OTEL_EXPORTER_OTLP_ENDPOINT`. The probe uses `OPENAI_API_KEY` from the environment and keeps the deterministic lane as the scoring source of truth.

The probe has two modes. `aol hosted --check-only` reports configuration without making a network request. A normal run requires the API key and writes the response usage fields, model identifier, provider latency, and response ID when the request succeeds. It does not score the hosted answer against the deterministic oracle.

## Key concepts

Portability has two parts: the runtime can export the expected telemetry fields, and the analyzer can interpret traces whose timing, model behavior, and topology vary. A hosted model may choose different tools or produce different token and latency distributions, so deterministic oracle scores cannot be transferred automatically.

## Why this checkpoint matters

The local experiments establish what the project can infer under controlled execution. This lane tests whether the boundary instrumentation and evidence projections remain usable when model calls and export infrastructure are real.

## Result and significance

The credential-free configuration check ran successfully. Docker is installed, but the first credentialed attempt from the Mac’s standalone Python installation stopped at local TLS certificate verification before reaching the API. No model response or external telemetry export was recorded. The integration extra now includes `certifi` and keeps certificate verification enabled.

The code path is ready for a credentialed run. The probe follows the official OpenAI API key and Responses API configuration described in the [OpenAI quickstart](https://platform.openai.com/docs/quickstart/make-your-first-api-request).

## Next step

Configure one hosted model and, if used, one OTLP endpoint. Run the probe, record model and backend versions, and compare trace completeness and field coverage before attempting diagnosis scores.

## Work snapshot

```text
deterministic lane -> sealed oracle -> scored diagnosis
hosted lane        -> OTLP backend -> field/shape inspection first
```

The notable boundary is evaluation. The hosted lane can test instrumentation portability; it cannot inherit deterministic correctness labels without a separate task evaluator. The current snapshot confirms configuration only.

Artifacts: [local-v0-hosted-probe](../data/published/local-v0-hosted-probe/).

## Significance

The credential-free check validates configuration and the failed credentialed attempt identifies a concrete portability dependency: the local Python certificate chain. Adding `certifi` while retaining certificate verification fixes the environment without weakening transport security. The absence of a successful model call at this checkpoint keeps the claim limited to code-path readiness.

## Market thesis

Observability integrations compete on time to first valid trace, so certificate, credential, and exporter failures are part of the product experience. Developer-platform teams value a check-only mode because it exposes configuration blockers before paid calls begin. A market-ready diagnostic package should treat setup validation as a first-class deliverable, especially for self-managed environments.
