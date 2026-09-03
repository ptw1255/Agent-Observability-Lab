"""Deterministic agent runtime used for the first experiment slice."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from enum import StrEnum

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode

from .tasks import ComparisonTask, DocumentTask, InvoiceTask


class Condition(StrEnum):
    BASELINE = "baseline"
    TRANSIENT_TOOL_FAILURE = "transient_tool_failure"
    RETRY_LOOP = "retry_loop"
    REDUNDANT_TOOL_USE = "redundant_tool_use"
    EXCESSIVE_PATH = "excessive_path"


@dataclass(frozen=True)
class RunResult:
    run_id: str
    task_id: str
    condition: Condition
    answer: object | None


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
                "gen_ai.agent.name": "deterministic-agent",
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
        logical_operation_id: str = "invoice-total",
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
                "agent_observability_lab.logical_operation_id": logical_operation_id,
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

    def _retrieval(
        self,
        task: DocumentTask,
        run_id: str,
        attempt: int,
        should_fail: bool,
        logical_operation_id: str = "document-retrieval",
    ) -> str:
        arguments = {"document_id": task.document_id, "query": task.query}
        with self.tracer.start_as_current_span(
            "execute_tool local_retrieval",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "retrieve",
                "gen_ai.tool.name": "local_retrieval",
                "gen_ai.data_source.id": task.document_id,
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.logical_operation_id": logical_operation_id,
                "agent_observability_lab.attempt_number": attempt,
                "agent_observability_lab.argument_fingerprint": _fingerprint(arguments),
            },
        ) as span:
            time.sleep(0.001)
            if should_fail:
                error = ToolExecutionError("document unavailable")
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
                span.set_attribute("error.type", "tool_unavailable")
                raise error
            return task.document_text

    def _excessive_reflection(self, run_id: str, depth: int, max_depth: int) -> None:
        """Create an intentionally deep but deterministic planning path."""
        with self.tracer.start_as_current_span(
            "plan reflection",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "plan",
                "gen_ai.agent.name": "deterministic-agent",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.step_number": depth,
            },
        ):
            self._model_call(f"reflection-{depth}", run_id, output_tokens=64)
            if depth < max_depth:
                self._excessive_reflection(run_id, depth + 1, max_depth)

    def _run_invoice(self, task: InvoiceTask, condition: Condition, run_id: str):
        self._model_call("plan", run_id)
        if condition == Condition.EXCESSIVE_PATH:
            self._excessive_reflection(run_id, depth=1, max_depth=5)

        if condition == Condition.RETRY_LOOP:
            for attempt in range(1, 4):
                try:
                    self._calculator(task, run_id, attempt=attempt, should_fail=True)
                except ToolExecutionError:
                    self._model_call("retry-decision", run_id, output_tokens=20)
            raise ToolExecutionError("retry budget exhausted")

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

        if condition == Condition.REDUNDANT_TOOL_USE:
            self._calculator(
                task,
                run_id,
                attempt=1,
                should_fail=False,
                logical_operation_id="invoice-total-duplicate",
            )
        self._model_call("finalize", run_id, output_tokens=16)
        return answer

    def _run_document(self, task: DocumentTask, condition: Condition, run_id: str):
        self._model_call("plan", run_id)
        if condition == Condition.EXCESSIVE_PATH:
            self._excessive_reflection(run_id, depth=1, max_depth=5)

        if condition == Condition.RETRY_LOOP:
            for attempt in range(1, 4):
                try:
                    self._retrieval(task, run_id, attempt=attempt, should_fail=True)
                except ToolExecutionError:
                    self._model_call("retry-decision", run_id, output_tokens=20)
            raise ToolExecutionError("retry budget exhausted")

        try:
            self._retrieval(
                task,
                run_id,
                attempt=1,
                should_fail=condition == Condition.TRANSIENT_TOOL_FAILURE,
            )
        except ToolExecutionError:
            self._model_call("recover", run_id, output_tokens=18)
            self._retrieval(task, run_id, attempt=2, should_fail=False)

        if condition == Condition.REDUNDANT_TOOL_USE:
            self._retrieval(
                task,
                run_id,
                attempt=1,
                should_fail=False,
                logical_operation_id="document-retrieval-duplicate",
            )
        self._model_call("answer", run_id, output_tokens=20)
        return task.expected_answer

    def _lookup(
        self,
        task: ComparisonTask,
        option_id: str,
        run_id: str,
        attempt: int,
        should_fail: bool,
        logical_operation_id: str,
    ) -> dict[str, float | str]:
        arguments = {"option_id": option_id, "query": task.query}
        with self.tracer.start_as_current_span(
            "execute_tool local_lookup",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "retrieve",
                "gen_ai.tool.name": "local_lookup",
                "gen_ai.data_source.id": option_id,
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.logical_operation_id": logical_operation_id,
                "agent_observability_lab.attempt_number": attempt,
                "agent_observability_lab.argument_fingerprint": _fingerprint(arguments),
            },
        ) as span:
            time.sleep(0.001)
            if should_fail:
                error = ToolExecutionError("option unavailable")
                span.record_exception(error)
                span.set_status(Status(StatusCode.ERROR, str(error)))
                span.set_attribute("error.type", "tool_unavailable")
                raise error
            return task.option(option_id)

    def _comparison_calculator(
        self,
        option_a: dict[str, float | str],
        option_b: dict[str, float | str],
        run_id: str,
    ) -> str:
        arguments = {
            "option_a_total": float(option_a["base_price"]) + float(option_a["shipping"]),
            "option_b_total": float(option_b["base_price"]) + float(option_b["shipping"]),
        }
        with self.tracer.start_as_current_span(
            "execute_tool calculator",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "execute_tool",
                "gen_ai.tool.name": "calculator",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.logical_operation_id": "comparison-total",
                "agent_observability_lab.attempt_number": 1,
                "agent_observability_lab.argument_fingerprint": _fingerprint(arguments),
            },
        ):
            time.sleep(0.001)
            return (
                str(option_a["option_id"])
                if arguments["option_a_total"] < arguments["option_b_total"]
                else str(option_b["option_id"])
            )

    def _run_comparison(
        self, task: ComparisonTask, condition: Condition, run_id: str
    ):
        self._model_call("plan", run_id)
        if condition == Condition.EXCESSIVE_PATH:
            self._excessive_reflection(run_id, depth=1, max_depth=5)

        if condition == Condition.RETRY_LOOP:
            for attempt in range(1, 4):
                try:
                    self._lookup(
                        task,
                        task.option_a_id,
                        run_id,
                        attempt,
                        should_fail=True,
                        logical_operation_id="comparison-option-a",
                    )
                except ToolExecutionError:
                    self._model_call("retry-decision", run_id, output_tokens=20)
            raise ToolExecutionError("retry budget exhausted")

        try:
            option_a = self._lookup(
                task,
                task.option_a_id,
                run_id,
                attempt=1,
                should_fail=condition == Condition.TRANSIENT_TOOL_FAILURE,
                logical_operation_id="comparison-option-a",
            )
        except ToolExecutionError:
            self._model_call("recover", run_id, output_tokens=18)
            option_a = self._lookup(
                task,
                task.option_a_id,
                run_id,
                attempt=2,
                should_fail=False,
                logical_operation_id="comparison-option-a",
            )
        option_b = self._lookup(
            task,
            task.option_b_id,
            run_id,
            attempt=1,
            should_fail=False,
            logical_operation_id="comparison-option-b",
        )
        if condition == Condition.REDUNDANT_TOOL_USE:
            self._lookup(
                task,
                task.option_b_id,
                run_id,
                attempt=1,
                should_fail=False,
                logical_operation_id="comparison-option-b-duplicate",
            )
        answer = self._comparison_calculator(option_a, option_b, run_id)
        self._model_call("finalize", run_id, output_tokens=16)
        return answer

    def run(
        self,
        task: InvoiceTask | DocumentTask | ComparisonTask,
        condition: Condition,
        run_id: str,
    ) -> RunResult:
        with self.tracer.start_as_current_span(
            "invoke_agent deterministic-agent",
            kind=SpanKind.INTERNAL,
            attributes={
                "gen_ai.operation.name": "invoke_agent",
                "gen_ai.agent.name": "deterministic-agent",
                "agent_observability_lab.run_id": run_id,
                "agent_observability_lab.task_id": task.task_id,
                "agent_observability_lab.runtime_lane": "deterministic",
            },
        ) as root:
            try:
                if isinstance(task, DocumentTask):
                    answer = self._run_document(task, condition, run_id)
                elif isinstance(task, ComparisonTask):
                    answer = self._run_comparison(task, condition, run_id)
                else:
                    answer = self._run_invoice(task, condition, run_id)
            except ToolExecutionError as error:
                root.set_status(Status(StatusCode.ERROR, str(error)))
                root.set_attribute("agent_observability_lab.task_outcome", "failed")
                root.set_attribute("error.type", "retry_budget_exhausted")
                answer = None
            else:
                root.set_attribute("agent_observability_lab.task_outcome", "success")
            return RunResult(run_id, task.task_id, condition, answer)
