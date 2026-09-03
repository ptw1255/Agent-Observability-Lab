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
        tool_spans = [span for span in spans if span["name"] == "execute_tool calculator"]
        findings: list[dict[str, object]] = []
        for span in tool_spans:
            if span["status"] == "ERROR" or span["attributes"].get("error.type"):
                findings.append(
                    {
                        "type": "tool_failure",
                        "span_id": span["span_id"],
                        "evidence": "tool span ended with error status",
                    }
                )

        reports.append(
            {
                "trace_id": trace_id,
                "sequence": [span["name"] for span in spans],
                "span_count": len(spans),
                "tool_call_count": len(tool_spans),
                "model_call_count": sum(span["name"].startswith("chat ") for span in spans),
                "findings": findings,
            }
        )
    return reports
