# Research: Per-Source Asset Cadence

**Feature**: 011-source-asset-cadence  
**Date**: 2026-03-22

## Decision Log

### Decision 1: Retire shared all-source schedule and assign one schedule per source asset

**Decision**: Use source-owned schedule definitions as the only scheduled execution authority for ingestion sources.

**Rationale**: This directly satisfies the feature goal of simplifying schedule ownership and eliminates ambiguity introduced by shared trigger plus internal due filtering.

**Alternatives considered**:

- Keep shared schedule and only improve due-filter logic: rejected because it keeps split authority and operational complexity.
- Keep shared schedule as fallback: rejected because dual authority risks duplicate triggers and unclear ownership.

---

### Decision 2: Remove scheduler-owned cadence policy hydration from scheduled execution path

**Decision**: Scheduled runs must no longer depend on separate persisted cadence policy reads to determine due status.

**Rationale**: In the target model, cadence is represented by source schedule definitions themselves, so separate due-evaluation policy state is redundant and error-prone.

**Alternatives considered**:

- Keep cadence policy tables for active due decisions: rejected because it duplicates schedule semantics and creates drift risk.
- Partially retain due selector for scheduled runs: rejected because it preserves old architecture complexity.

---

### Decision 3: Preserve source-level on-demand triggers as an explicit non-scheduled path

**Decision**: Keep operator-invoked source execution independent from scheduled cadence.

**Rationale**: Operators still need targeted reruns and diagnostics; this requirement is orthogonal to cadence ownership.

**Alternatives considered**:

- Remove on-demand triggers entirely: rejected due loss of operational control.
- Route on-demand through shared schedule queue: rejected because it conflicts with source-level ownership and responsiveness expectations.

---

### Decision 4: Retain run visibility while reclassifying legacy schedule artifacts as historical context

**Decision**: Keep source outcome and run audit visibility as first-class behavior while documenting migration interpretation for legacy cadence/eligibility artifacts.

**Rationale**: Operators need continuity in run diagnostics; migration should avoid breaking observability while still enforcing hard cutover on active scheduling.

**Alternatives considered**:

- Delete legacy records immediately: rejected because it harms troubleshooting and audit continuity.
- Preserve legacy logic as active compatibility layer: rejected because it weakens hard-cutover semantics.

---

### Decision 5: Validate cutover through local Dagit and compose-backed end-to-end checks

**Decision**: Require local verification that every active source asset has its own schedule behavior and trigger attribution post-cutover.

**Rationale**: The feature is operator-facing and schedule semantics are hard to validate from unit tests alone; local stack parity is required by constitution.

**Alternatives considered**:

- Test only with unit mocks: rejected due insufficient confidence in real orchestration behavior.
- Validate only in CI artifacts: rejected because local-first parity is a repository principle.
