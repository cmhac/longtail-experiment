# Contract: Topic and Geography Discovery Behavior

## Purpose

Define expected backend and frontend behavior for topic-tag and geography detail discovery flows.

## Route Contract

### Frontend Routes

- `/topics/{topicId}` renders the topic tag detail page for one topic.
- `/geographies/{geographyId}` renders the geography detail page for one geography.
- Valid metadata identifiers render the corresponding detail experience.
- Unknown metadata identifiers render a clear not-found experience.
- Retrieval failures render a generic discovery error experience while preserving shell navigation.

### Backend Endpoints

- `GET /api/topics/{topicId}` returns one topic detail payload with the datasets attributed to that topic.
- `GET /api/geographies/{geographyId}` returns one geography detail payload with the datasets attributed to that geography.
- Unknown metadata identifiers return metadata-not-found error responses.
- Non-validation runtime failures return explicit error payloads rather than partial success payloads.

## Topic Detail Payload Contract

A successful topic detail response MUST include:

- selected topic metadata:
  - `id`
  - `label`
  - `dataset_count`
- dataset list where every dataset belongs to the selected topic
- deterministic ordering suitable for stable browsing

The topic detail page MUST:

- display topic context before the dataset list
- render datasets using the existing dataset-browsing hierarchy
- link each dataset entry to the existing dataset detail route
- show an explicit no-datasets state when the topic exists but has zero visible datasets

## Geography Detail Payload Contract

A successful geography detail response MUST include:

- selected geography metadata:
  - `id`
  - `label`
  - `dataset_count`
- dataset list where every dataset belongs to the selected geography
- deterministic ordering suitable for stable browsing

The geography detail page MUST:

- display geography context before the dataset list
- render datasets using the existing dataset-browsing hierarchy
- link each dataset entry to the existing dataset detail route
- show an explicit no-datasets state when the geography exists but has zero visible datasets

## Metadata Navigation Contract

- Visible topic tag pills resolve to `/topics/{topicId}` using the same identity model as topic detail payloads.
- Visible geography pills resolve to `/geographies/{geographyId}` using the same identity model as geography detail payloads.
- Topic and geography labels displayed in destination pages MUST match the labels implied by the originating pills.

## Safety and Fallback Contract

- Externally sourced text is rendered as escaped content.
- Empty, error, and not-found states are explicit and non-blank.
- Shell navigation remains available in all metadata discovery states.

## Validation Contract

Implementation is compliant when all statements below are true:

1. Topic pills and geography pills navigate to stable metadata detail routes.
2. Topic detail and geography detail payloads use consistent metadata identity between routes and responses.
3. Topic detail dataset listings contain only datasets from the selected topic.
4. Geography detail dataset listings contain only datasets from the selected geography.
5. Empty, error, and not-found scenarios are explicit and distinguishable.
6. Metadata detail pages preserve onward navigation into existing dataset detail routes.
