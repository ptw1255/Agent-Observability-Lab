# Journal.12 — Feedback safety against recovery

## What we did

We ran two safety controls with feedback disabled and enabled:

- an invoice transient-tool-failure task, which should recover on its second calculator attempt;
- a two-option comparison baseline, which requires two different lookups and a calculator.

The feedback policy was unchanged. The purpose was to test whether its retry-loop rule would accidentally interfere with successful recovery or legitimate multi-step work.

## Concept to know

A feedback policy must be evaluated for both benefit and harm. Reducing calls is not automatically an improvement if the policy converts a recoverable task into a failure or blocks work that was necessary.

## Why we did it

Journal.11 showed a cost reduction on a deliberately terminal retry loop. This checkpoint tested the safety boundary: a transient failure should recover, and two different lookups should remain two different lookups.

## Result at this checkpoint

Feedback did not intervene in either control. Both transient runs returned `64.64`, used 2 tool calls and 3 model calls, and ended with successful root status. Both comparison runs returned `option-a-v1`, used 3 tool calls and 2 model calls, and preserved the sequence of lookup A, lookup B, calculator, and finalization.

The result supports a narrow safety claim: this retry-budget policy reduced work in the terminal retry-loop case without changing these two successful control paths. It does not establish safety for all tasks or all feedback rules. The policy currently acts only inside the explicit retry-loop branch, so the absence of intervention is expected for these controls.

## Next step

Implement and test a separate duplicate-suppression policy. It should use repeated successful tool fingerprints as evidence, suppress only the injected duplicate, and leave the two distinct comparison lookups untouched.

## Work snapshot

```text
retry-loop control             -> fails after 3 tool attempts
retry-loop + feedback          -> stops after 2 failed attempts
transient failure + feedback   -> must still recover
comparison + feedback          -> retains both required lookups
```

The notable result is that the traces are identical within each disabled/enabled pair. Feedback action is absent, outcomes are successful, and the required tool topology is unchanged. The next policy must prove the converse: it changes a redundant path while preserving the legitimate control.

Artifacts: [local-v0-feedback-safety](../data/published/local-v0-feedback-safety/).
