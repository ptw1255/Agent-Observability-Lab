# Journal.21 — Hosted baseline-path oracle

## What changed

Turned the completed hosted tool trace into a compact oracle: an explicit statement of what the intended, efficient path looks like for this one task. The oracle expects one hosted agent root, three model turns, two option lookups, one calculation, three first attempts, depth two, a clean root status, and no findings. It also specifies the six parent-child edges that connect the model turns and tools.

The oracle deliberately does not assert exact token counts or latency. Those are useful observations, but a hosted model can vary them from one valid execution to another. Treating a single run's 1,587 input tokens or 10,092.240 ms duration as a universal rule would turn normal provider variance into a false failure. The oracle instead scores stable execution semantics: what happened, in what order, and with what causal relationships.

We then scored the published successful trace against this oracle. It matched exactly: the seven-span sequence was exact, topology edge F1 was 1.0, model/tool/depth counts matched, all attempt numbers were correct, the root was clean, and the analyzer correctly reported no findings.

## Key concepts

An oracle is not telemetry. It is an independent expectation created from the known task contract. Telemetry says, “these spans occurred.” The oracle says, “for this controlled baseline, these are the spans and relationships that should occur.” Comparing them lets us distinguish a valid reconstruction from an analysis result that merely looks plausible.

The oracle applies to this fixed prompt, task, and adapter. A different valid prompt or model behavior could use another path. Holding these inputs fixed gives later deviations a defined comparison point.

## Why this checkpoint matters

The upcoming failure-mode experiment needs a comparison point. Without an oracle, a failed tool call is just an event. With the baseline oracle, we can ask concrete questions: Did a new model turn appear after failure? Did the same logical operation receive a second attempt? Did the trace retain the failure and recovery boundaries? Did the analyzer identify the deviation without reading an injected condition label?

This is the transition from observing a trace to testing whether telemetry is usable as machine-readable evidence.

## Result and significance

The hosted baseline is now scored, not merely described. The score confirms that the telemetry reconstructs this known successful path with complete structural agreement. That is a strong result for path reconstruction at reusable runtime boundaries.

It remains a narrow result. The oracle has not yet been tested against a hosted failure, retry, redundant lookup, or excessive-turn path. Those tests are necessary before claiming that the same evidence supports diagnosis or feedback.

## Next step

Add one controlled failure mode to the local tool executor: make the first calculator call fail while keeping the hosted model and task unchanged. Run it once, then compare the trace to the baseline oracle and inspect whether failure, recovery, and retry evidence remain observable without instrumenting business-logic internals.

## Work snapshot

```text
expected baseline                         observed trace                 score
3 hosted model turns                      3 hosted model turns           exact
2 lookups + 1 calculator                  2 lookups + 1 calculator       exact
6 causal parent-child edges               6 causal parent-child edges    F1 = 1.0
attempts [1, 1, 1], no errors             attempts [1, 1, 1], no errors  exact
```

The notable point is what the score excludes: it makes no claim about private reasoning quality, answer semantics beyond the controlled task, or a universal token budget. It tests only whether the trace exposes the execution structure we need for the next experiment.

## Significance

The oracle scores stable semantics—seven spans, six edges, three model turns, three first-attempt tools, depth two, and a clean root—while allowing token and latency variation. Exact sequence and 1.0 edge F1 establish that the analyzer can reproduce the known hosted path. Later failures can now be measured as missing, added, or changed execution rather than described informally.

## Market thesis

Regulated and high-consequence users will value an explicit expected-path contract because it turns a trace into auditable evidence. The contract can show that a required operation was skipped or retried without claiming access to model intent. An observability offering can package this as workflow conformance for tasks whose valid execution graph is known.
