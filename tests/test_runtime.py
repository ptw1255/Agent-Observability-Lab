import json
from pathlib import Path

import agent_observability_lab.hosted as hosted
from agent_observability_lab.runtime import Condition, DeterministicAgent
from agent_observability_lab.feedback import DuplicateSuppressionFeedback, RetryBudgetFeedback
from agent_observability_lab.hosted import (
    _execute_tool_call,
    _tool_schemas,
    configuration,
    observe_cost_envelope,
    run_tool_probe,
    summarize_reports,
)
from agent_observability_lab.tasks import ComparisonTask, DocumentTask, InvoiceTask
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
        "invoke_agent deterministic-agent",
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


def _run_document(tmp_path, condition):
    output = tmp_path / f"document-{condition.value}.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(session.tracer).run(
            DocumentTask(), condition, "opaque-document-run"
        )
    finally:
        session.shutdown()
    records = [json.loads(line) for line in output.read_text().splitlines()]
    return result, records


def test_document_task_uses_local_retrieval_boundary(tmp_path):
    result, records = _run_document(tmp_path, Condition.BASELINE)

    assert result.answer == "30 days"
    assert [record["name"] for record in records] == [
        "chat scripted-model",
        "execute_tool local_retrieval",
        "chat scripted-model",
        "invoke_agent deterministic-agent",
    ]
    retrieval = next(record for record in records if "local_retrieval" in record["name"])
    assert retrieval["attributes"]["gen_ai.data_source.id"] == "returns-policy-v1"


def test_comparison_task_uses_two_lookup_boundaries(tmp_path):
    output = tmp_path / "comparison.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(session.tracer).run(
            ComparisonTask(), Condition.BASELINE, "opaque-comparison-run"
        )
    finally:
        session.shutdown()
    records = [json.loads(line) for line in output.read_text().splitlines()]

    assert result.answer == "option-a-v1"
    assert [record["name"] for record in records] == [
        "chat scripted-model",
        "execute_tool local_lookup",
        "execute_tool local_lookup",
        "execute_tool calculator",
        "chat scripted-model",
        "invoke_agent deterministic-agent",
    ]
    lookup_ids = [
        record["attributes"]["gen_ai.data_source.id"]
        for record in records
        if record["name"] == "execute_tool local_lookup"
    ]
    assert lookup_ids == ["option-a-v1", "option-b-v1"]


def test_retry_feedback_stops_before_third_failed_attempt(tmp_path):
    output = tmp_path / "feedback.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(
            session.tracer, feedback=RetryBudgetFeedback(failure_limit=2)
        ).run(InvoiceTask(), Condition.RETRY_LOOP, "feedback-run")
    finally:
        session.shutdown()
    records = [json.loads(line) for line in output.read_text().splitlines()]
    tools = [record for record in records if record["name"] == "execute_tool calculator"]
    assert result.answer is None
    assert len(tools) == 2
    root = next(record for record in records if record["name"].startswith("invoke_agent"))
    assert root["attributes"]["agent_observability_lab.feedback_action"] == "stop_retry_loop"


def test_duplicate_feedback_suppresses_repeated_lookup(tmp_path):
    output = tmp_path / "duplicate-feedback.jsonl"
    session = TelemetrySession(output)
    try:
        result = DeterministicAgent(
            session.tracer, feedback=DuplicateSuppressionFeedback()
        ).run(ComparisonTask(), Condition.REDUNDANT_TOOL_USE, "duplicate-feedback-run")
    finally:
        session.shutdown()
    records = [json.loads(line) for line in output.read_text().splitlines()]
    lookups = [record for record in records if record["name"] == "execute_tool local_lookup"]
    root = next(record for record in records if record["name"].startswith("invoke_agent"))
    assert result.answer == "option-a-v1"
    assert len(lookups) == 2
    assert root["attributes"]["agent_observability_lab.feedback_actions"] == "suppress_duplicate_tool"


