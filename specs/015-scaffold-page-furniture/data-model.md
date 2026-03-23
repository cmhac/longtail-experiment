# Data Model: Frontend Page Furniture Baseline

## Overview

This feature introduces shell-structure entities and contract boundaries required to render a content-empty page furniture baseline that is locally verifiable and integration-ready.

## Entities

### 1) FrontendShell

Represents the root page structure rendered for baseline verification.

Fields:

- route_id: string (required, `root` for baseline)
- shell_status: enum { draft, renderable, verified } (required)
- main_region_mode: enum { empty_only } (required)
- required_slots: list[string] (required)

Validation rules:

- required_slots must include exactly: top_navigation, secondary_navigation, footer, scripts_analytics, ads_subscription.
- main_region_mode must remain `empty_only` for this feature.
- shell_status `verified` requires successful visual and automated checks.

Relationships:

- One FrontendShell contains many FurnitureSlot records.
- One FrontendShell is validated by one or more VerificationScenario records.

### 2) FurnitureSlot

Represents a named, ordered furniture region within the shell.

Fields:

- slot_id: string (required)
- slot_name: string (required)
- order_index: integer (required)
- visibility_state: enum { visible, hidden, failed } (required)
- adapter_key: string (required)

Validation rules:

- slot_name must be one of the five required furniture slots.
- order_index must be unique per shell.
- visibility_state `failed` must trigger verification failure.

Relationships:

- Each FurnitureSlot is fulfilled by one FurnitureAdapterContract.

### 3) FurnitureAdapterContract

Represents the typed contract for a slot adapter implementation.

Fields:

- adapter_key: string (required)
- slot_name: string (required)
- accepts_props_shape: string (required)
- render_mode: enum { placeholder_only, provider_backed } (required)
- is_contract_compliant: boolean (required)

Validation rules:

- adapter_key must be unique for active adapters.
- slot_name must match the target FurnitureSlot.
- placeholder baseline adapters use render_mode `placeholder_only`.
- is_contract_compliant must be true for shell verification.

Relationships:

- One FurnitureAdapterContract fulfills one or more FurnitureSlot instances over time.

### 4) ProcessHookContract

Represents a lifecycle extension boundary for future server integration.

Fields:

- hook_name: enum { env_bootstrap, data_bootstrap, publish_extension } (required)
- hook_stage: enum { pre_render, startup, pre_publish } (required)
- hook_status: enum { stubbed, active } (required)
- side_effect_policy: enum { no_side_effects_in_stub } (required)

Validation rules:

- All three hook_name values must exist in scaffold.
- hook_status must be `stubbed` in this feature scope.
- side_effect_policy must prohibit business logic in stubs.

Relationships:

- ProcessHookContract records are invoked by startup and publish lifecycle flows.

### 5) VerificationScenario

Represents a repeatable readiness check path for local development.

Fields:

- scenario_id: string (required)
- verification_type: enum { startup, visual_shell, quality_gates } (required)
- expected_outcome: string (required)
- result_state: enum { pass, fail } (required)

Validation rules:

- startup verification must pass before visual_shell verification is counted as valid.
- quality_gates verification must include lint, format, typecheck, test, and coverage checks.

Relationships:

- VerificationScenario validates one FrontendShell per run.

## State Transitions

### Baseline Shell Lifecycle

1. draft: shell contracts and slot skeleton exist.
2. renderable: shell and required slots load at root route without blocking runtime errors.
3. verified: renderable shell has passing startup, visual, and quality-gate verification.

Transition constraints:

- `draft -> verified` is allowed only via `renderable`.
- Missing required slot forces transition to `fail` in verification and blocks `verified` state.
- Any quality-gate failure blocks transition to `verified`.

## Invariants

- Root shell always contains five required furniture slots in deterministic order.
- Main content region remains empty-only for this feature.
- All slot adapters satisfy their typed contracts.
- Process hooks remain contract stubs with no business logic side effects.
- Verification scenarios are reproducible from documented local steps.
