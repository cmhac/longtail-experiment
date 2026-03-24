# Quickstart: Provider Adapter Bootstrap Standard

## Purpose

Use this guide to validate the planned bootstrap workflow end-to-end once implementation begins.

## Prerequisites

- Repository dependencies installed.
- Working tree on branch 021-bootstrap-provider-script.
- Existing pipeline tooling environment available.

## 1. Run the bootstrap command from repository root

Example shape (final command name and arguments are defined during implementation):

pnpm run provider:bootstrap -- --provider-group-key acme --source-key acme_cpi --module-name acme_cpi_source --cadence-label monthly --cron-schedule "0 0 1 \* \*" --series-item-key acme_cpi --canonical-series-key PRICE.US.CPI --provider-series-id CPIAUCSL

Expected result:

- Command exits successfully.
- One new adapter scaffold file appears under apps/pipeline/src/orchestration/jobs/sources/.
- Command output summarizes generated file path and next steps.

## 2. Validate generated scaffold shape

Confirm generated file includes:

- Source key constant.
- Workflow builder shell returning a registration object.
- SOURCE_SPEC dictionary skeleton.
- Placeholder sections for provider-specific fetch and mapping logic.

## 3. Validate failure scenarios

### 3.1 Missing required input

- Omit one required argument and run command.
- Expect non-zero exit with actionable validation message.

### 3.2 Existing file collision

- Re-run command with same module target.
- Expect non-zero exit and no overwrite.

### 3.3 Source identity collision

- Use an existing source key.
- Expect non-zero exit and explicit collision message.

## 4. Validate onboarding standard updates

- Check runbook content at docs/runbooks/provider-onboarding.md for script-first requirement.
- Check skill content at .agents/skills/onboard-provider/SKILL.md for runbook-read requirement and script usage requirement.

## 5. Run quality gates

Required before commit or handoff:

1. pnpm exec nx run-many -t test --all
2. pnpm exec nx run-many -t coverage --all

Optional focused checks during development:

1. pnpm run affected:lint
2. pnpm run affected:typecheck
3. pnpm run affected:test

## 6. Completion criteria

- Bootstrap command is callable from root package scripts.
- Scaffold creation works for valid input and fails safely for invalid/collision input.
- Documentation and skill guidance both define script-first onboarding.
- Full-suite and coverage stop gates pass.

## Validation Notes

- 2026-03-24: `pnpm exec nx run pipeline:test:provider-bootstrap` passed.
- 2026-03-24: `pnpm exec nx run-many -t test --all` passed.
- 2026-03-24: `pnpm exec nx run-many -t coverage --all` passed.
