# Contract: Source Adapter Manifest Metadata

## Purpose

Define the required location and manifest fields for maintained pipeline source adapters after the source-metadata relocation.

## Discovery Scope Contract

- Maintained source adapters live under `apps/pipeline/src/sources`.
- Only adapter modules that satisfy the repository adapter naming contract are discoverable.
- Discovery, schedule derivation, Dagit asset derivation, and bootstrap generation must all target the same maintained adapter package.
- The retired deep adapter directory is no longer treated as an active onboarding destination once this feature is complete.

## Required Manifest Fields

Every maintained source adapter manifest MUST include:

- `source_key`
- `provider_group_key`
- `title`
- `description`
- `series_item_keys`
- `canonical_series_keys`
- `ownership_mode`
- `cron_schedule`
- `cadence_label`
- `builder`

## Validation Rules

- `source_key`, `provider_group_key`, `title`, and `description` must be non-empty strings.
- `title` and `description` must reject blank or whitespace-only values.
- `series_item_keys` and `canonical_series_keys` must both be present, non-empty, and aligned.
- `source_key` must remain unique across all discovered manifests.
- Invalid manifests fail startup discovery and are not silently skipped.

## Bootstrap Contract

- The standard provider bootstrap flow must generate new adapters in the maintained adapter package.
- The generated scaffold must include placeholders or values for the required source title and description.
- Bootstrap validation must reject requests that do not provide valid source title and description inputs.

## Compliance Criteria

Implementation is compliant when all statements below are true:

1. A newly generated adapter is created in the maintained source package.
2. Discovery rejects adapters missing `title` or `description`.
3. Existing maintained adapters continue to register successfully after being migrated to the new manifest fields.
4. Documentation and onboarding skill guidance refer contributors to the maintained source package and metadata requirements.
