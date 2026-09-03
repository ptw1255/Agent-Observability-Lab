"""Small, explicit scoring functions for the first profile comparison."""

from __future__ import annotations

from collections.abc import Iterable


def _f1(precision_count: int, predicted_count: int, recall_count: int, actual_count: int) -> float:
    precision = precision_count / predicted_count if predicted_count else 1.0
    recall = recall_count / actual_count if actual_count else 1.0
    return round(2 * precision * recall / (precision + recall), 4) if precision + recall else 0.0


def score_report(report: dict[str, object], oracle: dict[str, object]) -> dict[str, object]:
    """Score one analyzer report against one oracle record."""
    predicted_sequence = list(report.get("sequence", []))
    expected_sequence = list(oracle.get("expected_sequence", []))
    predicted_edges = {
        (edge["parent_index"], edge["child_index"])
        for edge in report.get("parent_edges", [])
    }
    expected_edges = {
        (edge["parent_index"], edge["child_index"])
        for edge in oracle.get("expected_parent_edges", [])
    }
    edge_overlap = len(predicted_edges & expected_edges)

    predicted_findings = {item["type"] for item in report.get("findings", [])}
    expected_findings = set(oracle.get("expected_findings", []))
    finding_overlap = len(predicted_findings & expected_findings)

    return {
        "trace_id": report.get("trace_id"),
        "sequence_exact": predicted_sequence == expected_sequence,
        "sequence_length": {"predicted": len(predicted_sequence), "expected": len(expected_sequence)},
        "topology_edge_f1": _f1(
            edge_overlap,
            len(predicted_edges),
            edge_overlap,
            len(expected_edges),
        ),
        "findings": {
            "precision": round(
                finding_overlap / len(predicted_findings), 4
            ) if predicted_findings else 1.0,
            "recall": round(
                finding_overlap / len(expected_findings), 4
            ) if expected_findings else 1.0,
            "predicted": sorted(predicted_findings),
            "expected": sorted(expected_findings),
        },
    }


def score_reports(
    reports: Iterable[dict[str, object]], oracles: Iterable[dict[str, object]]
) -> list[dict[str, object]]:
    oracles_by_trace = {oracle["trace_id"]: oracle for oracle in oracles}
    return [score_report(report, oracles_by_trace[report["trace_id"]]) for report in reports]
