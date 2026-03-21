# Data Model: Core Pipeline Data Contract

## Entity: SourceProfile

- Description: Registry record for an upstream producer that defines onboarding and validation expectations.
- Fields:
  - sourceId: unique source identifier
  - sourceName: human-readable source name
  - sourceType: external or internal
  - ownershipContact: owning team or organization reference
  - expectedCadence: declared publication cadence
  - requiredProvenanceFields: required metadata keys for accepted observations
  - validationPolicyVersion: active validation policy reference
  - schemaVersion: canonical schema version reference
  - status: active, paused, deprecated
- Validation rules:
  - sourceId MUST be unique.
  - sourceType MUST be one of the allowed values.
  - requiredProvenanceFields MUST be non-empty.
  - status transitions MUST be auditable.
- Relationships:
  - SourceProfile has many DataSeries records.

## Entity: DataSeries

- Description: Canonical definition of a metric stream tracked over time.
- Fields:
  - seriesId: unique series identifier
  - sourceId: owning source reference
  - seriesName: display name
  - frequency: declared publication frequency
  - unitDescriptor: semantic unit label
  - categoryPathId: linked category hierarchy path reference
  - defaultGeographyPathId: optional default geography path reference
  - lifecycleState: active, paused, retired
  - taxonomyVersion: version marker for category/geography mapping
- Validation rules:
  - seriesId MUST be unique.
  - sourceId MUST reference an existing SourceProfile.
  - categoryPathId MUST resolve to a valid category path.
  - taxonomyVersion MUST be present at persistence time.
- Relationships:
  - DataSeries belongs to one SourceProfile.
  - DataSeries has many Observations.

## Entity: Observation

- Description: A single time-bound measurement for a series in canonical form.
- Fields:
  - observationId: unique observation version identifier
  - seriesId: parent series reference
  - referencePeriodStart: inclusive period start timestamp
  - referencePeriodEnd: inclusive period end timestamp
  - sourceFrequency: source-declared frequency marker
  - rawValue: value as provided by source
  - normalizedValue: value transformed for cross-series comparison
  - valueScale: scalar/percent/index basis descriptor
  - geographyPathId: optional geography hierarchy path reference
  - qualityState: accepted, quarantined, rejected
  - ingestTimestamp: timestamp when observation entered system
  - ingestTraceId: observability trace identifier for ingest transaction
  - contractVersion: canonical contract version applied at validation time
- Validation rules:
  - referencePeriodStart MUST be less than or equal to referencePeriodEnd.
  - rawValue MUST be present for accepted observations.
  - qualityState accepted MUST require complete provenance linkage.
  - normalizedValue MUST be present when unit normalization is required.
- Relationships:
  - Observation belongs to one DataSeries.
  - Observation has one ProvenanceRecord.
  - Observation may have one predecessor Observation through RevisionRecord.

## Entity: ProvenanceRecord

- Description: Immutable lineage metadata bound to one observation version.
- Fields:
  - provenanceId: unique lineage identifier
  - observationId: observation version reference
  - sourcePublishedAt: source publication timestamp or window
  - sourceRetrievalAt: timestamp data was retrieved from source
  - ingestRunId: ingest execution identifier
  - sourceDocumentRef: publication URL, document id, or internal artifact reference
  - acquisitionMethod: retrieval channel classification
  - immutableFlag: indicates locked provenance state
  - sourceChecksum: source payload checksum for reproducibility verification
- Validation rules:
  - observationId MUST be unique in ProvenanceRecord.
  - immutableFlag MUST be true for persisted accepted observations.
  - sourceDocumentRef MUST be present for accepted observations unless source policy explicitly allows omission.
- Relationships:
  - ProvenanceRecord belongs to one Observation.

## Entity: RevisionRecord

- Description: Explicit linkage between superseded and superseding observations.
- Fields:
  - revisionId: unique revision event identifier
  - supersededObservationId: prior observation version reference
  - currentObservationId: newer observation version reference
  - revisionReason: correction, backfill, methodology change, or source restatement
  - revisionPublishedAt: revision publication timestamp
  - revisionDetectedAt: timestamp revision was detected by ingest
- Validation rules:
  - supersededObservationId MUST differ from currentObservationId.
  - both linked observation records MUST map to the same DataSeries and reference period semantics.
  - revisionReason MUST be populated.
- Relationships:
  - RevisionRecord links two Observation versions.

## Entity: CategoryNode

- Description: Node in the thematic category hierarchy used for discovery and filtering.
- Fields:
  - categoryNodeId: unique category node identifier
  - parentCategoryNodeId: optional parent node reference
  - categoryLabel: category display label
  - categoryCode: stable code for machine filtering
  - hierarchyDepth: node depth from root
  - taxonomyVersion: taxonomy version reference
- Validation rules:
  - root nodes MUST have no parentCategoryNodeId.
  - non-root nodes MUST reference an existing parent within the same taxonomyVersion.
- Relationships:
  - CategoryNode forms a tree hierarchy.

## Entity: GeographyNode

- Description: Node in the geographic hierarchy used for location filtering and rollups.
- Fields:
  - geographyNodeId: unique geography node identifier
  - parentGeographyNodeId: optional parent node reference
  - geographyLabel: geography display label
  - geographyCode: stable geography code
  - geographyType: country, state, county, metro, district, or custom
  - hierarchyDepth: node depth from root
  - taxonomyVersion: taxonomy version reference
- Validation rules:
  - root nodes MUST have no parentGeographyNodeId.
  - non-root nodes MUST reference an existing parent within the same taxonomyVersion.
- Relationships:
  - GeographyNode forms a tree hierarchy.

## State Transitions

- SourceProfile:
  - Draft -> Active -> Paused -> Deprecated
- DataSeries:
  - Proposed -> Active -> Paused -> Retired
- Observation:
  - Received -> Validated -> Accepted
  - Received -> Validated -> Quarantined
  - Received -> Validated -> Rejected
- RevisionRecord:
  - Detected -> Linked -> Verified

## Persistence Notes (Locked)

- Backing store is PostgreSQL 16 with TimescaleDB 2.14 extension.
- Observation is modeled as time-series hypertable keyed by `referencePeriodStart` and
  partitioned with `seriesId` for ingest/query locality.
- Relational foreign keys enforce SourceProfile -> DataSeries -> Observation lineage.
- Unique constraints prevent duplicate accepted observation versions for identical
  series, reference period, and contract version without revision linkage.
