# Journal.1 — First instrumented task

## What changed

- Added `InvoiceTask`, a deterministic calculation task.
- Added five execution conditions: baseline, transient tool failure, retry loop, redundant tool use, and excessive path.
- Added OpenTelemetry spans at the agent, model, and calculator boundaries.
- Added local JSONL span export.
- Added a telemetry-only analyzer.
- Added tests for operation order, tool errors, anomaly findings, and label isolation.

Implementation commit: `a5e36d7`.

## Why we did it

The project needed one complete path from agent execution to telemetry to diagnosis. The invoice task has one tool and a fixed answer, which makes failures in instrumentation easy to locate.

The analyzer had to infer the failure from spans. The fault condition stayed in the test harness and oracle.

## Result at this checkpoint

Six tests passed.

The first slice established four facts:

- The runtime emits agent, model, and tool boundary spans.
- The analyzer detects tool failure, retry loops, candidate duplicate calls, and excessive paths in controlled cases.
- Parent span IDs preserve the basic operation tree.
- A test caught a condition leak in exception details. The emitted evidence now uses generic values such as `tool_unavailable`.

This result validates the measurement setup for one task. It does not establish general execution reconstruction.

## Next step

Add the local document-answer task with a deterministic retrieval tool. Keep the same five conditions, span boundaries, and analyzer input contract.
