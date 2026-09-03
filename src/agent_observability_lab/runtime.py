"""Deterministic agent runtime used for the first experiment slice."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from enum import StrEnum

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode


class Condition(StrEnum):
    BASELINE = "baseline"
    TRANSIENT_TOOL_FAILURE = "transient_tool_failure"


@dataclass(frozen=True)
class InvoiceTask:
    task_id: str = "invoice-total-v1"
    units: int = 3
    unit_price: float = 19.95
    tax_rate: float = 0.08

    @property
    def expected_total(self) -> float:
        return round(self.units * self.unit_price * (1 + self.tax_rate), 2)


@dataclass(frozen=True)
class RunResult:
    run_id: str
    task_id: str
    condition: Condition
    answer: float


class ToolExecutionError(RuntimeError):
    """A generic tool failure; fault-condition details stay in the oracle."""


def _fingerprint(arguments: dict[str, object]) -> str:
    payload = json.dumps(arguments, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


class DeterministicAgent:
    """A tiny model/tool loop instrumented at reusable boundaries only."""

    def __init__(self, tracer: trace.Tracer) -> None:
        self.tracer = tracer
        self._failed_once: set[str] = set()

    def _model_call(self, phase: str, run_id: str, output_tokens: int = 24) -> None:
        with self.tracer.start_as_current_span(
            "chat scripted-model",
            kind=SpanKind.CLIENT,
            attributes={
                "gen_ai.operation.name": "chat",
                "gen_ai.request.model": "scripted-model-v1",
                "gen_ai.provider.name": "agent-observability-lab",
                "gen_ai.agent.name": "invoice-agent",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.phase": phase,
                "gen_ai.usage.input_tokens": 32,
                "gen_ai.usage.output_tokens": output_tokens,
            },
        ):
            time.sleep(0.001)

    def _calculator(
        self,
        task: InvoiceTask,
        run_id: str,
        attempt: int,
        should_fail: bool,
    ) -> float:
        arguments = {
            "units": task.units,
            "unit_price": task.unit_price,
            "tax_rate": task.tax_rate,
        }
        with self.tracer.start_as_current_span(
            "execute_tool calculator",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "execute_tool",
                "gen_ai.tool.name": "calculator",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.logical_operation_id": "invoice-total",
                "agent_observability_lab.attempt_number": attempt,
                "agent_observability_lab.argument_fingerprint": _fingerprint(arguments),
            },
        ) as span:
            time.sleep(0.001)
            if should_fail:
                error = ToolExecutionError("calculator unavailable")
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
                span.set_attribute("error.type", "tool_unavailable")
                raise error
            return task.expected_total

    def run(self, task: InvoiceTask, condition: Condition, run_id: str) -> RunResult:
        with self.tracer.start_as_current_span(
            "invoke_agent invoice-agent",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "invoke_agent",
                "gen_ai.agent.name": "invoice-agent",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.task_id": task.task_id,
                "agent_observability_lab.runtime_lane": "deterministic",
            },
        ) as root:
            self._model_call("plan", run_id)
            try:
                answer = self._calculator(
                    task,
                    run_id,
                    attempt=1,
                    should_fail=condition == Condition.TRANSIENT_TOOL_FAILURE,
                )
            except ToolExecutionError:
                self._model_call("recover", run_id, output_tokens=18)
                answer = self._calculator(task, run_id, attempt=2, should_fail=False)
            self._model_call("finalize", run_id, output_tokens=16)
            root.set_attribute("agent_observability_lab.task_outcome", "success")
            return RunResult(run_id, task.task_id, condition, answer)
