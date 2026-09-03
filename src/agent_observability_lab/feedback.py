"""Small, opt-in policies that consume execution evidence during a run."""

from __future__ import annotations

from collections import defaultdict


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
