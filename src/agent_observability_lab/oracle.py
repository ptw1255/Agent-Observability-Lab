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


def _root_edges(sequence: list[str]) -> list[dict[str, int]]:
    return [
        {"parent_index": 0, "child_index": index}
        for index in range(1, len(sequence))
    ]


def _excessive_graph(task_id: str) -> tuple[list[str], list[dict[str, int]]]:
    base = BASELINE_GRAPHS[task_id]
    reflection: list[str] = []
    edges: list[dict[str, int]] = [{"parent_index": 0, "child_index": 1}]
    for depth in range(1, 6):
        reflection_index = 2 + (depth - 1) * 2
        model_index = reflection_index + 1
        reflection.extend(["plan reflection", "chat scripted-model"])
        parent = 0 if depth == 1 else reflection_index - 2
        edges.extend([
            {"parent_index": parent, "child_index": reflection_index},
            {"parent_index": reflection_index, "child_index": model_index},
        ])
    suffix = base[2:]
    sequence = base[:2] + reflection + suffix
    suffix_start = 2 + len(reflection)
    edges.extend(
        {"parent_index": 0, "child_index": suffix_start + index}
        for index in range(len(suffix))
    )
    return sequence, edges


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
    base_resources = BASELINE_RESOURCES[task_id]
    expected_findings: list[str] = []
    if condition == "baseline":
        expected_sequence = BASELINE_GRAPHS[task_id]
        resources = base_resources
    elif condition == "transient_tool_failure":
        tool_index = next(
            index for index, name in enumerate(BASELINE_GRAPHS[task_id])
            if name.startswith("execute_tool ")
        )
        expected_sequence = (
            BASELINE_GRAPHS[task_id][:tool_index]
            + [BASELINE_GRAPHS[task_id][tool_index], "chat scripted-model",
               BASELINE_GRAPHS[task_id][tool_index]]
            + BASELINE_GRAPHS[task_id][tool_index + 1:]
        )
        resources = {
            "expected_model_call_count": base_resources["expected_model_call_count"] + 1,
            "expected_tool_call_count": base_resources["expected_tool_call_count"] + 1,
            "expected_input_tokens": base_resources["expected_input_tokens"] + 32,
            "expected_output_tokens": base_resources["expected_output_tokens"] + 18,
        }
        expected_findings = ["tool_failure"]
    elif condition == "retry_loop":
        tool_name = next(name for name in BASELINE_GRAPHS[task_id] if name.startswith("execute_tool "))
        expected_sequence = [BASELINE_GRAPHS[task_id][0], BASELINE_GRAPHS[task_id][1]]
        for _ in range(3):
            expected_sequence.extend([tool_name, "chat scripted-model"])
        resources = {
            "expected_model_call_count": 4,
            "expected_tool_call_count": 3,
            "expected_input_tokens": 128,
            "expected_output_tokens": 84,
        }
        expected_findings = ["tool_failure", "retry_loop"]
    elif condition == "redundant_tool_use":
        expected_sequence = list(BASELINE_GRAPHS[task_id])
        tool_indices = [
            index for index, name in enumerate(expected_sequence)
            if name.startswith("execute_tool ")
        ]
        duplicate_index = tool_indices[-2] if task_id == "two-option-comparison-v1" else tool_indices[0]
        expected_sequence.insert(duplicate_index + 1, expected_sequence[duplicate_index])
        resources = {
            **base_resources,
            "expected_tool_call_count": base_resources["expected_tool_call_count"] + 1,
        }
        expected_findings = ["candidate_redundant_tool_use"]
    elif condition == "excessive_path":
        expected_sequence, expected_parent_edges = _excessive_graph(task_id)
        resources = {
            **base_resources,
            "expected_model_call_count": base_resources["expected_model_call_count"] + 5,
            "expected_max_depth": 6,
            "expected_input_tokens": base_resources["expected_input_tokens"] + 160,
            "expected_output_tokens": base_resources["expected_output_tokens"] + 320,
        }
        expected_findings = ["excessive_execution_path"]
    else:
        raise ValueError(f"oracle graph not yet defined: {task_id}/{condition}")
    if condition != "excessive_path":
        expected_parent_edges = _root_edges(expected_sequence)
    expected_attempt_numbers = [
        1 for name in expected_sequence if name.startswith("execute_tool ")
    ]
    if condition == "transient_tool_failure":
        tool_count = len(expected_attempt_numbers)
        expected_attempt_numbers = list(range(1, tool_count + 1)) if task_id != "two-option-comparison-v1" else [1, 2, 1, 1]
    elif condition == "retry_loop":
        expected_attempt_numbers = [1, 2, 3]
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
