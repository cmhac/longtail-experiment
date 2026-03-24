# Feature Specification: Self-Describing Source Adapters

**Feature Branch**: `020-self-describing-adapters`
**Created**: 2026-03-23
**Status**: Draft
**Input**: User description: "The ONLY thing required to onboard new sources is a single adapter module. No other files require editing. The adapter module itself is the complete registration unit."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Onboard a Source With No Edits Outside the Adapter (Priority: P1)

As a pipeline developer, I can create a single adapter module file and have the runtime automatically discover, register, schedule, and surface it in the operator UI — without editing any other file in the codebase.

**Why this priority**: This is the entire goal of the feature. Every other story depends on this being true. Currently onboarding requires touching five separate files; this reduces that to one.

**Independent Test**: Create a minimal but compliant adapter module under `apps/pipeline/src/orchestration/jobs/sources/`, start the runtime, and verify: (1) the source appears in the registered source catalog, (2) a schedule exists for it, (3) it is visible as an asset in the operator UI — without having touched any file other than the adapter module itself.

**Acceptance Scenarios**:

1. **Given** a compliant adapter module placed in the sources directory, **When** the pipeline runtime starts, **Then** the source is registered and executable without any additional wiring edits.
2. **Given** an adapter module that declares a cron cadence internally, **When** the runtime starts, **Then** a correctly configured schedule for that source exists and fires at the declared interval.
3. **Given** an adapter with multiple declared series, **When** the runtime starts, **Then** each series appears as a distinct operator-visible asset under the correct provider group.
4. **Given** no changes to `discovery.py`, `source_asset_schedules.py`, `source_asset_definitions.py`, `definitions.py`, or `runtime.py`, **When** a new adapter is added, **Then** all automated tests pass at the same level they did before the adapter was added.

---

### User Story 2 - Adapter Self-Description Is Validated at Startup (Priority: P2)

As a pipeline maintainer, I need the system to validate each adapter's self-declared metadata at startup and fail fast if it is incomplete or conflicting, so misconfigured adapters never silently enter production.

**Why this priority**: Without validation, the new zero-edit model is a footgun. Startup-time fail-fast with clear, module-scoped diagnostics is what makes the self-describing model trustworthy.

**Independent Test**: Introduce an adapter that is missing required metadata fields (e.g., no series declared, empty source key, duplicate source key) and verify the runtime halts with an actionable message that names the adapter file and the violated contract rule.

**Acceptance Scenarios**:

1. **Given** an adapter module missing required self-description fields, **When** the runtime starts, **Then** startup fails with a message identifying the adapter file and the missing field.
2. **Given** two adapter modules that declare the same source key, **When** the runtime starts, **Then** startup fails and names both conflicting adapter files.
3. **Given** an adapter with valid self-description, **When** the runtime starts, **Then** no validation error is raised and the source is registered normally.
4. **Given** repeated startups with the same set of valid adapters, **When** the runtime starts multiple times, **Then** registration order is identical every time.

---

### User Story 3 - Existing FRED Adapter Migrated to Self-Describing Format (Priority: P3)

As a pipeline developer, the existing FRED adapter serves as the reference implementation of the new self-describing format, so I have a concrete, working example to follow when onboarding new providers.

**Why this priority**: Migration of the existing adapter proves the new model works end-to-end against a real adapter, and eliminates the last remaining manually-wired source. It also removes all hardcoded bootstrapping artifacts.

**Independent Test**: After migrating the FRED adapter and removing all manually-wired entries from the five previously-touched files, start the runtime and verify FRED ingest, scheduling, and operator visibility all continue to function exactly as before.

**Acceptance Scenarios**:

1. **Given** the FRED adapter migrated to self-describing format, **When** the runtime starts, **Then** FRED sources are registered, scheduled, and visible in the operator UI exactly as before migration.
2. **Given** the migration complete, **When** any of the previously hand-edited files (`discovery.py`, `source_asset_schedules.py`, `source_asset_definitions.py`, `definitions.py`, `runtime.py`) are inspected, **Then** they contain zero FRED-specific hardcoded entries.
3. **Given** all FRED-specific entries removed from the five files and moved into the adapter, **When** the full test suite runs, **Then** all tests pass without modification.

---

### Edge Cases

