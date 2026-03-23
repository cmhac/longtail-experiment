# Data Model: Dynamic Source Workflow Registration

## Overview

This feature introduces explicit registration-composition entities to support deterministic adapter onboarding and actionable startup failures.

## Entities

### 1) AdapterDiscoveryCandidate

Represents one discoverable module candidate evaluated for onboarding.

Fields:

- module_name: string (required)
- source_key: string (optional until resolved)
- status: enum { candidate, valid, ignored, invalid } (required)
- ignore_reason: string (optional)

Validation rules:

- module_name must be unique per discovery pass.
- status `valid` requires a resolvable registration contract payload.
- status `ignored` requires a non-empty ignore_reason.

Relationships:

- One AdapterDiscoveryCandidate may produce one SourceRegistrationContractResult.

### 2) SourceRegistrationContractResult

Represents contract-validation output for one candidate adapter.

Fields:

- module_name: string (required)
- source_key: string (required)
- is_valid: boolean (required)
- violation_reason: string (optional)

Validation rules:

- is_valid=false requires a non-empty violation_reason.
- is_valid=true requires non-empty source_key.

Relationships:

- One SourceRegistrationContractResult may produce one StartupRegistrationError when invalid.

### 3) RegistrationCatalogSnapshot

Represents the deterministic ordered set of source registrations presented to runtime.

Fields:

- source_keys: list[string] (required)
- ordering_rule: string (required)
- generated_at: timestamp (required)

Validation rules:

- source_keys must be unique.
- ordering_rule must match the implemented deterministic policy.

Relationships:

- Snapshot is consumed by runtime verification and smoke assertions.

### 4) StartupRegistrationError

Represents actionable startup failure details when registration cannot proceed.

Fields:

- module_name: string (required)
- source_key: string (optional)
- reason_code: string (required)
- reason_message: string (required)

Validation rules:

- reason_code must map to one contract rule class (invalid_contract, duplicate_source_key, inactive_registration, etc.).
- reason_message must be actionable and include module identity.

Relationships:

- Many StartupRegistrationError records can occur in one failed startup pass.

## State Transitions

### Discovery and registration lifecycle

1. candidate: module discovered and queued for evaluation.
2. valid: module satisfies registration contract.
3. ignored: module intentionally excluded by discovery rules.
4. invalid: module fails contract validation.
5. registered: valid module is accepted into runtime registry.
6. startup_failed: any invalid or duplicate condition blocks startup.

Transition constraints:

- `candidate -> registered` is allowed only via `valid`.
- `invalid` or duplicate identity transitions force `startup_failed`.
- `ignored` candidates cannot transition to `registered` in the same discovery pass.

## Invariants

- Registration order must be deterministic for identical candidate sets.
- Duplicate source keys are never allowed in the same catalog snapshot.
- Startup failure records must identify the exact failing module and rule.
- Existing active source identities remain stable across migration to discovery-based registration.
