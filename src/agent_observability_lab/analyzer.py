"""Telemetry-only analysis for the first vertical slice."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def analyze(path: Path) -> list[dict[str, object]]:
    """Infer findings without reading condition labels or ground truth."""
    traces: dict[str, list[dict[str, object]]] = defaultdict(list)
    with path.open(encoding="utf-8") as source:
        for line in source:
            if line.strip():
                record = json.loads(line)
                traces[record["trace_id"]].append(record)

    reports: list[dict[str, object]] = []
    for trace_id, spans in traces.items():
        spans.sort(key=lambda item: item["start_time_unix_nano"])
        tool_spans = [span for span in spans if span["name"].startswith("execute_tool ")]
        span_by_id = {span["span_id"]: span for span in spans}
        findings: list[dict[str, object]] = []
        error_tools = []
        for span in tool_spans:
            if span["status"] == "ERROR" or span["attributes"].get("error.type"):
                error_tools.append(span)
                findings.append(
                    {
                        "type": "tool_failure",
                        "span_id": span["span_id"],
                        "evidence": "tool span ended with error status",
                    }
                )

        if len(tool_spans) >= 3 and len(error_tools) >= 2:
            findings.append(
                {
                    "type": "retry_loop",
                    "span_id": error_tools[-1]["span_id"],
                    "evidence": "repeated tool failures consumed multiple attempts",
                }
            )

        successful_tools = [span for span in tool_spans if span["status"] != "ERROR"]
        fingerprints: dict[str, list[dict[str, object]]] = defaultdict(list)
        for span in successful_tools:
            fingerprint = span["attributes"].get(
                "agent_observability_lab.argument_fingerprint"
            )
            if fingerprint:
                fingerprints[str(fingerprint)].append(span)
        for matching_spans in fingerprints.values():
            if len(matching_spans) >= 2:
                findings.append(
                    {
                        "type": "candidate_redundant_tool_use",
                        "span_id": matching_spans[-1]["span_id"],
                        "evidence": "successful tool calls share an argument fingerprint",
                    }
                )
                break

        def depth(span: dict[str, object]) -> int:
            current = span
            result = 0
            seen: set[str] = set()
            while current.get("parent_span_id"):
                parent_id = str(current["parent_span_id"])
                if parent_id in seen or parent_id not in span_by_id:
                    break
                seen.add(parent_id)
                result += 1
                current = span_by_id[parent_id]
            return result

        max_depth = max((depth(span) for span in spans), default=0)
        model_call_count = sum(span["name"].startswith("chat ") for span in spans)
        total_output_tokens = sum(
            int(span["attributes"].get("gen_ai.usage.output_tokens", 0))
            for span in spans
            if span["name"].startswith("chat ")
        )
        if max_depth >= 6 or model_call_count >= 6 or total_output_tokens >= 300:
            findings.append(
                {
                    "type": "excessive_execution_path",
                    "span_id": spans[-1]["span_id"],
                    "evidence": "depth, model calls, or output tokens exceeded the local envelope",
                }
            )

        sequence = [span["name"] for span in spans]
        sequence_index = {span["span_id"]: index for index, span in enumerate(spans)}
        parent_edges = [
            {
                "parent_index": sequence_index[span["parent_span_id"]],
                "child_index": sequence_index[span["span_id"]],
            }
            for span in spans
            if span.get("parent_span_id") in sequence_index
        ]
        total_input_tokens = sum(
            int(span["attributes"].get("gen_ai.usage.input_tokens", 0))
            for span in spans
            if span["name"].startswith("chat ")
        )
        total_duration_ms = max(
            (float(span["end_time_unix_nano"]) - float(span["start_time_unix_nano"])) / 1_000_000
            for span in spans
        ) if spans else 0.0
        attempt_numbers = [
            span["attributes"].get("agent_observability_lab.attempt_number")
            for span in tool_spans
        ]

        reports.append(
            {
                "trace_id": trace_id,
                "sequence": sequence,
                "parent_edges": parent_edges,
                "span_count": len(spans),
                "tool_call_count": len(tool_spans),
                "model_call_count": model_call_count,
                "max_depth": max_depth,
                "input_tokens": total_input_tokens,
                "output_tokens": total_output_tokens,
                "duration_ms": round(total_duration_ms, 3),
                "error_count": len(error_tools),
                "attempt_numbers": attempt_numbers,
                "findings": findings,
            }
        )
    return reports
