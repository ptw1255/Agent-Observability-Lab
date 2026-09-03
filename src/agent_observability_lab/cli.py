"""Command-line entry point for the first local vertical slice."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from .analyzer import analyze
from .runtime import Condition, DeterministicAgent
from .tasks import DocumentTask, InvoiceTask
from .telemetry import TelemetrySession


def main() -> None:
    parser = argparse.ArgumentParser(prog="aol")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run one deterministic task")
    run_parser.add_argument("--output", type=Path, required=True)
    run_parser.add_argument(
        "--task",
        choices=["invoice-total-v1", "document-answer-v1"],
        default="invoice-total-v1",
    )
    run_parser.add_argument(
        "--condition",
        choices=[condition.value for condition in Condition],
        default=Condition.BASELINE.value,
    )

    analyze_parser = subparsers.add_parser("analyze", help="analyze telemetry only")
    analyze_parser.add_argument("--input", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "run":
        session = TelemetrySession(args.output)
        try:
            run_id = str(uuid.uuid4())
            task = InvoiceTask() if args.task == "invoice-total-v1" else DocumentTask()
            result = DeterministicAgent(session.tracer).run(
                task, Condition(args.condition), run_id
            )
            print(json.dumps(result.__dict__, default=str, sort_keys=True))
        finally:
            session.shutdown()
    else:
        print(json.dumps(analyze(args.input), indent=2, sort_keys=True))
