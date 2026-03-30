# Feature Specification: Source Metadata and Adapter Relocation

**Feature Branch**: `038-source-metadata-relocation`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "Move provider adapter modules from apps/pipeline/src/orchestration/jobs/sources to apps/pipeline/src/sources, and add required human-readable source title and description fields to source specs that propagate through persistence, APIs, frontend, documentation, and onboarding skill guidance."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Find and Create Source Adapters Faster (Priority: P1)

A contributor adding or updating a source adapter can find the source-adapter area quickly in a shallower, easier-to-discover location and follow onboarding guidance without hunting through orchestration internals.

**Why this priority**: Faster discovery of the source-adapter area reduces onboarding friction for every future source change and lowers the chance of contributors editing the wrong area.

**Independent Test**: Can be fully tested by following the provider onboarding flow from repository root, generating a new source adapter, and confirming the generated adapter appears in the new source-adapter location and is discovered successfully without relying on the old nested directory.

**Acceptance Scenarios**:

1. **Given** a contributor follows provider onboarding guidance, **When** they create a new source adapter, **Then** the adapter is created in the new source-adapter location and the workflow remains discoverable.
2. **Given** a contributor browses the repository for existing source adapters, **When** they navigate to the documented source-adapter area, **Then** they find all maintained adapters in the new location without needing to inspect deep orchestration folders.

---

### User Story 2 - See Human-Readable Source Information Everywhere (Priority: P2)

An operator or discovery user can see a clear human-readable source name and description throughout the system instead of relying on internal source keys as the primary source identity.

**Why this priority**: Human-readable source information improves comprehension, trust, and usability across administrative and discovery surfaces.

**Independent Test**: Can be fully tested by ingesting records from a source with the new metadata and verifying that persisted source records, service responses, and user-facing screens show the source title and description consistently while preserving stable source-key identity behind the scenes.

**Acceptance Scenarios**:

1. **Given** a source adapter declares a title and description, **When** its records are ingested and queried, **Then** the source title and description are stored and returned alongside the source identity.
2. **Given** a user views source-backed content in the application, **When** source information is displayed, **Then** the user sees the source title and description rather than an internal key as the primary label.

---

### User Story 3 - Enforce Complete Source Metadata at Onboarding Time (Priority: P3)

A maintainer can rely on source metadata being complete and consistent because every source manifest must provide a title and description and the system rejects incomplete definitions.

**Why this priority**: Validation prevents incomplete source definitions from entering the system and avoids inconsistent naming or blank source metadata in downstream experiences.

**Independent Test**: Can be fully tested by attempting to register one source that includes the required metadata and one that omits it, then confirming the complete source succeeds and the incomplete source fails with an actionable validation error.

**Acceptance Scenarios**:

1. **Given** a source adapter omits the required title or description, **When** discovery or startup validation runs, **Then** the adapter is rejected with a clear error identifying the missing metadata.
2. **Given** existing sources are migrated to the new metadata requirements, **When** startup validation runs, **Then** all maintained sources continue to register successfully with complete source metadata.

### Edge Cases

