# Journal.3 — Two-option comparison task

## What changed

- Added `ComparisonTask` with expected answer `option-a-v1`.
- Added versioned local fixtures for options A and B.
- Added deterministic `local_lookup` operations.
- Reused the calculator boundary for the final comparison.
- Applied all five execution conditions to the multi-tool task.
- Added task selection to the CLI.
- Added tests for operation order, distinct lookup identities, and duplicate-call detection.

Implementation commit: `56ff9ac`.

## Why we did it

The invoice task has one calculator call. The document task has one retrieval call. The comparison task has two required lookups followed by a calculation.

That healthy multi-tool path gives the analyzer a control case for redundancy detection. Two tool calls can be required even when they are close together in the trace.

## Result at this checkpoint

Fifteen tests passed across the three tasks.

The baseline comparison trace contains two different lookup data-source IDs and two different argument fingerprints. The analyzer reports no redundant-tool finding.

The redundant condition repeats option B with the same normalized arguments. The analyzer reports `candidate_redundant_tool_use`.

All five conditions run through the comparison task, and the telemetry tests keep the condition labels out of analyzer input.

This completes the three-task deterministic workload. It does not provide reconstruction scores yet.

## Next step

Define the sealed oracle schema, telemetry schema, and P0/P1/P2 projections. Then score operation sequences, topology, resource totals, and findings across the three tasks.
