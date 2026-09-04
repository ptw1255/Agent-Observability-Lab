# Journal.09 — Excessive-path profile comparison

## What changed

We ran the invoice task with the `excessive_path` condition. The baseline calculates the invoice total with one model call before the calculator and one after it. The injected condition added five nested `plan reflection` spans, each containing a model call, before the calculator. The task and answer stayed the same.

The resulting trace contained 14 spans: the root, the initial planning call, five reflection spans with five model calls, the calculator, and the finalization call. Its maximum depth was 6, it made 7 model calls, and it recorded 360 output tokens. The analyzer compared those measurements with the local excessive-path envelope.

We passed the raw trace through P0, P1, and P2 and scored each projection against a sealed oracle. The oracle included the nested parent edges; it was corrected after the first run revealed that a flat root-to-child assumption did not represent the actual reflection topology.

## Key concepts

An execution can be correct and still be inefficient. A trace may expose this through indirect signals such as unusually deep nesting, more model calls, more output tokens, or greater elapsed time. These signals describe execution cost and shape; they do not explain whether the extra reasoning was useful.

The detector emits `excessive_execution_path` when any configured v0 threshold is crossed: maximum depth of at least 6, at least 6 model calls, or at least 300 output tokens. The thresholds are an experimental rule, not a universal definition of inefficiency. They must be evaluated against a known baseline and reported with the underlying measurements.

Parentage is different from sequence. Sequence says which spans were observed in time order. Parentage says which operation contained which child. The nested reflection spans make parentage measurable: the analyzer can recover that each reflection contains the next reflection and its model call.

## Why this checkpoint matters

The earlier experiments tested failures and duplicate tool work. This condition tests a different limitation: whether observability can identify a costly path even when no tool fails and the final answer remains correct.

The profile comparison tested whether the signal comes from structure alone, standard GenAI attributes such as token counts, or the additional boundary metadata in P2. This matters because a correct answer does not imply an efficient execution path.

## Result and significance

All three profiles reconstructed the 14-span sequence and nested topology exactly, with sequence exactness true and topology edge F1 of 1.0. All three predicted `excessive_execution_path` with precision 1.0 and recall 1.0.

P0 still detected the path because it preserved span names and parentage, which allowed the analyzer to calculate depth and model-call count. P0 did not recover input or output token totals because those are attributes. P1 recovered all expected standard resource totals. P2 recovered the same totals and the custom attempt metadata; the custom fields did not improve this particular finding.

The first scoring attempt produced a misleading topology score because the oracle builder assumed every span was a direct child of the root. The measured trace exposed that assumption. Updating the oracle to encode the nested edges brought the score to 1.0. This is a useful experimental result: the scoring system must represent the execution topology it claims to evaluate.

The detector identifies the intentionally deep path from its six-level depth, seven model calls, and 360 output tokens. Those measurements do not establish whether the extra reasoning improved the answer. A production efficiency judgment would also require task quality, latency distributions, and repeated runs.

## Next step

Run the complete local matrix with repeated baseline and failure-mode trials. Aggregate the profile scores and execution measurements so the project can separate a repeatable signal from a single illustrative trace.

Artifacts: [local-v0-excessive-profile-comparison](../data/published/local-v0-excessive-profile-comparison/).

## Work snapshot

The trace, shown as parent-child structure rather than raw JSON, looks like this:

```text
invoke_agent deterministic-agent
├─ chat scripted-model                 plan
├─ plan reflection                     depth 1
│  ├─ chat scripted-model              reflection-1
│  └─ plan reflection                  depth 2
│     ├─ chat scripted-model           reflection-2
│     └─ plan reflection               depth 3
│        ├─ chat scripted-model        reflection-3
│        └─ plan reflection            depth 4
│           ├─ chat scripted-model     reflection-4
│           └─ plan reflection         depth 5
│              └─ chat scripted-model  reflection-5
├─ execute_tool calculator
└─ chat scripted-model                 finalize
```

Notable evidence:

- The five nested reflection spans create the abnormal depth. The model calls inside them create the excess call count.
- The calculator succeeds, the root status is `UNSET`, and the task still returns the correct answer. This is an inefficient-path signal, not a failure signal.
- P0 can reconstruct the shape from span names and parentage. P1 adds the 224 input and 360 output token totals. P2 adds boundary correlation fields, but they are not needed for this finding.
- The trace shows that extra work happened. It does not show whether the extra reasoning was useful.

## Significance

The excessive path is visible even in P0 because five nested reflection spans change depth and model-call count. P1 adds the 224 input and 360 output tokens needed to quantify the resource increase, while P2 adds no diagnostic lift for this condition. The corrected oracle also shows that scoring infrastructure can create false conclusions when it flattens the topology it claims to measure.

## Market thesis

The cost-observability segment will value baseline-relative path analysis more than a universal token threshold. AI platform teams need to know whether higher spend came from more calls, deeper orchestration, larger context, or normal model variance. A product that shows the execution source of cost can complement FinOps dashboards without declaring every expensive response wasteful.

## Supporting market detail

The abnormal run reaches depth six, makes seven model calls, and records 360 output tokens while the calculator succeeds and the answer remains correct. P0 sees the structural expansion; P1 quantifies its token cost; P2 adds no new finding for this condition. The first oracle incorrectly flattened the nested reflections, proving that an inaccurate reference graph can make correct telemetry look wrong. A production offer must build envelopes by task and preserve the path behind each cost alert so an engineer can judge whether the extra work was justified.

## Conclusion

Path-aware cost diagnosis must show where execution expanded and which baseline made it abnormal.
