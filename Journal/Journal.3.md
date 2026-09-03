# Journal.3 — Two-option comparison task

## What will change

Add a third deterministic task with this healthy operation sequence:

```text
invoke_agent → chat plan → lookup A → lookup B → calculator → chat finalize
```

The task will use local fixtures with known values and a fixed expected answer.

## Why we are doing it

The first task has one calculator call. The second has one retrieval call. The comparison task adds multiple tool identities and a deeper valid graph.

This gives the analyzer a case where multiple tool calls are required. That distinction is needed before testing whether repeated work is redundant.

## Result at this checkpoint

No implementation result yet. This checkpoint defines the next task.

The task is ready to close when:

- all five conditions run through the same runtime;
- the healthy sequence and parentage are correct;
- lookup and calculator spans use the existing boundary contract;
- condition labels stay out of telemetry;
- the 12 existing tests still pass.

## Next step

- Add versioned fixtures for lookup A and lookup B.
- Add deterministic lookup operations.
- Add task selection and expected-answer checks.
- Test all five conditions on the multi-tool graph.
- Record the implementation commit in `Journal.4`.
