# Journal.24 — Minimal validated-outcome signal

## What changed

Added a single task-level attribute to the root span for the hosted comparison task: `agent_observability_lab.answer_validation`. Its value is one of three classes:

- `valid`: the final response exactly matches the known expected option ID.
- `invalid`: a final response exists but does not match the expected option ID.
- `unavailable`: no final response text was available to validate.

The raw model response text is not added to telemetry. Validation happens once, after the model/tool loop ends, at the agent boundary. The analyzer now carries this classification into its report alongside path structure, resource totals, error count, and findings. Local tests cover all three classes and verify the hosted loop reports `valid` for a known correct simulated run.

## Key concepts

Topology describes execution; outcome validation describes whether the completed execution met a task contract. Neither replaces the other. A trace can be structurally efficient and still produce a wrong answer. A trace can contain a tool failure and still produce a correct answer if the agent has enough other evidence to finish safely.

The design intentionally records the smallest useful outcome signal. It is not full transcript logging, a reasoning trace, or a general-purpose judge model. For this controlled task, the experiment already has a sealed expected answer. Comparing the final response to that answer produces one low-sensitivity classification that downstream analysis can use.

## Why this checkpoint matters

Journal.23 exposed a limit of topology-only evidence. The calculator failed and the model did not retry, but the trace did not reveal whether the final answer was correct. The root span completed cleanly, which tells us only that the runtime did not crash.

Adding this outcome signal lets the next identical failure run separate two materially different cases:

- A required tool failed, no retry occurred, but the agent still returned a validated answer from the lookup evidence.
- A required tool failed, no retry occurred, and the agent returned an invalid or unavailable result.

That distinction is necessary before treating observability as a feedback signal. A runtime should not intervene merely because a tool failed if the task still completed correctly; it should intervene when the failure correlates with an unvalidated outcome or an unsafe path.

## Result and significance

The implementation is ready and has not made a paid API request. It preserves the experiment's privacy boundary: telemetry gains a compact outcome class, not the model's response text or private reasoning. The next hosted run will determine whether the previous no-retry pattern nevertheless produced a validated answer.

## Next step

Repeat the same first-calculator failure once with the new validation signal. Compare its failure span, retry behavior, and root-level validation class. Then decide whether the next feedback policy should intervene on tool failure alone or on the combination of tool failure and invalid/unavailable outcome.

## Work snapshot

```text
before: tool failure -> no retry observed -> runtime completed
        answer quality unknown

after:  tool failure -> no retry observed -> runtime completed
        root.answer_validation = valid | invalid | unavailable
```

The notable design choice is scope: one attribute at the agent boundary closes a critical evidentiary gap without manually tracing each business-logic step or storing model output text.

## Significance

The three-state validator adds task outcome without adding transcript content to the trace. `valid`, `invalid`, and `unavailable` distinguish a correct completion, an incorrect completion, and missing evidence, which are different operational states. The signal remains trustworthy only when the task has a sealed expected answer or another independent validator.

## Market thesis

Verticals with explicit task contracts—transaction routing, document classification, workflow completion, and structured support actions—can use compact outcome signals alongside traces. This gives reliability teams a way to correlate execution defects with business completion while limiting content collection. The market value depends on integrating with an outcome source the customer already trusts.
