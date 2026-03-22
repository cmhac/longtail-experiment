# Contract: Bounded Parallel Source Execution

## Purpose

Define deterministic launch and completion semantics for running due sources with bounded concurrency.

## Inputs

- runId: Current orchestration run identifier
- dueSources: Deterministically ordered list of due source keys
- maxActiveSources: Positive integer concurrency ceiling
- overlapGuard: Source-scoped duplicate execution protection policy

## Execution Rules

1. Active source executions MUST never exceed maxActiveSources.
2. Sources MUST be launched in deterministic order from the dueSources list.
3. When a source completes, the next queued due source MUST be launched if capacity is available.
4. Failure of one source MUST NOT automatically cancel other due sources.
5. A source with active execution in another run MUST be marked deferred or blocked per overlap policy and not launched concurrently.

## Output Semantics

For each source in dueSources, emit terminal classification:

- success
- partial_success
- failure
- deferred

For run summary, emit aggregate counts:

- dueSourceCount
- executedSourceCount
- deferredSourceCount
- failedSourceCount

## Determinism Requirements

- Given identical dueSources, policy settings, and overlap state, source launch order MUST be identical.
- Deferred/blocked outcomes MUST include explicit reasonCode values.

## Error Handling

- Invalid maxActiveSources (<= 0) MUST fail run startup with explicit validation error.
- Runtime launch failures for one source MUST still produce terminal outcomes for remaining due sources.
