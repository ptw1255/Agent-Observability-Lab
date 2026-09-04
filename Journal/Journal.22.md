# Journal.22 — Controlled hosted calculator failure

## What changed

Added one optional fault mode to the hosted tool adapter: the first call to the local calculator returns a generic `tool_unavailable` error instead of a result. The hosted model still receives the same comparison task, the same tool schemas, and the same option fixtures. The runtime does not alter the model prompt after the failure; it returns a structured error through the ordinary function-call-output channel and lets the model decide what to do next.

The failed calculator call is still a normal tool boundary in the trace. It has the calculator tool name, the same logical-operation ID as a later retry, the same normalized argument fingerprint, an error status, and attempt number 1. If the model asks for the calculator again, that second span receives attempt number 2. The raw trace deliberately does not contain the fault-mode label. The analyzer must infer a failure from observable span status and error attributes, not from an experiment label.

We tested this loop locally with a simulated provider exchange. The simulated model made two lookups, encountered one calculator failure, retried the calculator, and then answered. The resulting telemetry had four model turns, four tool calls, one tool error, attempt numbers `[1, 1, 1, 2]`, and one `tool_failure` finding. This verifies the adapter's evidence contract before a paid hosted run.

## Key concepts

A controlled failure is an intervention, not a hidden ground-truth label embedded in telemetry. We know that the first calculator call is forced to fail because the experiment harness controls it. The analyzer does not receive that knowledge. It sees only what a production observer would see: a named tool operation ended in error, followed by subsequent model and tool activity.

This separation is essential. If a condition name such as `first_calculator_failure` appeared in a span attribute, detecting the failure would be trivial and scientifically uninteresting. Instead, the evidence comes from error status, causal placement, logical-operation identity, argument fingerprint, and attempt sequence.

## Why this checkpoint matters

The successful baseline showed that telemetry reconstructs one efficient hosted path. A diagnostic system must also describe deviations from that path. This experiment introduces one controlled deviation: a reusable tool boundary fails once while every other part of the hosted task remains fixed.

The baseline oracle gives us a specific comparison. We expect a new error span and an extra model/tool turn relative to the successful path. The question is whether the trace makes that recovery visible without manual instrumentation inside the calculator's arithmetic logic.

## Result and significance

The implementation is ready, tested locally, and has not made a paid API request. The local test establishes that the instrumentation produces a recoverable-failure trace when the provider chooses to retry. It cannot establish that the real hosted model will retry within the turn budget; that behavior is the observation the next run will measure.

## Next step

Run the hosted comparison task once with the first-calculator failure enabled and an eight-turn cap. Inspect the trace and score it against an explicit recovery oracle. The run should reveal whether the hosted model retries, changes its plan, or terminates after receiving the tool error.

## Work snapshot

```text
baseline:  lookup A + lookup B -> calculator succeeds -> answer
failure:   lookup A + lookup B -> calculator errors -> model observes error
expected recovery signal:       -> calculator retries as attempt 2 -> answer

telemetry evidence: error status + same logical operation + same argument fingerprint
```

The harness guarantees the injected error. The live result will record what the model does after the error and whether the trace explains that behavior.

## Significance

The simulated provider test proves that the hosted adapter can represent a failed calculator, correlate a second attempt, and produce one `tool_failure` finding before spending money on a live run. It also fixes the experimental variable: the prompt, tools, fixtures, and runtime stay constant while only calculator availability changes. The live result will measure model response to failure after instrumentation has passed its local check.

## Market thesis

Observability vendors can use controlled fault injection to test whether their agent traces support recovery analysis. The target user is a platform engineer validating an agent before production, not only an on-call engineer reviewing an outage. A packaged failure probe can turn integration testing into evidence about retry behavior and missing telemetry fields.
