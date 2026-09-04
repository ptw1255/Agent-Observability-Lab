# Agent Observability Lab

> Can OpenTelemetry reconstruct an AI agent's execution behavior well enough to identify inefficient or failed execution paths without instrumenting every business-logic step manually?

## TL;DR

This study found that OpenTelemetry can reconstruct the **externally visible execution path** of an AI agent without logging private reasoning or tracing every line of business logic. At shared agent, model, and tool boundaries, telemetry recovered model calls, tool calls, retries, failures, parent-child topology, latency, token growth, and safety-cap termination.

The key lesson is that a tool failure is not automatically a task failure. In one real hosted run, a calculator failed, the agent did not retry, and the final answer was still independently validated as correct. The right feedback action was to observe the dependency failure, not interrupt the task. In another run, two required lookups failed repeatedly; the agent retried them until its six-turn safety cap ended the run. That evidence supported intervention on the next attempt.

The practical conclusion: use telemetry to determine whether execution is progressing, repeating, failing, or becoming expensive—not to infer hidden reasoning. Combine that execution evidence with an independent outcome signal, such as a validator or workflow assertion, before acting on it.

## What this project is

Agent Observability Lab is a laptop-sized, reproducible study of agent execution. It treats an agent run as an operational system: a model invokes tools, tools succeed or fail, retries consume time and tokens, and a runtime eventually completes or stops. The project asks what can be reconstructed from those shared boundaries with OpenTelemetry, a blind analyzer, and a small amount of correlation metadata.

The first study includes a deterministic control lane and real hosted-model runs. It produced a healthy tool path, a tool failure followed by a validated answer, and a repeated lookup outage that reached a six-turn safety cap. The evidence is published as sanitized JSONL traces, analyses, oracle scores, and a first-study report.

The wording is intentional: this project studies **execution paths**, not hidden chain-of-thought. Telemetry may reveal calls, failures, retries, topology, latency, and cost. It does not reveal a model's unrecorded intent or prove answer correctness without a separate evaluator.

## Why this could matter

The market hypothesis is specific: teams operating tool-using agents may see expensive runs, tool outages, long incident reviews, or runs that end without completing, yet lack a compact account of the path that caused the symptom. The open issues propose testing this against manual review, generic APM, LLM observability products, offline evaluation tools, and in-house analyzers. Candidate buyer-owned outcomes include investigation time, retries avoided, token and tool spend, release confidence, and audit evidence.

This repository demonstrates a narrower operational claim: shared telemetry boundaries can explain whether the runtime is making progress or repeating failed work. In the hosted outage, the model retried the same two unavailable lookups six times. The trace exposed twelve failed calls, six attempts for each logical lookup, token growth, and the safety-cap termination. That is evidence a runtime or operator can act on.

The market questions are deliberately still open. The repository has not selected an ideal customer profile, buyer-owned metric, product package, or design partner. Those decisions are tracked in the public backlog:

- [Choose a market category and beachhead](https://github.com/ptw1255/Agent-Observability-Lab/issues/1)
- [Rank ICPs and identify user, champion, and buyer](https://github.com/ptw1255/Agent-Observability-Lab/issues/2)
- [Define a measurable business case](https://github.com/ptw1255/Agent-Observability-Lab/issues/3)
- [Position against logs, APM, LLM observability, evals, and in-house analysis](https://github.com/ptw1255/Agent-Observability-Lab/issues/4)
- [Specify the first pilot offer and product package](https://github.com/ptw1255/Agent-Observability-Lab/issues/5)
- [Test that offer with a design partner](https://github.com/ptw1255/Agent-Observability-Lab/issues/6)

The technical work makes those conversations testable. A prospective team can ask: Which runs are failing or expanding? What evidence can leave the runtime? Which action follows from the finding? The repository answers those questions at the trace level. The issues define the customer research needed before making a commercial claim.

## What the first study demonstrated

| Observed path | What telemetry showed | Recommended action |
| --- | --- | --- |
| Calculator failed; final answer validated | One failed tool call, no retry, valid outcome | Observe the dependency failure; do not force recovery. |
| Both required lookups unavailable | Repeated failures of the same logical operations, growing model path, cap termination | Intervene before another identical attempt. |

This is the project’s central lesson: a tool error is evidence, not a verdict. The decision becomes useful when execution evidence and task outcome are considered together.

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

The hosted lane uses focused, bounded probes rather than a completed 15-run matrix. A local Docker observability stack can receive the same traces for visual inspection without becoming the source of truth for scoring.

## Central comparison

Each trace will be analyzed through three evidence profiles:

1. structural telemetry: span names, timing, status, and parentage;
2. standard OpenTelemetry GenAI attributes;
3. minimally enriched boundary telemetry, such as argument fingerprints and attempt numbers.

Comparing the same runs across these profiles will show what basic telemetry can recover and which additional boundary fields materially improve diagnosis. No spans will be added to individual business-logic branches merely to make a detector succeed.

## What you can inspect

- a deterministic local workload and fault-injection harness;
- a small labeled trace dataset;
- a telemetry-only execution-graph reconstructor;
- explainable detectors for failures, loops, duplication, and excessive paths;
- an evidence-profile ablation report;
- a clear account of what telemetry can and cannot infer;
- an outcome-aware feedback decision that distinguishes observation from next-attempt intervention.

The complete v0 protocol is in [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md). The expected learning path, outcome interpretation, and concise variable definitions are in [LEARNING_GUIDE.md](LEARNING_GUIDE.md). Collection, provenance, storage, and project-memory rules are in [DATA_MANAGEMENT.md](DATA_MANAGEMENT.md).

Progress is recorded as numbered checkpoints in the [Journal](Journal/). Start with [Journal.00](Journal/Journal.00.md); [Journal.32](Journal/Journal.32.md) records how to interpret the hosted-path comparison. Journal filenames use two-digit numbering so GitHub displays them in numerical order. New checkpoints continue as `Journal.N+1` with zero-padding.

## First-slice development

```shell
python3 -m pip install -e '.[dev]'
pytest -q
```

The tests validate span export, parent topology, failure recording, and blind detection. They do not run the planned 75-run experiment.

The current first slice has 43 passing tests, three task types, five execution conditions, evidence projections, scoring utilities, a complete 75-run local matrix, retry-feedback and safety comparisons, duplicate-suppression results, a calibrated hosted probe, a five-run hosted cost baseline, a hosted cost-envelope observation, a successful hosted tool trace, a scored hosted baseline-path oracle, a validated answer after a non-retried tool failure, and a real hosted retry path that reached its safety cap. The first study now has real evidence for both feedback branches: observe only and intervene on the next attempt.

The consolidated findings and limits are in the [first-study report](reports/local-v0-first-study/FINAL_REPORT.md).

## References

- [OpenTelemetry GenAI semantic conventions](https://github.com/open-telemetry/semantic-conventions-genai)
- [GenAI agent and framework spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-agent-spans.md)
- [GenAI model spans](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-spans.md)

## License

[MIT](LICENSE)
