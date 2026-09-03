# Decision Record

## DR-001 — Canonical local telemetry

- **Decision:** Keep immutable local JSONL as the canonical telemetry input.
- **Reason:** Analysis remains reproducible and independent of an observability vendor or backend query behavior.
- **Consequence:** OTLP backends are inspection and ingestion targets, not sources of scoring truth.

## DR-002 — Separate oracle

- **Decision:** Store fault labels, expected outcomes, and actual execution graphs outside analyzer-visible telemetry.
- **Reason:** The reconstruction and diagnosis must be blind to the answers they are evaluated against.
- **Consequence:** Analysis and scoring are separate commands with separate input permissions.

## DR-003 — Progressive evidence profiles

- **Decision:** Analyze each run as P0 structural, P1 standard GenAI, and P2 boundary-enriched telemetry.
- **Reason:** The comparison identifies the smallest evidence contract that provides useful diagnosis.
- **Consequence:** Derived projections must be schema-validated and reproducible from the raw trace.

## DR-004 — Local-first, not local-only

- **Decision:** Require a deterministic local control lane and allow optional Docker, hosted-model, and OTLP integrations.
- **Reason:** The control protects internal validity while the integration lane tests realism and portability.
- **Consequence:** Hosted results are reported separately and never pooled with deterministic results.

## New decision template

### DR-XXX — Title

- **Date:**
- **Decision:**
- **Context:**
- **Evidence:**
- **Alternatives:**
- **Reason:**
- **Consequences:**
