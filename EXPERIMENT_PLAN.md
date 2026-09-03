# Local v0 Experiment Plan

## 1. Decision summary

The first version will be a small, deterministic experiment that can run entirely on a MacBook Pro. It will not call a hosted model, require Docker, or depend on an observability service.

The experiment will ask one narrow question:

> How accurately can a telemetry-only analyzer reconstruct and diagnose agent execution when instrumentation exists only at shared agent, model, and tool boundaries?

The design uses three tasks, five conditions, five repetitions, and three evidence profiles. That produces 75 agent runs and three analysis views of each run. The purpose is to establish a trustworthy baseline before introducing real models, distributed systems, or adaptive runtime behavior.

## 2. Research boundaries

### What “execution semantics” means here

- the model and tool operations that occurred;
- their order and parent-child relationships;
- errors, retries, recovery, and termination;
- latency, token counts, call counts, and maximum depth;
- repeated or unusually expensive paths relative to a healthy baseline.

### What it does not mean

- hidden chain-of-thought;
- unrecorded model intent;
- a complete causal explanation for why a model chose an action;
- answer correctness without a separate task evaluator.

The project should use “execution path” rather than “reasoning path” except when discussing the distinction explicitly.

## 3. Claims to test

### H1 — Structure

Boundary spans are sufficient to reconstruct operation order and execution topology.

### H2 — Failures

Span status, errors, timing, and repeated operation signatures are sufficient to identify tool failures and retry loops.

### H3 — Inefficiency

Calls, topology, tokens, and normalized operation signatures can identify candidate redundant work and excessive execution paths relative to baseline behavior.

### H4 — Evidence value

Standard GenAI telemetry improves diagnosis over structural spans alone, and a small number of boundary-level correlation fields improves it further.

The experiment will not claim that every expensive or repeated operation is inherently wasteful. “Redundant” and “excessive” are comparative labels established by controlled ground truth in v0.

## 4. Local execution constraints

The future implementation should meet these constraints:

- run on macOS with Python and a local virtual environment;
- require no API key and make no network calls during an experiment;
- use a deterministic scripted model adapter and fixture-backed tools;
- export traces to local JSONL rather than requiring a collector or backend;
- finish the full 75-run experiment and analysis in under five minutes;
- use less than 1 GB of memory;
- keep generated v0 artifacts below 25 MB;
- support one command to run the experiment and one command to analyze it;
- produce identical logical outcomes for a fixed seed.

Docker, Jaeger, Grafana, hosted models, and notebooks are explicitly deferred. A trace viewer may be added later as an optional convenience, not as a v0 dependency.

## 5. Workload

### Agent runtime

Use one small tool-calling loop with replaceable model and tool adapters. The scripted model will choose actions from task fixtures and expose deterministic token counts. The runtime will enforce a fixed step and retry budget.

### Tasks

Use three task families with known correct answers and known valid operation graphs.

| Task | Healthy path | Why it is useful |
| --- | --- | --- |
| Invoice total | Model → calculator → model | Smallest complete tool loop |
| Local document answer | Model → local retrieval → model | Adds a retrieval-like boundary and fixture evidence |
| Two-option comparison | Model → lookup A → lookup B → calculator → model | Adds multiple tools and a deeper valid topology |

Each family will have one fixed v0 task instance. More instances are deferred until the harness and metrics are validated.

### Conditions

Every task will run under the same five conditions.

| Condition | Controlled injection | Expected observable signature |
| --- | --- | --- |
| Baseline | None | Valid short topology with no errors |
| Transient tool failure | First selected tool call fails, then succeeds | Tool error followed by recovery |
| Retry loop | Selected tool repeatedly fails until the retry budget is exhausted | Repeated signature, repeated errors, terminal failure |
| Redundant tool use | One successful deterministic tool call is repeated | Duplicate successful signature with no new fixture information |
| Excessive path | Add unnecessary nested model/reflection steps | Elevated depth, model calls, tokens, and latency |

The task input, fixtures, expected answer, model policy, and budgets remain fixed within a task. Only the injected condition changes.

### Run count

```text
3 tasks × 5 conditions × 5 repetitions = 75 runs
```

