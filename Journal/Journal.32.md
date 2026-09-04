# Journal.32 — Reading the hosted comparison

## What changed

Added direct interpretation guidance to the first-study report and the hosted comparison visualization. The new commentary explains that each chart column uses its own scale, identifies the healthy baseline, and states the operational meaning of the two failure paths.

The guidance makes the central comparison explicit. The calculator failure did not expand the path and still produced a validated outcome, so the correct response is observation rather than forced recovery. The lookup outage doubled model turns, quadrupled tool calls, ended without a validated outcome, and reached the safety cap, so it supports intervention on the next attempt.

## Key concepts

A useful visualization does more than show larger bars. It needs an interpretation rule that connects a pattern to a decision. Without that rule, a reader might incorrectly treat every tool error as failure or compare bars across incompatible units.

For this project, the decision-relevant unit is not a single metric. It is the combination of execution expansion, repeated failure, and task outcome.

## Why this checkpoint matters

The comparison is central evidence for the project’s feedback claim. Readers should not need to infer the policy from raw token counts or span totals. Clear commentary keeps the visualization honest and makes the lesson portable to a different agent runtime.

## Result and significance

The report now tells readers exactly how to interpret the comparison: compare within each metric; inspect whether the path expanded; then combine that observation with outcome validation before choosing an action.

## Next step

Embed the comparison as a report figure if the final publication format supports it. Keep the accompanying interpretation text; the chart should reinforce the argument, not carry it alone.

## Work snapshot

```text
tool failure alone                  -> not enough to intervene
tool failure + valid outcome        -> observe only
repeated failure + expanded path
  + terminal/unvalidated outcome    -> intervene on next attempt
```

The notable point is that the visualization explains proportionality: different failures deserve different actions.

## Significance

The interpretation rule prevents two common reading errors: comparing bars that use different units and treating every tool failure as a failed task. The healthy baseline, validated calculator-failure path, and capped lookup-outage path differ in execution expansion and outcome. The chart now supports the same decision rule as the underlying traces instead of asking the reader to infer policy from bar height.

## Market thesis

Executive buyers need agent-observability reports that connect technical evidence to a decision. A visualization that separates tolerated dependency failure from a costly retry loop can support budget, reliability, and control reviews. The target user still needs drill-down links to spans, while the executive view should show the action, evidence, and measured consequence.

## Supporting market detail

The healthy path, calculator failure, and lookup outage use different scales for spans, calls, tokens, and duration. The interpretation text directs readers to compare within each metric, inspect path expansion, and then apply the outcome class. This prevents a failed calculator with a valid answer from receiving the same action as twelve failed lookups and an unavailable outcome. An executive view can summarize that decision while preserving trace links for the engineer who must verify it.

## Conclusion

The final visualization communicates proportional action only when each metric stays tied to execution shape and outcome.
