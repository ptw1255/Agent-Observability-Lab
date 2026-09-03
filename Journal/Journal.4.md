# Journal.4 — Telemetry profiles and scoring contract

## What will change

Define the data contracts that turn the three-task workload into a scored experiment:

- raw span record schema;
- sealed ground-truth record schema;
- P0 structural projection;
- P1 standard GenAI projection;
- P2 boundary-enriched projection;
- analyzer result schema;
- experiment manifest and run registry fields.

## Why we are doing it

The runtime now produces controlled behavior for three task shapes. The next question is how much of each behavior survives when telemetry fields are removed or restricted.

The profile definitions must be frozen before scoring. The oracle must remain unavailable to the analyzer.

## Result at this checkpoint

No implementation result yet. This is the next protocol task.

The work is ready to close when each projection can be generated from one raw trace, the oracle remains separate, and the analyzer emits machine-readable findings with span evidence.

## Next step

- Add versioned JSON schemas.
- Define allowed fields for P0, P1, and P2.
- Define the ground-truth operation graph format.
- Add projection tests that verify fields are removed or retained correctly.
- Add scoring for sequence and parent-edge reconstruction.
- Record the first profile comparison in `Journal.5`.
