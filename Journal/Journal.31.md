# Journal.31 — First-study final report

## What changed

Consolidated the deterministic control work and real hosted-model experiments into a first-study report. The report connects each conclusion to published traces, analyses, or feedback decisions and distinguishes direct observations from proposed next experiments.

The consolidation matters because the project no longer consists only of implementation checkpoints. It now has a coherent evidence chain: a controlled local baseline, a real hosted successful path, a tool failure with a validated outcome, and a repeated outage that reached a safety cap. Those runs demonstrate both restraint and intervention using the same telemetry contract.

## Key concepts

A final report sets the scope boundary. It states what the experiment supports, what remains unsupported, and what a next study must change to add information beyond more volume.

For this project, the central boundary is between execution evidence and semantic evaluation. OpenTelemetry reconstructs the former. A trusted external signal supplies the latter. The feedback policy becomes credible only when it respects both.

## Why this checkpoint matters

The real hosted lookup outage completed the missing intervention branch within the six-turn safety budget. Continuing to run the same simple task would add cost and little new evidence. Consolidation turns the work into a reusable study with a closed first protocol.

## Result and significance

The first study has a qualified answer to both research questions:

- Boundary-level OpenTelemetry reconstructs important externally observable agent behavior without per-business-logic instrumentation.
- That evidence can support proportionate post-run feedback when combined with an independent outcome class.

The report also records the strongest limitation: telemetry does not reveal hidden reasoning or establish answer correctness on its own.

## Next step

Treat a new study as a new protocol. The highest-value extension is a hosted shadow-mode retry budget across several tasks or models, where the system recommends an earlier stop and leaves execution unchanged. That would test timeliness and generalization across new conditions.

## Work snapshot

```text
real hosted branch 1
  calculator failure + valid answer -> observe only

real hosted branch 2
  repeated lookup failures + cap termination -> intervene on next attempt

study conclusion
  execution telemetry + outcome signal -> explainable feedback decision
```

The trace exposed enough runtime behavior to support a safer next decision while private model reasoning remained unavailable.

## Significance

The report closes the first protocol with two real hosted branches: calculator failure plus valid outcome leads to observation, while repeated lookup failure plus unavailable outcome leads to intervention on the next attempt. The same telemetry contract supports both decisions, which demonstrates one proportional policy across two observed branches. Further work must change task, model, or runtime conditions to test generalization.

## Market thesis

The study can be packaged as an independent agent-execution benchmark and a service-led diagnostic pilot. Observability vendors such as Arize could value the trace profiles, sealed oracle, controlled failures, and write-back findings as validation of their instrumentation. End customers will value the work when it reduces diagnosis time or prevents repeated paid calls under their own workloads.

## Supporting market detail

The report contains an exact hosted baseline, a failed calculator with a valid result, and a lookup outage terminated after six repeated turns. Those paths exercise observation and intervention recommendations under one telemetry contract. A vendor partner can run the P0/P1/P2 protocol through its own exporter and write detector results back as trace annotations. A customer pilot should measure median time to attributed diagnosis and accepted finding rate before pricing recurring software.

## Conclusion

The completed study is ready to serve as both a vendor benchmark and a customer diagnostic pilot.