- An adapter module is present in the sources directory but does not export the required self-description attributes — startup must fail with a named diagnostic, not silently skip.
- Two adapter modules declare the same source key — startup must fail and name both conflicting files.
- An adapter module exports malformed metadata (e.g., empty series list, empty cron string) — startup must reject it with an actionable message.
- An adapter module that is a helper or utility (does not end in `_source.py`) must be ignored without error.
- An adapter declares zero series — this is a contract violation and must be rejected.
- An adapter's declared cron expression is syntactically invalid — startup must report the adapter file and the invalid cron string.
- The sources directory contains no adapter modules at all — runtime starts with zero registered sources and logs this condition without crashing.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST automatically discover, register, schedule, and surface any compliant adapter module placed under `apps/pipeline/src/orchestration/jobs/sources/` without requiring edits to any other file.
- **FR-002**: Adapter modules MUST be the complete and sole registration unit: they MUST declare all information needed for runtime registration, scheduling, and operator visibility internally.
- **FR-003**: The adapter module MUST declare: source key, provider group key, one or more series with their series item keys and canonical series keys, schedule cadence (cron expression and human label), and builder function — all in a machine-readable format that the runtime can read without being told what to expect.
- **FR-004**: The system MUST validate adapter self-description at startup and fail fast with a module-scoped, actionable error message for any adapter that violates the contract.
- **FR-005**: The system MUST reject duplicate source keys across adapters and name both conflicting modules in the failure message.
- **FR-006**: The system MUST continue to ignore non-adapter modules in the sources directory (files not ending in `_source.py`).
- **FR-007**: The system MUST derive Dagit asset definitions dynamically from adapter metadata so that operator-visible assets are created without hand-written per-series asset functions.
- **FR-008**: The system MUST derive schedule definitions dynamically from adapter metadata so that per-source schedules are created without hand-written schedule variables.
- **FR-009**: The system MUST preserve existing FRED source execution semantics, scheduling behavior, and persistence behavior exactly after migrating FRED to the self-describing format.
- **FR-010**: The system MUST register sources in deterministic order (alphabetical by source key) regardless of filesystem ordering.
- **FR-011**: All previously hand-edited registration files (`discovery.py`, `source_asset_schedules.py`, `source_asset_definitions.py`, `definitions.py`, `runtime.py`) MUST contain zero source-specific hardcoded entries after this feature is complete. Any source-specific content in those files is a defect.
- **FR-012**: Documentation (`docs/runbooks/provider-onboarding.md`, `docs/runbooks/local-stack-baseline.md`, `AGENTS.md`) and the `onboard-provider` agent skill MUST be updated to reflect the new single-file onboarding model.
- **FR-013**: The system MUST update or remove the `WORKSPACE_DEFINITION_CATALOG` smoke check in `definitions.py` so it derives expected catalog entries from registered adapters rather than a hardcoded tuple.
- **FR-014**: The system MUST update or remove the `EXPECTED_RUNTIME_SOURCE_KEYS` constant in `runtime.py` so it derives expected keys from registered adapters rather than a hardcoded tuple.
- **FR-015**: The system MUST include an automated guard test that fails when any source-specific hardcoded onboarding entry appears in `discovery.py`, `source_asset_schedules.py`, `source_asset_definitions.py`, `definitions.py`, or `runtime.py`.
- **FR-016**: Adapter manifest validation MUST reject syntactically invalid cron expressions and include both module identity and invalid cron value in the startup error message.

### Key Entities

- **Adapter Module**: A `*_source.py` file that is the sole and complete definition of a source. Declares its own source key, provider group, series list, cadence, and builder. Is the only file a developer creates to onboard a new source.
- **Adapter Manifest**: The machine-readable self-description exported by an adapter module. Contains all registration, scheduling, and visibility metadata needed by the runtime.
- **Self-Describing Discovery**: The mechanism by which the runtime scans adapter modules, reads their manifests, and assembles registration, schedule, and asset definitions automatically.
- **Bootstrap Artifact**: Any hardcoded, source-specific entry in a non-adapter file that must be manually added when onboarding a source. All bootstrap artifacts are eliminated by this feature.

### Assumptions

- The sources directory path (`apps/pipeline/src/orchestration/jobs/sources/`) is stable and does not change as part of this feature.
- The Dagster `@asset` decorator model supports programmatic/dynamic asset creation from metadata, or an equivalent mechanism exists (e.g., factory functions that generate asset objects from a list).
- The Dagster schedule model supports programmatic schedule generation from a list of metadata records.
- Existing test assertions that hardcode expected source keys, asset names, or schedule names will need to be updated to derive expectations from the registered adapter catalog — this is an acceptable and expected part of the migration.
- The `ownership_mode` concept (grouped vs. split) is preserved; adapters declare it as part of their manifest.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: Onboarding a new source requires creating exactly one new file and zero edits to any existing file, verified across 100% of new-provider onboarding attempts.
- **SC-002**: All five previously manually-edited registration surfaces contain zero source-specific hardcoded entries after migration, verified by automated test.
- **SC-003**: Startup validation catches 100% of missing-required-field and duplicate-source-key violations with actionable module-named diagnostics, verified by negative-path tests.
- **SC-004**: FRED ingest, scheduling, and operator visibility behavior is identical before and after migration, verified by the existing test suite passing without modification to test assertions.
- **SC-005**: Registration order is identical across 10 repeated runtime startups with the same adapter set, verified by determinism test.
- **SC-006**: The provider onboarding and local-stack runbooks describe the new single-file model accurately, and a developer following them can onboard a new source without consulting any other documentation.
- **SC-007**: Automated anti-hardcoding guard tests fail on every intentionally injected bootstrap artifact in the five target files and pass when no artifacts are present.
- **SC-008**: Cron syntax validation rejects 100% of invalid manifest cron expressions with module-scoped diagnostics, verified by negative-path tests.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and automated test gates without suppressions, bypasses, or workaround-only code, and the full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or above 90% in affected projects, and can satisfy the commit-time coverage stop rule (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack. No new compose services are required. (Yes)
- **CA-004 Contracts and Data Integrity**: This feature changes registration and wiring composition only. No canonical observation schema, persistence contracts, or data provenance logic changes. (Yes)
- **CA-005 Documentation Fidelity**: `docs/runbooks/provider-onboarding.md`, `docs/runbooks/local-stack-baseline.md`, `AGENTS.md`, and `.agents/skills/onboard-provider/SKILL.md` are all updated in the same change to reflect the new single-file onboarding model. (Yes)
