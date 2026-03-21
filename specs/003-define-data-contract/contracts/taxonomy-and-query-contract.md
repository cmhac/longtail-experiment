# Contract: Taxonomy and Query Dimensions

## Purpose

Define category and geography hierarchy requirements that enable reliable discovery, filtering, and rollups across heterogeneous time-series data.

## Version

- Contract: taxonomy-and-query-dimensions
- Version: v1
- Status: Draft for implementation planning

## Taxonomy Requirements

- Each DataSeries MUST map to at least one valid category hierarchy path.
- Taxonomy nodes MUST maintain parent-child relationships with explicit taxonomyVersion.
- Taxonomy changes MUST preserve historical references for previously accepted observations.

## Geography Requirements

- Observations with available location context MUST map to a valid geography hierarchy path.
- Non-geographic series MUST be explicitly labeled as non-geographic.
- Geography hierarchy MUST support multi-level rollups.

## Query Filter Requirements

System query interfaces MUST support filters for:

- category hierarchy path
- geography hierarchy path or non-geographic status
- sourceId or sourceType
- frequency
- reference period boundaries
- revision state

## Validation Rules

- categoryPathId MUST resolve within declared taxonomyVersion.
- geographyPathId, when present, MUST resolve within declared taxonomyVersion.
- parent-child hierarchy integrity MUST be enforced for both category and geography trees.

## Contract Behavior

- Filtering by parent category SHOULD include descendant nodes.
- Filtering by geography scope SHOULD include descendants when requested.
- Query behavior MUST remain stable for historical records even when taxonomy evolves.

## Compatibility and Evolution

- Additive taxonomy fields are backward compatible.
- Hierarchy semantic changes require documented migration strategy.
- Query filter deprecations require compatibility window and versioned notice.
