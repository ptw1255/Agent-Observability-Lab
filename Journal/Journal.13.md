# Journal.13 — Feedback suppression of duplicate work

## What we will do

Add a separate opt-in policy that observes successful tool argument fingerprints during a comparison. If an identical successful request is about to repeat, the policy will suppress that duplicate and allow the task to continue with the original result.

Compare redundant-tool-use with feedback disabled and enabled. Also run the baseline comparison with feedback enabled as a negative control.

## Concept to know

Duplicate suppression is more semantically sensitive than retry stopping. Two identical-looking calls may still be intentional if external state changed or the tool is not idempotent. This local experiment uses deterministic read-only fixtures, so suppression is safe by construction; the limitation must remain explicit.

## Why we are doing it

Journal.8 showed that argument fingerprints are the custom field that makes duplicate detection possible. Journal.12 showed that the retry policy did not interfere with legitimate work. This checkpoint tests whether the same evidence can support a targeted intervention on redundant successful work.

## Result at this checkpoint

The duplicate-suppression policy has not been implemented or run yet.

## Next step

Implement the policy, compare tool counts, answers, findings, and trace annotations, and record whether feedback removes only the injected duplicate.

## Work snapshot

```text
comparison baseline             -> lookup A -> lookup B -> calculator
comparison redundant/no feedback -> lookup A -> lookup B -> lookup B -> calculator
comparison redundant/feedback    -> expected: lookup A -> lookup B -> calculator
```

The notable evidence is the repeated argument fingerprint. The policy should act on that boundary signal, not on a manually added branch-specific “skip duplicate” instruction.
