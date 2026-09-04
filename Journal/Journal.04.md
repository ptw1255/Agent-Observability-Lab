# Journal.04 — Telemetry profiles and scoring contract

## What changed

We defined three views of one raw trace:

- P0 keeps structural fields: span names, IDs, parentage, timing, status, and events.
- P1 adds standard GenAI fields such as model, provider, tool, operation, error type, and token usage.
- P2 adds selected boundary fields such as argument fingerprint, logical operation ID, attempt number, and step number.

We added JSON schemas for telemetry spans, ground truth, and scoring results. The analyzer now emits:

- ordered operation sequence;
- parent-child edges using sequence indexes;
- model and tool call counts;
- input and output token totals;
- maximum depth;
- duration and error count;
- detector findings with implicated span IDs.

The CLI can create a projection with `project` and score analyzer output with `score`. Eighteen tests cover field retention, field removal, and score calculation at this checkpoint.

Implementation commit: `07bb13f`.

## Key concepts

P0, P1, and P2 are an ablation. The execution stays fixed while the evidence available to the analyzer changes.

If P0 reconstructs topology and P1 restores token accounting, the result identifies the contribution of generic structure and standard GenAI attributes. If P2 improves anomaly attribution, the result identifies a custom boundary field that the runtime must carry.

The oracle stores the expected graph and findings separately. The analyzer can see a projection. The scoring step can see both the analyzer report and oracle. This preserves the blind inference test.

## Why this checkpoint matters

The project needs to answer “how much telemetry is enough?” A single rich trace cannot answer that question. The profiles let us remove classes of fields without changing the underlying agent execution.

The scoring contract also turns qualitative trace inspection into repeatable measurements. A sequence match, parent-edge F1, and finding precision/recall can be compared across tasks and profiles.

## Result and significance

Eighteen tests passed.

P0, P1, and P2 projections can be generated from the same raw JSONL trace. The analyzer emits scoreable topology and resource fields. The scoring code compares exact sequence, topology edges, resource matches, and findings.

The full oracle-generation and 75-run scoring workflow remains pending. No broad research conclusion exists at this checkpoint.

## Next step

Generate one baseline invoice oracle, run the three projections, and record the first measured profile comparison.

## Significance

The ablation makes telemetry design measurable. P0 tests what generic tracing contributes, P1 tests standard GenAI attributes, and P2 tests four project-specific correlation fields against the same execution. This structure lets an engineering team justify each required field through a change in reconstruction, resource accounting, or finding accuracy.

## Market thesis

Observability vendors and enterprise platform teams need evidence for schema decisions because every captured attribute adds storage, integration, and privacy cost. A scored ablation can show which GenAI fields are table stakes and which enriched fields produce a diagnostic return. That evidence is useful to product managers defining defaults and to architects approving telemetry contracts.
