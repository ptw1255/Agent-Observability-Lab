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

from opentelemetry.trace import SpanKind, Status, StatusCode

from .analyzer import analyze
from .runtime import _fingerprint
from .tasks import ComparisonTask
from .telemetry import TelemetrySession


class HostedAPIError(RuntimeError):
    """An API error whose message preserves the server's safe diagnostic text."""


def configuration() -> dict[str, object]:
    return {
        "api_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
        "model": os.environ.get("AOL_HOSTED_MODEL", "gpt-5"),
        "otlp_endpoint_configured": bool(os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")),
        "response_endpoint": os.environ.get(
            "AOL_HOSTED_ENDPOINT", "https://api.openai.com/v1/responses"
        ),
    }


def _prompt(scenario: str) -> str:
    if scenario == "cost-stress":
        return (
            "For each invoice below, calculate the total after tax, identify the "
            "highest total, and return a JSON object with five totals and the highest "
            "invoice ID. Verify the arithmetic before responding. "
            "A: 3 units at $19.95, 8% tax. B: 7 units at $12.40, 6.5% tax. "
            "C: 14 units at $8.75, 9.25% tax. D: 5 units at $31.60, 7.75% tax. "
            "E: 11 units at $16.20, 5% tax."
        )
    return (
        "Calculate the invoice total for 3 units at $19.95 with an 8% tax rate. "
        "Return only the numeric total."
    )


def _tls_context() -> ssl.SSLContext:
    """Build a verified TLS context from certifi's CA bundle."""
    try:
        import certifi
    except ImportError as error:
        raise RuntimeError(
            "Hosted integration requires the integration extra: "
            "pip install -e '.[integration]'"
        ) from error
    return ssl.create_default_context(cafile=certifi.where())


def _post_response(
    endpoint: str, api_key: str, payload_body: dict[str, object], tls_context: ssl.SSLContext
) -> dict[str, object]:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload_body).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60, context=tls_context) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        raw_detail = error.read().decode("utf-8", errors="replace")
        try:
            detail = json.loads(raw_detail).get("error", {}).get("message", raw_detail)
        except json.JSONDecodeError:
            detail = raw_detail
        raise HostedAPIError(f"OpenAI API request failed ({error.code}): {detail}") from error


def _record_usage(span, body: dict[str, object], started: float) -> None:
    usage = body.get("usage", {})
    if "input_tokens" in usage:
        span.set_attribute("gen_ai.usage.input_tokens", usage["input_tokens"])
    if "output_tokens" in usage:
        span.set_attribute("gen_ai.usage.output_tokens", usage["output_tokens"])
    reasoning_tokens = usage.get("output_tokens_details", {}).get("reasoning_tokens")
    if reasoning_tokens is not None:
        span.set_attribute("agent_observability_lab.reasoning_tokens", reasoning_tokens)
    if body.get("id"):
        span.set_attribute("gen_ai.response.id", body["id"])
    span.set_attribute(
        "agent_observability_lab.provider_latency_ms",
        round((time.perf_counter() - started) * 1000, 3),
    )


def _tool_schemas() -> list[dict[str, object]]:
    """The two deliberately small, read-only tools exposed to the hosted model."""
    return [
        {
            "type": "function",
            "name": "lookup_option",
            "description": "Look up one option's delivered-cost inputs by option ID.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "option_id": {
                        "type": "string",
                        "enum": ["option-a-v1", "option-b-v1"],
                    }
                },
                "required": ["option_id"],
                "additionalProperties": False,
            },
        },
        {
            "type": "function",
            "name": "calculate_lower_cost",
            "description": "Compare two already-calculated delivered totals and return the lower option.",
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {
                    "option_a_total": {"type": "number"},
                    "option_b_total": {"type": "number"},
                },
                "required": ["option_a_total", "option_b_total"],
                "additionalProperties": False,
            },
        },
    ]


