# Journal.11 — Observability findings as a runtime feedback signal

## What we will do

Use the completed matrix to define a small feedback experiment. A runtime will receive structured observability findings after a step or run, then decide whether to continue, retry, suppress duplicate work, or stop. The same task should be run with feedback disabled and enabled.

## Concept to know

Detection and intervention are separate claims. A trace analyzer may correctly identify a retry loop, but that does not show that feeding the finding back into the runtime improves execution. Feedback can also create new failure modes, such as stopping too early or hiding a legitimate repeated call.

The feedback signal must include evidence, not only a label. A useful record should identify the finding type, confidence or rule version, affected span or operation, and the measurements that caused the finding.

## Why we are doing it

The matrix answers how much execution behavior can be reconstructed from telemetry in a controlled setting. The project’s follow-up question is whether that reconstructed evidence can become an input to agent control logic without manually instrumenting every business branch.

## Result at this checkpoint

The feedback experiment has not been run. The completed matrix establishes the detection baseline that the intervention experiment should use.

## Next step

Choose one bounded intervention first—retry-budget protection or duplicate-tool suppression—define its safety rule and success metrics, and run it against the same deterministic failure conditions.

## Work snapshot

The current evidence pipeline is:

```text
agent spans
  -> restricted evidence profile
  -> telemetry-only analyzer
  -> structured finding + evidence
  -> optional runtime feedback policy
```

The notable boundary is the arrow from finding to policy. Everything before it has been measured in the matrix. The next experiment must test whether the final arrow improves behavior without turning an imperfect detector into an unsafe controller.
