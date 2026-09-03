# Journal.5 — First profile comparison

## What we did

We ran one baseline invoice case through the complete pipeline:

```text
raw trace → oracle → P0/P1/P2 → analyzer → scoring
```

The oracle records the healthy operation sequence, parent edges, empty finding set, expected model/tool counts, and expected token totals. The same raw trace feeds all three projections.

We published the trace, projections, oracle, analyzer outputs, and scores under `data/published/local-v0-profile-comparison/`.

Implementation commit: `0012bc9`.

## Concept to know

An oracle is the known answer used to score an inference. It is separate from telemetry because putting the condition or expected finding into the trace would make the test circular.

The baseline run also shows why a healthy case is necessary. A detector can report zero findings on a healthy trace, but that result says little about anomaly detection. The healthy case primarily tests sequence, topology, and resource reconstruction.

## Why we did it

The projection and scoring code needed one measured integration check before the full matrix. One raw trace projected three ways holds execution constant and isolates the evidence change.

The baseline case gives us a reference sequence and resource total for the invoice task. Those values will support the next failure comparison.

## Result at this checkpoint

The reconstructed sequence was:

```text
invoke_agent → chat plan → calculator → chat finalize
```

P0, P1, and P2 each produced:

- exact sequence match: `true`;
- topology-edge F1: `1.0`;
- model call count match: `true`;
- tool call count match: `true`;
- no predicted findings.

P0 lost input and output token totals because it removes attributes. P1 restored both totals. P2 matched P1 because this healthy path has no repeated operation that requires boundary correlation fields.

This is a one-run pipeline result. It shows that structure survives P0 and token accounting requires P1. It does not measure anomaly detection.

## Next step

Run the transient calculator-failure case through P0, P1, and P2. Compare failed-span detection, recovery-path reconstruction, and attempt attribution.

## Artifacts

- [Published comparison directory](../data/published/local-v0-profile-comparison/)
