# Journal.12 — Feedback safety against recovery

## What we will do

Run the transient-tool-failure task with retry-budget feedback enabled and compare it with the disabled control. Then run a legitimate multi-step comparison task to check that feedback does not suppress required independent tool calls.

## Concept to know

A feedback policy must be evaluated for both benefit and harm. Reducing calls is not automatically an improvement if the policy converts a recoverable task into a failure or blocks work that was necessary.

## Why we are doing it

Journal.11 showed a cost reduction on a deliberately terminal retry loop. This checkpoint tests the safety boundary: a transient failure should recover, and two different lookups should remain two different lookups.

## Result at this checkpoint

The safety comparison has not been run yet. The existing feedback result only supports a narrow claim about stopping repeated terminal failures.

## Next step

Run the controls, compare task outcomes and resource measurements, and record whether the policy needs stronger evidence before it can be considered a safe runtime signal.

## Work snapshot

```text
retry-loop control             -> fails after 3 tool attempts
retry-loop + feedback          -> stops after 2 failed attempts
transient failure + feedback   -> must still recover
comparison + feedback          -> must retain both required lookups
```

The notable question is not only “did work decrease?” It is “did the policy change behavior only where the evidence justified it?”
