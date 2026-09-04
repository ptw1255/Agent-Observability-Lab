# Journal.25 — Valid answer after a failed required tool

## What changed

Repeated the identical hosted calculator-failure task after adding the root-level validation class. The externally visible path again did not retry: two option lookups succeeded, the calculator failed on its first attempt, and the model made one final model turn. The trace has seven spans, three model calls, three tool calls, one calculator error, and attempt numbers `[1, 1, 1]`.

The new evidence changes the conclusion. The root span records `answer_validation = valid`. The model skipped the expected calculator-recovery topology and still produced the sealed correct option ID for this controlled task. The recovery oracle reports a structural mismatch—7 spans observed versus 9 expected, no calculator attempt 2, and topology edge F1 of 0.8571—while the task outcome is validated.

No model response text is stored in the raw trace. The only outcome evidence is the root-level class. This means the repo can publish the trace's structure, error, resource use, and validation result without publishing the response itself.

## Key concepts

An execution-path deviation is not automatically a task failure. The calculator failure is real, and the missing retry is real. But the task contract asked for the lower-cost option, not for proof that a particular calculator tool was used successfully. The model had both lookup results and could still reach the correct answer.

This creates a useful three-way distinction:

- **Dependency failure:** a tool span ended in error.
- **Path deviation:** the expected retry branch did not occur.
- **Task failure:** the final task outcome is invalid or unavailable.

Only the first two occurred in this run. Conflating them would lead to an unnecessary intervention.

## Why this checkpoint matters

The project asks whether observability can become a feedback signal for agent runtimes. A naive policy would stop or retry every time a required tool fails. This run shows why that policy is too coarse: it would interrupt an agent that has already produced a validated answer.

The combined evidence is more useful. Telemetry identifies the failed calculator and the missing recovery. The minimal outcome signal shows that the agent still completed the task correctly. Together, they support a more discriminating policy: observe the failure, preserve it for reliability analysis, but do not automatically override a validated outcome.

## Result and significance

OpenTelemetry plus one agent-boundary validation class distinguishes the unusual path from a failed task in this run. The distinction required no manual tracing inside the option lookup or calculator implementation and no storage of private reasoning or response text.

It is also a bounded result. Validation is possible here because the comparison task has a sealed expected answer. Real production tasks may need another outcome source: a unit test, workflow state transition, human approval, or downstream business event. The telemetry schema can carry that classification, but it cannot invent a trustworthy validator.

## Next step

Implement a small outcome-aware feedback decision that consumes the analyzer report. It should classify this run as **observe only**—tool failure present, recovery absent, but answer validated—while reserving intervention for the combination of tool failure and invalid or unavailable outcome. Test that policy locally before deciding whether another hosted run is needed.

## Work snapshot

```text
calculator attempt 1 -> ERROR
calculator attempt 2 -> absent
recovery oracle      -> mismatch
answer_validation    -> valid

policy implication: record the failure; do not interrupt a validated task.
```

The notable result is that the same trace can support both reliability learning and restraint. It flags the failed dependency without mistaking a correct, completed task for an agent failure.

## Significance

The second hosted failure repeats the seven-span, no-retry path and adds the decisive fact: `answer_validation = valid`. The failed calculator and missing recovery remain reliability findings, but they did not prevent the model from choosing the lower-cost option from the two lookup results. This run proves that an automatic retry based only on tool status would have added work after the task contract was already satisfied.

## Market thesis

Production agent teams will value systems that reduce false recovery actions as much as systems that detect errors. The target buyer owns both availability and model/tool spend, so a correct outcome after a dependency failure should remain visible without triggering automatic reruns. This restraint can differentiate a feedback product from alerting systems that map every error to the same action.