Five repetitions are enough to validate determinism and collect basic timing variation on a laptop. This v0 is a functional proof, not a statistically general benchmark.

## 6. Instrumentation rule

Instrumentation belongs only in reusable runtime adapters:

- agent invocation;
- scripted model invocation;
- tool invocation;
- shared retry handling.

Do not instrument each application branch, loop body, or fault scenario. Do not place the scenario label, expected anomaly, or expected answer in analyzer-visible telemetry.

The fault injector will create a separate ground-truth sidecar. This is the oracle used for scoring, not an additional telemetry stream.

## 7. Evidence profiles

The same rich boundary trace will be projected into three progressively informative profiles before analysis. This avoids rerunning behavior merely to remove fields.

### P0 — Structural

- trace ID, span ID, and parent span ID;
- span name and kind;
- start and end timestamps;
- status and exception events.

This approximates generic tracing with no GenAI-specific knowledge.

### P1 — Standard GenAI

P0 plus applicable standard OpenTelemetry GenAI fields:

- operation name;
- agent, model, provider, and tool identifiers;
- input and output token usage;
- error type.

The implementation must pin and record the semantic-convention version because the GenAI conventions are still evolving.

### P2 — Boundary enriched

P1 plus a minimal documented lab namespace:

- normalized tool-argument fingerprint;
- logical operation ID;
- attempt number;
- runtime step number.

These fields must describe runtime facts, not experiment labels. Ablations will show whether each one makes a detector artificially easy or provides genuinely necessary correlation.

### Oracle — Withheld ground truth

The oracle is not an evidence profile and is never passed to the analyzer. It contains the exact operation graph, injected condition, activation point, attempts, expected answer, and known unnecessary operations.

## 8. Telemetry contract

The implementation will prefer OpenTelemetry semantic conventions and use `agent_observability_lab.*` only where no suitable standard field exists.

| Dimension | Required evidence |
| --- | --- |
| Identity | service, operation, model, provider, tool |
| Correlation | trace/span parentage and an opaque run ID that does not encode the condition |
| Topology | start/end timestamps and parent-child edges |
| Cost | input/output tokens and call counts |
| Reliability | status, exception, error type |
| Retry | logical operation, attempt, retry outcome |
| Duplication | normalized argument fingerprint |
| Reproducibility | code revision, schema version, seed |

Prompt text, model output, raw tool arguments, hidden reasoning, and secrets will not be exported. Synthetic fixtures will be safe to publish, but content capture remains off to preserve the study's boundary.

## 9. Reconstruction tasks

The blind analyzer receives one evidence profile at a time and performs four tasks.

### A. Reconstruct the operation sequence

Recover the ordered agent, model, retrieval, and tool operations.

### B. Reconstruct topology

Recover parent-child edges, terminal status, maximum depth, and critical path.

### C. Reconstruct resources

Compute model calls, tool calls, token totals, errors, attempts, and end-to-end latency.

### D. Diagnose the condition

Emit zero or more evidence-backed findings:

- `tool_failure`;
- `retry_loop`;
- `candidate_redundant_tool_use`;
- `excessive_execution_path`.

Every finding must name the implicated spans and the rule or baseline comparison that triggered it.

## 10. Initial explainable detectors

Use simple rules before considering learned anomaly detection.

| Finding | Initial rule |
| --- | --- |
| Tool failure | Tool span has error status or exception evidence |
| Retry loop | Repeated logical operation or matching signature fails until budget exhaustion |
| Candidate redundant call | Multiple successful calls share a tool and argument fingerprint with no intervening input dependency |
| Excessive path | Depth, model-call count, or tokens exceed the task's baseline envelope |

P0 may be unable to distinguish some repeated operations. That is an expected and useful result. The report should say which evidence is missing instead of guessing.

## 11. Scoring

### Structural metrics

- exact operation-sequence match rate;
- parent-child edge precision, recall, and F1;
- maximum-depth absolute error;
- exact call-count and error-count match rate;
- relative error for duration and token totals.

### Diagnostic metrics

- per-class precision, recall, and F1;
- macro F1 across the four findings;
- number of baseline false positives;
- attribution accuracy for the implicated span or subgraph.

