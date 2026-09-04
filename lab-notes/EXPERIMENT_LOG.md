# Experiment Log

Add one entry for each attempted experiment, including invalid or failed collections.

## Entry template

### YYYY-MM-DD — `<experiment-id>`

- **Question:**
- **Protocol/configuration:**
- **What changed:**
- **Expected result:**
- **Observed result:**
- **Unexpected behavior:**
- **Artifacts and checksums:**
- **Conclusion:**
- **Next action:**

### 2026-09-03 — `local-v0-hosted-tool-path-and-failure`

- **Question:** Can shared OpenTelemetry boundaries reconstruct a real hosted model/tool path and distinguish a failed dependency from a failed task?
- **Protocol/configuration:** One hosted comparison task using read-only local lookup and calculator tools; one successful baseline; two runs with the first calculator call forced to fail; `store: false`; local JSONL as canonical evidence; no prompt, response text, fault label, or API key in telemetry.
- **What changed:** The failure runs added a generic tool error. The second failure run added a root-level `answer_validation` class derived from the sealed task answer.
- **Expected result:** The baseline should match its path oracle. A failure should create an error span; a recovery path, if chosen by the model, would add a second calculator attempt.
- **Observed result:** The baseline matched exactly. Both failure runs recorded one calculator error and no retry. The validated failure run ended with `answer_validation = valid`.
- **Unexpected behavior:** The hosted model did not retry the calculator, yet still completed the controlled task correctly from lookup evidence.
- **Artifacts and checksums:** Sanitized traces, analyses, oracles, scores, and feedback decision are committed under `data/published/local-v0-hosted-tool-probe-attempt-02`, `...attempt-03-failure`, and `...attempt-04-validated-failure`.
- **Conclusion:** Telemetry reconstructed the failure and missing recovery. A minimal independent outcome class was required to avoid treating the tool failure as an automatic task failure.
- **Next action:** Either publish the first-study assessment or run one optional hosted invalid/unavailable-outcome extension.
