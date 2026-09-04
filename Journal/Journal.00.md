# Journal.00 — Project setup

## What changed

Created the public repository `ptw1255/Agent-Observability-Lab` and defined the first research plan.

The project asks:

> Can OpenTelemetry reconstruct an AI agent's execution behavior well enough to identify inefficient or failed execution paths without instrumenting every business-logic step manually?

The repository now contains:

- the research and experiment plan;
- the learning guide and core variable definitions;
- data collection, provenance, and publication rules;
- experiment and decision-log templates;
- a numbered journal for checkpoint history;
- a local-first implementation path.

The initial experiment is bounded to three deterministic tasks, five execution conditions, five repetitions, and three evidence profiles. Optional hosted-model and Docker/OTLP integrations are planned after the deterministic control works.

## Key concepts

The project has two separate tracks:

1. **Execution measurement:** collect spans for agent, model, and tool boundaries.
2. **Execution interpretation:** infer sequences, topology, failures, retries, cost, and candidate inefficiencies from those spans.

The project does not treat telemetry as a record of hidden chain-of-thought. It measures observable runtime behavior. Answer correctness requires a separate evaluator.

The data flow is:

```text
frozen protocol → raw telemetry + sealed oracle → projections → analyzer → scored report
```

The oracle contains the known condition and expected behavior. The analyzer receives telemetry projections without the oracle. That separation makes the result auditable.

## Why this checkpoint matters

The repository needed a fixed research boundary before implementation. Without that boundary, the project could drift into a trace viewer, a provider comparison, or a collection of ad hoc agent demos.

The local-first scope keeps the first result reproducible on a MacBook Pro. The deterministic control makes it possible to distinguish an instrumentation problem from model variability. The optional integration lane leaves room to test real providers and observability backends after the core measurement works.

The journal creates a running record of decisions, evidence, and next actions. Each later checkpoint should let a new reader understand how the project reached its current state.

## Result and significance

The project has a public home, a defined research question, a bounded v0 protocol, and a data-management policy.

No agent experiment had been run when this checkpoint was created. `Journal.01` begins the implementation history with the first instrumented task.

## Next step

Build the first deterministic agent slice around the invoice task. Record the implementation and its evidence in `Journal.01`.

## Significance

This checkpoint fixed the unit of proof before code existed: a trace-derived claim must be scored against a separate oracle. That decision prevents later demonstrations from treating visible telemetry as its own validation source. It also creates a reusable evaluation method that can compare instrumentation profiles, model providers, and agent runtimes without changing the research question.

## Market thesis

The agent-observability market will value a reproducible proof standard because vendors currently compete on how much telemetry they collect and display. Buyers still need evidence that a given field changes diagnosis accuracy or incident response. A benchmark that identifies the minimum sufficient telemetry can influence platform requirements, procurement tests, and integration standards.
