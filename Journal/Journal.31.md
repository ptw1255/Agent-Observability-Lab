# Journal.31 — First-study final report

## What changed

Consolidated the deterministic control work and real hosted-model experiments into a first-study report. The report connects each conclusion to published traces, analyses, or feedback decisions and distinguishes direct observations from proposed next experiments.

The consolidation matters because the project no longer consists only of implementation checkpoints. It now has a coherent evidence chain: a controlled local baseline, a real hosted successful path, a tool failure with a validated outcome, and a repeated outage that reached a safety cap. Those runs demonstrate both restraint and intervention using the same telemetry contract.

## Key concepts

A final report is not a claim that every question is closed. It is a scope boundary. It states exactly what the experiment supports, what it does not support, and what a next study must change to add information rather than merely more volume.

For this project, the central boundary is between execution evidence and semantic evaluation. OpenTelemetry reconstructs the former. A trusted external signal supplies the latter. The feedback policy becomes credible only when it respects both.

## Why this checkpoint matters

The real hosted lookup outage completed the missing intervention branch without exceeding the six-turn safety budget. Continuing to run the same simple task would add cost but little new evidence. Consolidation turns the work into a reusable study rather than an open-ended sequence of API calls.

## Result and significance

The first study has a qualified answer to both research questions:

- Boundary-level OpenTelemetry reconstructs important externally observable agent behavior without per-business-logic instrumentation.
- That evidence can support proportionate post-run feedback when combined with an independent outcome class.

The report also records the strongest limitation: telemetry does not reveal hidden reasoning or establish answer correctness on its own.

## Next step

Treat a new study as a new protocol. The highest-value extension is a hosted shadow-mode retry budget across several tasks or models, where the system recommends an earlier stop but does not yet intervene. That would test timeliness and generalization rather than repeating the completed first-study scenario.

## Work snapshot

```text
real hosted branch 1
  calculator failure + valid answer -> observe only

real hosted branch 2
  repeated lookup failures + cap termination -> intervene on next attempt

study conclusion
  execution telemetry + outcome signal -> explainable feedback decision
```

The notable result is practical rather than mystical: observability did not read the model's mind. It exposed enough of the runtime's behavior to make a safer next decision.

## Significance

The report closes the first protocol with two real hosted branches: calculator failure plus valid outcome leads to observation, while repeated lookup failure plus unavailable outcome leads to intervention on the next attempt. The same telemetry contract supports both decisions, which demonstrates proportionality rather than a collection of unrelated rules. Further work must change task, model, or runtime conditions to test generalization.

## Market thesis

The study can be packaged as an independent agent-execution benchmark and a service-led diagnostic pilot. Observability vendors such as Arize could value the trace profiles, sealed oracle, controlled failures, and write-back findings as validation of their instrumentation. End customers will value the work when it reduces diagnosis time or prevents repeated paid calls under their own workloads.
