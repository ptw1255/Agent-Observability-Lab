"""Command-line entry point for the first local vertical slice."""

from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from .analyzer import analyze
from .feedback import DuplicateSuppressionFeedback, RetryBudgetFeedback
from .hosted import configuration, run_probe
from .projections import EvidenceProfile, project_file
from .oracle import build_oracle
from .matrix import run_matrix
from .runtime import Condition, DeterministicAgent
from .scoring import score_reports
from .tasks import ComparisonTask, DocumentTask, InvoiceTask
from .telemetry import TelemetrySession


def main() -> None:
    parser = argparse.ArgumentParser(prog="aol")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="run one deterministic task")
    run_parser.add_argument("--output", type=Path, required=True)
    run_parser.add_argument(
        "--task",
        choices=["invoice-total-v1", "document-answer-v1", "two-option-comparison-v1"],
        default="invoice-total-v1",
    )
    run_parser.add_argument(
        "--condition",
        choices=[condition.value for condition in Condition],
        default=Condition.BASELINE.value,
    )
    run_parser.add_argument(
        "--feedback",
        choices=["none", "retry_budget", "duplicate_suppression"],
        default="none",
        help="optional evidence-driven runtime policy",
    )

    analyze_parser = subparsers.add_parser("analyze", help="analyze telemetry only")
    analyze_parser.add_argument("--input", type=Path, required=True)
    analyze_parser.add_argument("--output", type=Path)

    project_parser = subparsers.add_parser("project", help="create a restricted evidence profile")
    project_parser.add_argument("--input", type=Path, required=True)
    project_parser.add_argument("--output", type=Path, required=True)
    project_parser.add_argument("--profile", choices=[profile.value for profile in EvidenceProfile], required=True)

    score_parser = subparsers.add_parser("score", help="score analyzer output against an oracle")
    score_parser.add_argument("--analysis", type=Path, required=True)
    score_parser.add_argument("--oracle", type=Path, required=True)
    score_parser.add_argument("--output", type=Path)

    oracle_parser = subparsers.add_parser("oracle", help="build one sealed baseline oracle")
    oracle_parser.add_argument("--input", type=Path, required=True)
    oracle_parser.add_argument("--task", required=True)
    oracle_parser.add_argument("--condition", default="baseline")
    oracle_parser.add_argument("--output", type=Path, required=True)

    matrix_parser = subparsers.add_parser("matrix", help="run the deterministic experiment matrix")
    matrix_parser.add_argument("--output", type=Path, required=True)
    matrix_parser.add_argument("--repetitions", type=int, default=5)

    hosted_parser = subparsers.add_parser("hosted", help="inspect or run the hosted portability probe")
    hosted_parser.add_argument("--output", type=Path, required=False)
    hosted_parser.add_argument("--model")
    hosted_parser.add_argument("--check-only", action="store_true")

    args = parser.parse_args()
    if args.command == "hosted":
        if args.check_only or not args.output:
            print(json.dumps(configuration(), indent=2, sort_keys=True))
        else:
            print(json.dumps(run_probe(args.output, args.model), indent=2, sort_keys=True))
    elif args.command == "run":
        session = TelemetrySession(args.output)
        try:
            run_id = str(uuid.uuid4())
            task = {
                "invoice-total-v1": InvoiceTask,
                "document-answer-v1": DocumentTask,
                "two-option-comparison-v1": ComparisonTask,
            }[args.task]()
            feedback = {
                "none": None,
                "retry_budget": RetryBudgetFeedback(),
                "duplicate_suppression": DuplicateSuppressionFeedback(),
            }[args.feedback]
            result = DeterministicAgent(session.tracer, feedback=feedback).run(
                task, Condition(args.condition), run_id
            )
            print(json.dumps(result.__dict__, default=str, sort_keys=True))
        finally:
            session.shutdown()
    elif args.command == "analyze":
        rendered = json.dumps(analyze(args.input), indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
    elif args.command == "project":
        project_file(args.input, args.output, EvidenceProfile(args.profile))
    elif args.command == "score":
        analysis = json.loads(args.analysis.read_text(encoding="utf-8"))
        oracle = json.loads(args.oracle.read_text(encoding="utf-8"))
        if isinstance(analysis, dict):
            analysis = [analysis]
        if isinstance(oracle, dict):
            oracle = [oracle]
        result = score_reports(analysis, oracle)
        rendered = json.dumps(result, indent=2, sort_keys=True)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)
    elif args.command == "oracle":
        oracle = build_oracle(args.input, args.task, args.condition)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(oracle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(run_matrix(args.output, args.repetitions), indent=2, sort_keys=True))
