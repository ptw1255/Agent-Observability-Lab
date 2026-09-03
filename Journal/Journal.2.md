# Journal.2 — Local document-answer task

## What changed

- Added `DocumentTask` with the expected answer `30 days`.
- Added the versioned `returns-policy-v1` fixture.
- Added the `local_retrieval` tool boundary.
- Added task selection to the runtime and CLI.
- Applied all five execution conditions to the document task.
- Updated the analyzer to accept any `execute_tool` span.
- Added cross-task tests for expected answers and condition-label isolation.

Implementation commit: `56ff9ac`.

## Why we did it

The invoice task covers one calculator call. The document task adds a retrieval operation and a fixture-backed evidence source. This tests whether the same boundary contract works across two tool types.

The task stays local and deterministic. The retrieval tool reads one synthetic document and makes no network request.

## Result at this checkpoint

Twelve tests passed across the two tasks.

The document task preserves the expected healthy sequence:

```text
invoke_agent → chat plan → local_retrieval → chat answer
```

The analyzer identifies the controlled findings from document-task telemetry, and the exported spans contain no condition labels. The existing invoice tests remain green.

This adds a second validated workload. It does not provide P0/P1/P2 scores or a conclusion about OpenTelemetry coverage.

## Next step

Add the two-option comparison task. It will use two lookup tools and a calculator, then test whether the analyzer can distinguish a legitimate multi-tool path from redundant tool use.
