# Journal.6 — Transient-failure profile comparison

## What we did

We opened the next comparison checkpoint and defined the case to measure: the invoice task's calculator fails on its first attempt, the agent makes a recovery model call, and the calculator succeeds on its second attempt.

The expected execution path is:

```text
invoke_agent
  → chat plan
  → calculator [error]
  → chat recover
  → calculator [success]
  → chat finalize
```

The case will use the same raw-trace, projection, analyzer, and scoring commands from Journal.5.

## Concept to know

Failure diagnosis has levels:

- status shows that an operation failed;
- the span name identifies the operation;
- `error.type` describes the failure category;
- logical operation ID and attempt number connect the failure to recovery.

P0 contains status and parentage. P1 adds standard operation and error attributes. P2 adds the fields that connect two calculator spans as attempts of one logical operation.

The comparison will show whether a profile can detect a failure and whether it can explain the recovery path with enough precision to support runtime feedback.

## Why we are doing it

The baseline comparison showed healthy topology in all profiles and token recovery in P1. A transient failure tests evidence that matters during abnormal execution.

This case also separates two claims. Detecting a failed span is easier than attributing a later successful span to recovery from that failure.

## Result at this checkpoint

No new profile comparison has been run yet.

The checkpoint is ready to close when each profile reports:

- the failed calculator span;
- the recovery path;
- the number of attempts it can identify;
- `tool_failure` precision and recall;
- the evidence fields missing from that profile.

## Next step

- Extend the oracle builder for the known transient condition.
- Run and publish the three projections.
- Compare detector findings and attempt attribution.
- Record the measured result in Journal.7.
