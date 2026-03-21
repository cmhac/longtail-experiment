# Contract: Migration Readiness

## Purpose

Define deterministic migration application, failure handling, and revision verification behavior for local development.

## Required Behavior

- Migration command MUST apply revisions using one canonical shared-db migration path.
- Migration execution MUST fail fast at first error.
- Failure output MUST include actionable recovery guidance.
- Rerun MUST be explicit and developer-triggered.
- Status check MUST confirm observed revision equals expected latest revision.

## Failure Handling

- Partial migration state MUST be treated as non-ready until explicit rerun succeeds.
- Recovery guidance MUST include at minimum: how to inspect migration state, how to repair prerequisites, and how to rerun.

## Verification Outputs

- Migration apply command result.
- Revision status command result.
- Pass/fail readiness marker for local implementation start.

## Defect Remediation Scope

- All reproducible setup and migration defects discovered during this feature are in-scope fixes before completion.
- Each fix must include documentation updates and rerun verification evidence.

## Compatibility and Evolution

- New migration revisions must preserve deterministic local replay from a fresh database.
- Changes to failure semantics require updates to this contract and quickstart verification steps.
