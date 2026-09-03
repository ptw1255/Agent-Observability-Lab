# Journal.3 — Next task: two-option comparison

## What we are going to do

Add the third deterministic workload: a comparison that uses two lookup tools and a calculator.

The intended healthy path is:

```text
agent invocation → model: plan → lookup A → lookup B → calculator → model: finalize
```

The task will use local synthetic fixtures with known values and a deterministic answer. It should exercise a deeper valid topology and multiple tool identities without introducing parallel execution yet.

## Why we are doing it

The invoice task tests one calculator boundary, and the document task tests retrieval plus answer generation. The comparison task tests whether the same telemetry and detector logic can reconstruct a multi-tool path and distinguish legitimate multiple calls from redundant calls.

## Meaningful results at this checkpoint

Not yet. This is the next implementation task.

The result will be meaningful if the task can be added while preserving:

- the same five controlled conditions;
- boundary-only instrumentation;
- condition-blind analyzer input;
- correct operation ordering and parentage;
- passing tests for the first two tasks.

## What we need to do next

- Add versioned lookup fixtures for the two options.
- Add deterministic lookup and calculator tool adapters or compose the existing calculator boundary.
- Add task selection and expected-answer evaluation.
- Test all five conditions on the new multi-tool topology.
- Start capturing task-specific healthy graph definitions for the future oracle.
