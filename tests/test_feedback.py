from agent_observability_lab.feedback import (
    outcome_aware_decision_table,
    outcome_aware_tool_failure_decision,
)


def test_valid_outcome_after_tool_failure_is_observe_only():
    decision = outcome_aware_tool_failure_decision(
        {"findings": [{"type": "tool_failure"}], "answer_validation": "valid"}
    )

    assert decision["action"] == "observe_only"


def test_unvalidated_outcome_after_tool_failure_is_intervened_on_next_attempt():
    decision = outcome_aware_tool_failure_decision(
        {"findings": [{"type": "tool_failure"}], "answer_validation": "unavailable"}
    )

    assert decision["action"] == "intervene_on_next_attempt"


def test_missing_validation_does_not_trigger_an_unsupported_intervention():
    decision = outcome_aware_tool_failure_decision({"findings": [{"type": "tool_failure"}]})

    assert decision["action"] == "insufficient_evidence"


def test_decision_table_is_explicitly_synthetic_and_complete():
    table = outcome_aware_decision_table()

    assert table["synthetic"] is True
    assert [case["decision"]["action"] for case in table["cases"]] == [
        "no_action",
        "observe_only",
        "intervene_on_next_attempt",
        "insufficient_evidence",
    ]
