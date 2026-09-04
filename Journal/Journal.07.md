# Journal.07 — Retry-loop profile comparison

## What changed

We ran one invoice case where the calculator failed three times and the runtime exhausted its retry budget.

The resulting trace contained eight spans:

```text
invoke_agent
  → chat plan
  → calculator [error]
  → chat retry
  → calculator [error]
  → chat retry
  → calculator [error]
  → chat retry
```

We extended the oracle builder for the retry graph and recorded the failed root outcome, three tool calls, four model calls, and the expected findings `tool_failure` and `retry_loop`.

We projected the raw trace into P0, P1, and P2, ran the analyzer on each projection, scored the reports, and published the artifacts under `data/published/local-v0-retry-profile-comparison/`.

## Key concepts

A retry loop is a sequence of related failures. One error proves that an operation failed. Repeated errors plus a terminal budget outcome show that the runtime continued attempting the same work.

P0 can see failed statuses, repeated tool spans, and the failed root status. P1 adds the tool name and generic error type. P2 adds logical operation ID and attempt number, which identify attempts one through three as one operation.

The current model calls remain scripted local Python operations. Token counts are fixed test values, and local delays provide duration. The retry failures are controlled exceptions. This comparison measures telemetry and analyzer behavior; the hosted-model lane will test real model-selected execution later.

## Why this checkpoint matters

The transient comparison tested one failure followed by recovery. A retry loop tests repeated failure with no successful recovery.

That distinction matters for runtime feedback. A post-run report can identify a loop. A live detector could stop the next retry only if the loop is recognizable before the budget is consumed.

## Result and significance

All profiles reconstructed the eight-span sequence exactly. Each profile achieved topology-edge F1 of `1.0`, matched the failed root status, and detected both expected findings with precision and recall of `1.0`.

P0 and P1 could not match the attempt sequence because their projections remove the custom attempt field. P2 matched `[1, 2, 3]`.

P0 matched model and tool call counts but lost token totals. P1 and P2 matched all four resource fields.

This result shows that repeated failure detection works from generic structure and standard attributes in this controlled case. P2 adds attempt attribution. The result covers one task and one retry pattern.

## Next step

Run the redundant-tool-use comparison on the two-option task. Test whether P0, P1, and P2 can distinguish two required lookup calls from a repeated lookup with identical arguments.

## Artifacts

- [Published comparison directory](../data/published/local-v0-retry-profile-comparison/)

## Significance

The trace exposes both the repeated calculator failures and the terminal budget outcome. P0 and P1 detect the loop from repeated failed structure; P2 adds exact attempt identity `[1, 2, 3]`. The result also defines the timing question for feedback: a post-run detector can describe the exhausted loop, while an in-run controller must recognize the pattern before the next paid attempt.

## Market thesis

Retry storms are a direct bridge between agent observability and operational cost control. The target buyer is an AI platform or reliability lead responsible for failure rate, latency, and provider spend. A system that attributes repeated attempts to one logical operation can support alerts today and bounded retry controls after the signal is proven safe.

## Supporting market detail

The retry trace ends after three failed calculator attempts and four model calls, with both the tool spans and root marked as failed. P0 and P1 can recognize repeated failed structure after the run; P2 records the exact `[1, 2, 3]` attempt sequence. An alerting product can group the eight spans into one retry-loop incident instead of seven independent events. A runtime-control product needs the same evidence before attempt three and must prove that stopping early does not suppress a later recovery.

## Conclusion

Retry-loop detection becomes commercially useful when it supports one attributed incident and a tested stop rule.
