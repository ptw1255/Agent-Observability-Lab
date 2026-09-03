"""Run and aggregate the deterministic task-condition experiment matrix."""

from __future__ import annotations

import json
import uuid
from collections import defaultdict
from pathlib import Path

from .analyzer import analyze
from .oracle import build_oracle
from .projections import EvidenceProfile, project_file
from .runtime import Condition, DeterministicAgent
from .scoring import score_reports
from .tasks import ComparisonTask, DocumentTask, InvoiceTask
from .telemetry import TelemetrySession


TASKS = {
    "invoice-total-v1": InvoiceTask,
    "document-answer-v1": DocumentTask,
    "two-option-comparison-v1": ComparisonTask,
}


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_one(root: Path, task_id: str, condition: Condition, repetition: int) -> list[dict[str, object]]:
    run_root = root / task_id / condition.value / f"rep-{repetition:02d}"
    raw_path = run_root / "raw-trace.jsonl"
    run_id = str(uuid.uuid4())
    session = TelemetrySession(raw_path)
    try:
        result = DeterministicAgent(session.tracer).run(
            TASKS[task_id](), condition, run_id
        )
    finally:
        session.shutdown()
    _write_json(run_root / "run-result.json", result.__dict__)
    oracle = build_oracle(raw_path, task_id, condition.value)
    _write_json(run_root / "oracle.json", oracle)

    rows: list[dict[str, object]] = []
    for profile in EvidenceProfile:
        projected_path = run_root / f"{profile.value}.jsonl"
        analysis_path = run_root / f"{profile.value}-analysis.json"
        score_path = run_root / f"{profile.value}-score.json"
        project_file(raw_path, projected_path, profile)
        reports = analyze(projected_path)
        _write_json(analysis_path, reports)
        scores = score_reports(reports, [oracle])
        _write_json(score_path, scores)
        rows.append({
            "task_id": task_id,
            "condition": condition.value,
            "repetition": repetition,
            "profile": profile.value,
            "analysis": reports[0],
            "score": scores[0],
        })
    return rows


def run_matrix(output_root: Path, repetitions: int = 5) -> dict[str, object]:
    """Run every task-condition pair and write a machine-readable aggregate."""
    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    rows: list[dict[str, object]] = []
    for task_id in TASKS:
        for condition in Condition:
            for repetition in range(1, repetitions + 1):
                rows.extend(_run_one(output_root / "runs", task_id, condition, repetition))

    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[(str(row["profile"]), str(row["condition"]))].append(row)
    summaries = []
    for (profile, condition), entries in sorted(grouped.items()):
        scores = [entry["score"] for entry in entries]
        findings = [score["findings"] for score in scores]
        resource_matches = [score["resource_matches"] for score in scores]
        summaries.append({
            "profile": profile,
            "condition": condition,
            "run_count": len(entries),
            "sequence_exact_rate": sum(score["sequence_exact"] for score in scores) / len(scores),
            "topology_edge_f1_mean": round(sum(score["topology_edge_f1"] for score in scores) / len(scores), 4),
            "finding_precision_mean": round(sum(item["precision"] for item in findings) / len(findings), 4),
            "finding_recall_mean": round(sum(item["recall"] for item in findings) / len(findings), 4),
            "resource_match_rates": {
                field: round(sum(match[field] for match in resource_matches) / len(resource_matches), 4)
                for field in resource_matches[0]
            },
        })
    aggregate = {
        "experiment": "local-v0-matrix",
        "task_count": len(TASKS),
        "condition_count": len(Condition),
        "repetitions_per_pair": repetitions,
        "task_condition_runs": len(TASKS) * len(Condition) * repetitions,
        "profiled_runs": len(rows),
        "summaries": summaries,
    }
    _write_json(output_root / "aggregate.json", aggregate)
    _write_json(output_root / "rows.json", rows)
    return aggregate
