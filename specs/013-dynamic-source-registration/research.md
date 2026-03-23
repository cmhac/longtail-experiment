# Research: Dynamic Source Workflow Registration

## Decision 1: Use deterministic discovery via central specification list

- Decision: Keep one central discovery entrypoint that iterates discoverable adapter specifications and registers workflows in stable source-key order.
- Rationale: This removes runtime bootstrap churn while preserving determinism and contract safety.
- Alternatives considered:
  - Fully implicit filesystem reflection only.
    - Rejected because contract drift and accidental module pickup are harder to govern.
  - Keep hard-coded runtime bootstrap imports.
    - Rejected because it scales poorly and creates frequent merge conflicts.

## Decision 2: Fail fast on contract violations with module-scoped diagnostics

- Decision: Invalid adapter registrations should halt startup and report module name, source key, and violation reason.
- Rationale: Silent skip behavior risks partially onboarded providers and hidden production drift.
- Alternatives considered:
  - Log-and-skip invalid modules.
    - Rejected because onboarding failures could go unnoticed until runtime incidents.
  - Generic startup failure without module context.
    - Rejected because it slows remediation and increases operator ambiguity.

## Decision 3: Treat duplicate source identity as a hard registration error

- Decision: Duplicate source keys are rejected before registry registration proceeds.
- Rationale: Duplicate source identity would create ambiguous ownership and non-deterministic execution targeting.
- Alternatives considered:
  - Last-write-wins registration.
    - Rejected because behavior depends on discovery order and is unsafe.
  - Keep both and namespace internally.
    - Rejected because it violates explicit source identity expectations.

## Decision 4: Define explicit non-adapter behavior

- Decision: Discovery should include only modules that satisfy the adapter registration contract and ignore helper modules by design.
- Rationale: Source folders may contain utilities, constants, or shared helpers not meant for runtime registration.
- Alternatives considered:
  - Attempt to interpret every module as an adapter.
    - Rejected because helper modules would produce noisy failures.

## Decision 5: Preserve existing source behavior while changing only composition path

- Decision: Existing active adapters keep current execution and scheduling semantics; only registration composition becomes dynamic.
- Rationale: The issue scope is onboarding ergonomics and reliability, not workflow semantic changes.
- Alternatives considered:
  - Refactor execution semantics alongside registration changes.
    - Rejected because this broadens risk and confounds acceptance criteria.

## Decision 6: Validate onboarding via orchestration smoke and local Dagit checks

- Decision: Keep readiness validation focused on orchestration tests plus endpoint/workspace checks.
- Rationale: This aligns with current local-first process and verifies both runtime and operator visibility.
- Alternatives considered:
  - Unit-only validation.
    - Rejected because it misses integration wiring and workspace-load regressions.
