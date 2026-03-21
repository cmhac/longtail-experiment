# Contract: Provenance and Revision Lineage

## Purpose

Define immutable lineage requirements for accepted observations and explicit handling of revised source publications.

## Version

- Contract: provenance-and-revision
- Version: v1
- Status: Draft for implementation planning

## Provenance Requirements

Each accepted observation version MUST include:

- provenanceId: unique lineage record identifier
- observationId: linked observation version identifier
- sourceId: source profile identifier
- sourcePublishedAt: source publication timestamp or window
- sourceRetrievalAt: retrieval timestamp
- ingestRunId: ingest execution identifier
- sourceDocumentRef: source artifact reference
- acquisitionMethod: retrieval channel classification
- immutableFlag: true after persistence

## Revision Requirements

When a source revises prior values, system MUST create a RevisionRecord containing:

- revisionId: unique revision event identifier
- supersededObservationId: prior observation version
- currentObservationId: replacement observation version
- revisionReason: correction/backfill/methodology/restatement
- revisionPublishedAt: revision publication timestamp
- revisionDetectedAt: detection timestamp

## Validation Rules

- Immutable provenance fields MUST NOT be modified after accepted persistence.
- supersededObservationId and currentObservationId MUST reference same series and compatible period semantics.
- revisionReason MUST be present for all linked revisions.
- Every revision event MUST preserve query access to both prior and current values.

## Contract Behavior

- In-place destructive replacement of accepted observations is disallowed.
- Provenance omissions for accepted observations are disallowed unless source policy explicitly allows and is recorded in source profile.
- Revision lineage MUST support reproducible audit trails during quality review.

## Compatibility and Evolution

- Provenance field additions are additive and backward compatible.
- Changes to immutability or revision semantics require major version change and migration guidance.
