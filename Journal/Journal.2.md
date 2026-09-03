# Journal.2 — Local document-answer task

## What we did

Added the second deterministic workload: a local document-answer task backed by a fixture-based retrieval tool.

The intended healthy path is:

```text
agent invocation → model: plan → local retrieval → model: answer
```

- Added the versioned `returns-policy-v1` synthetic document fixture.
- Added a deterministic `local_retrieval` tool boundary.
- Added task selection to the runtime and CLI.
- Ran all five existing conditions against the new task in tests.
- Extended the analyzer to recognize generic tool spans, not only calculator spans.
- Preserved the condition-blind telemetry contract.

## Why we are doing it

The invoice task validates a single calculator boundary. The document task tests whether the same telemetry contract works when the agent uses a retrieval-like operation and carries evidence from one boundary into the final model call.

This gives us a second topology without introducing multiple tools, distributed execution, or provider variability.

## Meaningful results at this checkpoint

Yes, as an implementation and instrumentation result, but not yet as a research conclusion.

The document task was added without:

- adding spans to business-logic branches;
- exposing the condition label in telemetry;
- changing the analyzer's telemetry-only input contract;
- making the existing invoice tests fail.

The full test suite passes: 12 tests. Both the calculator and local-retrieval tasks now produce generic boundary evidence for all five conditions, and the condition-blindness checks pass for both tasks.

## What we need to do next

- Add the two-option comparison task.
- Preserve the same five conditions and evidence contract across a multi-tool healthy path.
- Add the task's fixtures and tests.
- Begin defining the oracle and task-aware scoring inputs.
- Record the resulting implementation commit in the next journal checkpoint.

## Success check

The existing invoice task remains green, and the document task produces the expected healthy sequence and controlled anomaly findings from telemetry alone. This check passed.