- A source adapter is moved to the new location but stale documentation or tooling still points contributors to the retired nested path.
- A source manifest includes an internal key but leaves the title or description blank, whitespace-only, or otherwise unusable for display.
- Existing persisted source records predate the new metadata fields and must remain queryable during and after migration.
- A source title changes while the underlying source key remains stable, requiring display updates without changing source identity or breaking existing relationships.
- Backend and frontend surfaces receive mixed data during rollout, where some sources have migrated metadata and others have not yet been backfilled.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST treat the new source-adapter location as the standard home for maintained source adapter modules.
- **FR-002**: The provider onboarding flow MUST create new source adapters in the new source-adapter location.
- **FR-003**: Source discovery and runtime registration MUST continue to discover all valid source adapters after the location change without requiring per-source manual registration edits.
- **FR-004**: Contributor-facing onboarding and runbook guidance MUST identify the new source-adapter location as the standard place to add and maintain source adapters.
- **FR-005**: The onboarding skill used for provider implementation MUST instruct contributors and agents to use the new source-adapter location and updated onboarding flow.
- **FR-006**: Every source manifest MUST include a human-readable source title.
- **FR-007**: Every source manifest MUST include a human-readable source description.
- **FR-008**: Source discovery and validation MUST reject any source manifest that omits the required title or description, or provides an empty value for either field.
- **FR-009**: The system MUST preserve stable internal source-key identity for scheduling, ingestion, persistence, and traceability even when human-readable source metadata is added.
- **FR-010**: Persisted source records MUST store the source title and source description as first-class source-level metadata.
- **FR-011**: Existing persisted source records MUST be migrated or backfilled so maintained sources have complete title and description metadata after rollout.
- **FR-012**: Source-related service responses MUST expose source title and description wherever source information is returned today.
- **FR-013**: User-facing application surfaces that currently present source keys as source labels MUST instead use the human-readable source title as the primary label.
- **FR-014**: User-facing application surfaces that present source details MUST make the source description available when source context is shown.
- **FR-015**: The system MUST keep dataset and source relationships stable across the metadata rollout so existing links, filters, and lookups continue to resolve correctly.
- **FR-016**: Quality and regression coverage MUST verify the new source-adapter location, required source metadata validation, persisted source metadata availability, and user-facing display behavior.

### Assumptions

- Internal `source_key` values remain the canonical machine identity and are not replaced by titles.
- The source title and description are owned at the source level, not individually redefined per dataset.
- Existing maintained source adapters will all be updated in the same feature so fail-fast validation can become mandatory immediately after rollout.
- Source descriptions are short editorial summaries suitable for display in administrative and discovery contexts, not long-form documentation.

### Key Entities _(include if feature involves data)_

- **Source Manifest**: The contributor-authored source definition that declares source identity, scheduling metadata, ownership metadata, and the required human-readable title and description.
- **Source Profile**: The persisted source-level record that represents one source identity and stores its human-readable metadata for downstream query and display use.
- **Source Adapter Catalog**: The discoverable set of maintained source adapters used for onboarding, registration, scheduling, and operational visibility.
- **Source Presentation Payload**: Any service or application response that includes source information for operators or end users and must expose the source title and description.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In onboarding validation, contributors can locate the maintained source-adapter area and generate a new adapter in under 2 minutes without needing undocumented path discovery.
- **SC-002**: 100% of maintained source manifests include a non-empty source title and description after rollout, with incomplete manifests blocked from registration.
- **SC-003**: 100% of source-related user-facing surfaces audited in this feature show a human-readable source title as the primary source label instead of an internal source key.
- **SC-004**: 100% of maintained persisted source records include a populated source title and description after migration or backfill completes.
- **SC-005**: In regression validation, existing source-backed navigation and lookup flows continue to resolve correctly for all migrated sources with no loss of source-to-dataset traceability.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and
  automated test gates without suppressions, bypasses, or workaround-only code, and the
  full-suite stop rule (`pnpm exec nx run-many -t test --all`) can be satisfied before
  commit and before AI agent handoff/end of work. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or
  above 90% in affected projects, and can satisfy the commit-time coverage stop rule
  (`pnpm exec nx run-many -t coverage --all`). (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack,
  or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes,
  provenance/timestamp impacts, and trend-alert reliability safeguards are defined.
  (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be
  created or updated in the same change for any impacted behavior, contracts, setup, or
  runbooks, including AGENTS.md when repository structure/workflows/tooling change.
  (Yes)
- **CA-006 Configuration Integrity**: Any new service or pipeline component that requires
  credentials or external API keys will fail hard (exception/non-zero exit/job-level
  failure) when those variables are absent — no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
- **CA-007 Frontend UI System**: For frontend changes, the feature uses HeroUI
  components, Tailwind utilities, and shared abstractions in
  `apps/frontend/src/components` for repeated patterns; it does not introduce duplicate
  one-off component patterns or new local CSS without a documented exception.
  (Yes)
