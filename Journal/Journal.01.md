# Journal.01 — First instrumented task

## What changed

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

## Key concepts

A span records one timed operation. A parent span ID links a child operation to the operation that created it. Those IDs form the execution tree that the analyzer later reconstructs.

Boundary instrumentation records the start and end of reusable interfaces such as agent invocation, model calls, and tool calls. It does not describe every line inside the task implementation. The experiment is testing whether these interfaces expose enough structure for diagnosis.

The analyzer receives the trace file. The injected condition stays in the test harness and future oracle. This separation makes the diagnosis an inference from evidence.

## Why this checkpoint matters

The project needed a controlled case with a fixed answer and one tool. That keeps the first debugging loop small:

```text
agent behavior → spans → JSONL → analyzer finding
```

The first slice also established the privacy rule. The telemetry may say that a tool was unavailable. It must not say that the experiment intentionally ran the `transient_tool_failure` condition.

## Result and significance

Six tests passed.

The runtime emitted agent, model, and tool spans. The analyzer detected the four controlled anomaly patterns. Parent span IDs preserved the basic operation tree.

A blindness test found a leak in the first implementation. The exception type and message exposed the injected condition. The runtime now emits generic failure evidence such as `tool_unavailable`.

This validates the measurement apparatus for one task. It does not establish general execution reconstruction.

## Next step

Add a local document-answer task with a deterministic retrieval tool. Preserve the five conditions, boundary instrumentation, and analyzer input contract.

## Significance

The first slice proves that one reusable boundary contract can produce an execution tree and four anomaly signatures from a fixed task. The failed blindness test is part of the result: exception text initially leaked the injected condition, and replacing it with `tool_unavailable` restored a legitimate inference problem. Future detector scores depend on this correction because leaked condition names would make perfect accuracy meaningless.

## Market thesis

The first target user is the engineer on call for a production agent. That user needs a trace to name the failed model or tool operation without exposing experimental labels or private reasoning. A product that preserves this blindness boundary can support incident diagnosis while reducing the privacy cost of agent observability.
