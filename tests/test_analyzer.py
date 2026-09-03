import json

from agent_observability_lab.analyzer import analyze
import pytest

from agent_observability_lab.runtime import Condition, DeterministicAgent
from agent_observability_lab.tasks import ComparisonTask, DocumentTask, InvoiceTask
from agent_observability_lab.telemetry import TelemetrySession


def test_analyzer_detects_tool_failure_from_telemetry(tmp_path):
    output = tmp_path / "trace.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            InvoiceTask(), Condition.TRANSIENT_TOOL_FAILURE, "opaque-run-id"
        )
    finally:
        session.shutdown()

    reports = analyze(output)
    assert len(reports) == 1
    assert [finding["type"] for finding in reports[0]["findings"]] == ["tool_failure"]

    # The analyzer input contains runtime correlation only, not the condition label.
    raw = output.read_text()
    assert "transient_tool_failure" not in raw


@pytest.mark.parametrize(
    ("condition", "finding"),
    [
        (Condition.RETRY_LOOP, "retry_loop"),
        (Condition.REDUNDANT_TOOL_USE, "candidate_redundant_tool_use"),
        (Condition.EXCESSIVE_PATH, "excessive_execution_path"),
    ],
)
def test_analyzer_detects_additional_conditions_without_labels(tmp_path, condition, finding):
    output = tmp_path / f"{condition.value}.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(session.tracer).run(
            InvoiceTask(), condition, "opaque-run-id"
        )
    finally:
        session.shutdown()

    reports = analyze(output)
    finding_types = {item["type"] for item in reports[0]["findings"]}
    assert finding in finding_types
    assert condition.value not in output.read_text()
    if condition == Condition.EXCESSIVE_PATH:
        assert result.answer == 64.64
    if condition == Condition.RETRY_LOOP:
        assert result.answer is None


@pytest.mark.parametrize("condition", list(Condition))
def test_document_task_conditions_remain_blind(tmp_path, condition):
    output = tmp_path / f"document-{condition.value}.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(session.tracer).run(
            DocumentTask(), condition, "opaque-document-run"
        )
    finally:
        session.shutdown()

    report = analyze(output)[0]
    raw = output.read_text()
    assert condition.value not in raw
    if condition == Condition.RETRY_LOOP:
        assert result.answer is None
        assert "retry_loop" in {item["type"] for item in report["findings"]}
    else:
        assert result.answer == "30 days"


def test_comparison_baseline_does_not_look_redundant(tmp_path):
    output = tmp_path / "comparison-baseline.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            ComparisonTask(), Condition.BASELINE, "opaque-comparison-run"
        )
    finally:
        session.shutdown()

    finding_types = {item["type"] for item in analyze(output)[0]["findings"]}
    assert "candidate_redundant_tool_use" not in finding_types


def test_comparison_redundant_lookup_is_detected(tmp_path):
    output = tmp_path / "comparison-redundant.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            ComparisonTask(), Condition.REDUNDANT_TOOL_USE, "opaque-comparison-run"
        )
    finally:
        session.shutdown()

    finding_types = {item["type"] for item in analyze(output)[0]["findings"]}
    assert "candidate_redundant_tool_use" in finding_types