### Instrumentation comparison

Report every metric separately for P0, P1, and P2, then show the marginal improvement from each evidence profile. The main result is a capability map, not one aggregate score.

### Provisional v0 success criteria

- at least 95% exact operation-sequence reconstruction under P2;
- at least 0.90 topology-edge F1 under P2;
- at least 0.80 diagnostic macro F1 under P2;
- no more than one false diagnosis across the 15 baseline runs;
- complete local execution in under five minutes;
- no analyzer access to ground truth or scenario labels.

These thresholds indicate whether the lab is ready to expand. They do not establish production validity, and the report must include raw counts alongside rates.

## 12. Experiment protocol

1. Generate versioned task fixtures and expected answers.
2. Generate the sealed condition schedule and ground-truth schema.
3. Run all 75 cases through the same runtime with a fixed seed schedule.
4. Export one local JSONL trace record per run or one clearly indexed combined file.
5. Validate that traces contain no scenario labels or prohibited content.
6. Derive P0, P1, and P2 projections from each trace.
7. Run the analyzer independently on each profile.
8. Score the inferred graph, resources, and findings against the oracle.
9. Inspect and document every false positive and false negative.
10. Generate a Markdown summary and machine-readable JSON report.

The implementation should include automated tests that assert the analyzer cannot load oracle files and that scenario labels do not appear in exported spans.

## 13. Planned local interface

The exact CLI may change during implementation, but v0 should target a workflow this small:

```shell
# Planned commands; not implemented yet.
python -m agent_observability_lab run --all
python -m agent_observability_lab analyze --all-profiles
```

Expected local outputs:

```text
artifacts/
├── traces.jsonl
├── ground_truth.jsonl
└── report/
    ├── results.json
    └── summary.md
```

Trace and ground-truth files must remain physically and logically separate.

## 14. Planned repository structure

```text
Agent-Observability-Lab/
├── README.md
├── EXPERIMENT_PLAN.md
├── src/agent_observability_lab/
│   ├── runtime.py
│   ├── tasks.py
│   ├── faults.py
│   ├── telemetry.py
│   ├── projections.py
│   ├── analyzer.py
│   └── cli.py
├── fixtures/
├── tests/
└── artifacts/
```

Only planning documents exist initially. This layout describes the later local implementation.

## 15. Result format

The final v0 report should answer each question separately.

| Question | Required result |
| --- | --- |
| What operations occurred? | Sequence reconstruction by evidence profile |
| How were they connected? | Topology reconstruction by evidence profile |
| Where did failure occur? | Detection and span attribution |
| Was retry behavior abnormal? | Loop detection and supporting evidence |
| Was work inefficient? | Baseline-relative candidate finding, with caveats |
| Why did the model choose an action? | Explicitly marked not recoverable from this telemetry |
| Was the answer correct? | Reported from the separate evaluator, not inferred from traces |

This prevents a strong result in one dimension from being presented as proof that all agent semantics are observable.

## 16. Deferred work

The following are intentionally outside local v0:

- hosted or local language models;
- multiple agent frameworks;
- distributed context propagation;
- trace sampling and dropped spans;
- asynchronous and parallel tool execution;
- an observability UI or collector stack;
- learned anomaly detectors;
- production workloads;
- runtime intervention.

The first expansion after v0 should test incomplete telemetry and async context propagation. A real-model replication should follow only after the deterministic protocol is trustworthy.

## 17. Follow-up: telemetry as feedback

The feedback question remains a separate experiment. Only a v0 detector that meets its success criteria should become a candidate signal.

The progression should be:

1. offline recommendation;
2. shadow-mode recommendation compared with actual runtime behavior;
3. bounded local intervention, such as stopping after a retry or depth budget.

The follow-up must compare task success, latency, tokens, and failure rate against a no-feedback control. It should not assume that a correct diagnosis automatically implies a safe intervention.

## 18. Definition of done for v0

Local v0 is complete when another person can clone the repository, run the entire experiment on a laptop without credentials or external services, reproduce the machine-readable report, audit every diagnosis back to specific spans, and see exactly which execution facts become recoverable at P0, P1, and P2.
