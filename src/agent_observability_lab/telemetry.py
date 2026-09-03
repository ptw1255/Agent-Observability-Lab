"""Small local OpenTelemetry setup with a canonical JSONL exporter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    SpanExporter,
    SpanExportResult,
)


def _value(value: object) -> object:
    """Convert OpenTelemetry values into JSON-safe values."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_value(item) for item in value]
    return str(value)


class JsonlSpanExporter(SpanExporter):
    """Write one normalized, append-only JSON object per ended span."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8")

    def export(self, spans: Sequence[object]) -> SpanExportResult:
        for span in spans:
            context = span.get_span_context()
            parent = span.parent
            record = {
                "trace_id": format(context.trace_id, "032x"),
                "span_id": format(context.span_id, "016x"),
                "parent_span_id": format(parent.span_id, "016x") if parent else None,
                "name": span.name,
                "kind": span.kind.name,
                "start_time_unix_nano": span.start_time,
                "end_time_unix_nano": span.end_time,
                "duration_ms": round((span.end_time - span.start_time) / 1_000_000, 3),
                "status": span.status.status_code.name,
                "attributes": {key: _value(value) for key, value in span.attributes.items()},
                "events": [
                    {
                        "name": event.name,
                        "attributes": {
                            key: _value(value) for key, value in event.attributes.items()
                        },
                    }
                    for event in span.events
                ],
            }
            self._file.write(json.dumps(record, sort_keys=True) + "\n")
        self._file.flush()
        return SpanExportResult.SUCCESS

    def shutdown(self) -> None:
        self._file.close()

    def force_flush(self, timeout_millis: int = 30_000) -> bool:
        self._file.flush()
        return True


class TelemetrySession:
    """Own a tracer provider so tests and runs do not share global state."""

    def __init__(self, output_path: Path, otlp_endpoint: str | None = None) -> None:
        self.exporter = JsonlSpanExporter(output_path)
        self.provider = TracerProvider(
            resource=Resource.create({"service.name": "agent-observability-lab"})
        )
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        if otlp_endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
            except ImportError as error:
                raise RuntimeError(
                    "OTLP export requires the integration extra: pip install -e '.[integration]'"
                ) from error
            self.provider.add_span_processor(
                SimpleSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
            )
        self.tracer = self.provider.get_tracer("agent-observability-lab", "0.1.0")

    def shutdown(self) -> None:
        self.provider.shutdown()
