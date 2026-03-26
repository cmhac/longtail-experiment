# Contract: Source Discovery Behavior

## Purpose

Define expected backend and frontend behavior for source list and source detail discovery flows.

## Route Contract

### Frontend Routes

- `/sources` renders the source directory page.
- `/sources/{sourceId}` renders the source detail page for one source.
- Valid source identifiers render the source detail experience.
- Unknown source identifiers render a clear not-found experience.
- Retrieval failures render a generic discovery error experience while preserving shell navigation.

### Backend Endpoints

- `GET /api/sources` returns a list of discoverable sources.
- `GET /api/sources/{sourceId}` returns one source detail payload with the datasets attributed to that source.
- Unknown source identifiers return a source-not-found error response.
- Non-validation runtime failures return explicit error payloads rather than partial success payloads.

## Source List Payload Contract

A successful source list response MUST include:

- source entries with:
  - `id`
  - `name`
  - `dataset_count`
  - optional `source_type`
- deterministic ordering suitable for stable browsing
- total source count context when returned at page level

The source list page MUST:

- show each discoverable source exactly once
- show an explicit empty state when no sources are available
- treat all returned source text as escaped content

## Source Detail Payload Contract

A successful source detail response MUST include:

- selected source metadata:
  - `id`
  - `name`
  - `dataset_count`
  - optional `source_type`
- dataset list where every dataset belongs to the selected source

The source detail page MUST:

- display source context before the dataset list
- render datasets using the existing dataset-browsing hierarchy
- link each dataset entry to the existing dataset detail route
- show an explicit no-datasets state when the source exists but has zero datasets

## Source Identifier Contract

- The source identifier used in routes and payloads MUST be stable across source list and source detail responses.
- The identifier MUST resolve case and punctuation consistently for source navigation.
- Dataset payload `source.id` values and source discovery `id` values MUST represent the same source identity model.

## Safety and Fallback Contract

- Externally sourced text is rendered as escaped content.
- Empty, error, and not-found states are explicit and non-blank.
- Shell navigation remains available in all source discovery states.
- Unknown frontend source routes render the not-found experience inside the shared shell.

## Validation Contract

Implementation is compliant when all statements below are true:

1. Source directory entries and source detail payloads use the same source identity model.
2. Source detail dataset listings contain only datasets from the selected source.
3. Empty, error, and not-found scenarios are explicit and distinguishable.
4. Source detail pages preserve onward navigation into existing dataset detail routes.
