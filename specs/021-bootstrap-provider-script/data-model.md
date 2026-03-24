# Data Model: Provider Adapter Bootstrap Standard

## Overview

This feature models bootstrap inputs and generated onboarding artifacts for provider adapter creation. It does not introduce persistent database schema changes.

## Entities

### 1. ProviderBootstrapRequest

- Description: Normalized command input used to generate one adapter scaffold.
- Fields:
  - provider_name (string, required): Human-readable provider identifier used in generated metadata.
  - provider_group_key (string, required): Lowercase grouping key used for related series.
  - source_key (string, required): Unique workflow/schedule identity.
  - module_name (string, required): Output module filename stem; final file must end with \_source.py.
  - ownership_mode (enum, required): grouped or split.
  - cadence_label (enum, required): hourly, daily, weekly, monthly, custom_interval.
  - cron_schedule (string, required): Five-field cron expression for schedule metadata.
  - series_items (array<SeriesSeed>, required, min length 1): Series declarations to seed scaffold structure.
  - output_dir (string, optional): Defaults to pipeline source adapter directory.
  - force_overwrite (boolean, optional, default false): Reserved for future use; initial version remains false-only behavior.
- Validation rules:
  - provider_group_key and source_key must match repository naming convention (lowercase snake-case).
  - module_name must resolve to filename ending with \_source.py.
  - source_key must not collide with existing discovered adapter source keys.
  - output file path must not already exist.
  - ownership_mode and cadence_label must be allowed enum values.
  - series_items length must equal canonical series declarations length when both are provided.

### 2. SeriesSeed

- Description: Input fragment describing one series scaffold entry.
- Fields:
  - series_item_key (string, required)
  - provider_series_id (string, required)
  - canonical_series_key (string, required)
  - metric_name (string, optional placeholder allowed)
  - frequency (string, optional placeholder allowed)
- Validation rules:
  - series_item_key should be prefixed by provider_group_key for consistency.
  - canonical_series_key must be uppercase dotted namespace format.

### 3. GeneratedAdapterScaffold

- Description: File artifact created by bootstrap command.
- Fields:
  - absolute_path (string)
  - module_name (string)
  - source_key_constant_name (string)
  - builder_function_name (string)
  - source_spec_present (boolean)
  - placeholder_sections (array<string>)
  - generated_at (datetime string)
- Validation rules:
  - Must contain required module-level exports expected by onboarding contract.
  - Must be syntactically valid Python.
  - Must include source spec skeleton with aligned series-item/canonical key tuples.

### 4. OnboardingStandardReference

- Description: Documentation/skill artifact that communicates the required bootstrap-first process.
- Fields:
  - artifact_type (enum): runbook or skill.
  - artifact_path (string)
  - requires_bootstrap_first (boolean)
  - requires_runbook_read_before_implementation (boolean, skill-only)
- Validation rules:
  - Runbook and skill references must not conflict on onboarding sequence.

## Relationships

- ProviderBootstrapRequest 1-to-1 GeneratedAdapterScaffold.
- ProviderBootstrapRequest 1-to-many SeriesSeed.
- OnboardingStandardReference documents constraints on how ProviderBootstrapRequest should be created/executed.

## State Transitions

### Bootstrap request lifecycle

1. drafted: Inputs gathered from command arguments.
2. validated: All naming, collision, and structural checks pass.
3. generated: Scaffold file written successfully.
4. failed: Validation or generation error occurred; no partial overwrite allowed.

### Onboarding guidance lifecycle

1. inconsistent: Runbook and skill instructions diverge.
2. aligned: Both define bootstrap as standard first step.
3. enforced: New onboarding tasks follow aligned guidance.
