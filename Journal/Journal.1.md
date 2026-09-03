# Journal.1 — First task and first telemetry slice

## What we did

- Added a deterministic invoice-total task.
- Added five controlled execution conditions:
  - baseline;
  - transient tool failure;
  - retry loop;
  - redundant tool use;
  - excessive execution path.
- Instrumented reusable agent, model, and tool boundaries with OpenTelemetry spans.
- Exported spans to local JSONL.
- Added a telemetry-only analyzer.
- Added tests that verify failure detection and ensure condition labels do not leak into telemetry.

## Why we did it

We needed the smallest end-to-end slice that could test the central research method: can an analyzer infer execution behavior from telemetry without being given the scenario label or ground truth?

The invoice task is intentionally simple. A simple task makes it easier to distinguish instrumentation defects from analyzer defects before adding more complex execution graphs.

## Meaningful results at this checkpoint

Yes, but only as an apparatus result—not yet as a research conclusion.

- The runtime can emit model and tool boundary spans.
- The analyzer can detect a tool failure, retry loop, candidate duplicate call, and excessive path in controlled cases.
- The blindness test caught and helped remove a telemetry leak where the injected condition was visible through the exception details.
- The test suite passes: 6 tests.

We cannot yet claim that OpenTelemetry reliably reconstructs agent execution in general. We have only validated that the first controlled example and measurement boundary work as intended.

## What we need to do next

- Add the local document-answer task.
- Preserve the same five conditions and boundary instrumentation contract.
- Define its healthy operation graph and sealed oracle record.
- Add task-specific tests without changing the analyzer's input contract.
- Then add the two-option comparison task.

## Reference

Implementation milestone: commit `a5e36d7`.
