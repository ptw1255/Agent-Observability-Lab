# Agent Observability Lab

> Can OpenTelemetry reconstruct an AI agent's execution behavior well enough to identify inefficient or failed execution paths without instrumenting every business-logic step manually?

## TL;DR

### What we found

You can understand how an AI agent ran without recording its hidden reasoning or adding telemetry inside every function. This project added OpenTelemetry at three shared boundaries: the agent run, each model call, and each tool call. Those spans showed which calls happened, which call caused the next one, where a tool failed, whether the agent retried it, how long the run took, how many tokens it used, and why a safety cap stopped it.

### Why it matters

The important discovery is that the same tool error can require two different actions.

In one real hosted run, the calculator failed once. The agent did not retry it, but it still returned the correct answer from data it already had. An automatic retry would have added cost without improving the result. The right action was to record the calculator failure and let the completed task stand.

In another run, both required lookups were unavailable. The agent called them again on every turn: six model calls, twelve failed tool calls, 4,268 input tokens, and no completed answer. The safety cap stopped the run. The right next action was to block another identical attempt until the dependency recovered or the runtime chose another path.

OpenTelemetry made these cases distinguishable from runtime evidence. That turns tracing into evidence for a control decision instead of a record that someone reviews only after cost or failure has accumulated.

### Theory/Hypothesis for Scaled Environments

What do these results mean when agents are expected to handle production workflows, especially at hyperscale? A single unnecessary retry may be cheap, but the same behavior repeated across thousands or millions of runs becomes material cost, added latency, dependency pressure, and avoidable failure. This study supports the hypothesis that shared OpenTelemetry signals can help production runtimes distinguish a useful recovery attempt from a path that is no longer making progress, then stop, reroute, or escalate that run before more resources are wasted. If that result holds across larger systems and more varied workflows, observability can become part of the agent's control loop—not just a record of what went wrong afterward—and teams can apply that control without writing custom instrumentation for every workflow step.

### How it works

The runtime combines two inputs:

1. **Execution evidence:** calls, order, parentage, errors, retries, latency, and tokens from OpenTelemetry spans.
2. **Outcome evidence:** one independent result such as `valid`, `invalid`, or `unavailable` from a task validator or workflow check.

The resulting rule is simple:

- A tool fails and the outcome is valid: record the failure and do not force recovery.
- Failures repeat and no valid outcome exists: stop, back off, use another dependency, or send the run for review.

Those decisions rely on observable runtime behavior and whether the task met its contract. Hidden chain-of-thought stays outside the project’s scope.

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
