# Journal.10 — Repeated local matrix and cross-condition synthesis

## What changed

We implemented and ran the deterministic matrix with five repetitions for each of the three tasks and five conditions. That produced 75 task-condition runs. Each run has a raw trace, oracle, P0/P1/P2 projections, analyses, and scores. The three projections produced 225 profiled analyses in total.

The matrix command also writes machine-readable `rows.json` and `aggregate.json` files. The aggregate groups results by evidence profile and condition, reporting sequence recovery, topology recovery, resource measurement, and finding precision and recall.

## Key concepts

A single trace demonstrates that a detector can work once. Repeated trials test whether the result is stable. This distinction matters for latency, token totals, and any threshold-based detector because one run can be unusually fast, slow, or otherwise unrepresentative.

The matrix also creates controls. Baseline runs show what normal execution looks like. Injected conditions show whether the analyzer separates a known failure mode from that normal path. The oracle supplies labels for evaluation; it is not evidence available to the analyzer during inference.

## Why this checkpoint matters

The first profile comparisons established local examples: custom argument identity mattered for duplicate detection, while structure was enough for the deliberately excessive path. The matrix tested whether those conclusions survived across tasks, conditions, and repeated runs.

This moved the project from “can this trace be explained?” to “how reliably can the same evidence support an explanation?”

## Result and significance

All 75 task-condition runs completed, and all 225 profile scores were generated. For every profile and condition, sequence exactness and topology edge F1 were 1.0. Finding precision and recall were also 1.0 for the injected conditions.

The profile differences were consistent with the single-run experiments:

- P0 recovered execution shape and findings, but not token totals or custom attempt metadata.
- P1 recovered the standard token totals and all findings except redundant-tool use, because it lacked argument fingerprints.
- P2 recovered the standard measurements plus custom correlation fields and detected redundant use across all three task types.

The repeated matrix supports the earlier conclusions within this deterministic harness. It does not estimate real-world model reliability: every run uses the same scripted model, fixtures, timing pattern, and injected fault logic.

## Next step

Use the aggregate data to write the first cross-condition interpretation, then design a small feedback-signal experiment that asks whether an agent runtime could consume these observability findings to change behavior.

## Work snapshot

The matrix snapshot shows one row per profile and condition, with repeated runs collapsed into rates:

| Profile | Condition | Runs | Sequence | Topology F1 | Finding P/R |
|---|---|---:|---:|---:|---:|
| P0 | baseline | 15 | 1.0 | 1.0 | 1.0 / 1.0 |
| P0 | transient / retry / excessive | 15 each | 1.0 | 1.0 | 1.0 / 1.0 |
| P0 | redundant | 15 | 1.0 | 1.0 | 1.0 / 0.0 |
| P1 | redundant | 15 | 1.0 | 1.0 | 1.0 / 0.0 |
| P2 | every condition | 15 each | 1.0 | 1.0 | 1.0 / 1.0 |
```

Notable evidence: redundancy is the one finding that requires a custom semantic correlation field. The other findings can be reconstructed from span structure, status, and standard measurements in this harness. The full per-run evidence is in the published matrix artifacts.

Artifacts: [local-v0-matrix](../data/published/local-v0-matrix/).

## Significance

The 75 runs and 225 profile analyses convert five illustrative traces into a stable result inside the deterministic harness. Sequence and topology remain exact across every condition, and the only repeated diagnostic gap is redundant-tool recall in P0 and P1. This consistency supports a capability map: structure covers failure, retry, and the injected excessive path; argument identity is required for duplicate detection; token accounting begins at P1.

## Market thesis

The broader market can use this matrix as a benchmark for claims about agent trace quality. Platform buyers can ask vendors to demonstrate diagnosis across controlled failure modes instead of accepting screenshots or unscored examples. The commercial value lies in making telemetry sufficiency and detector limitations testable before production deployment.
