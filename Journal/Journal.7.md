# Journal.7 — Retry-loop profile comparison

## What we will do

Run one invoice case where the calculator fails three times and the runtime exhausts its retry budget.

The expected path contains:

```text
plan → calculator error → retry decision → calculator error → retry decision → calculator error → retry decision
```

The root agent span should end with a failed task outcome.

## Concept to know

A retry loop is an execution pattern, not one error. The analyzer needs repeated attempts, repeated failure evidence, and a relationship between those attempts.

The current runtime does not call a model provider. `chat scripted-model` spans come from a local deterministic Python method. Its token counts are fixed test values, and a short local delay supplies measurable duration. Calculator and retrieval operations are also local functions. Retry failures come from controlled `ToolExecutionError` exceptions, which OpenTelemetry records as exception events inside the tool spans.

This makes the current result an instrumentation and analyzer result. It does not measure real model behavior. The hosted-model lane will replace the scripted model adapter after the deterministic comparisons are complete.

P0 can count failed tool spans and observe the terminal root status. P1 can identify the tool and error type. P2 can show that the failures share one logical operation and consume attempts one through three.

The comparison will show whether retry-loop detection depends on custom attempt metadata or can operate from repeated span structure alone.

## Why we are doing it

The transient case tested recovery after one failure. The retry-loop case tests repeated failure with no successful recovery.

This is the failure pattern most likely to support a runtime action such as stopping after a retry budget is exhausted.

## Result at this checkpoint

No retry-loop profile comparison has been run yet.

The checkpoint is ready to close when each profile records:

- repeated failed calculator spans;
- terminal root failure;
- retry-loop finding precision and recall;
- attempt sequence recoverability;
- the evidence required to attribute all attempts to one operation.

## Next step

- Extend the oracle builder for the retry-loop graph.
- Run and publish P0, P1, and P2 projections.
- Compare loop detection, root outcome, and attempt attribution.
- Record the measured result in Journal.8.
