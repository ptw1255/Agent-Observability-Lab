# Journal.6 — Transient-failure profile comparison

## What will change

Run one transient tool-failure invoice case through:

```text
raw trace → P0/P1/P2 projections → telemetry-only analyzer → oracle scoring
```

The expected path contains a failed calculator attempt, a recovery model call, a successful calculator attempt, and finalization.

## Why we are doing it

The baseline comparison showed that P0 preserves healthy topology and P1 preserves token accounting. A failure case tests whether the profiles preserve enough evidence to diagnose an abnormal path.

The comparison should separate direct error detection from retry attribution:

- P0 has span status and parentage.
- P1 adds tool identity and error type.
- P2 adds logical operation and attempt correlation.

## Result at this checkpoint

No new comparison has been run yet. This is the next experiment step.

The checkpoint is ready to close when the report records, by profile:

- failed-span identification;
- recovery-path reconstruction;
- attempt count;
- `tool_failure` finding precision and recall;
- the evidence fields each profile lacks.

## Next step

- Add a baseline-failure oracle builder path for the known transient condition.
- Run and publish the three profile projections.
- Compare detector findings and attempt attribution.
- Record the measured result in Journal.7.
