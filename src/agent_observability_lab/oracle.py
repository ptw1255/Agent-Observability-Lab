"""Build sealed ground-truth records for known deterministic task graphs."""

from __future__ import annotations

import json
from pathlib import Path


BASELINE_GRAPHS = {
    "invoice-total-v1": [
        "invoke_agent deterministic-agent",
        "chat scripted-model",
        "execute_tool calculator",
        "chat scripted-model",
    ],
    "document-answer-v1": [
        "invoke_agent deterministic-agent",
        "chat scripted-model",
        "execute_tool local_retrieval",
        "chat scripted-model",
    ],
    "two-option-comparison-v1": [
        "invoke_agent deterministic-agent",
        "chat scripted-model",
        "execute_tool local_lookup",
        "execute_tool local_lookup",
        "execute_tool calculator",
        "chat scripted-model",
    ],
}

BASELINE_RESOURCES = {
    "invoice-total-v1": {
        "expected_model_call_count": 2,
        "expected_tool_call_count": 1,
        "expected_input_tokens": 64,
        "expected_output_tokens": 40,
    },
    "document-answer-v1": {
        "expected_model_call_count": 2,
        "expected_tool_call_count": 1,
        "expected_input_tokens": 64,
        "expected_output_tokens": 44,
    },
    "two-option-comparison-v1": {
        "expected_model_call_count": 2,
        "expected_tool_call_count": 3,
        "expected_input_tokens": 64,
        "expected_output_tokens": 40,
    },
}


def build_baseline_oracle(trace_path: Path, task_id: str) -> dict[str, object]:
    """Build one baseline oracle from a raw trace and a known task graph."""
    if task_id not in BASELINE_GRAPHS:
        raise ValueError(f"unknown task graph: {task_id}")
    records = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    trace_ids = {record["trace_id"] for record in records}
    if len(trace_ids) != 1:
        raise ValueError("oracle builder expects exactly one trace")
    run_ids = {
        record.get("attributes", {}).get("agent_observability_lab.run_id")
        for record in records
        if record.get("attributes", {}).get("agent_observability_lab.run_id")
    }
    if len(run_ids) != 1:
        raise ValueError("oracle builder expects exactly one opaque run ID")
    expected_sequence = BASELINE_GRAPHS[task_id]
    return {
        "trace_id": next(iter(trace_ids)),
        "run_id": next(iter(run_ids)),
        "task_id": task_id,
        "condition": "baseline",
        "expected_sequence": expected_sequence,
        "expected_parent_edges": [
            {"parent_index": 0, "child_index": index}
            for index in range(1, len(expected_sequence))
        ],
        "expected_findings": [],
        "expected_outcome": "success",
        **BASELINE_RESOURCES[task_id],
    }
