"""Small hosted-model portability probe; deterministic scoring stays separate."""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
import uuid
from statistics import mean
from pathlib import Path

from opentelemetry.trace import SpanKind

from .analyzer import analyze
from .telemetry import TelemetrySession


def configuration() -> dict[str, object]:
    return {
        "api_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "model": os.environ.get("AOL_HOSTED_MODEL", "gpt-5"),
        "otlp_endpoint_configured": bool(os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")),
        "response_endpoint": os.environ.get(
            "AOL_HOSTED_ENDPOINT", "https://api.openai.com/v1/responses"
        ),
    }


def run_probe(output: Path, model: str | None = None) -> dict[str, object]:
    """Make one hosted request and record the reusable telemetry boundary."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required; use the configuration check first")
    model_name = model or os.environ.get("AOL_HOSTED_MODEL", "gpt-5")
    endpoint = os.environ.get(
        "AOL_HOSTED_ENDPOINT", "https://api.openai.com/v1/responses"
    )
    run_id = str(uuid.uuid4())
    prompt = (
        "Calculate the invoice total for 3 units at $19.95 with an 8% tax rate. "
        "Return only the numeric total."
    )
    payload = json.dumps({"model": model_name, "input": prompt, "store": False}).encode()
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    session = TelemetrySession(
        output,
        otlp_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT"),
    )
    try:
        with session.tracer.start_as_current_span(
            "invoke_agent hosted-probe",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "invoke_agent",
                "gen_ai.agent.name": "hosted-probe",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.task_id": "invoice-total-v1",
                "agent_observability_lab.runtime_lane": "hosted",
            },
        ) as root:
            started = time.perf_counter()
            with session.tracer.start_as_current_span(
                "chat hosted-model",
                kind=SpanKind.CLIENT,
                attributes={
                    "gen_ai.operation.name": "chat",
                    "gen_ai.request.model": model_name,
                    "gen_ai.provider.name": "openai",
                    "gen_ai.agent.name": "hosted-probe",
                    "agent_observability_lab.run_id": run_id,
                },
            ) as span:
                try:
                    try:
                        import certifi
                    except ImportError as error:
                        raise RuntimeError(
                            "Hosted integration requires the integration extra: "
                            "pip install -e '.[integration]'"
                        ) from error
                    tls_context = ssl.create_default_context(cafile=certifi.where())
                    with urllib.request.urlopen(
                        request, timeout=60, context=tls_context
                    ) as response:
                        body = json.loads(response.read().decode())
                except urllib.error.HTTPError as error:
                    root.set_attribute("agent_observability_lab.task_outcome", "failed")
                    span.record_exception(error)
                    raise
                usage = body.get("usage", {})
                if "input_tokens" in usage:
                    span.set_attribute("gen_ai.usage.input_tokens", usage["input_tokens"])
                if "output_tokens" in usage:
                    span.set_attribute("gen_ai.usage.output_tokens", usage["output_tokens"])
                reasoning_tokens = usage.get("output_tokens_details", {}).get(
                    "reasoning_tokens"
                )
                if reasoning_tokens is not None:
                    span.set_attribute(
                        "agent_observability_lab.reasoning_tokens", reasoning_tokens
                    )
                if body.get("id"):
                    span.set_attribute("gen_ai.response.id", body["id"])
                span.set_attribute(
                    "agent_observability_lab.provider_latency_ms",
                    round((time.perf_counter() - started) * 1000, 3),
                )
            root.set_attribute("agent_observability_lab.task_outcome", "success")
    finally:
        session.shutdown()
    return {
        "run_id": run_id,
        "model": model_name,
        "runtime_lane": "hosted",
        "trace_path": str(output),
        "response_id": body.get("id"),
        "usage": body.get("usage", {}),
    }


def summarize_reports(reports: list[dict[str, object]]) -> dict[str, object]:
    """Summarize a narrow set of comparable hosted traces."""
    if not reports:
        raise ValueError("at least one hosted report is required")

    def distribution(field: str) -> dict[str, float]:
        values = [float(report[field]) for report in reports]
        return {
            "min": round(min(values), 3),
            "mean": round(mean(values), 3),
            "max": round(max(values), 3),
        }

    return {
        "run_count": len(reports),
        "model_call_count": distribution("model_call_count"),
        "input_tokens": distribution("input_tokens"),
        "output_tokens": distribution("output_tokens"),
        "duration_ms": distribution("duration_ms"),
        "span_count": distribution("span_count"),
        "finding_types": sorted(
            {
                finding["type"]
                for report in reports
                for finding in report["findings"]
            }
        ),
    }


def run_baseline(
    output_root: Path, repetitions: int = 5, model: str | None = None
) -> dict[str, object]:
    """Run comparable hosted probes and write a local cost-baseline summary."""
    if repetitions < 1:
        raise ValueError("repetitions must be at least 1")
    runs: list[dict[str, object]] = []
    reports: list[dict[str, object]] = []
    for repetition in range(1, repetitions + 1):
        run_root = output_root / f"run-{repetition:02d}"
        result = run_probe(run_root / "raw-trace.jsonl", model)
        report = analyze(run_root / "raw-trace.jsonl")[0]
        (run_root / "analysis.json").write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        runs.append({"repetition": repetition, "result": result, "report": report})
        reports.append(report)
    summary = {
        "model": model or os.environ.get("AOL_HOSTED_MODEL", "gpt-5"),
        "runtime_lane": "hosted",
        "summary": summarize_reports(reports),
        "runs": runs,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary
