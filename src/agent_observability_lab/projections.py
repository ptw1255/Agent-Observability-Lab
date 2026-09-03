"""Generate restricted evidence profiles from canonical JSONL spans."""

from __future__ import annotations

import json
from enum import StrEnum
from pathlib import Path


class EvidenceProfile(StrEnum):
    P0 = "p0"
    P1 = "p1"
    P2 = "p2"


STANDARD_ATTRIBUTES = {
    "gen_ai.operation.name",
    "gen_ai.request.model",
    "gen_ai.provider.name",
    "gen_ai.agent.name",
    "gen_ai.tool.name",
    "gen_ai.data_source.id",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "error.type",
}

P2_ATTRIBUTES = {
    "agent_observability_lab.run_id",
    "agent_observability_lab.logical_operation_id",
    "agent_observability_lab.attempt_number",
    "agent_observability_lab.argument_fingerprint",
    "agent_observability_lab.step_number",
    "agent_observability_lab.task_id",
    "agent_observability_lab.runtime_lane",
}


def project_record(record: dict[str, object], profile: EvidenceProfile) -> dict[str, object]:
    """Return one profile-projected span without mutating the raw record."""
    projected = dict(record)
    attributes = record.get("attributes", {})
    if profile == EvidenceProfile.P0:
        projected["attributes"] = {}
    elif profile == EvidenceProfile.P1:
        projected["attributes"] = {
            key: value for key, value in attributes.items() if key in STANDARD_ATTRIBUTES
        }
    else:
        projected["attributes"] = {
            key: value
            for key, value in attributes.items()
            if key in STANDARD_ATTRIBUTES or key in P2_ATTRIBUTES
        }
    return projected


def project_file(input_path: Path, output_path: Path, profile: EvidenceProfile) -> None:
    """Project a raw JSONL trace file into one evidence profile."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_path.open(encoding="utf-8") as source, output_path.open(
        "w", encoding="utf-8"
    ) as destination:
        for line in source:
            if line.strip():
                record = json.loads(line)
                destination.write(
                    json.dumps(project_record(record, profile), sort_keys=True) + "\n"
                )
