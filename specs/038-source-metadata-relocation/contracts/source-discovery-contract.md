# Contract: Source Discovery Metadata

## Purpose

Define expected pipeline, backend, and frontend behavior for stable source identity and human-readable source metadata after the source-metadata rollout.

## Source Identity Contract

- Source-related APIs and frontend routes use a stable source identifier derived from persisted source identity.
- The stable source identifier remains unchanged when a source title or description is edited.
- Source titles are human-readable labels and are not used as the canonical machine identifier.

## Source Summary Payload Contract

A successful source list response MUST include source entries with:

- `id`
- `title`
- `description`
- `dataset_count`
- optional `source_type`

The source list experience MUST:

- use `title` as the primary source label
- make source description available in source browsing context
- show each discoverable source exactly once
- preserve explicit empty and error states

## Source Detail Payload Contract

A successful source detail response MUST include:

- selected source metadata:
  - `id`
  - `title`
  - `description`
  - `dataset_count`
  - optional `source_type`
- dataset list where every dataset belongs to the selected source

The source detail experience MUST:

- display the source title as the primary page label
- render the source description in the source context area
- preserve existing dataset navigation behavior
- show an explicit no-datasets state when the source exists but has zero datasets

## Persistence Contract

- Persisted source profiles store stable source identity plus source title and description as first-class source-level metadata.
- Source metadata returned by source discovery responses comes from persisted source-level data, not from reconstructing the label from dataset rows or source keys.
- Existing source-to-dataset membership remains intact after migration/backfill.

## Migration and Backfill Contract

- Existing maintained sources must have populated source title and description after migration/backfill completes.
- Source discovery responses must not regress to blank or key-derived labels for maintained sources after rollout.

## Compliance Criteria

Implementation is compliant when all statements below are true:

1. Source list and source detail responses use the same stable source identifier.
2. Source titles and descriptions are present in source list and source detail payloads.
3. Source-facing frontend routes render human-readable source titles instead of internal keys as the primary label.
4. Title changes do not break source routes, source membership, or source-to-dataset traceability.
