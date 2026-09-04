"""Small, opt-in policies that consume execution evidence during a run."""

from __future__ import annotations

from collections import defaultdict


def outcome_aware_tool_failure_decision(report: dict[str, object]) -> dict[str, object]:
    """Recommend a post-run action from telemetry and a minimal outcome class.

    This policy intentionally consumes only analyzer output. It does not read
    prompts, model text, injected-condition labels, or business-logic internals.
    Because validation is available only after the run, this recommends action
    for a subsequent attempt or human workflow; it does not rewrite history.
    """
    finding_types = {str(finding["type"]) for finding in report.get("findings", [])}
    validation = report.get("answer_validation")
    tool_failure = "tool_failure" in finding_types
    evidence = {
        "tool_failure": tool_failure,
        "answer_validation": validation,
    }
    if not tool_failure:
        return {
            "type": "outcome_aware_tool_failure_decision",
            "action": "no_action",
            "evidence": evidence,
            "rationale": "no failed tool boundary was observed",
        }
    if validation == "valid":
        return {
            "type": "outcome_aware_tool_failure_decision",
            "action": "observe_only",
            "evidence": evidence,
            "rationale": "the task outcome validated despite the tool failure",
        }
    if validation in {"invalid", "unavailable"}:
        return {
            "type": "outcome_aware_tool_failure_decision",
            "action": "intervene_on_next_attempt",
            "evidence": evidence,
            "rationale": "a tool failure coincided with an unvalidated task outcome",
        }
    return {
        "type": "outcome_aware_tool_failure_decision",
        "action": "insufficient_evidence",
        "evidence": evidence,
        "rationale": "the trace lacks a recognized task-outcome validation class",
    }


class RetryBudgetFeedback:
    """Stop a retry loop after repeated failures of one logical operation."""

    def __init__(self, failure_limit: int = 2) -> None:
        if failure_limit < 1:
            raise ValueError("failure_limit must be at least 1")
        self.failure_limit = failure_limit
        self._failures: dict[str, int] = defaultdict(int)

    def observe_tool_failure(self, logical_operation_id: str) -> bool:
        self._failures[logical_operation_id] += 1
        return self._failures[logical_operation_id] >= self.failure_limit


class DuplicateSuppressionFeedback:
    """Reuse a successful read-only tool result for an identical request."""

    def __init__(self) -> None:
        self._results: dict[str, object] = {}

    def cached_result(self, argument_fingerprint: str) -> object | None:
        return self._results.get(argument_fingerprint)

    def record_success(self, argument_fingerprint: str, result: object) -> None:
        self._results[argument_fingerprint] = result
