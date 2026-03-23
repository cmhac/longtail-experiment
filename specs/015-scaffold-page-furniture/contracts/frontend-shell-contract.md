# Contract: Frontend Shell and Furniture Adapters

## Purpose

Define the structural and behavioral contract for the content-empty frontend shell baseline, including required furniture slots, adapter boundaries, and lifecycle hook stubs.

## Scope

- Root shell structure and required slot presence.
- Furniture slot adapter interfaces and placeholder behavior.
- Process hook stub boundaries for environment/data/publish extension points.
- Local readiness verification expectations.

## Contract Definitions

### 1) Root Shell Contract

Requirements:

- Root route must render an app shell containing exactly one empty main content region.
- Shell must expose required named regions: top navigation, secondary navigation, footer, scripts/analytics, ads/subscription.
- Shell must remain renderable when slot adapters are replaced by contract-compliant alternatives.

Validation outcomes:

- Invalid when any required region is missing from rendered output.
- Invalid when main region includes feature/product content in this scaffold scope.

### 2) Furniture Slot Adapter Contract

Requirements:

- Every required slot is fulfilled by an adapter implementation bound to a typed contract.
- Contract requires stable slot identity and defined adapter output shape.
- Baseline adapters render placeholder output only.

Validation outcomes:

- Invalid when adapter output cannot be mapped to required slot identity.
- Invalid when adapter violates required contract shape.
- Invalid when placeholder adapter introduces business/product data coupling.

### 3) Process Hook Stub Contract

Requirements:

- System provides stubs for `env_bootstrap`, `data_bootstrap`, and `publish_extension` lifecycle hooks.
- Hook stubs define invocation boundaries and expected extension signatures.
- Hook stubs must avoid side effects and business logic in this feature.

Validation outcomes:

- Invalid when required hook stub is absent.
- Invalid when hook stub behavior performs feature logic beyond boundary declaration.

### 4) Startup and Verification Contract

Requirements:

- Developers can start frontend locally and load root shell without blocking runtime errors.
- Visual verification confirms all required slot placeholders are present.
- Affected quality gates pass without suppression or bypass.

Validation outcomes:

- Invalid when startup fails under documented local steps.
- Invalid when required slot placeholders are not visibly present.
- Invalid when affected lint/format/typecheck/test/coverage checks fail.

## Non-Goals

- Implementing editorial or product page content.
- Integrating private furniture provider packages.
- Implementing production business logic in process hooks.

## Evidence Expectations

Acceptance evidence should include:

- Root route render check showing shell and all five furniture placeholders.
- Tests proving slot contract coverage and missing-slot failure detection.
- Local startup output confirming successful app launch.
- Frontend quality command results showing passing affected gates.
- Documentation updates describing startup and shell verification flow.

## Adapter Replacement Notes

- Replacement adapters must preserve slot identity and continue returning renderable output for the same `slot_name`.
- App shell composition must resolve adapters from a registry so provider swaps avoid root page rewiring.
- Any replacement that omits a required slot must fail contract validation during tests/type checks before merge.
