# Research: Local Dagit Access

**Feature**: 009-dagit-local-dev  
**Date**: 2026-03-22

## Decision Log

### Decision 1: Use the existing pipeline definitions module as the UI workspace source

**Decision**: Configure local Dagit startup against the repository's existing orchestration definitions entrypoint rather than creating a parallel example workspace.

**Rationale**: The feature goal is to view the current implementation in the UI, so startup must point to the same definitions developers already maintain.

**Alternatives considered**:

- Create a minimal demo workspace for Dagit: rejected because it does not prove visibility of real repository definitions.
- Load definitions dynamically from ad hoc scripts: rejected due to added startup ambiguity and weaker reproducibility.

---

### Decision 2: Keep feature scope local-only and explicitly exclude infrastructure deployment

**Decision**: Constrain this feature to local startup, local verification, and local troubleshooting; do not design deployment or infrastructure automation in this phase.

**Rationale**: The user explicitly requested local development focus because deployment code has not been authored yet.

**Alternatives considered**:

- Include optional deployment design notes now: rejected because it expands scope and creates non-actionable acceptance criteria for this feature.
- Add provisional infrastructure stubs: rejected due to likely churn before deployment requirements are defined.

---

### Decision 3: Define repeatable startup and verification as operator contract outcomes

**Decision**: Treat startup command execution, UI endpoint reachability, and definition visibility checks as explicit acceptance contract outcomes.

**Rationale**: Repeatability and visibility are the business outcomes for this feature, and they can be validated independently from deeper orchestration functionality.

**Alternatives considered**:

- Rely only on process-start success logs: rejected because process health alone does not confirm UI usability or definitions visibility.
- Verify only manual UI clicks without a written flow: rejected because it is non-repeatable and harder to troubleshoot.

---

### Decision 4: Prioritize troubleshooting for known local failure classes

**Decision**: Document remediation paths for missing prerequisites, occupied ports, workspace loading failures, and partial local environment setup.

**Rationale**: These failure classes directly map to the edge cases in the specification and are common blockers for local onboarding.

**Alternatives considered**:

- Document only a happy-path startup sequence: rejected because it shifts recovery burden to ad hoc team support.
- Add broad low-probability diagnostics matrix: rejected because it introduces maintenance overhead with low near-term value.

---

### Decision 5: Preserve existing quality gates and add targeted test coverage

**Decision**: Reuse established pipeline/orchestration tests and quality commands, adding only targeted checks needed to verify Dagit startup wiring and definition visibility.

**Rationale**: Maintains constitution quality standards while minimizing unnecessary test surface expansion.

**Alternatives considered**:

- Introduce a dedicated standalone Dagit test suite: rejected because it duplicates existing orchestration coverage and increases maintenance cost.
- Skip automated checks and rely on manual validation: rejected due to coverage and reliability constraints.
