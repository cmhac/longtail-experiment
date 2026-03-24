# Feature Specification: Provider Adapter Bootstrap Standard

**Feature Branch**: `021-bootstrap-provider-script`  
**Created**: 2026-03-24  
**Status**: Draft  
**Input**: User description: "we're going to create a script that bootstraps a new source provider script. it will create the general format of the source adapter, giving devs and coding agents a clean starting point in which to build their provider You may choose which templating tool to install and use for this. it should be wired up as a top level monorepo script in the root package.json. Before you write teh spec, to prepare, review the code linked below. then write the spec ... We should update the documentation to specify that using this script is THE standard way to create a new source adapter. And we should also update teh agent skill to direct agents to read the provider onboarding runbook doc AND to use this script to bootstarp their new provider adapter."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Generate A New Provider Scaffold (Priority: P1)

A pipeline developer starts a new ingestion provider and uses a single standard command to generate a ready-to-edit source adapter scaffold with the required structure and naming conventions.

**Why this priority**: Provider onboarding speed and consistency depend on having a reliable baseline artifact before any provider-specific logic is implemented.

**Independent Test**: Can be fully tested by running the bootstrap command in a clean branch and confirming a new provider adapter file is generated with the required sections and valid identifiers.

**Acceptance Scenarios**:

1. **Given** a developer wants to add a new provider, **When** they run the monorepo bootstrap command with required provider metadata, **Then** a new adapter scaffold is created in the expected source directory with required module exports and placeholder sections.
2. **Given** a requested adapter filename or source key already exists, **When** the bootstrap command is run, **Then** the command fails with an explicit collision message and does not overwrite existing files.

---

### User Story 2 - Enforce A Single Onboarding Standard (Priority: P2)

A maintainer relies on onboarding documentation that treats the bootstrap command as the required path for creating new source adapters, reducing drift across contributors.

**Why this priority**: Documentation determines team behavior and is critical for avoiding inconsistent adapter implementations.

**Independent Test**: Can be fully tested by reviewing runbook guidance to confirm manual bootstrapping instructions are replaced or reframed to require the script as the standard entry point.

**Acceptance Scenarios**:

1. **Given** onboarding documentation for providers, **When** a contributor follows it, **Then** they are instructed to use the bootstrap command as the standard first step before custom provider logic.

---

### User Story 3 - Guide Agent-Driven Onboarding (Priority: P3)

A coding agent executing provider onboarding follows skill instructions that require reading the provider onboarding runbook and using the bootstrap command before implementing provider-specific logic.

**Why this priority**: Agent behavior must align with human onboarding standards to keep generated changes consistent and reviewable.

**Independent Test**: Can be fully tested by inspecting skill guidance and confirming it explicitly requires both runbook review and bootstrap script usage during onboarding workflows.

**Acceptance Scenarios**:

1. **Given** an agent skill execution for provider onboarding, **When** the agent starts onboarding work, **Then** the skill instructs the agent to read the runbook and generate the adapter through the standard bootstrap command.

### Edge Cases

- Provider name, source key, or series identifiers include invalid characters or invalid casing.
- Requested output file path already exists from a previous attempt.
- Developer supplies only a subset of required metadata for a valid scaffold.
- Developer requests grouped multi-series setup but provides mismatched series and canonical key counts.
- Generated scaffold is created but cannot be discovered because filename suffix requirements are not satisfied.
- Command is invoked from a non-root working directory in the monorepo.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The system MUST provide a monorepo-level command to bootstrap a new source adapter scaffold from the repository root command interface.
- **FR-002**: The bootstrap command MUST generate a new adapter module file in the source adapter directory using the repository's required naming pattern for discoverable adapter modules.
- **FR-003**: The generated adapter scaffold MUST include all required structural sections needed to complete onboarding, including source key declaration, workflow builder function shell, source manifest declaration, and placeholder areas for series metadata and record mapping.
- **FR-004**: The bootstrap command MUST require core provider metadata inputs needed to create a valid scaffold and MUST reject execution when required inputs are missing.
- **FR-005**: The bootstrap command MUST validate user-provided identifiers and reject values that would violate repository naming conventions.
- **FR-006**: The bootstrap command MUST detect collisions with existing adapter module paths and existing source identities and MUST fail without overwriting files.
- **FR-007**: The generated scaffold MUST support both single-series and multi-series onboarding patterns through explicit scaffold sections that guide the correct workflow shape.
- **FR-008**: The command output MUST include a concise summary of what was generated and what the next onboarding steps are.
- **FR-009**: Root-level monorepo scripts documentation in package metadata MUST expose the bootstrap command so contributors can discover and execute it consistently.
- **FR-010**: Provider onboarding documentation MUST define the bootstrap command as the standard and required first step for creating new source adapters.
- **FR-011**: Provider onboarding documentation MUST describe how to continue from generated scaffold to provider-specific implementation and verification.
- **FR-012**: The agent onboarding skill for provider implementation MUST instruct agents to read the provider onboarding runbook before coding and to use the bootstrap command to create the adapter starting point.
- **FR-013**: The agent onboarding skill MUST prohibit manual adapter file creation as the default path unless the bootstrap command is unavailable and an explicit exception is documented in the task output.

### Assumptions

- The repository retains dynamic adapter discovery based on module naming and module-level source manifest exports.
- The bootstrap command is intended for contributor and agent usage in local development workflows, not as a production runtime dependency.
- The scaffold may include placeholders that require follow-up implementation, but generated files must be syntactically valid and discoverable.
- Existing provider adapters remain unchanged by this feature unless users intentionally regenerate or migrate them.

### Key Entities _(include if feature involves data)_

- **Provider Bootstrap Request**: Structured input for command execution, including provider identity, source identity, ownership mode intent, cadence metadata, and series declaration inputs.
- **Generated Adapter Scaffold**: The created adapter module containing required onboarding structure, placeholders, and metadata sections needed for subsequent provider-specific completion.
- **Onboarding Guidance Asset**: Runbook and skill instructions that define required onboarding sequence and standard command usage across human and agent contributors.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: In onboarding dry runs, contributors can generate a valid new provider scaffold in under 2 minutes from command invocation.
- **SC-002**: At least 95% of bootstrap command executions with valid inputs produce scaffolds that pass discovery naming and required-structure checks on the first attempt.
- **SC-003**: 100% of newly added provider adapters in subsequent onboarding workstreams are created through the standard bootstrap command path rather than manual initial file creation.
- **SC-004**: Reviewer-reported onboarding issues related to missing required adapter sections are reduced by at least 80% compared with the previous manual bootstrap baseline.

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
  failure) when those variables are absent - no soft outcome recording, no silent
  swallowing. `docker/compose/local.secrets.env` is declared as an `env_file` source
  for any Docker Compose service that requires secrets. (N/A)
