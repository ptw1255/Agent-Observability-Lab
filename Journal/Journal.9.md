# Journal.9 — Excessive-path profile comparison

## What we will do

Run the invoice task with the `excessive_path` condition. The baseline calculates the invoice total with one model call before the tool and one after it. The injected condition adds nested reflection steps and extra model calls before the calculator runs, while keeping the task and answer unchanged.

Pass the same raw trace through P0, P1, and P2. Score each projection against a sealed oracle that describes the longer execution path and expected resource totals.

## Concept to know

An execution can be correct and still be inefficient. A trace may expose this through indirect signals such as unusually deep nesting, more model calls, more output tokens, or greater elapsed time. These signals describe execution cost and shape; they do not explain whether the extra reasoning was useful.

The detector will emit `excessive_execution_path` when the configured v0 thresholds are crossed. The thresholds are an experimental rule, not a universal definition of inefficiency. They must be evaluated against a known baseline and reported with the underlying measurements.

## Why we are doing it

The earlier experiments tested failures and duplicate tool work. This condition tests a different limitation: whether observability can identify a costly path even when no tool fails and the final answer remains correct.

The profile comparison will show whether the signal comes from structure alone, standard GenAI attributes such as token counts, or the additional boundary metadata in P2.

## Result at this checkpoint

This experiment has not been run yet. A useful result will include the measured depth, model-call count, output tokens, duration, and profile-specific finding precision and recall.

## Next step

Generate and publish the excessive-path trace, oracle, projections, analyses, and score files. Then use the next journal checkpoint to interpret whether the extra path is detectable and which telemetry fields provide the evidence.
