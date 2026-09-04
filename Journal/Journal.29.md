# Journal.29 — Hosted lookup-outage extension

## What changed

Added one optional hosted failure mode in which every local option lookup returns a generic unavailable error. The hosted comparison prompt, model, and tool schemas remain unchanged. The model still chooses what to do after receiving tool errors; the harness does not force a final answer, a retry, or an intervention.

This differs from the calculator failure in one important way. The two lookups are the only source of option prices for the controlled task. If both fail, the model has no tool-supplied comparison evidence. The run gives the hosted model a controlled opportunity to produce an invalid or unavailable outcome, retry a dependency, or reveal another failure-handling behavior.

The raw trace will not contain the fault-mode label. Each failure is represented as an ordinary `tool_unavailable` error at the `local_lookup` boundary. The root span will still contain only the minimal `valid`, `invalid`, or `unavailable` outcome class. A local simulated-provider test produces two failed lookups and an invalid answer class; the outcome-aware policy correctly recommends `intervene_on_next_attempt`.

## Key concepts

This is a dependency-starved scenario, not a scripted incorrect-answer scenario. The experiment controls availability of the data boundary but leaves the model's response behavior open. That distinction lets a real hosted trace tell us something about the runtime: whether it retries, stops, guesses, or reports that it cannot complete the task.

The expected policy action remains conditional on observed evidence. A tool outage alone does not determine the action. If a surprising valid outcome occurs, the policy should still observe only. If the outcome is invalid or unavailable, then the combined evidence supports a next-attempt intervention.

## Why this checkpoint matters

The project has directly observed the restraint branch of the decision table: calculator failure plus valid answer led to `observe_only`. The intervention branch was previously only synthetic. This extension is the smallest real hosted scenario that can exercise that branch without changing models, adding a new backend, or collecting model response text.

It adds evidence where it matters most for the feedback claim: can the same telemetry contract support a different, proportionate decision when the agent lacks a needed dependency?

## Result and significance

The adapter is ready and tested locally. No paid request has been made. A live run is bounded to six model turns, matching the project’s cost-conscious hosted scope. The actual outcome remains open and will be recorded rather than assumed.

## Next step

Run the hosted lookup-outage task once, inspect the trace and validation class, then generate the outcome-aware feedback decision. This one run will either add real evidence for `intervene_on_next_attempt` or demonstrate another case where the model completes despite a dependency outage.

## Work snapshot

```text
same comparison task
  -> lookup option A: unavailable
  -> lookup option B: unavailable
  -> hosted model decides next action
  -> root records valid | invalid | unavailable
  -> telemetry policy recommends observe only | intervene on next attempt
```

The notable safeguard is that neither the expected policy action nor the outcome class is injected into telemetry. The trace must earn its decision through the observed errors, path, and independent validation result.

## Significance

The lookup outage removes both sources of task data while leaving model behavior unconstrained. The local simulation confirms that two failed lookups can flow through the same telemetry and policy contracts, but it does not predict whether the hosted model will retry, guess, or stop. The live run is designed to supply the missing intervention-branch evidence at a six-turn cost cap.

## Market thesis

Agents that depend on retrieval, customer records, or external APIs need observability for dependency starvation, not only individual tool errors. Reliability teams care about whether the agent backs off, switches sources, or repeats an unavailable request. A controlled outage study can validate that behavior before the same pattern creates customer-facing latency and spend.
