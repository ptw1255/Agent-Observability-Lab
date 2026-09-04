# Journal.13 — Feedback suppression of duplicate work

## What changed

We added an opt-in `DuplicateSuppressionFeedback` policy that caches successful read-only tool results by argument fingerprint. When an identical request is attempted again, the policy returns the cached result, skips a second tool span, and records `suppress_duplicate_tool` on the root span.

We compared redundant-tool-use with feedback disabled and enabled. We also ran the baseline comparison with feedback enabled as a negative control.

## Key concepts

Duplicate suppression is more semantically sensitive than retry stopping. Two identical-looking calls may still be intentional if external state changed or the tool is not idempotent. This local experiment uses deterministic read-only fixtures, so suppression is safe by construction; the limitation must remain explicit.

## Why this checkpoint matters

Journal.8 showed that argument fingerprints are the custom field that makes duplicate detection possible. Journal.12 showed that the retry policy did not interfere with legitimate work. This checkpoint tests whether the same evidence can support a targeted intervention on redundant successful work.

## Result and significance

The redundant disabled control used 4 tool calls and produced `candidate_redundant_tool_use`. The redundant enabled run used 3 tool calls, produced the same answer `option-a-v1`, and recorded `suppress_duplicate_tool`. The baseline enabled control also used 3 tool calls, produced `option-a-v1`, and recorded no feedback action.

The policy removed only the injected duplicate in this read-only deterministic fixture. The result supports a narrow intervention claim: an argument fingerprint can support duplicate suppression when the tool result is safe to reuse.

## Next step

Run the same policy against a hosted model or OTLP-exported lane only after defining how idempotence, cache freshness, and external state will be handled.

## Work snapshot

```text
comparison baseline             -> lookup A -> lookup B -> calculator
comparison redundant/no feedback -> lookup A -> lookup B -> lookup B -> calculator
comparison redundant/feedback    -> expected: lookup A -> lookup B -> calculator
```

The notable evidence is the repeated argument fingerprint. The policy acted on that boundary signal and the runtime recorded the action. The baseline control demonstrates that two distinct lookup fingerprints remain two tool calls.

Artifacts: [local-v0-feedback-duplicate-suppression](../data/published/local-v0-feedback-duplicate-suppression/).

## Significance

The policy removed one repeated lookup, preserved `option-a-v1`, and left the three-tool baseline unchanged. Its safety comes from the fixture contract: the lookup is read-only, deterministic, and safe to reuse. The result does not extend to tools that mutate state, return time-sensitive data, or depend on identity outside the fingerprint.

## Market thesis

Workflow-automation teams can value duplicate suppression when external tool calls carry latency, rate limits, or transaction fees. The feature requires an explicit idempotence and freshness contract, which makes it more suitable for platform-managed read tools than arbitrary third-party actions. A commercial offer should pair the savings estimate with the list of tools approved for reuse.
