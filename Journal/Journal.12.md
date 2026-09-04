# Journal.12 — Feedback safety against recovery

## What changed

We ran two safety controls with feedback disabled and enabled:

- an invoice transient-tool-failure task, which should recover on its second calculator attempt;
- a two-option comparison baseline, which requires two different lookups and a calculator.

The feedback policy was unchanged. The purpose was to test whether its retry-loop rule would accidentally interfere with successful recovery or legitimate multi-step work.

## Key concepts

A feedback policy must be evaluated for both benefit and harm. Reducing calls is not automatically an improvement if the policy converts a recoverable task into a failure or blocks work that was necessary.

## Why this checkpoint matters

Journal.11 showed a cost reduction on a deliberately terminal retry loop. This checkpoint tested the safety boundary: a transient failure should recover, and two different lookups should remain two different lookups.

## Result and significance

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

## Significance

The unchanged transient and comparison controls establish two safety properties for the retry policy: one failure can still recover, and two distinct lookups remain intact. These controls matter as much as the saved retry because an intervention that lowers call counts by breaking successful tasks has negative value. The current evidence remains limited to one explicit retry branch and one deterministic multi-tool task.

## Market thesis

Risk-sensitive buyers will judge agent controls by both false interventions and waste removed. A reliability product must report successful recoveries and untouched valid paths alongside savings. The first buyer is likely an AI platform lead who can compare operational cost reduction with task-success regression risk.

## Supporting market detail

The transient control still uses two tool calls and three model calls and returns `64.64` with feedback active. The comparison control still performs lookup A, lookup B, and calculation and returns `option-a-v1`. Neither run records a feedback action, which confirms that the current retry rule stays inactive outside its target pattern. A pilot report should present these preserved outcomes beside avoided calls so the buyer can see both benefit and regression exposure.

## Conclusion

The retry policy clears its first safety gate by leaving one recoverable failure and one required multi-tool path unchanged.
