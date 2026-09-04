# Journal.06 — Transient-failure profile comparison

## What changed

We ran one invoice case where the calculator failed on attempt one, the agent made a recovery model call, and the calculator succeeded on attempt two.

The raw trace was projected into P0, P1, and P2. The telemetry-only analyzer processed each projection. The oracle recorded the expected six-span sequence, parent edges, one tool failure, two tool calls, three model calls, and the expected token totals.

We published the raw trace, oracle, projections, analyzer reports, and scores under `data/published/local-v0-transient-profile-comparison/`.

## Key concepts

Failure diagnosis has levels:

- span status shows that an operation failed;
- the span name identifies the operation;
- `error.type` describes the failure category;
- logical operation ID and attempt number connect the failed operation to recovery.

P0 contains status and parentage. P1 adds standard operation and error attributes. P2 adds the custom fields that connect two calculator spans as attempts of one logical operation.

## Why this checkpoint matters

The baseline comparison showed healthy topology in all profiles and token recovery in P1. This case tests evidence from abnormal execution.

It also separates two claims. Detecting a failed span is easier than attributing a later successful span to recovery from that failure.

## Result and significance

The analyzer reconstructed the six-span sequence exactly in all profiles. Each profile achieved topology-edge F1 of `1.0` and detected `tool_failure` with precision and recall of `1.0`.

P0 and P1 could not match the attempt sequence because their projections remove the custom attempt field. P2 matched `[1, 2]`.

P0 matched model and tool call counts but lost input and output token totals. P1 and P2 matched all four resource fields.

This single recovery case shows that status and standard span structure can locate a failure. Attempt attribution requires P2 correlation fields. The result does not establish performance across the full experiment matrix.

## Next step

Run the terminal retry-loop case through P0, P1, and P2. Test whether repeated failures and retry-budget exhaustion remain detectable when attempt metadata is removed.

## Artifacts

- [Published comparison directory](../data/published/local-v0-transient-profile-comparison/)

## Significance

All profiles locate the failed calculator and reconstruct the recovery topology, but only P2 proves that the two calculator spans are attempts of one logical operation. That difference matters in incident review: two failures with similar names can be unrelated, while a correlated attempt sequence describes recovery behavior. The result assigns a specific purpose to logical-operation ID and attempt number.

## Market thesis

Reliability teams will pay for failure attribution only when the evidence explains what recovered and what remained broken. Attempt correlation turns a collection of error spans into an incident narrative that an on-call engineer can act on. This capability fits agent-observability products that must distinguish transient dependency failure from repeated independent calls.
