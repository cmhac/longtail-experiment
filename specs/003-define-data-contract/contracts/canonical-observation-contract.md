# Contract: Canonical Observation

## Purpose

Define the required structure and validation behavior for all accepted time-series observations, independent of source origin.

## Version

- Contract: canonical-observation
- Version: v1
- Status: Draft for implementation planning

## Required Fields

- seriesId: stable identifier of the metric stream
- observationId: unique identifier for observation version
- referencePeriodStart: period start timestamp
- referencePeriodEnd: period end timestamp
- sourceFrequency: source-declared cadence marker
- rawValue: source-reported value
- normalizedValue: comparable value in canonical semantics when applicable
- valueScale: descriptor of value semantics
- qualityState: accepted, quarantined, rejected
- ingestTimestamp: ingestion timestamp

## Optional Fields

- geographyPathId: hierarchy path when geography is available
- normalizationNote: short explanation when normalization is non-trivial

## Validation Rules

- referencePeriodStart MUST be less than or equal to referencePeriodEnd.
- rawValue MUST be present for accepted observations.
- qualityState accepted MUST include linked provenance and source profile references.
- normalizedValue MUST be present when raw unit semantics differ from canonical comparison unit.
- duplicate accepted observations for the same series and period require explicit revision linkage.

## Contract Behavior

- Failed mandatory validation MUST produce quarantine or rejection with explicit reason.
- Accepted observations MUST be queryable by series, source, period, frequency, category, and geography dimensions.
- Canonical shape applies equally to external feeds and internal producer systems.

## Compatibility and Evolution

- New fields MUST be additive and documented.
- Breaking field semantics require contract version bump and migration notes.
- Historical accepted records remain valid under their original contract version metadata.

## Runtime Mapping Notes

- Runtime schema authority is `apps/pipeline/src/contract/schemas/canonical_observation.py`.
- Canonical runtime field names currently implemented are: `source_name`, `source_type`, `series_key`, `metric_name`, `frequency_granularity`, `observed_on`, `reported_at`, `value`, `unit`, `attributes`.
- `source_type` is constrained to `external|internal` and normalized in `apps/pipeline/src/contract/normalizers/source_payload_mapper.py`.

## Migration Guidance

- Relational persistence changes for canonical observations must be introduced through `libs/db/alembic/versions/` revisions.
- New non-null canonical fields require one migration that backfills existing rows before adding constraints.
- Migration revisions should preserve read compatibility for `apps/backend/src/contract/query/canonical_query.py` projections during rollout.
