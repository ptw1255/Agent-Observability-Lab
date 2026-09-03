# Agent Observability Lab

> Can OpenTelemetry reconstruct an AI agent's execution behavior well enough to identify inefficient or failed execution paths without instrumenting every business-logic step manually?

Agent Observability Lab is a laptop-sized, hands-on study of telemetry as machine-readable evidence about agent execution. It will run the same deterministic tasks under controlled failure modes, then test what a blind analyzer can infer from traces alone.

The wording is intentional: this project studies **execution paths**, not hidden chain-of-thought. Telemetry may reveal calls, failures, retries, topology, latency, and cost. It generally cannot reveal a model's unrecorded intent or prove answer correctness without a separate evaluator.

## Status

**Planning only.** The experiment has not been implemented or run, and this repository contains no results yet.

## Local v0 scope

The first experiment is designed to run locally on a MacBook Pro without Docker, a hosted observability backend, a model API key, or network access:

- one deterministic agent runtime;
- three fixture-backed tasks;
- five execution conditions;
- five repetitions per task-condition pair;
- 75 total runs;
- OpenTelemetry traces exported to local JSONL files;
- a telemetry-only analyzer scored against sealed ground truth.

The five conditions are baseline, transient tool failure, retry loop, redundant tool use, and an excessive-depth/cost path.

## Central comparison

Each trace will be analyzed through three evidence profiles:

1. structural telemetry: span names, timing, status, and parentage;
2. standard OpenTelemetry GenAI attributes;
3. minimally enriched boundary telemetry, such as argument fingerprints and attempt numbers.

Comparing the same runs across these profiles will show what basic telemetry can recover and which additional boundary fields materially improve diagnosis. No spans will be added to individual business-logic branches merely to make a detector succeed.

## Planned outputs

- a deterministic local workload and fault-injection harness;
- a small labeled trace dataset;
- a telemetry-only execution-graph reconstructor;
- explainable detectors for failures, loops, duplication, and excessive paths;
- an evidence-profile ablation report;
- a clear account of what telemetry can and cannot infer;
- a later, separate study of telemetry as an agent-runtime feedback signal.

The complete v0 protocol is in [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md).

## References

- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)
- [GenAI agent and framework spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
- [GenAI model spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

## License

[MIT](LICENSE)
