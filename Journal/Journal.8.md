# Journal.8 — Redundant-tool-use profile comparison

## What we will do

Run one two-option comparison case with the redundant condition. The healthy task requires lookup A and lookup B. The injected path repeats lookup B with the same normalized arguments before the calculator runs.

The comparison will pass the raw trace through P0, P1, and P2, then score the analyzer findings against a sealed oracle.

## Concept to know

Multiple tool calls are legitimate when the task depends on multiple inputs. A repeated successful call becomes a candidate duplicate when the tool identity and normalized argument fingerprint match and the trace shows no new dependency between calls.

P0 and P1 preserve operation names and tool identity, but they remove the custom argument fingerprint. P2 retains the fingerprint and logical operation fields needed to correlate equivalent calls.

The finding will remain `candidate_redundant_tool_use`. Telemetry can show repeated equivalent work; task context and ground truth establish whether the repeat was unnecessary in this experiment.

## Why we are doing it

The comparison task provides the required control case: two different lookups in the baseline. The redundant condition adds one repeated lookup. This tests whether the analyzer can avoid flagging required multi-tool work while identifying the injected duplicate.

## Result at this checkpoint

No redundant-tool profile comparison has been run yet.

The checkpoint is ready to close when:

- the baseline operation graph remains free of a redundancy finding;
- the redundant path produces the expected candidate finding;
- the profiles show which evidence is required;
- sequence and topology scores remain interpretable.

## Next step

- Extend the oracle builder for comparison redundancy.
- Run and publish the three projections.
- Compare duplicate detection by profile.
- Record the measured result in Journal.9.
