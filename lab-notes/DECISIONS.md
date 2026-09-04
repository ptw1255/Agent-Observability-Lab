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

## DR-005 — Outcome-aware feedback is post-run and proportionate

- **Date:** 2026-09-03
- **Decision:** Use tool-failure evidence together with a minimal root-level outcome class for post-run feedback decisions. A valid outcome after a tool failure produces `observe_only`; invalid or unavailable outcome produces `intervene_on_next_attempt`; absent validation produces `insufficient_evidence`.
- **Context:** A real hosted calculator failure had no retry but still produced a validated correct answer. A tool-failure-only policy would have requested needless recovery.
- **Evidence:** `data/published/local-v0-hosted-tool-probe-attempt-04-validated-failure/analysis.json` and `feedback-decision.json`.
- **Alternatives:** Intervene on every tool failure; store full model responses to decide outcome; make no feedback decision.
- **Reason:** The selected policy preserves dependency reliability evidence while avoiding an unsupported intervention after a validated task.
- **Consequences:** The policy needs a trustworthy task-outcome source and currently acts after completion. It does not claim to evaluate private reasoning or replace semantic evaluation.

## DR-006 — Treat a capped, terminated run as intervention evidence

- **Date:** 2026-09-03
- **Decision:** Recommend `intervene_on_next_attempt` when telemetry shows a terminated run through root `ERROR` or failed task outcome, even if no answer-validation class is available.
- **Context:** The lookup-outage run reached its six-turn safety cap after twelve failed tool calls, so no final model response existed to validate.
- **Evidence:** `data/published/local-v0-hosted-tool-probe-attempt-05-lookup-outage/analysis.json` and `feedback-decision.json`.
- **Alternatives:** Mark missing validation as insufficient evidence; automatically rerun the same unavailable lookup path; ignore root termination if individual errors are already present.
- **Reason:** A bounded runtime termination is direct evidence that the current execution did not reach a validated outcome. Retrying the identical dependency immediately would repeat the observed failure pattern.
- **Consequences:** The policy now distinguishes an incomplete trace from a terminal failed run. The recommended action remains a next-attempt decision, not a claim that the model's private reasoning was understood.

## New decision template

### DR-XXX — Title

- **Date:**
- **Decision:**
- **Context:**
- **Evidence:**
- **Alternatives:**
- **Reason:**
- **Consequences:**
