# Journal.5 — First profile comparison

## What will change

Run one baseline invoice case through the complete evidence pipeline:

```text
raw trace → P0/P1/P2 projections → telemetry-only analyzer → oracle scoring
```

The oracle will contain the expected operation sequence, parent edges, and empty finding set for the healthy baseline.

## Why we are doing it

The projection and scoring code exists. This checkpoint verifies that the contracts work together on one trace before expanding to all tasks, conditions, and repetitions.

The comparison should show which fields each profile removes and whether the analyzer can reconstruct the healthy graph from each remaining evidence set.

## Result at this checkpoint

No profile comparison has been run yet. This is the next experiment step.

The comparison is ready to close when:

- one raw trace produces valid P0, P1, and P2 files;
- the oracle remains outside analyzer input;
- each profile generates a machine-readable analyzer report;
- sequence and topology scores are recorded;
- missing evidence in lower profiles is documented.

## Next step

- Add a small oracle-builder utility for known task graphs.
- Generate the baseline invoice oracle.
- Run the three projections and score them.
- Record the first measured P0/P1/P2 comparison in Journal.6.
