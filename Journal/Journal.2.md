# Journal.2 — Next task: local document answer

## What we are going to do

Add the second deterministic workload: a local document-answer task backed by a fixture-based retrieval tool.

The intended healthy path is:

```text
agent invocation → model: plan → local retrieval → model: answer
```

The task should use a small synthetic document set and ask a question with one known answer. The retrieval tool must return deterministic fixture evidence and no network request.

## Why we are doing it

The invoice task validates a single calculator boundary. The document task tests whether the same telemetry contract works when the agent uses a retrieval-like operation and carries evidence from one boundary into the final model call.

This gives us a second topology without yet introducing multiple tools, distributed execution, or provider variability.

## Meaningful results at this checkpoint

Not yet. This is the next implementation task, so there are no new observations or scores.

The result will be meaningful if the new task can be added without:

- adding spans to business-logic branches;
- exposing the condition label in telemetry;
- changing the analyzer's telemetry-only input contract;
- making the existing invoice tests fail.

## What we need to do next

- Add a versioned local document fixture.
- Add a deterministic retrieval tool adapter.
- Add task selection to the runtime and CLI.
- Run the five conditions against the new task in tests.
- Extend the oracle shape to record the new healthy operation graph.
- Record the resulting implementation commit in the next journal checkpoint.

## Success check

The existing invoice task remains green, and the document task produces the expected healthy sequence and controlled anomaly findings from telemetry alone.
