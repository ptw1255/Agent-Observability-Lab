# Agent Observability Lab

> Can OpenTelemetry reconstruct an AI agent's execution behavior well enough to identify inefficient or failed execution paths without instrumenting every business-logic step manually?

Agent Observability Lab is a laptop-sized, hands-on study of telemetry as machine-readable evidence about agent execution. It will run the same deterministic tasks under controlled failure modes, then test what a blind analyzer can infer from traces alone.

The wording is intentional: this project studies **execution paths**, not hidden chain-of-thought. Telemetry may reveal calls, failures, retries, topology, latency, and cost. It generally cannot reveal a model's unrecorded intent or prove answer correctness without a separate evaluator.

## Local-first v0 scope

The experiment is designed to be developed and launched from a MacBook Pro. Its deterministic control path remains credential-free and reproducible, while optional integration profiles may use Docker, a hosted model API, and an OTLP-compatible observability backend:

- one deterministic agent runtime;
- three fixture-backed tasks;
- five execution conditions;
- five repetitions per task-condition pair;
- 75 total runs;
- OpenTelemetry traces exported to canonical local JSONL files and, optionally, an OTLP backend;
- a telemetry-only analyzer scored against sealed ground truth.

The five conditions are baseline, transient tool failure, retry loop, redundant tool use, and an excessive-depth/cost path.

After the deterministic matrix is validated, a small 15-run integration lane will repeat each task-condition pair once with one hosted model adapter. A local Docker observability stack can receive the same traces for visual inspection without becoming the source of truth for scoring.

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

The complete v0 protocol is in [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md). The expected learning path, outcome interpretation, and concise variable definitions are in [LEARNING_GUIDE.md](LEARNING_GUIDE.md). Collection, provenance, storage, and project-memory rules are in [DATA_MANAGEMENT.md](DATA_MANAGEMENT.md).

Progress is recorded as numbered checkpoints in the [Journal](Journal/). Start with [Journal.00](Journal/Journal.00.md); [Journal.22](Journal/Journal.22.md) records the controlled hosted calculator-failure adapter. Journal filenames use two-digit numbering so GitHub displays them in numerical order. New checkpoints continue as `Journal.N+1` with zero-padding.

## First-slice development

```shell
python3 -m pip install -e '.[dev]'
pytest -q
```

The tests validate span export, parent topology, failure recording, and blind detection. They do not run the planned 75-run experiment.

The current first slice has 34 passing tests, three task types, five execution conditions, evidence projections, scoring utilities, a complete 75-run local matrix, retry-feedback and safety comparisons, duplicate-suppression results, a calibrated hosted probe, a five-run hosted cost baseline, a hosted cost-envelope observation, a successful hosted tool trace, a scored hosted baseline-path oracle, and a tested controlled hosted-failure adapter. The next step is one controlled hosted tool failure run.

## References

- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)
- [GenAI agent and framework spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
- [GenAI model spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

## License

[MIT](LICENSE)
