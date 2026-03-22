# Research: FRED Interest Rate Source

**Feature**: 008-add-fred-source  
**Date**: 2026-03-22

## Decision Log

### Decision 1: Treat durable observation persistence as in-scope enabling work

**Decision**: Include canonical observation-store migration and runtime repository wiring in this feature.

**Rationale**: Current runtime uses a discard-only repository, so real provider records cannot persist. Shipping a FRED source without persistence would violate the primary user value and create misleading run success signals.

**Alternatives considered**:

- Defer persistence to a separate follow-up feature: rejected, because this would make the first real-world source incomplete and non-verifiable.
- Persist to temporary local files: rejected, because it bypasses canonical contracts and breaks local stack parity.

---

### Decision 2: Source credentials come from local secret env file

**Decision**: Read `FRED_API_KEY` from local secret environment configuration under `docker/compose/local.secrets.env` (gitignored) using existing stack/environment loading flow.

**Rationale**: Aligns with current repository secret-handling direction and keeps credential material outside tracked source files.

**Alternatives considered**:

- Hardcode credentials in source code or tracked env files: rejected for security and compliance reasons.
- Prompt for credentials at runtime interactively: rejected; not automatable for scheduled runs.

---

### Decision 3: Use dedicated source adapter with canonical payload mapping

**Decision**: Implement `fred_fedfunds_source` as a dedicated source workflow adapter that maps provider observations into the canonical ingest payload shape and delegates validation/persistence to `SourceIngestRunner` + `CanonicalIngestService`.

**Rationale**: Preserves established architecture and keeps source-specific parsing/transport concerns isolated from canonical contract enforcement.

**Alternatives considered**:

- Embed provider fetch logic directly in runtime wiring: rejected due to coupling and poor testability.
- Add provider-specific validation directly in canonical service: rejected because it pollutes shared contract layer with source details.

---

### Decision 4: Incremental fetch baseline uses last persisted observation period

**Decision**: Compute provider request window from the latest persisted observation date for the source series and request only needed trailing range.

**Rationale**: Satisfies duplicate-avoidance and call-efficiency goals while remaining deterministic and simple for a first external source.

**Alternatives considered**:

- Always request full history each run: rejected due to unnecessary call volume and duplicate processing risk.
- Maintain separate source-specific checkpoint table: rejected initially; persisted canonical observations already provide a reliable checkpoint source.

---

### Decision 5: Fail closed on missing/invalid credentials, fail soft on bad records

**Decision**: Missing/invalid credentials cause source-level failure with explicit reason; malformed provider records are quarantined through existing contract-validation paths, allowing partial-success outcomes when valid rows exist.

**Rationale**: Credential errors are configuration blockers that operators must fix immediately. Record-level quality issues should remain observable without discarding all valid data.

**Alternatives considered**:

- Treat missing credentials as not_due/no-op: rejected because it hides operational misconfiguration.
- Fail entire run on first malformed record: rejected because it reduces data availability and ignores existing partial-success semantics.

---

### Decision 6: Add migration 0004 for canonical observation tables

**Decision**: Introduce a new Alembic revision to create canonical observation storage tables required by the Postgres observation repository.

**Rationale**: Existing migrations (0001-0003) do not provide durable canonical observation tables; a repository implementation without schema support is non-functional.

**Alternatives considered**:

- Reuse ingestion runtime tables for observation data: rejected because runtime run-state schema is not designed for canonical time-series storage.
- Store observations in in-memory-only repository for local runs: rejected because it does not satisfy persistence requirements.

---

### Decision 7: Align repository SQL with existing relational contract schema

**Decision**: Implement durable repository persistence against `source_profiles` -> `data_series` -> `observations(series_id)` and read by joining `data_series.series_key`.

**Rationale**: Real end-to-end execution exposed a mismatch where repository SQL referenced `observations.series_key`, but the live contract schema stores observation linkage as `series_id`. Aligning SQL to the relational contract is required for successful real runs.

**Alternatives considered**:

- Keep a denormalized `series_key` column directly on `observations`: rejected because it diverges from established ORM contract and creates duplicate-key drift risk.
- Add temporary compatibility queries while preserving incorrect writes: rejected because it obscures contract violations and delays root-cause correction.
