# Journal.23 — Hosted failure: detection without recovery

## What changed

Ran the controlled hosted calculator failure once. The model followed the normal first phase: one model turn requested both option lookups. On the next turn, it requested the calculator. The runtime made that calculator operation fail once and returned a generic `tool_unavailable` result through the normal tool-output channel.

The model then made one more model call and ended the run. It did not request the calculator again. The trace contains seven spans rather than the nine spans expected for a recovery path: three model turns, two successful lookups, one failed calculator, and no calculator retry. The failed calculator is marked `ERROR`, has `error.type = tool_unavailable`, and has attempt number 1. There is no fault-mode label in the trace.

We scored the observed trace against a recovery oracle that expected a fourth model turn, a second calculator attempt, and a final answer after recovery. The detector portion did exactly what it should: it found `tool_failure` with precision and recall of 1.0. The structural comparison then exposed the missing recovery: sequence mismatch, 7 observed spans versus 9 expected, 3 observed model calls versus 4 expected, 3 observed tool calls versus 4 expected, and no matching retry attempt. Topology edge F1 was 0.8571 because the shared first part of the path matched while the recovery branch was absent.

## Key concepts

Failure detection and recovery detection are different claims. A tool-failure detector answers, “Did a tool operation end in error?” It does not automatically answer, “Did the agent respond appropriately afterward?” The first claim requires one error span. The second requires a baseline or recovery expectation that describes the missing subsequent work.

The clean root status is also not proof that the task succeeded. It only means the runtime completed without an unhandled exception. Because this experiment intentionally avoids storing model response text, this trace does not tell us whether the model gave a correct answer, declined to answer, or made an unsupported guess after the calculator error. That privacy-preserving design is useful, but it establishes a boundary on what topology alone can prove.

## Why this checkpoint matters

This is the first real negative result in the hosted lane, and it makes the project more credible. The earlier deterministic experiment showed how a controlled runtime can retry. The real hosted model showed a different behavior under the same broad failure: it did not retry within the observed path.

That difference is precisely why observability needs explicit expectations. The raw error span tells us a dependency failed. The recovery oracle tells us that the expected retry branch never happened. Neither inference required a condition label or instrumentation inside the lookup and calculator business logic.

## Result and significance

OpenTelemetry successfully identified the failed tool boundary and preserved enough topology to show that the expected recovery path did not occur. For this experiment, telemetry is already useful as machine-readable evidence of an inefficient or failed execution path: the run ended after a failed required operation without the expected retry.

The evidence remains incomplete for answer quality. We can say the agent failed to execute the expected recovery topology. We cannot, from this privacy-preserving trace alone, say whether its final natural-language answer was wrong. The next design task is to add a minimal task-outcome signal at the agent boundary, such as a boolean answer-validation result, without recording private reasoning or full model text.

## Next step

Define and add that minimal outcome signal for the controlled comparison task. Then rerun the same failure once and test a stronger question: can telemetry distinguish “tool failed but the agent still produced a validated answer” from “tool failed and the agent ended without a validated result?”

## Work snapshot

```text
expected recovery path                     observed hosted path
lookup A + lookup B                        lookup A + lookup B
calculator attempt 1 -> ERROR              calculator attempt 1 -> ERROR
model observes error                       model makes one final turn
calculator attempt 2 -> success            no retry
final answer                               run ends

detector: tool_failure found               yes
recovery oracle: sequence / retry match    no
```

The notable result is the combination: the telemetry accurately identifies the local failure, while the oracle makes the missing recovery visible. That is stronger evidence than either a raw error log or a successful-path trace alone.

## Significance

The live model did not follow the expected recovery path: seven spans appeared instead of nine, no second calculator attempt occurred, and topology edge F1 fell to 0.8571 while failure precision and recall stayed at 1.0. This separates detector success from agent success. The clean root also exposes an observability gap because runtime completion does not establish that the task produced a correct result.

## Market thesis

Customer-support and workflow agents need observability that distinguishes a dependency error from failed recovery. An on-call engineer can act on the missing retry branch even when the process exits cleanly. Vendors that report only root status or error counts will miss this class of incomplete execution.
