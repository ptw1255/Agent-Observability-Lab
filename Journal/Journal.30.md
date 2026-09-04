# Journal.30 — Hosted lookup outage reached the safety cap

## What we did

Ran the real hosted lookup-outage extension with a six-turn cap. The model repeatedly requested both unavailable option lookups on every turn. The runtime completed all six allowed hosted model calls, recorded twelve failed lookup spans, and then stopped the run at the configured safety boundary rather than allowing an unbounded retry cycle.

Each option lookup has a stable logical-operation ID, normalized argument fingerprint, and attempt number. The trace shows attempts 1 through 6 for option A and attempts 1 through 6 for option B. This is not merely a count of many errors: the same two logical operations were retried repeatedly after the runtime had already returned generic unavailability errors.

The original cap implementation raised a terminal Python exception after preserving the trace. We converted that condition into a normal terminal evidence state for future runs: root status `ERROR`, task outcome `failed`, answer validation `unavailable`, and a `terminated_by_turn_cap` result flag. The observed trace was analyzed directly and already contains the essential evidence: root error status, failed task outcome, six model calls, and twelve failed lookups.

## Concept to know

A safety cap is a bounded control action. It does not repair the unavailable dependency or decide the correct answer. It prevents a known-bad execution pattern from consuming further model calls once a fixed resource limit has been reached.

The telemetry makes the reason for that stop inspectable. It shows repeated failures of the same logical operations, the six-turn expansion, token growth, and terminal root status. This is qualitatively different from a timeout with no context: a reviewer can see which dependency was retried, how often, and where the cost accumulated.

## Why we did it

The prior hosted failure showed a case where a tool error did not warrant recovery because the task outcome was valid. This run exercises the opposite branch with real model behavior. The model lacked both data sources, kept retrying them, and never reached a validated outcome before the cap.

This is the strongest real-hosted feedback evidence in the study. The same telemetry contract that supported `observe_only` after a valid outcome now supports `intervene_on_next_attempt` after a terminated retry path.

## Result at this checkpoint

The real outage run produced:

```text
6 hosted model turns
12 failed local lookup calls
6 attempts each for option A and option B
4,268 input tokens and 873 output tokens
17,559.951 ms total duration
root status ERROR; task outcome failed
```

The analyzer found tool failures, a retry loop, and an excessive execution path. The retry-loop inference is now tied to repeated failures of one logical operation across three or more attempts, rather than merely a high count of tool errors. The outcome-aware policy returned `intervene_on_next_attempt` because the runtime terminated before a validated task outcome.

This is a direct answer to the feedback question. Telemetry did not just describe the outage after the fact; it supplied the evidence needed to justify a bounded stop and a different next action, such as backoff, alternate data source, human review, or a later retry. It should not immediately rerun the same unavailable dependency blindly.

## Next step

No additional paid hosted run is necessary for the first study. Consolidate this final real-hosted result into the research assessment and, if desired, write a concise final report that contrasts the two feedback branches:

- tool failure plus valid outcome: observe only;
- repeated tool failure plus terminated/unvalidated outcome: intervene on the next attempt.

## Work snapshot

```text
turns 1–6
  model -> lookup A ERROR, lookup B ERROR

telemetry reconstruction
  same logical lookups, attempts 1..6, repeated errors, expanding model path

bounded action
  turn cap reached -> root ERROR / task failed -> intervene on next attempt
```

The notable result is proportionality. The project now has real hosted evidence for both restraint and intervention, using the same small boundary-level telemetry contract.
