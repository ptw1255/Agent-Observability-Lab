# Journal.14 — Interim meaning checkpoint

## What we did

We paused implementation after the first complete evidence and feedback slices and reviewed the published results against the original question:

> Can OpenTelemetry reconstruct an AI agent’s execution behavior well enough to identify inefficient or failed reasoning paths without manually instrumenting every business-logic step?

The evidence base now includes five repeated runs for each of three tasks and five controlled conditions: 75 task-condition runs and 225 P0/P1/P2 profile analyses. We also compared a retry-budget feedback policy with feedback disabled and checked it against transient recovery and required multi-step work.

## Concept to know

There are three different claims in this project:

1. **Reconstruction:** Can telemetry recover the observed execution graph and resource measurements?
2. **Diagnosis:** Can rules identify a known failure or inefficiency from that evidence?
3. **Control:** Can a runtime safely use the diagnosis to change what it does?

The project has meaningful evidence for the first two claims in this deterministic harness. It has only an initial result for the third. A correct detector is not automatically a safe controller.

## Why we did it

Without this checkpoint, it would be easy to mistake perfect scores in a small harness for a general result about AI agents. The purpose of the pause is to state exactly what has been learned, what remains uncertain, and whether the next experiment is worth doing.

## Result at this checkpoint

Yes, the work is meaningful—but as a feasibility study, not as a broad benchmark.

The strongest result is the evidence-profile comparison:

- Span names and parentage were enough to reconstruct the controlled execution topology and detect failures, retry behavior, and the deliberately excessive path.
- Standard model/tool and token attributes made resource use measurable.
- Redundant tool use was not detectable from P0 or P1 in this setup. P2’s argument fingerprint enabled the duplicate finding across the matrix.
- The five repetitions reproduced the same conclusions, so these results are stable within the deterministic harness.
- The duplicate-suppression intervention removed the injected repeated lookup while preserving the baseline comparison path and answer.

The feedback result is also meaningful but narrow. Stopping a terminal retry loop after two failures reduced the invoice case from 3 tool calls, 4 model calls, and 84 output tokens to 2 tool calls, 2 model calls, and 44 output tokens. The task remained explicitly failed. Feedback did not change transient recovery or the required two-lookup comparison control.

What the project has **not** shown:

- that telemetry reveals hidden chain-of-thought or private model intent;
- that the thresholds generalize to real agents;
- that a real hosted model will produce the same topology or failure signatures;
- that a feedback policy is safe under non-idempotent tools, changing external state, or ambiguous duplicates;
- that the measured latency is representative—the current sleeps and scripted model are deliberately local and deterministic.

The correct interim conclusion is: **runtime telemetry can provide machine-readable evidence for reconstructing and diagnosing several observable execution-path problems, but semantic interpretation and safe intervention still require task context, boundary metadata, and separate validation.**

## Next step

Run a small hosted-model or real-OTLP integration lane. Keep the integration lane separate from the deterministic evidence claims.

## Work snapshot

```text
75 deterministic runs
  -> 225 evidence-profile analyses
  -> topology: reconstructed consistently
  -> failures/retries/excessive path: detected consistently
  -> redundant tool use: requires argument fingerprint
  -> retry feedback: reduced work in terminal loop
  -> safety controls: successful recovery and required lookups preserved
```

The notable point is the boundary between observation and meaning. The trace reliably records what spans happened, in what structure, with what status and cost. It does not independently establish why the model chose that path or whether a repeated action was semantically justified.
