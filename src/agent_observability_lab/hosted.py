"""Small hosted-model portability probe; deterministic scoring stays separate."""

from __future__ import annotations

import json
import os
import ssl
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

from opentelemetry.trace import SpanKind

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
