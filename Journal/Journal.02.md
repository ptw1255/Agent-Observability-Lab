# Journal.02 — Local document-answer task

## What changed

We added `DocumentTask`, which asks:

```text
What is the return window for unopened items?
```

The expected answer is `30 days`. The retrieval operation reads the versioned `returns-policy-v1` fixture from the local repository.

The healthy trace is:

```text
invoke_agent → chat plan → execute_tool local_retrieval → chat answer
```

We applied all five conditions to the retrieval operation. A transient retrieval failure produces a generic tool error, a recovery model call, and a second retrieval attempt. The retry condition fails retrieval three times. The redundant condition repeats the same query. The excessive condition adds nested reflection before retrieval.

Task selection now exists in the runtime and CLI. The analyzer recognizes any span whose name begins with `execute_tool`, so it can inspect calculator, retrieval, and lookup operations through one rule.

Implementation commit: `56ff9ac`.

## Key concepts

Retrieval is an agent boundary with its own identity and data source. The trace records `local_retrieval` and `returns-policy-v1`; the document text remains outside telemetry.

The same span contract can cover different tool types. That matters because a detector tied to `calculator` would measure one demo. A detector tied to the operation boundary can transfer across workloads.

The argument fingerprint is a short hash of normalized inputs. It lets the analyzer recognize an equivalent query without exporting the query text.

## Why this checkpoint matters

The invoice task tests one calculator call. A retrieval task adds a different operation type and a fixture-backed evidence source. That gives us a second topology while keeping the runtime local and deterministic.

The task also tests whether privacy and blindness rules survive a different tool. The analyzer must identify a failed retrieval from span evidence without seeing the condition name or document answer.

## Result and significance

Twelve tests passed across the two tasks.

The document task produced the expected healthy sequence and retrieval data-source ID. All five conditions executed through the same runtime. The analyzer found the controlled conditions, and condition-blindness checks passed.

This validates the boundary contract across calculator and retrieval tools. It does not provide profile scores or a conclusion about OpenTelemetry coverage.

## Next step

Add a two-option comparison task with two required lookups and a calculator. Use it to test whether the analyzer can distinguish a legitimate multi-tool path from redundant work.

## Significance

The same analyzer rule now covers calculator and retrieval spans, so the diagnostic contract is attached to the tool boundary rather than one demo function. The retrieval fixture also proves that the trace can identify a data source while leaving document content outside telemetry. That separation is required before the project can claim portability across agent workloads with different tools and data sensitivity.

## Market thesis

AI platform teams will value observability that works across tool types without copying business content into a vendor system. Retrieval-heavy products in customer support, enterprise search, and knowledge management face both traceability and data-governance requirements. A boundary contract that identifies the failing source while withholding document text gives those teams a lower-risk adoption path.
