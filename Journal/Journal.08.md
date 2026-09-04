# Journal.08 — Redundant-tool-use profile comparison

## What changed

We ran one two-option comparison case with the `redundant_tool_use` condition. The healthy task requires one lookup for option A and one lookup for option B. The injected path performs the option B lookup twice with the same normalized arguments, then runs the calculator and produces the answer.

The raw trace was copied into three evidence projections and analyzed the same way in each case:

- P0 removed all span attributes.
- P1 retained standard model, tool, token, and error attributes.
- P2 retained P1 plus the run identifier, logical operation identifier, attempt number, step number, task identifier, and argument fingerprint.

The analyzer was scored against a sealed oracle describing the known seven-span path and the expected `candidate_redundant_tool_use` finding. The oracle is not used by the analyzer; it only provides the reference needed to measure whether the inference was correct.

## Key concepts

Multiple tool calls are legitimate when a task depends on multiple inputs. A call-count detector would misclassify the baseline because it contains two required lookups. A repeated successful call becomes a candidate duplicate when the tool identity and normalized argument fingerprint match and the trace shows no new dependency between calls.

The argument fingerprint is a compact correlation key derived from normalized tool arguments. It does not record the full business logic or the model's private reasoning. It answers a narrower question: did two observed tool spans request equivalent work? P0 and P1 remove that key, while P2 retains it.

The finding is deliberately named `candidate_redundant_tool_use`. Telemetry can show repeated equivalent work, but telemetry alone cannot prove that the repeat was semantically unnecessary. In this controlled experiment, the task definition and oracle establish that the repeat was injected redundancy.

## Why this checkpoint matters

The comparison task provides the required control case: two different lookups in the baseline. The redundant condition adds one repeated lookup without changing the task. This isolates the question of whether an analyzer can avoid flagging legitimate multi-tool work while identifying an injected duplicate.

## Result and significance

All three profiles reconstructed the seven-span sequence and parent topology exactly. P1 and P2 also recovered the expected model and tool counts and token totals. P0 could not recover token totals because those values are attributes rather than span structure.

P0 and P1 predicted no redundancy finding. Their finding recall was 0.0 because neither profile contained the argument fingerprint needed to compare equivalent lookup requests. P2 predicted `candidate_redundant_tool_use` with precision 1.0 and recall 1.0. P2 also matched the expected tool-attempt sequence; P0 and P1 did not retain the custom attempt metadata.

P0 and P1 both miss the injected duplicate; P2 detects it with precision 1.0 and recall 1.0. The execution graph and standard resource attributes are insufficient for this duplicate-use question. The argument fingerprint supplies the missing equivalence evidence without instrumenting every business-logic step.

## Next step

Run the excessive-path condition on the invoice task. It will add repeated reflection/model work without changing the business task, allowing us to test whether span depth, model-call count, output tokens, and latency identify an expensive execution path.

Artifacts: [local-v0-redundant-profile-comparison](../data/published/local-v0-redundant-profile-comparison/).

## Significance

Redundancy is the first finding that fails under both P0 and P1 and succeeds under P2. The topology, tool count, and standard attributes show that three lookups occurred, but they cannot establish that two requests were equivalent. The argument fingerprint supplies that missing fact without exporting raw arguments, so this checkpoint demonstrates a measurable privacy-versus-diagnostic trade.

## Market thesis

Execution-efficiency products need more than cost dashboards because a high call count can reflect necessary work. Teams operating agents with paid search, database, or SaaS tools will value a content-minimized way to identify repeated equivalent requests. The market claim should remain “candidate duplicate” until task context or human review confirms that the second call added no value.
