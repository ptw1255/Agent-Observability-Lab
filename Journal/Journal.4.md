# Journal.4 — Telemetry profiles and scoring contract

## What changed

- Added P0, P1, and P2 evidence projections.
- Added versioned telemetry, ground-truth, and result schema files.
- Extended the analyzer with parent edges, depth, token totals, duration, and error counts.
- Added sequence, topology-edge, and finding scoring functions.
- Added CLI commands for `project` and `score`.
- Added tests for field retention, field removal, score calculation, and scoreable analyzer output.

Implementation commit: `382124f`.

## Why we did it

The three tasks and five conditions provide controlled behavior. The profile contract defines which evidence the analyzer can see, and the scoring contract defines how its output will be compared with the oracle.

The profile comparison must use one raw trace projected three ways. That keeps behavior constant while evidence changes.

## Result at this checkpoint

Eighteen tests passed.

The implementation now supports:

- P0 with structural fields and no attributes;
- P1 with standard GenAI attributes;
- P2 with standard attributes plus selected boundary correlation fields;
- machine-readable analyzer reports with sequence and parent-edge data;
- scoring for exact sequence, topology-edge F1, and finding precision/recall.

The full oracle-generation and 75-run scoring workflow is still pending. No reconstruction score has been produced from a real experiment dataset.

## Next step

Create one sealed oracle record for a baseline invoice trace. Project that trace into P0, P1, and P2, run the analyzer on each profile, and record the first profile comparison in Journal.5.
