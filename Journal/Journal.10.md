# Journal.10 — Repeated local matrix and cross-condition synthesis

## What we will do

Run the planned deterministic matrix with five repetitions for each of the three tasks and five conditions. Store each raw trace and its oracle, then produce P0, P1, and P2 analyses and scores for every run.

Aggregate the results by condition and evidence profile. Report sequence recovery, topology recovery, resource measurement, finding precision and recall, attempt attribution, and run-to-run variation.

## Concept to know

A single trace demonstrates that a detector can work once. Repeated trials test whether the result is stable. This distinction matters for latency, token totals, and any threshold-based detector because one run can be unusually fast, slow, or otherwise unrepresentative.

The matrix also creates controls. Baseline runs show what normal execution looks like. Injected conditions show whether the analyzer separates a known failure mode from that normal path. The oracle supplies labels for evaluation; it is not evidence available to the analyzer during inference.

## Why we are doing it

The first profile comparisons established local examples: custom argument identity mattered for duplicate detection, while structure was enough for the deliberately excessive path. The matrix tests whether those conclusions survive across tasks, conditions, and repeated runs.

This is the point where the project moves from “can this trace be explained?” to “how reliably can the same evidence support an explanation?”

## Result at this checkpoint

The repeated matrix has not been run yet. The existing published comparisons are single-run demonstrations and should not be treated as estimates of detector performance.

## Work snapshot

For each matrix checkpoint, this section will show one representative trace shape and the measurements that matter. The snapshot should make it easy to see the difference between a normal path and an injected path before reading the aggregate tables.

```text
task-condition / repetition
├─ representative span tree
├─ sequence and topology summary
├─ model calls / tool calls
├─ input tokens / output tokens / duration
└─ findings and the evidence supporting them
```

The notable point to preserve is the link between a finding and its evidence. For example, a retry finding should point to repeated failed tool spans and attempt numbers; an excessive-path finding should point to depth, call count, token cost, or latency. A label without that evidence is not a useful observability result.

## Next step

Implement the matrix runner and aggregation report, run the 75 deterministic trials, inspect failures in the collection workflow, and record the first cross-condition findings in Journal.11.
