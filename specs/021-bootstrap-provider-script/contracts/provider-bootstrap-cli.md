# Contract: Provider Bootstrap CLI

## Interface Summary

- Interface type: Repository CLI command
- Consumer: Human contributors and coding agents onboarding new providers
- Provider: Monorepo root script entry in package.json

## Command Surface

## Command

pnpm run provider:bootstrap -- [arguments]

## Required arguments

- --provider-group-key <value>
- --source-key <value>
- --module-name <value>
- --cadence-label <value>
- --cron-schedule <value>
- --series-item-key <value>
- --canonical-series-key <value>
- --provider-series-id <value>

## Optional arguments

- --provider-name <value>
- --metric-name <value>
- --dataset-description <value>
- --dataset-geographic-scope <value>
- --topic-tags <comma-separated-values>
- --ownership-mode <grouped|split>
- --output-dir <path>

## Behavioral guarantees

1. Successful invocation creates exactly one new adapter scaffold file.
2. Invocation never overwrites an existing adapter file.
3. Invalid or missing required arguments cause non-zero exit with actionable message.
4. Source identity collisions cause non-zero exit with explicit collision detail.
5. Success output includes generated file path and next onboarding actions.

## Validation rules

- provider-group-key, source-key, and module-name must satisfy repository naming conventions.
- module-name must resolve to a discoverable adapter filename ending with _source.py.
- cadence-label must be one of supported cadence values.
- cron-schedule must be syntactically valid five-field cron expression.
- multi-series argument groups must preserve index alignment across series item, provider series, and canonical series keys.

## Output contract

## Success output

- Exit code: 0
- Standard output includes:
  - STATUS: success
  - GENERATED_FILE: absolute or repo-relative path
  - SOURCE_KEY: resolved source identity
  - NEXT_STEPS: checklist-style follow-up actions

## Error output

- Exit code: non-zero
- Standard error includes:
  - STATUS: failure
  - ERROR_CODE: one of invalid_input, file_exists, source_key_collision, generation_failed
  - MESSAGE: actionable human-readable reason

## Compatibility and versioning

- Contract version: 1.0
- Backward compatibility requirement: New optional arguments may be added without breaking existing invocations.
- Breaking changes to required arguments or output keys must be reflected in runbook and onboarding skill in the same change.