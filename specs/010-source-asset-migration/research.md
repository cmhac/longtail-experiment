# Research: Source-Per-Asset Migration

**Feature**: 010-source-asset-migration  
**Date**: 2026-03-22

## Decision Log

### Decision 1: Use one-time big-bang cutover for scheduling authority migration

**Decision**: Perform a single release-window cutover that retires legacy scheduling/coordinator paths and activates source-asset scheduling as the only runtime path.

**Rationale**: Clarifications confirm greenfield tolerance for fast cutover and low historical-data risk, reducing complexity and migration overhead.

**Alternatives considered**:

- Incremental per-source cutover: rejected due added migration control complexity and slower delivery.
- Incremental per-domain cutover: rejected because group partitioning adds planning overhead without meaningful current-scale benefit.

---

### Decision 2: Enforce deterministic source asset discovery and contract validation

**Decision**: Standardize source module registration contract and deterministic discovery order, with fail-fast startup errors for malformed or duplicate sources.

**Rationale**: Deterministic startup and clear contract failures reduce hidden orchestration drift and avoid flaky behavior during and after cutover.

**Alternatives considered**:

- Keep manual runtime wiring: rejected because it does not scale and increases merge conflict risk.
- Allow best-effort registration with warnings: rejected because silent partial startup creates operational ambiguity.

---

### Decision 3: Preserve forward run visibility, not strict historical parity, in greenfield

**Decision**: Maintain run summary and source outcome visibility for all post-cutover executions; do not require strict pre-cutover parity migration.

**Rationale**: Clarified project stage prioritizes rapid architecture shift over historical reconciliation while still requiring observable operations after cutover.

**Alternatives considered**:

- Full historical parity across legacy and asset paths: rejected as unnecessary effort at current data volume.
- No persistence guarantees post-cutover: rejected because it undermines operator trust and triage.

---

### Decision 4: Keep Dagster as the sole scheduling authority with no legacy fallback

**Decision**: After cutover, legacy schedule triggers remain disabled even when some sources fail, and operator recovery occurs inside the source-asset path.

**Rationale**: Single authority avoids duplicate cadence triggers and aligns with the architecture objective of platform-native scheduling.

**Alternatives considered**:

- Temporary fallback to legacy scheduler for failed sources: rejected because it reintroduces dual-authority complexity.
- Auto-toggle fallback mode on failures: rejected due hidden behavior changes and operational unpredictability.

---

### Decision 5: Expand in-scope migration population to include newly onboarded sources during implementation

**Decision**: Initial delivery includes all currently supported sources and any newly onboarded source in the implementation window.

**Rationale**: This prevents mixed onboarding semantics and ensures source-as-asset is the default pattern immediately.

**Alternatives considered**:

- Freeze source onboarding during migration: rejected because it blocks development flow.
- Defer all new sources to post-migration follow-up: rejected because it creates immediate technical debt.

---

### Decision 6: Use focused orchestration regression coverage for cutover confidence

**Decision**: Expand existing orchestration tests to cover source-level trigger routing, scheduling exclusivity, lock/defer behavior, and failed-source visibility after cutover.

**Rationale**: Reusing established test suites enforces constitution coverage requirements with minimal duplicate infrastructure.

**Alternatives considered**:

- Build a separate migration-only test harness: rejected due maintenance overhead.
- Depend on manual smoke-only checks: rejected due insufficient confidence for architecture cutover.
