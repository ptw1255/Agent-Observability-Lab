# Journal.5 — First profile comparison

## What changed

- Generated one baseline invoice trace.
- Built a sealed oracle containing the expected sequence, parent edges, and empty finding set.
- Projected the same raw trace into P0, P1, and P2.
- Ran the telemetry-only analyzer on each projection.
- Scored each report against the oracle.
- Published the raw trace, projections, oracle, analyses, and scores under `data/published/local-v0-profile-comparison/`.

Implementation commit: `07bb13f`.

## Why we did it

The schema, projection, and scoring utilities needed one end-to-end check before we generate the full dataset. Using one raw trace for all three profiles holds execution constant while changing the evidence available to the analyzer.

The baseline case also establishes the healthy sequence and resource totals for the invoice task.

## Result at this checkpoint

The trace contains four spans in the reconstructed order:

```text
invoke_agent → chat plan → calculator → chat finalize
```

All three profiles produced:

- exact sequence match: `true`;
- topology-edge F1: `1.0`;
- model call count match: `true`;
- tool call count match: `true`;
- no predicted findings for the healthy run.

P0 lost both token totals because it removes all attributes. P1 restored input and output token matches. P2 matched P1 for this case because the extra correlation fields were unnecessary for a healthy, non-repeated path.

This is a pipeline result for one baseline case. It shows that structure survives P0 and token accounting requires P1. It does not measure anomaly detection yet; the empty finding set makes that comparison vacuous.

## Next step

Run the transient tool-failure invoice case through P0, P1, and P2. Measure which profile can identify the failed calculator, the recovery path, and the two attempts. Record the comparison in Journal.6.

## Artifacts

- [Published comparison directory](../data/published/local-v0-profile-comparison/)
