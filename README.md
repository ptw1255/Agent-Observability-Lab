# Agent Observability Lab

> Can OpenTelemetry reconstruct the execution behavior of an AI agent well enough to identify inefficient or failed reasoning paths without instrumenting every business-logic step manually?

Agent Observability Lab is a planned, hands-on study of telemetry as machine-readable evidence about agent execution. The project will run identical tasks under controlled agent failure modes, collect traces at runtime boundaries, and test what an analyzer can infer without access to scenario labels or hidden chain-of-thought.

## Status

**Planning only.** The experiment has not been implemented or run, and this repository contains no results yet.

## What the study will measure

The planned telemetry covers:

- model and tool calls;
- latency and token usage;
- errors, retries, and recovery;
- parent-child relationships and execution topology.

From those signals, the study will attempt to infer:

- retry loops;
- redundant tool usage;
- expensive reasoning paths;
- tool failures and recovery;
- abnormal execution depth.

The study deliberately distinguishes observable execution behavior from private model reasoning. It does not claim that traces reveal hidden chain-of-thought. It asks whether traces reveal enough operational structure to diagnose agent behavior.

## Research path

1. Establish a deterministic baseline and a boundary-only instrumentation policy.
2. Run the same task corpus under controlled failure modes.
3. Reconstruct operation sequence, topology, cost, and anomalies from telemetry alone.
4. Compare inferred behavior with separately recorded ground truth.
5. Evaluate whether observability signals are reliable enough to inform agent-runtime decisions.

The complete study design, hypotheses, metrics, controls, and decision criteria are in [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md).

## Intended outputs

- a reproducible agent workload and fault-injection harness;
- OpenTelemetry traces and a documented telemetry contract;
- a telemetry-only reconstruction and anomaly detector;
- a labeled benchmark dataset;
- a report describing what telemetry can, cannot, and should not infer;
- a follow-up evaluation of observability as a feedback signal for agent runtimes.

## References

- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)
- [GenAI agent and framework spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
- [GenAI model spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

## License

[MIT](LICENSE)
