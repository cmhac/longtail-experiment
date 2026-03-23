# Feature Specification: Dynamic Source Workflow Registration

**Feature Branch**: `013-dynamic-source-registration`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "Read issue 2 of this repo and build a spec from it"

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Onboard Source Without Bootstrap Edits (Priority: P1)

As a pipeline developer, I can add a valid source adapter and have it registered automatically during startup, so onboarding a new provider does not require edits in runtime bootstrap wiring.

**Why this priority**: This removes the current high-friction bottleneck and directly addresses the main failure mode from manual registration.

**Independent Test**: Add a valid adapter that meets the registration contract, start runtime, and verify the new source appears in registered source keys without bootstrap code edits.

**Acceptance Scenarios**:

1. **Given** a valid new source adapter module, **When** runtime starts, **Then** the source is registered automatically and available for execution.
2. **Given** no runtime bootstrap edits for that adapter, **When** onboarding validation is run, **Then** onboarding succeeds and reports the source as active.

---

### User Story 2 - Deterministic and Safe Registration (Priority: P2)

As a pipeline maintainer, I need dynamic registration to be deterministic and guarded, so startup behavior is stable and failures are actionable.

**Why this priority**: Automatic discovery is only safe if order is stable and invalid modules fail fast with clear remediation signals.

**Independent Test**: Run startup repeatedly with the same adapter set and verify source registration order is unchanged; introduce malformed and duplicate adapters and verify clear failures.

**Acceptance Scenarios**:

1. **Given** the same set of valid adapters, **When** runtime starts multiple times, **Then** registration order is consistent across runs.
2. **Given** a malformed adapter missing required contract elements, **When** runtime starts, **Then** startup fails with a clear module-scoped contract violation message.
3. **Given** two adapters that declare the same source identity, **When** registration runs, **Then** registration fails and reports duplicate source identity conflict.

---

### User Story 3 - Operator and QA Confidence in Onboarding Flow (Priority: P3)

As an operator or QA engineer, I can validate onboarding behavior through updated smoke tests and runbook guidance, so source onboarding remains reliable as providers scale.

**Why this priority**: Documentation and test updates ensure behavior remains understandable and verifiable for the wider team.

**Independent Test**: Follow onboarding runbook steps and run updated smoke/loader tests to verify expected registered sources and clear handling of invalid modules.

**Acceptance Scenarios**:

1. **Given** updated onboarding documentation, **When** a developer follows the documented onboarding flow, **Then** they can onboard a new valid adapter without undocumented bootstrap edits.
2. **Given** updated smoke and loader tests, **When** affected orchestration tests are executed, **Then** they confirm dynamic registration behavior and preserve existing source behavior.

---

### Edge Cases

- A discovered module is present but does not declare required registration metadata.
- Two discovered modules map to the same source identity.
- A non-adapter helper module is present in the discovery scope.
- Discovery returns zero valid modules due to misconfiguration.
- Existing sources remain valid but one newly added adapter is malformed.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST support source workflow registration through a single discovery/registration entrypoint rather than per-source bootstrap edits.
- **FR-002**: The system MUST preserve existing behavior for currently active sources during and after migration to dynamic registration.
- **FR-003**: The system MUST register valid source adapters in deterministic order.
- **FR-004**: The system MUST reject malformed adapters at startup with actionable error messages that identify the failing module and violated contract rule.
- **FR-005**: The system MUST prevent duplicate source identities from being registered.
- **FR-006**: The system MUST define and enforce what discovered files are treated as adapters versus ignored as non-adapter modules.
- **FR-007**: The system MUST provide tests that verify discovery success paths, malformed adapter failures, duplicate identity rejection, and deterministic ordering.
- **FR-008**: The system MUST update onboarding documentation so adding a compliant source adapter no longer requires manual runtime bootstrap wiring edits.
- **FR-009**: The system MUST keep source execution semantics, scheduling behavior, and persistence behavior unchanged except for registration/composition wiring.

### Key Entities _(include if feature involves data)_

- **Adapter Registration Contract**: A required set of adapter-declared registration attributes used to determine whether a discovered module is valid for onboarding.
- **Discovered Adapter Module**: A module found within the onboarding discovery scope that may be accepted or rejected based on the contract.
- **Registration Failure Record**: A structured startup-time error artifact that identifies module identity, failing rule, and remediation clue.
- **Registration Catalog Snapshot**: The ordered set of registered source identities used for runtime verification and smoke assertions.

### Assumptions

- Existing source identities and trigger behavior remain unchanged unless explicitly updated in a future feature.
- Discovery scope is limited to the current source adapter location used by onboarding guidance.
- Startup should fail closed for contract violations instead of skipping invalid adapters silently.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In onboarding validation, a new compliant source adapter is discoverable and registered with zero runtime bootstrap file edits in 100% of trial runs.
- **SC-002**: Across at least 10 repeated startup runs with the same adapter set, registration order remains identical in 100% of runs.
- **SC-003**: For malformed or duplicate adapters, startup emits a module-specific actionable failure message in 100% of negative test cases.
- **SC-004**: Existing active source onboarding and execution checks continue to pass at the same success rate as pre-change baselines.
- **SC-005**: Developer onboarding documentation enables a first-time contributor to follow the source onboarding flow without referencing undocumented runtime wiring steps.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and automated test gates without suppressions, bypasses, or workaround-only code. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or above 90% in affected projects. (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack, or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes, provenance/timestamp impacts, and trend-alert reliability safeguards are defined. (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be created or updated in the same change for any impacted behavior, contracts, setup, or runbooks, including AGENTS.md when repository structure/workflows/tooling change. (Yes)
