# Contract: Source Workflow Registration

## Purpose

Define onboarding and runtime registration rules for source adapters under discovery-based composition.

## Scope

- Discovery eligibility and non-adapter exclusion.
- Adapter contract validity requirements.
- Deterministic registration ordering.
- Duplicate source identity prevention.
- Actionable startup failure semantics.

## Contract Definitions

### 1) Discovery Eligibility Contract

Requirements:

- Only modules that satisfy adapter registration contract criteria are eligible for registration.
- Non-adapter modules in discovery scope must be ignored according to explicit policy.
- Discovery must produce deterministic candidate ordering.

Validation outcomes:

- Invalid when helper/non-adapter modules are treated as registration candidates contrary to policy.
- Invalid when candidate ordering differs for the same module set.

### 2) Adapter Registration Contract

Requirements:

- Adapter registration must declare an active registration payload.
- Source identity must be non-empty and stable.
- Workflow identity must be non-empty.

Validation outcomes:

- Invalid when status is inactive.
- Invalid when source identity is missing/blank.
- Invalid when workflow identity is missing/blank.

### 3) Duplicate Identity Contract

Requirements:

- Source identity must be unique across discovered adapters in one startup pass.

Validation outcomes:

- Invalid when two modules declare the same source identity.
- Runtime startup must fail fast for duplicate identity conflicts.

### 4) Startup Failure Contract

Requirements:

- Contract violations must halt registration before partial success.
- Failure diagnostics must identify module and source identity context where available.
- Failure reason must be actionable for remediation.

Validation outcomes:

- Invalid when startup continues with unresolved contract violations.
- Invalid when diagnostics omit module identity or violation reason.

### 5) Behavior Preservation Contract

Requirements:

- Existing active source adapters retain prior execution behavior.
- Scheduling and persistence semantics remain unchanged except registration composition path.

Validation outcomes:

- Invalid when existing source execution behavior changes without explicit feature scope expansion.
- Invalid when schedule authority behavior regresses as part of registration refactor.

## Non-Goals

- Redesigning source execution semantics.
- Changing schedule policy behavior.
- Introducing persistence model changes unrelated to registration composition.

## Evidence Expectations

Acceptance evidence should include:

- Discovery test showing valid adapter onboarding.
- Negative tests for malformed adapter and duplicate source identity.
- Smoke test confirming runtime wiring and workspace load.
- Runbook/onboarding docs reflecting no manual runtime bootstrap wiring requirement.
