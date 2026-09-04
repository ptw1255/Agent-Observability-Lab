import json
from pathlib import Path

from agent_observability_lab.analyzer import analyze
from agent_observability_lab.projections import EvidenceProfile, project_file
from agent_observability_lab.oracle import (
    build_baseline_oracle,
    build_hosted_tool_baseline_oracle,
    build_hosted_tool_recovery_oracle,
    build_oracle,
)
from agent_observability_lab.scoring import score_report
from agent_observability_lab.runtime import Condition, DeterministicAgent
from agent_observability_lab.tasks import ComparisonTask, InvoiceTask
from agent_observability_lab.telemetry import TelemetrySession


def test_profiles_remove_and_retain_expected_fields(tmp_path):
    raw_path = tmp_path / "raw.jsonl"
    session = TelemetrySession(raw_path)
    try:
        DeterministicAgent(session.tracer).run(InvoiceTask(), Condition.BASELINE, "opaque-run")
    finally:
        session.shutdown()

    p0_path = tmp_path / "p0.jsonl"
    p1_path = tmp_path / "p1.jsonl"
    p2_path = tmp_path / "p2.jsonl"
    project_file(raw_path, p0_path, EvidenceProfile.P0)
    project_file(raw_path, p1_path, EvidenceProfile.P1)
    project_file(raw_path, p2_path, EvidenceProfile.P2)

    p0 = json.loads(p0_path.read_text().splitlines()[0])
    p1 = json.loads(p1_path.read_text().splitlines()[0])
    p2 = json.loads(p2_path.read_text().splitlines()[0])
    assert p0["attributes"] == {}
    assert "gen_ai.request.model" in p1["attributes"]
    assert "agent_observability_lab.run_id" not in p1["attributes"]
    assert "agent_observability_lab.run_id" in p2["attributes"]


def test_scoring_compares_sequence_edges_and_findings():
    report = {
        "trace_id": "trace-1",
        "sequence": ["root", "tool"],
        "parent_edges": [{"parent_index": 0, "child_index": 1}],
        "findings": [{"type": "tool_failure"}],
    }
    oracle = {
        "trace_id": "trace-1",
        "expected_sequence": ["root", "tool"],
        "expected_parent_edges": [{"parent_index": 0, "child_index": 1}],
        "expected_findings": ["tool_failure"],
    }
    result = score_report(report, oracle)
    assert result["sequence_exact"] is True
    assert result["topology_edge_f1"] == 1.0
    assert result["findings"]["precision"] == 1.0
    assert result["findings"]["recall"] == 1.0


def test_analyzer_reports_scoreable_topology_fields(tmp_path):
    output = tmp_path / "trace.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(InvoiceTask(), Condition.BASELINE, "opaque-run")
    finally:
        session.shutdown()

    report = analyze(output)[0]
    assert report["sequence"]
    assert report["parent_edges"]
    assert report["model_call_count"] == 2
    assert report["tool_call_count"] == 1


def test_baseline_oracle_matches_invoice_graph(tmp_path):
    output = tmp_path / "trace.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(InvoiceTask(), Condition.BASELINE, "opaque-run")
    finally:
        session.shutdown()

    oracle = build_baseline_oracle(output, "invoice-total-v1")
    assert oracle["expected_sequence"] == [
        "invoke_agent deterministic-agent",
        "chat scripted-model",
        "execute_tool calculator",
        "chat scripted-model",
    ]
    assert oracle["expected_parent_edges"] == [
        {"parent_index": 0, "child_index": 1},
        {"parent_index": 0, "child_index": 2},
        {"parent_index": 0, "child_index": 3},
    ]


def test_transient_oracle_captures_recovery_attempts(tmp_path):
    output = tmp_path / "transient.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            InvoiceTask(), Condition.TRANSIENT_TOOL_FAILURE, "opaque-run"
        )
    finally:
        session.shutdown()

    oracle = build_oracle(output, "invoice-total-v1", "transient_tool_failure")
    assert oracle["expected_findings"] == ["tool_failure"]
    assert oracle["expected_attempt_numbers"] == [1, 2]


def test_retry_oracle_captures_terminal_failure(tmp_path):
    output = tmp_path / "retry.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            InvoiceTask(), Condition.RETRY_LOOP, "opaque-run"
        )
    finally:
        session.shutdown()

    oracle = build_oracle(output, "invoice-total-v1", "retry_loop")
    assert oracle["expected_findings"] == ["tool_failure", "retry_loop"]
    assert oracle["expected_attempt_numbers"] == [1, 2, 3]
    assert oracle["expected_root_status"] == "ERROR"


def test_redundant_comparison_oracle_captures_duplicate_tool_use(tmp_path):
    output = tmp_path / "redundant.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            ComparisonTask(), Condition.REDUNDANT_TOOL_USE, "opaque-run"
        )
    finally:
        session.shutdown()

    oracle = build_oracle(output, "two-option-comparison-v1", "redundant_tool_use")
    assert oracle["expected_findings"] == ["candidate_redundant_tool_use"]
    assert oracle["expected_attempt_numbers"] == [1, 1, 1, 1]
    assert oracle["expected_tool_call_count"] == 4
    assert oracle["expected_sequence"][4] == "execute_tool local_lookup"
    assert oracle["expected_sequence"][5] == "execute_tool calculator"


def test_excessive_path_oracle_captures_depth_and_cost(tmp_path):
    output = tmp_path / "excessive.jsonl"
    session = TelemetrySession(output)
    try:
        DeterministicAgent(session.tracer).run(
            InvoiceTask(), Condition.EXCESSIVE_PATH, "opaque-run"
        )
    finally:
        session.shutdown()

    oracle = build_oracle(output, "invoice-total-v1", "excessive_path")
    assert oracle["expected_findings"] == ["excessive_execution_path"]
    assert oracle["expected_max_depth"] == 6
    assert oracle["expected_output_tokens"] == 360
    assert len(oracle["expected_parent_edges"]) == 13
    assert {"parent_index": 2, "child_index": 4} in oracle["expected_parent_edges"]


def test_hosted_tool_oracle_scores_the_published_baseline_trace():
    root = Path(__file__).resolve().parents[1]
    trace = root / "data/published/local-v0-hosted-tool-probe-attempt-02/raw-trace.jsonl"
    report = analyze(trace)[0]
    oracle = build_hosted_tool_baseline_oracle(trace)
    score = score_report(report, oracle)

    assert oracle["runtime_lane"] == "hosted"
    assert score["sequence_exact"] is True
    assert score["topology_edge_f1"] == 1.0
    assert all(score["resource_matches"].values())
    assert score["attempt_sequence_match"] is True
    assert score["runtime_lane_match"] is True


def test_hosted_recovery_oracle_exposes_missing_retry_in_published_failure_trace():
    root = Path(__file__).resolve().parents[1]
    trace = root / "data/published/local-v0-hosted-tool-probe-attempt-03-failure/raw-trace.jsonl"
    report = analyze(trace)[0]
    oracle = build_hosted_tool_recovery_oracle(trace)
    score = score_report(report, oracle)

    assert score["sequence_exact"] is False
    assert score["resource_matches"]["model_call_count"] is False
    assert score["resource_matches"]["tool_call_count"] is False
    assert score["attempt_sequence_match"] is False
    assert score["findings"]["predicted"] == ["tool_failure"]
    assert score["findings"]["expected"] == ["tool_failure"]
