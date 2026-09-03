"""Versioned deterministic task definitions and local fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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
class DocumentTask:
    task_id: str = "document-answer-v1"
    document_id: str = "returns-policy-v1"
    query: str = "What is the return window for unopened items?"
    expected_answer: str = "30 days"

    @property
    def document_text(self) -> str:
        fixture = (
            Path(__file__).resolve().parents[2]
            / "fixtures"
            / "documents"
            / f"{self.document_id}.md"
        )
        return fixture.read_text(encoding="utf-8")
