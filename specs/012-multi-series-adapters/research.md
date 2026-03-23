# Research: Multi-Series Source Adapter Model

## Decision 1: Use grouped adapter as the default ownership mode

- Decision: A provider can own multiple series under one grouped adapter by default, and grouped series can share one cadence in initial rollout.
- Rationale: This minimizes adapter duplication and onboarding overhead while satisfying the immediate need to ingest multiple topics from one provider.
- Alternatives considered:
  - Split every series into dedicated adapters from day one.
    - Rejected because it increases operational overhead and module sprawl before cadence divergence is needed.
  - Keep strict one-series-per-source indefinitely.
    - Rejected because it blocks efficient provider expansion.

## Decision 2: Preserve optional split-adapter strategy for cadence divergence

- Decision: Series can move to dedicated split adapters when cadence or operational requirements diverge.
- Rationale: This preserves long-term flexibility and avoids lock-in to one ownership strategy.
- Alternatives considered:
  - Forbid split adapters and enforce grouped-only ownership.
    - Rejected because it cannot support future high-frequency or special-operability series.
  - Treat split mode as mandatory for all providers.
    - Rejected because current needs do not justify permanent complexity.

## Decision 3: Treat series as independently operable items in orchestration

- Decision: Operators should be able to run and inspect individual series items, even when ingestion code is grouped by provider.
- Rationale: Incident response and backfill workflows require narrow targeting.
- Alternatives considered:
  - Only provide grouped runs with no series-specific actions.
    - Rejected because operators would rerun unrelated workloads and lose precision.

## Decision 4: Maintain per-series identity and checkpointing in grouped runs

- Decision: Grouped runs must still preserve per-series identity, outcome visibility, and incremental boundaries.
- Rationale: Data integrity and auditability depend on distinct series lineage regardless of adapter grouping.
- Alternatives considered:
  - Aggregate grouped series into one undifferentiated run outcome.
    - Rejected because it degrades troubleshooting and traceability.

## Decision 5: Require explicit migration guardrails for grouped-to-split transitions

- Decision: Ownership transitions must include duplicate-trigger prevention and clear operational attribution.
- Rationale: Coexistence windows are high-risk for duplicate ingestion and ambiguous schedule ownership.
- Alternatives considered:
  - Informal/manual migration with no codified safeguards.
    - Rejected because it is error-prone and difficult to audit.

## Decision 6: Keep architecture aligned with 010/011 scheduling authority

- Decision: The source-asset scheduling authority model remains intact while introducing series-level operational semantics.
- Rationale: Recent cutover guarantees should not be weakened by this feature.
- Alternatives considered:
  - Reintroduce a shared all-source schedule model.
    - Rejected because it conflicts with accepted hard-cutover behavior.
