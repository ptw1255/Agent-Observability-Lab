# Journal.14 — Interim meaning checkpoint

## What changed

We paused implementation after the first complete evidence and feedback slices and reviewed the published results against the original question:

> Can OpenTelemetry reconstruct an AI agent’s execution behavior well enough to identify inefficient or failed reasoning paths without manually instrumenting every business-logic step?

The evidence base now includes five repeated runs for each of three tasks and five controlled conditions: 75 task-condition runs and 225 P0/P1/P2 profile analyses. We also compared a retry-budget feedback policy with feedback disabled and checked it against transient recovery and required multi-step work.

## Key concepts

There are three different claims in this project:

1. **Reconstruction:** Can telemetry recover the observed execution graph and resource measurements?
2. **Diagnosis:** Can rules identify a known failure or inefficiency from that evidence?
3. **Control:** Can a runtime safely use the diagnosis to change what it does?

The deterministic matrix supplies evidence for reconstruction and diagnosis. The three feedback experiments supply one intervention result and two safety controls. Controller safety still requires broader task and tool coverage.

## Why this checkpoint matters

Without this checkpoint, it would be easy to mistake perfect scores in a small harness for a general result about AI agents. The purpose of the pause is to state exactly what has been learned, what remains uncertain, and whether the next experiment is worth doing.

## Result and significance

The work supports a feasibility conclusion within the deterministic harness. It does not yet support a cross-framework or production benchmark.

The strongest result is the evidence-profile comparison:

- Span names and parentage were enough to reconstruct the controlled execution topology and detect failures, retry behavior, and the deliberately excessive path.
- Standard model/tool and token attributes made resource use measurable.
- Redundant tool use was not detectable from P0 or P1 in this setup. P2’s argument fingerprint enabled the duplicate finding across the matrix.
- The five repetitions reproduced the same conclusions, so these results are stable within the deterministic harness.
- The duplicate-suppression intervention removed the injected repeated lookup while preserving the baseline comparison path and answer.

Stopping a terminal retry loop after two failures reduced the invoice case from 3 tool calls, 4 model calls, and 84 output tokens to 2 tool calls, 2 model calls, and 44 output tokens. The task remained explicitly failed. Feedback did not change transient recovery or the required two-lookup comparison control.

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

## Significance

This checkpoint converts perfect local scores into a bounded conclusion and names the remaining sources of uncertainty. The strongest result is field-specific: structure supports topology and several failure findings, standard attributes restore resource accounting, and argument fingerprints support duplicate candidates. The feedback evidence supports one cost-saving action and two safety controls, which justifies a hosted portability test rather than a production claim.

## Market thesis

The agent-observability market needs capability maps that separate reconstruction, diagnosis, and control. Buyers can use those layers to decide whether they need a trace viewer, a diagnostic engine, or a runtime policy. The study is most useful to teams moving from dashboards to automated action because it states where evidence stops supporting the next decision.

## Supporting market detail

The local matrix provides 225 scored analyses for reconstruction and diagnosis, while feedback evidence covers one stopped loop, one preserved recovery, and one preserved multi-tool baseline. That imbalance shows where product maturity differs: the analyzer has repeated controlled evidence, and the controller has three narrow cases. A buyer can adopt the analysis layer before granting runtime authority. The next hosted lane tests exporter and model portability without weakening the local claims.

## Conclusion

The evidence supports diagnostic adoption now and limits automated control to experiments with explicit safety cases.
