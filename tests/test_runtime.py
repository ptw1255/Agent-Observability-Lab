import json

from agent_observability_lab.runtime import Condition, DeterministicAgent, InvoiceTask
from agent_observability_lab.telemetry import TelemetrySession


def _run(tmp_path, condition):
    output = tmp_path / f"{condition.value}.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(session.tracer).run(
            InvoiceTask(), condition, f"test-{condition.value}"
        )
    finally:
        session.shutdown()
    records = [json.loads(line) for line in output.read_text().splitlines()]
    return result, records


def test_baseline_has_expected_answer_and_topology(tmp_path):
    result, records = _run(tmp_path, Condition.BASELINE)

    assert result.answer == 64.64
    assert [record["name"] for record in records] == [
        "chat scripted-model",
        "execute_tool calculator",
        "chat scripted-model",
        "invoke_agent invoice-agent",
    ]
    assert all(record["status"] == "UNSET" for record in records)


def test_transient_failure_is_recorded_and_recovered(tmp_path):
    result, records = _run(tmp_path, Condition.TRANSIENT_TOOL_FAILURE)

    assert result.answer == 64.64
    tool_records = [record for record in records if record["name"] == "execute_tool calculator"]
    assert len(tool_records) == 2
    assert tool_records[0]["status"] == "ERROR"
    assert tool_records[1]["status"] == "UNSET"
    assert tool_records[0]["attributes"]["agent_observability_lab.attempt_number"] == 1