def _execute_tool_call(
    task: ComparisonTask, name: str, arguments: dict[str, object]
) -> tuple[str, str, dict[str, object], str]:
    """Execute only the local fixture tools; the model has no external authority."""
    if name == "lookup_option":
        option_id = arguments.get("option_id")
        if option_id not in {task.option_a_id, task.option_b_id}:
            raise ValueError("lookup_option received an unsupported option_id")
        option = task.option(str(option_id))
        result = {
            **option,
            "delivered_total": float(option["base_price"]) + float(option["shipping"]),
        }
        return "local_lookup", f"comparison-{option_id}", result, str(option_id)
    if name == "calculate_lower_cost":
        option_a_total = float(arguments["option_a_total"])
        option_b_total = float(arguments["option_b_total"])
        answer = task.option_a_id if option_a_total < option_b_total else task.option_b_id
        result = {"lower_option_id": answer, "option_a_total": option_a_total, "option_b_total": option_b_total}
        return "calculator", "comparison-lower-cost", result, "comparison-totals"
    raise ValueError(f"unsupported hosted tool: {name}")


def _tool_metadata(task: ComparisonTask, name: str, arguments: dict[str, object]) -> tuple[str, str, str]:
    """Resolve stable span identity before a local tool is attempted."""
    if name == "lookup_option":
        option_id = arguments.get("option_id")
        if option_id not in {task.option_a_id, task.option_b_id}:
            raise ValueError("lookup_option received an unsupported option_id")
        return "local_lookup", f"comparison-{option_id}", str(option_id)
    if name == "calculate_lower_cost":
        float(arguments["option_a_total"])
        float(arguments["option_b_total"])
        return "calculator", "comparison-lower-cost", "comparison-totals"
    raise ValueError(f"unsupported hosted tool: {name}")


def _output_text(body: dict[str, object]) -> str | None:
    for item in body.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                return str(content.get("text", ""))
    return None


def _validate_comparison_answer(answer: str | None, task: ComparisonTask) -> str:
    """Emit a minimal task-level outcome without retaining model response text."""
    if answer is None:
        return "unavailable"
    return "valid" if answer.strip() == task.expected_answer else "invalid"


