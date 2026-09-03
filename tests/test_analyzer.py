import json

from agent_observability_lab.analyzer import analyze
from agent_observability_lab.runtime import Condition, DeterministicAgent, InvoiceTask
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
