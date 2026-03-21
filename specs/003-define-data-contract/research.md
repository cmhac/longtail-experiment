# Research: Core Pipeline Data Contract

## Canonical Observation Envelope

- Decision: Use a single canonical observation envelope for all time-series sources, regardless of source type or publication cadence.
- Rationale: A unified envelope minimizes source-specific branching and enables consistent validation, storage, and downstream querying.
- Alternatives considered:
  - Source-specific schemas per provider: rejected due to high maintenance and inconsistent analytics behavior.
  - Canonical schema only at query time: rejected because delayed normalization weakens ingest-time quality controls.

## Provenance Immutability and Revision Lineage

- Decision: Treat provenance fields as immutable per observation version and model revisions as explicit linked records rather than destructive updates.
- Rationale: Long-horizon trend analysis requires auditability, reproducibility, and transparent correction history.
- Alternatives considered:
  - In-place updates of prior values: rejected because it loses historical traceability.
  - Snapshot-only periodic exports: rejected because lineage becomes indirect and harder to query.

## Frequency Handling Strategy

- Decision: Preserve source-declared frequency and reference period as first-class fields while normalizing date semantics into a common timeline model.
- Rationale: Different sources publish daily, weekly, monthly, quarterly, and ad hoc values that must remain comparable without erasing publication intent.
- Alternatives considered:
  - Force all series into one frequency during ingest: rejected because it introduces interpolation assumptions too early.
  - Leave period semantics unstructured: rejected because period alignment would be unreliable.

## Raw and Normalized Values

- Decision: Store both raw source value and normalized value when transformation affects units, scale, or interpretability.
- Rationale: Analysts need direct source fidelity for verification and normalized values for cross-series comparison.
- Alternatives considered:
  - Store normalized only: rejected because provenance review cannot reproduce source-reported figures.
  - Store raw only: rejected because cross-series analysis cost increases and consistency decreases.

## Taxonomy and Geography Hierarchies

- Decision: Model category and geography as versioned hierarchies and require each series to map to a valid category path; geography is required when available and explicitly marked when absent.
- Rationale: Hierarchical filtering and rollups are core discovery workflows and must remain stable as classifications evolve.
- Alternatives considered:
  - Flat tags only: rejected because parent-child rollups are not reliable.
  - Free-text geography labels: rejected due to inconsistent filtering behavior.

## Source Registry and Onboarding Controls

- Decision: Maintain a source profile registry that defines expected cadence, required metadata, validation rules, and source type (external or internal).
- Rationale: A source registry reduces onboarding ambiguity and ensures contract compliance before data is accepted.
- Alternatives considered:
  - Implicit source behavior from first payload: rejected due to inconsistent validation and governance gaps.
  - Separate contracts for internal and external sources: rejected because one canonical model is a core objective.

## Storage Direction for Phase Implementation

- Decision: Lock persistence to PostgreSQL 16 with TimescaleDB 2.14 extension.
- Rationale: The contract needs relational integrity across provenance, revisions, taxonomy/geography hierarchies, and efficient time-series partitioning for observation-scale workloads.
- Alternatives considered:
  - Document-only storage for all entities: rejected because relational integrity and revision linking become harder to enforce.
  - Plain PostgreSQL without time-series extension: rejected because hypertable features reduce operational complexity for high-volume periodized observations.
  - Time-series-only store without relational metadata model: rejected because provenance and taxonomy requirements need richer relational constraints.

## Canonical Single Source of Truth

- Decision: Canonical contract authority is dual-layer and explicit: normative contract in `specs/003-define-data-contract/contracts/canonical-observation-contract.md` and runtime enforcement in `apps/pipeline/src/contract/schemas/canonical_observation.py`.
- Rationale: Separating normative and runtime authority preserves governance clarity while ensuring executable validation parity.
- Alternatives considered:
  - Multiple source-specific runtime schemas: rejected because it fragments validation logic and weakens consistency.
  - Documentation-only contract authority: rejected because it cannot enforce runtime guarantees.

## Locked Module Stack

- Decision: Lock core modules before implementation: Pydantic 2.x for validation, SQLAlchemy 2.x for ORM and repository model definitions, Alembic for migrations, psycopg 3.x for database driver access, structlog and OpenTelemetry for observability.
- Rationale: Early module lock-in prevents architecture churn and ensures tasks map to concrete implementation targets.
- Alternatives considered:
  - Delay module selection until coding starts: rejected because it risks implementation drift and rework.
  - Use ad hoc dict validation and raw SQL only: rejected because maintainability, schema evolution, and traceability suffer.

## Validation and Quality Gate Coverage

- Decision: Add ingest contract validation tests, provenance immutability tests, revision-link integrity tests, taxonomy/geography filter tests, and observability assertions (structured log fields and trace context propagation) under existing backend and pipeline quality gates.
- Rationale: Constitution quality and coverage requirements require automated verification of core contract behavior.
- Alternatives considered:
  - Rely on manual QA for contract validation: rejected due to repeatability and coverage risk.
  - Add tests after implementation complete: rejected because contract-first approach requires early guardrails.
