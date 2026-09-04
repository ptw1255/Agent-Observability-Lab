# Journal.03 — Two-option comparison task

## What changed

We added `ComparisonTask` with two local option fixtures:

- option A delivered cost: `120 + 10 = 130`;
- option B delivered cost: `115 + 25 = 140`.

The expected answer is `option-a-v1`. The healthy execution path is:

```text
invoke_agent → chat plan → local_lookup A → local_lookup B → calculator → chat finalize
```

The five conditions now run against this multi-tool graph. The redundant condition repeats the lookup for option B with the same normalized arguments. The baseline calls option A and option B once each.

We added tests for task selection, operation order, data-source identity, distinct argument fingerprints, and duplicate-call detection.

Implementation commit: `8e4ecfa`.

## Key concepts

Repeated calls do not automatically mean redundant work. A healthy comparison requires two lookup calls. The analyzer needs operation identity and argument evidence before it can flag a repeated call as a candidate duplicate.

The comparison task gives us two cases:

```text
healthy:   lookup A + lookup B
redundant: lookup A + lookup B + lookup B
```

The topology and fingerprints provide the observable difference. The word `candidate` remains important because telemetry alone cannot prove that a repeated successful call had zero semantic value in every real agent.

## Why this checkpoint matters

The first two tasks contain one main tool call. They cannot test whether the analyzer understands a required multi-tool path.

This task creates a legitimate reason for multiple tool calls. That establishes the control case needed for redundancy detection and moves the workload closer to a real agent workflow.

## Result and significance

Fifteen tests passed across the three tasks.

The baseline comparison trace contains two different lookup data-source IDs and two different argument fingerprints. The analyzer reports no redundant-tool finding.

The redundant condition repeats option B with the same normalized arguments. The analyzer reports `candidate_redundant_tool_use`.

All five conditions run through the comparison task, and condition labels remain absent from analyzer input.

This completes the three-task deterministic workload. Reconstruction scores have not been generated yet.

## Next step

Define the telemetry schema, sealed oracle schema, P0/P1/P2 projections, and scoring contract.

## Significance

This checkpoint creates the negative control required for duplicate detection. Two lookup spans are healthy because they address different options; the third lookup is suspicious because it repeats option B with the same fingerprint. The distinction prevents a detector from equating tool-call volume with waste and establishes why argument identity must accompany call counts.

## Market thesis

Tool-heavy agents create a specific observability segment around execution efficiency. Buyers will reject detectors that flag every multi-tool workflow as waste because valid agents often need several data sources. A product that distinguishes necessary fan-out from repeated equivalent work can serve workflow-automation and customer-support teams that pay for both model calls and external tools.

## Supporting market detail

The healthy comparison requires lookup A, lookup B, and one calculator call, so three tools alone cannot establish waste. The injected run adds a second option-B lookup with the same fingerprint and no new input dependency. This creates a concrete procurement question: can the observability system distinguish required multi-source work from an equivalent repeated request? Teams paying per search, database query, or SaaS action can attach a unit cost to the confirmed duplicate after human or task-level review.

## Conclusion

Duplicate-call value starts with argument identity and ends with task-aware confirmation.
