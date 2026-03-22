# Research: Parallel Source Scheduling and Bounded Concurrency

## Per-Source Scheduling Strategy

- Decision: Keep one scheduler tick cadence and evaluate due-state per source using explicit source schedule policy metadata.
- Rationale: Preserves operational simplicity while enabling hourly/daily/weekly/monthly source-specific eligibility.
- Alternatives considered:
  - Separate scheduler per source cadence: rejected because operational overhead scales poorly.
  - Keep global hourly execution for all sources: rejected because low-frequency sources are over-processed.

## Bounded Parallel Execution Model

- Decision: Execute due sources with a configurable maximum active-source limit and launch queued due sources as slots free.
- Rationale: Prevents run-time explosion as source count grows while increasing throughput over strict sequential execution.
- Alternatives considered:
  - Fully sequential execution: rejected because run durations can exceed cadence windows.
  - Unbounded parallel execution: rejected due to DB contention, unstable runtime load, and queue spikes.

## Deterministic Launch Ordering

- Decision: Maintain deterministic source ordering among simultaneously due sources before applying parallel slot allocation.
- Rationale: Stable execution ordering improves reproducibility, debugging, and test determinism.
- Alternatives considered:
  - Random ordering: rejected because troubleshooting and reproducibility degrade.
  - Registration insertion-order only: rejected because distributed updates can make insertion order non-deterministic.

## Due-State Persistence Semantics

- Decision: Persist run-time source eligibility snapshots and source terminal outcomes with explicit reason codes.
- Rationale: Operators need to know whether a source was executed, not due, deferred by policy, or failed.
- Alternatives considered:
  - Persist outcomes only: rejected because non-execution reasons are invisible.
  - Logs-only eligibility details: rejected because durable audit and queryability are required.

## On-Demand Subset Execution

- Decision: Support operator-specified source subsets for on-demand runs without mutating baseline cadence metadata.
- Rationale: Enables targeted reruns and incident remediation while preserving schedule policy integrity.
- Alternatives considered:
  - On-demand all-sources only: rejected because it can trigger unnecessary work during incidents.
  - Mutating cadence for emergency reruns: rejected because temporary operations should not change durable policy.

## Overlap and Duplicate Execution Safety

- Decision: Keep source-level execution lock policy to prevent duplicate concurrent execution for the same source across overlapping runs.
- Rationale: Ensures correctness when frequent ticks and on-demand runs coexist.
- Alternatives considered:
  - Run-level lock only: rejected because it blocks unrelated sources unnecessarily.
  - No overlap protection: rejected due to duplicate writes and inconsistent outcomes.

## Capacity and Fairness Considerations

- Decision: Prioritize due hourly and daily sources during backlog conditions while preserving eventual execution for lower-frequency due sources.
- Rationale: Prevents repeated starvation of high-priority freshness while ensuring bounded fairness.
- Alternatives considered:
  - Strict FIFO by due timestamp only: rejected because prolonged backlogs can hurt high-frequency freshness.
  - Priority-only with no fairness guard: rejected because low-frequency due sources could starve indefinitely.

## Clarification Resolution Checklist

- Parallelism objective behavior: Resolved
- Per-source cadence and due-state evaluation model: Resolved
- Overlap handling with bounded concurrency: Resolved
- On-demand subset execution behavior: Resolved
- Operational visibility for deferred and not-due states: Resolved