def test_hosted_configuration_is_safe_without_credentials(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    config = configuration()
    assert config["api_key_configured"] is False
    assert config["model"] == "gpt-5"
    assert config["otlp_endpoint_configured"] is False


def test_hosted_baseline_summary_reports_cost_distribution():
    summary = summarize_reports(
        [
            {
                "model_call_count": 1,
                "input_tokens": 30,
                "output_tokens": 500,
                "duration_ms": 8000.0,
                "span_count": 2,
                "findings": [],
            },
            {
                "model_call_count": 1,
                "input_tokens": 32,
                "output_tokens": 520,
                "duration_ms": 9000.0,
                "span_count": 2,
                "findings": [],
            },
        ]
    )
    assert summary["run_count"] == 2
    assert summary["output_tokens"]["mean"] == 510.0
    assert summary["duration_ms"]["max"] == 9000.0


def test_cost_envelope_is_separate_from_execution_path_findings():
    baseline = {
        "summary": {
            "run_count": 5,
            "output_tokens": {"max": 500.0},
            "duration_ms": {"max": 8000.0},
        }
    }
    observation = observe_cost_envelope(
        {"output_tokens": 700, "duration_ms": 7500}, baseline
    )
    assert observation["exceeded"] is True
    assert observation["exceeded_metrics"] == ["output_tokens"]


def test_hosted_tools_are_read_only_and_use_versioned_fixture_inputs():
    task = ComparisonTask()
    schemas = _tool_schemas()

    assert [schema["name"] for schema in schemas] == [
        "lookup_option",
        "calculate_lower_cost",
    ]
    tool_name, logical_id, option_a, data_source = _execute_tool_call(
        task, "lookup_option", {"option_id": task.option_a_id}
    )
    assert tool_name == "local_lookup"
    assert logical_id == "comparison-option-a-v1"
    assert data_source == task.option_a_id

    tool_name, logical_id, result, _ = _execute_tool_call(
        task,
        "calculate_lower_cost",
        {"option_a_total": option_a["delivered_total"], "option_b_total": 145.0},
    )
    assert tool_name == "calculator"
    assert logical_id == "comparison-lower-cost"
    assert result["lower_option_id"] == task.option_a_id


def test_hosted_tool_probe_records_model_to_tool_topology_without_network(
    tmp_path, monkeypatch
):
    responses = iter(
        [
            {
                "id": "resp-turn-1",
                "usage": {"input_tokens": 10, "output_tokens": 20},
                "output": [
                    {
                        "type": "function_call",
                        "name": "lookup_option",
                        "call_id": "call-a",
                        "arguments": '{"option_id":"option-a-v1"}',
                    },
                    {
                        "type": "function_call",
                        "name": "lookup_option",
                        "call_id": "call-b",
                        "arguments": '{"option_id":"option-b-v1"}',
                    },
                ],
            },
            {
                "id": "resp-turn-2",
                "usage": {"input_tokens": 20, "output_tokens": 20},
                "output": [
                    {
                        "type": "function_call",
                        "name": "calculate_lower_cost",
                        "call_id": "call-c",
                        "arguments": '{"option_a_total":130,"option_b_total":140}',
                    }
                ],
            },
            {
                "id": "resp-turn-3",
                "usage": {"input_tokens": 30, "output_tokens": 8},
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "option-a-v1"}],
                    }
                ],
            },
        ]
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-a-real-secret")
    monkeypatch.setattr(hosted, "_tls_context", lambda: object())
    monkeypatch.setattr(hosted, "_post_response", lambda *args: next(responses))

    result = run_tool_probe(tmp_path / "hosted-tools", max_turns=6)

    assert result["answer"] == "option-a-v1"
    assert result["report"]["model_call_count"] == 3
    assert result["report"]["tool_call_count"] == 3
    assert result["report"]["findings"] == []
    records = [json.loads(line) for line in Path(result["trace_path"]).read_text().splitlines()]
    model_spans = [record for record in records if record["name"] == "chat hosted-model"]
    tool_spans = [record for record in records if record["name"].startswith("execute_tool")]
    assert {span["parent_span_id"] for span in tool_spans}.issubset(
        {span["span_id"] for span in model_spans}
    )
