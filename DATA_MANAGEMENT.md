# Data Management and Project Record

## Purpose

This policy keeps every conclusion connected to reproducible evidence while preventing the analyzer from seeing the answers it is meant to infer.

The governing rule is:

> Raw evidence is immutable. Ground truth is separate. Derived data is reproducible. Decisions are recorded.

## Data layers

| Layer | Contents | Handling rule |
| --- | --- | --- |
| Protocol | Tasks, conditions, seeds, budgets, detector versions | Commit before running an experiment. |
| Raw telemetry | Original OpenTelemetry spans | Never edit or overwrite after collection. |
| Oracle | Injected condition, actual graph, and expected outcome | Keep physically separate and unavailable to the analyzer. |
| Derived data | P0/P1/P2 projections and reconstructed graphs | Regenerate from raw telemetry. |
| Results | Scores, findings, tables, and reports | Tie to exact code, configuration, and dataset versions. |
| Project record | Decisions, surprises, limitations, and next actions | Update throughout the project. |

## Directory convention

```text
configs/
fixtures/
schemas/
data/
├── raw/<experiment-id>/
├── oracle/<experiment-id>/
├── derived/<experiment-id>/{p0,p1,p2}/
└── published/
experiments/
├── registry.csv
└── <experiment-id>/manifest.json
reports/<experiment-id>/
lab-notes/
├── EXPERIMENT_LOG.md
└── DECISIONS.md
Journal/
├── Journal.1.md
└── Journal.N.md
```

Working files under `data/raw`, `data/oracle`, and `data/derived` are ignored by Git. Validated milestone datasets should be published as versioned GitHub Release assets with checksums. Small, sanitized examples may be committed under `data/published`.

## Identifiers and provenance

Each experiment receives a readable ID such as `local-v0-001`. Each run receives an opaque UUID that does not encode its task condition.

The experiment manifest and registry should preserve:

| Field | Purpose |
| --- | --- |
| `experiment_id` | Groups runs performed under one frozen protocol. |
| `run_id` | Correlates one execution across files without revealing its condition. |
| `started_at_utc` | Establishes when the run occurred. |
| `git_commit` | Identifies the exact implementation. |
| `config_hash` | Detects configuration changes. |
| `task_id` | Identifies the versioned task fixture. |
| `seed` | Reproduces deterministic choices. |
| `runtime_lane` | Distinguishes deterministic and hosted-model runs. |
| `model_provider` / `model_id` | Records the actual model boundary when applicable. |
| `telemetry_schema` | Identifies the telemetry contract and semantic-convention version. |
| `environment` | Records relevant Python, OS, architecture, and Docker versions. |
| `artifact_checksums` | Detects mutation of collected evidence. |
| `status` | Records whether collection and validation completed. |

Hosted providers may resolve a requested model alias to a different response model ID. Record both when available.

## Separation between telemetry and oracle

Analyzer-visible telemetry may contain an opaque run ID and task ID. It must not contain:

- condition or scenario labels;
- injected-fault identifiers;
- expected anomaly labels;
- expected answers;
- raw prompts, responses, or tool arguments;
- secrets or credentials.

The oracle sidecar maps the opaque run ID to the condition, fault activation point, actual operation graph, attempts, expected answer, and known unnecessary operations.

The analyzer must accept only an explicit telemetry path. Automated tests should verify that analyzer code cannot import or open oracle files.

## Per-experiment lifecycle

1. Freeze and commit the task fixtures, configuration, schemas, and detector version.
2. Generate an experiment ID, opaque run IDs, and the sealed condition schedule.
3. Record the Git revision, environment, and configuration hash.
4. Execute without overwriting an existing experiment directory.
5. Validate and checksum raw telemetry and oracle files.
6. Derive P0, P1, and P2 projections from raw telemetry.
7. Run the analyzer independently against each projection.
8. Score analyzer output against the oracle in a separate scoring step.
9. Record false positives, false negatives, unexpected behavior, and decisions.
10. Produce a Markdown report, machine-readable results, and dataset checksums.

If instrumentation is incorrect, preserve or quarantine the failed experiment. Correct the implementation and create a new experiment ID rather than repairing raw traces.

## Required validation

A future `validate` command should check:

- every run has one root agent span;
- run IDs and trace IDs are unique;
- parent span references are valid;
- required fields satisfy the pinned schema;
- the collected run count matches the manifest;
- every run has a corresponding oracle record;
- scenario labels and expected answers are absent from telemetry;
- secrets and prohibited content are absent;
- artifact checksums have not changed;
- P0/P1/P2 projections contain only fields allowed by their profiles.

Backend ingestion should be checked by matching expected trace IDs and counts. The backend is not used as ground truth or as the canonical analysis source.

## Project memory

Use [lab-notes/EXPERIMENT_LOG.md](lab-notes/EXPERIMENT_LOG.md) for chronological observations and [lab-notes/DECISIONS.md](lab-notes/DECISIONS.md) for choices that affect the protocol or interpretation.

Use the numbered files in [Journal/](Journal/) for human-readable implementation checkpoints. Each checkpoint must state what was done, why it was done, whether it produced a meaningful result, and what should happen next. Start with `Journal.1.md`; every later checkpoint increments the number by one and is never renamed or reused.

An experiment-log entry should answer:

- What question was tested?
- What changed?
- What result was expected?
- What happened?
- What was surprising?
- Which artifacts support the conclusion?
- What should happen next?

A decision record should capture its context, evidence, alternatives, rationale, and consequences. Threshold changes must be recorded before evaluating the test set.

## Git and publication policy

Commit:

- schemas and configurations;
- task and tool fixtures;
- detector definitions;
- the experiment registry;
- reports, decisions, and notes;
- small sanitized examples.

Do not commit:

- API keys or local environment files;
- raw provider payloads containing unapproved content;
- temporary backend storage;
- unvalidated working traces;
- generated virtual environments or caches.

For v0, JSONL is the canonical raw format and JSON/Markdown are the canonical result formats. A query engine or columnar copy may be added for convenience, but it remains derived data rather than a new source of truth.
