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

TRANSIENT_INVOICE_GRAPH = [
    "invoke_agent deterministic-agent",
    "chat scripted-model",
    "execute_tool calculator",
    "chat scripted-model",
    "execute_tool calculator",
    "chat scripted-model",
]

TRANSIENT_INVOICE_RESOURCES = {
    "expected_model_call_count": 3,
    "expected_tool_call_count": 2,
    "expected_input_tokens": 96,
    "expected_output_tokens": 58,
}

RETRY_INVOICE_GRAPH = [
    "invoke_agent deterministic-agent",
    "chat scripted-model",
    "execute_tool calculator",
    "chat scripted-model",
    "execute_tool calculator",
    "chat scripted-model",
    "execute_tool calculator",
    "chat scripted-model",
]

RETRY_INVOICE_RESOURCES = {
    "expected_model_call_count": 4,
    "expected_tool_call_count": 3,
    "expected_input_tokens": 128,
    "expected_output_tokens": 84,
}

REDUNDANT_COMPARISON_GRAPH = [
    "invoke_agent deterministic-agent",
    "chat scripted-model",
    "execute_tool local_lookup",
    "execute_tool local_lookup",
    "execute_tool local_lookup",
    "execute_tool calculator",
    "chat scripted-model",
]

REDUNDANT_COMPARISON_RESOURCES = {
    "expected_model_call_count": 2,
    "expected_tool_call_count": 4,
    "expected_input_tokens": 64,
    "expected_output_tokens": 40,
}

EXCESSIVE_INVOICE_GRAPH = [
    "invoke_agent deterministic-agent",
    "chat scripted-model",
    "plan reflection",
    "chat scripted-model",
    "plan reflection",
    "chat scripted-model",
    "plan reflection",
    "chat scripted-model",
    "plan reflection",
    "chat scripted-model",
    "plan reflection",
    "chat scripted-model",
    "execute_tool calculator",
    "chat scripted-model",
]

EXCESSIVE_INVOICE_RESOURCES = {
    "expected_model_call_count": 7,
    "expected_tool_call_count": 1,
    "expected_max_depth": 6,
    "expected_input_tokens": 224,
    "expected_output_tokens": 360,
}

EXCESSIVE_INVOICE_EDGES = [
    {"parent_index": 0, "child_index": 1},
    {"parent_index": 0, "child_index": 2},
    {"parent_index": 2, "child_index": 3},
    {"parent_index": 2, "child_index": 4},
    {"parent_index": 4, "child_index": 5},
    {"parent_index": 4, "child_index": 6},
    {"parent_index": 6, "child_index": 7},
    {"parent_index": 6, "child_index": 8},
    {"parent_index": 8, "child_index": 9},
    {"parent_index": 8, "child_index": 10},
    {"parent_index": 10, "child_index": 11},
    {"parent_index": 0, "child_index": 12},
    {"parent_index": 0, "child_index": 13},
]


def build_oracle(trace_path: Path, task_id: str, condition: str) -> dict[str, object]:
    """Build one oracle from a raw trace and a known deterministic task graph."""
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
    if condition == "baseline":
        expected_sequence = BASELINE_GRAPHS[task_id]
        resources = BASELINE_RESOURCES[task_id]
        expected_findings = []
        expected_attempt_numbers = [
            1 for name in expected_sequence if name.startswith("execute_tool ")
        ]
    elif task_id == "invoice-total-v1" and condition == "transient_tool_failure":
        expected_sequence = TRANSIENT_INVOICE_GRAPH
        resources = TRANSIENT_INVOICE_RESOURCES
        expected_findings = ["tool_failure"]
        expected_attempt_numbers = [1, 2]
    elif task_id == "invoice-total-v1" and condition == "retry_loop":
        expected_sequence = RETRY_INVOICE_GRAPH
        resources = RETRY_INVOICE_RESOURCES
        expected_findings = ["tool_failure", "retry_loop"]
        expected_attempt_numbers = [1, 2, 3]
    elif task_id == "two-option-comparison-v1" and condition == "redundant_tool_use":
        expected_sequence = REDUNDANT_COMPARISON_GRAPH
        resources = REDUNDANT_COMPARISON_RESOURCES
        expected_findings = ["candidate_redundant_tool_use"]
        expected_attempt_numbers = [1, 1, 1, 1]
    elif task_id == "invoice-total-v1" and condition == "excessive_path":
        expected_sequence = EXCESSIVE_INVOICE_GRAPH
        resources = EXCESSIVE_INVOICE_RESOURCES
        expected_findings = ["excessive_execution_path"]
        expected_attempt_numbers = [1]
    else:
        raise ValueError(f"oracle graph not yet defined: {task_id}/{condition}")
    expected_parent_edges = [
        {"parent_index": 0, "child_index": index}
        for index in range(1, len(expected_sequence))
    ]
    if task_id == "invoice-total-v1" and condition == "excessive_path":
        expected_parent_edges = EXCESSIVE_INVOICE_EDGES
    return {
        "trace_id": next(iter(trace_ids)),
        "run_id": next(iter(run_ids)),
        "task_id": task_id,
        "condition": condition,
        "expected_sequence": expected_sequence,
        "expected_parent_edges": expected_parent_edges,
        "expected_findings": expected_findings,
        "expected_outcome": "failed" if condition == "retry_loop" else "success",
        "expected_root_status": "ERROR" if condition == "retry_loop" else "UNSET",
        "expected_attempt_numbers": expected_attempt_numbers,
        **resources,
    }


def build_baseline_oracle(trace_path: Path, task_id: str) -> dict[str, object]:
    return build_oracle(trace_path, task_id, "baseline")
