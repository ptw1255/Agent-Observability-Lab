# Journal.01 — First instrumented task

## What we did

We built the first complete measurement path around `InvoiceTask`. The deterministic agent calculates the price of three items after tax and returns a fixed answer of `64.64`.

The runtime emits one root span for the agent invocation and child spans for each model and calculator operation. The first healthy trace is:

```text
invoke_agent → chat plan → execute_tool calculator → chat finalize
```

We added five controlled conditions so the same task can produce different execution shapes:

- baseline;
- one transient calculator failure followed by recovery;
- three failed calculator attempts;
- a repeated successful calculator call;
- nested reflection steps that increase depth and token use.

The JSONL exporter writes one record per ended span. The analyzer groups records by trace ID, orders them by start time, counts operations, and reports error spans.

Implementation commit: `a5e36d7`.

## Concept to know

A span records one timed operation. A parent span ID links a child operation to the operation that created it. Those IDs form the execution tree that the analyzer later reconstructs.

Boundary instrumentation records the start and end of reusable interfaces such as agent invocation, model calls, and tool calls. It does not describe every line inside the task implementation. The experiment is testing whether these interfaces expose enough structure for diagnosis.

The analyzer receives the trace file. The injected condition stays in the test harness and future oracle. This separation makes the diagnosis an inference from evidence.

## Why we did it

The project needed a controlled case with a fixed answer and one tool. That keeps the first debugging loop small:

```text
agent behavior → spans → JSONL → analyzer finding
```

The first slice also established the privacy rule. The telemetry may say that a tool was unavailable. It must not say that the experiment intentionally ran the `transient_tool_failure` condition.

## Result at this checkpoint

Six tests passed.

The runtime emitted agent, model, and tool spans. The analyzer detected the four controlled anomaly patterns. Parent span IDs preserved the basic operation tree.

A blindness test found a leak in the first implementation. The exception type and message exposed the injected condition. The runtime now emits generic failure evidence such as `tool_unavailable`.

This validates the measurement apparatus for one task. It does not establish general execution reconstruction.

## Next step

Add a local document-answer task with a deterministic retrieval tool. Preserve the five conditions, boundary instrumentation, and analyzer input contract.