def run_probe(
    output: Path,
    model: str | None = None,
    scenario: str = "baseline",
    reasoning_effort: str | None = None,
) -> dict[str, object]:
    """Make one hosted request and record the reusable telemetry boundary."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required; use the configuration check first")
    model_name = model or os.environ.get("AOL_HOSTED_MODEL", "gpt-5")
    endpoint = os.environ.get(
        "AOL_HOSTED_ENDPOINT", "https://api.openai.com/v1/responses"
    )
    run_id = str(uuid.uuid4())
    payload_body: dict[str, object] = {
        "model": model_name,
        "input": _prompt(scenario),
        "store": False,
    }
    if reasoning_effort:
        payload_body["reasoning"] = {"effort": reasoning_effort}
    payload = json.dumps(payload_body).encode()
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
                except (urllib.error.HTTPError, HostedAPIError) as error:
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
        "scenario": scenario,
        "reasoning_effort": reasoning_effort,
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


def observe_cost_envelope(
    report: dict[str, object], baseline_summary: dict[str, object], multiplier: float = 1.25
) -> dict[str, object]:
    """Compare one hosted call with a narrow same-lane baseline."""
    if multiplier <= 1:
        raise ValueError("multiplier must be greater than 1")
    baseline = baseline_summary["summary"]
    output_limit = float(baseline["output_tokens"]["max"]) * multiplier
    duration_limit = float(baseline["duration_ms"]["max"]) * multiplier
    exceeded_metrics = []
    if float(report["output_tokens"]) > output_limit:
        exceeded_metrics.append("output_tokens")
    if float(report["duration_ms"]) > duration_limit:
        exceeded_metrics.append("duration_ms")
    return {
        "type": "hosted_cost_envelope",
        "baseline_run_count": baseline["run_count"],
        "multiplier": multiplier,
        "output_token_limit": round(output_limit, 3),
        "duration_ms_limit": round(duration_limit, 3),
        "observed_output_tokens": report["output_tokens"],
        "observed_duration_ms": report["duration_ms"],
        "exceeded": bool(exceeded_metrics),
        "exceeded_metrics": exceeded_metrics,
    }


def run_cost_probe(
    output_root: Path, baseline_path: Path, model: str | None = None
) -> dict[str, object]:
    """Run one higher-effort call and compare its cost with a baseline summary."""
    result = run_probe(
        output_root / "raw-trace.jsonl",
        model=model,
        scenario="cost-stress",
        reasoning_effort="high",
    )
    report = analyze(output_root / "raw-trace.jsonl")[0]
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    observation = observe_cost_envelope(report, baseline)
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (output_root / "cost-observation.json").write_text(
        json.dumps(observation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {"result": result, "report": report, "observation": observation}


def run_tool_probe(
    output_root: Path,
    model: str | None = None,
    max_turns: int = 6,
    fault_mode: str = "none",
) -> dict[str, object]:
    """Run one bounded hosted tool loop against read-only local fixtures.

    This is intentionally a single task, with at most ``max_turns`` paid model
    requests. It records no API key, prompt text, or model response text.
    """
    if max_turns < 1:
        raise ValueError("max_turns must be at least 1")
    if fault_mode not in {
        "none",
        "first_calculator_failure",
        "all_option_lookups_unavailable",
    }:
        raise ValueError(f"unsupported hosted fault mode: {fault_mode}")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required; use the configuration check first")
    model_name = model or os.environ.get("AOL_HOSTED_MODEL", "gpt-5")
    endpoint = os.environ.get("AOL_HOSTED_ENDPOINT", "https://api.openai.com/v1/responses")
    task = ComparisonTask()
    run_id = str(uuid.uuid4())
    trace_path = output_root / "raw-trace.jsonl"
    attempt_counts: dict[str, int] = {}
    calculator_failed_once = False
    conversation_items: list[object] = [
        {
            "role": "user",
            "content": (
                "Determine which option has the lower delivered cost. Call lookup_option "
                "for option-a-v1 and option-b-v1, then call calculate_lower_cost with "
                "the resulting totals. After the tools return, answer only the option ID."
            ),
        }
    ]
    payload_body: dict[str, object] = {
        "model": model_name,
        "store": False,
        "tools": _tool_schemas(),
        "input": conversation_items,
    }
    session = TelemetrySession(
        trace_path, otlp_endpoint=os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
    )
    final_response_id: str | None = None
    final_answer: str | None = None
    answer_validation = "unavailable"
    terminated_by_turn_cap = False
    try:
        with session.tracer.start_as_current_span(
            "invoke_agent hosted-tool-agent",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "invoke_agent",
                "gen_ai.agent.name": "hosted-tool-agent",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.task_id": task.task_id,
                "agent_observability_lab.runtime_lane": "hosted",
                "agent_observability_lab.max_model_turns": max_turns,
            },
        ) as root:
            tls_context = _tls_context()
            for turn in range(1, max_turns + 1):
                started = time.perf_counter()
                with session.tracer.start_as_current_span(
                    "chat hosted-model",
                    kind=SpanKind.CLIENT,
                    attributes={
                        "gen_ai.operation.name": "chat",
                        "gen_ai.request.model": model_name,
                        "gen_ai.provider.name": "openai",
                        "gen_ai.agent.name": "hosted-tool-agent",
                        "agent_observability_lab.run_id": run_id,
                        "agent_observability_lab.turn_number": turn,
                    },
                ) as model_span:
                    try:
                        body = _post_response(endpoint, api_key, payload_body, tls_context)
                    except (urllib.error.HTTPError, HostedAPIError) as error:
                        root.set_attribute("agent_observability_lab.task_outcome", "failed")
                        model_span.record_exception(error)
                        model_span.set_status(Status(StatusCode.ERROR, str(error)))
                        raise
                    _record_usage(model_span, body, started)
                    final_response_id = str(body["id"]) if body.get("id") else None
                    calls = [
                        item
                        for item in body.get("output", [])
                        if item.get("type") == "function_call"
                    ]
                    if not calls:
                        final_answer = _output_text(body)
                        answer_validation = _validate_comparison_answer(final_answer, task)
                        root.set_attribute(
                            "agent_observability_lab.answer_validation", answer_validation
                        )
                        root.set_attribute("agent_observability_lab.task_outcome", "success")
                        break

                    outputs: list[dict[str, str]] = []
                    for call in calls:
                        name = str(call.get("name", ""))
                        call_id = str(call.get("call_id", ""))
                        if not call_id:
                            raise RuntimeError("hosted function call did not include call_id")
                        try:
                            arguments = json.loads(str(call.get("arguments", "{}")))
                            if not isinstance(arguments, dict):
                                raise ValueError("hosted function arguments must be an object")
                            tool_name, logical_id, data_source = _tool_metadata(
                                task, name, arguments
                            )
                        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
                            with session.tracer.start_as_current_span(
                                "execute_tool rejected_tool_call",
                                kind=SpanKind.INTERNAL,
                                attributes={
                                    "gen_ai.operation.name": "execute_tool",
                                    "gen_ai.tool.name": name or "unknown",
                                    "agent_observability_lab.run_id": run_id,
                                },
                            ) as tool_span:
                                tool_span.record_exception(error)
                                tool_span.set_status(Status(StatusCode.ERROR, str(error)))
                                tool_span.set_attribute("error.type", "invalid_tool_call")
                            result = {"error": str(error)}
                        else:
                            attempt_counts[logical_id] = attempt_counts.get(logical_id, 0) + 1
                            with session.tracer.start_as_current_span(
                                f"execute_tool {tool_name}",
                                kind=SpanKind.INTERNAL,
                                attributes={
                                    "gen_ai.operation.name": "execute_tool",
                                    "gen_ai.tool.name": tool_name,
                                    "gen_ai.data_source.id": data_source,
                                    "agent_observability_lab.run_id": run_id,
                                    "agent_observability_lab.logical_operation_id": logical_id,
                                    "agent_observability_lab.attempt_number": attempt_counts[logical_id],
                                    "agent_observability_lab.argument_fingerprint": _fingerprint(arguments),
                                },
                            ) as tool_span:
                                try:
                                    if (
                                        fault_mode == "first_calculator_failure"
                                        and name == "calculate_lower_cost"
                                        and not calculator_failed_once
                                    ):
                                        calculator_failed_once = True
                                        raise RuntimeError("calculator unavailable")
                                    if (
                                        fault_mode == "all_option_lookups_unavailable"
                                        and name == "lookup_option"
                                    ):
                                        raise RuntimeError("option lookup unavailable")
                                    _, _, result, _ = _execute_tool_call(task, name, arguments)
                                except (RuntimeError, ValueError, KeyError, TypeError) as error:
                                    tool_span.record_exception(error)
                                    tool_span.set_status(Status(StatusCode.ERROR, str(error)))
                                    tool_span.set_attribute("error.type", "tool_unavailable")
                                    result = {
                                        "error": {
                                            "type": "tool_unavailable",
                                            "message": str(error),
                                        }
                                    }
                        outputs.append(
                            {
                                "type": "function_call_output",
                                "call_id": call_id,
                                "output": json.dumps(result, sort_keys=True),
                            }
                        )
                if final_answer is not None:
                    break
                if not final_response_id:
                    raise RuntimeError("hosted response did not include an ID")
                # With store=False, carry all prior response items forward explicitly.
                # This preserves function-call and reasoning context without relying on
                # server-side response state.
                conversation_items.extend(body.get("output", []))
                conversation_items.extend(outputs)
                payload_body = {
                    "model": model_name,
                    "store": False,
                    "tools": _tool_schemas(),
                    "input": conversation_items,
                }
            else:
                root.set_attribute("agent_observability_lab.task_outcome", "failed")
                root.set_attribute("agent_observability_lab.answer_validation", "unavailable")
                root.set_status(
                    Status(StatusCode.ERROR, f"hosted tool probe exceeded {max_turns} model turns")
                )
                terminated_by_turn_cap = True
    finally:
        session.shutdown()

    report = analyze(trace_path)[0]
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "analysis.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "run_id": run_id,
        "model": model_name,
        "runtime_lane": "hosted",
        "task_id": task.task_id,
        "fault_mode": fault_mode,
        "max_turns": max_turns,
        "answer": final_answer,
        "answer_validation": answer_validation,
        "terminated_by_turn_cap": terminated_by_turn_cap,
        "response_id": final_response_id,
        "trace_path": str(trace_path),
        "analysis_path": str(output_root / "analysis.json"),
        "report": report,
    }
