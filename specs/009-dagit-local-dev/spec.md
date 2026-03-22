# Feature Specification: Local Dagit Access

**Feature Branch**: `009-dagit-local-dev`  
**Created**: 2026-03-22  
**Status**: Draft  
**Input**: User description: "setting up dagit. We'll focus on local dev for now as deployment code has not been written for any infra yet. The goal is to be able to start up dagit and view our existing implementation in the UI."

## User Scenarios & Testing _(mandatory)_

### User Story 1 - Launch Dagit Locally (Priority: P1)

As a developer, I can start the local orchestration UI from the repository and see that it is available in a browser so I can inspect pipeline assets and jobs without manual backend probing.

**Why this priority**: If local UI startup fails, the feature provides no usable value and blocks all remaining workflow improvements.

**Independent Test**: Can be fully tested by running the documented startup command in a fresh local environment and confirming the UI is reachable and responsive.

**Acceptance Scenarios**:

1. **Given** a developer has the local prerequisites installed, **When** they run the documented startup workflow, **Then** the UI starts successfully without requiring undocumented steps.
2. **Given** the UI startup is complete, **When** the developer opens the local UI endpoint, **Then** the main page loads and confirms the workspace is available.

---

### User Story 2 - View Existing Definitions (Priority: P2)

As a developer, I can see the project's current orchestrated definitions in the UI so I can verify that the local setup is pointed at the existing implementation.

**Why this priority**: Visibility into existing definitions is the core reason to run the UI, but it depends on startup capability.

**Independent Test**: Can be fully tested by opening the UI and confirming known existing definitions appear with expected names and navigation.

**Acceptance Scenarios**:

1. **Given** the local UI is running, **When** the developer views the definitions landing page, **Then** existing jobs/assets/schedules for the repository are listed.
2. **Given** definitions are listed, **When** the developer opens a definition detail view, **Then** metadata and related links are displayed without runtime errors.

---

### User Story 3 - Troubleshoot Common Local Failures (Priority: P3)

As a developer, I can follow documented troubleshooting steps for common startup failures so I can recover quickly without ad hoc team support.

**Why this priority**: Troubleshooting guidance reduces onboarding friction and repeated interruptions, but only after baseline startup and visibility work.

**Independent Test**: Can be fully tested by simulating common failure states and confirming documentation provides actionable recovery steps that restore local UI access.

**Acceptance Scenarios**:

1. **Given** startup fails due to a known local precondition issue, **When** the developer follows the runbook guidance, **Then** they can complete recovery and relaunch the UI.

### Edge Cases

- The local startup command is run from an incorrect working directory.
- The configured local endpoint is already in use by another process.
- The local environment can start the UI process, but no definitions are loaded due to workspace misconfiguration.
- Startup prerequisites are partially installed, causing non-obvious errors during launch.

## Requirements _(mandatory)_

### Functional Requirements

- **FR-001**: The feature MUST provide a single documented local startup path that enables developers to launch the orchestration UI from this repository.
- **FR-002**: The startup path MUST be repeatable across developer machines that satisfy documented prerequisites.
- **FR-003**: The local UI session MUST load the repository's existing orchestration definitions that are already implemented.
- **FR-004**: Developers MUST be able to access a local browser endpoint and navigate from the landing page to at least one definition detail view.
- **FR-005**: The feature MUST include explicit local-only scope boundaries and state that deployment/infrastructure rollout is out of scope for this feature.
- **FR-006**: The feature MUST provide troubleshooting guidance for at least the documented common failure modes in local startup and definition loading.
- **FR-007**: The feature MUST define a verification flow that confirms all of the following: (a) local UI endpoint is reachable, (b) at least one existing definition is visible in listing views, and (c) at least one definition detail view opens successfully.

### Key Entities _(include if feature involves data)_

- **Local UI Session**: A developer-initiated local runtime session that exposes the orchestration interface and serves workspace pages.
- **Workspace Definition Catalog**: The set of existing repository orchestration definitions expected to appear in the UI, including navigable summary and detail views.
- **Startup Verification Result**: A pass/fail outcome produced by the local verification flow with enough information to confirm readiness or identify common failures.

## Assumptions

- Developers have access to the existing repository code and local development prerequisites documented by the project.
- Existing orchestration definitions are valid and intended to be visible in a local UI without requiring new business logic.
- Authentication and remote multi-user access controls are not required for this local development phase.
- Deployment automation and infrastructure provisioning will be addressed in a future feature.

## Success Criteria _(mandatory)_

### Measurable Outcomes

- **SC-001**: 100% of developers following the documented local startup path can reach the UI landing page in 10 minutes or less on a correctly prepared machine.
- **SC-002**: 100% of local verification runs confirm that at least one known existing definition is visible in the UI after startup.
- **SC-003**: At least 90% of simulated common local startup issues are resolved by following documented troubleshooting steps without direct teammate assistance.
- **SC-004**: During feature acceptance, developers can complete the end-to-end flow (start UI, view definitions, open one detail page) in a single uninterrupted attempt.

## Constitution Alignment _(mandatory)_

- **CA-001 Quality Gates**: Feature can satisfy linting, formatting, type checking, and automated test gates without suppressions, bypasses, or workaround-only code. (Yes)
- **CA-002 Coverage**: Feature includes tests to keep backend/frontend coverage at or above 90% in affected projects. (Yes)
- **CA-003 Local Stack**: Feature is runnable in the unified local Docker Compose stack, or explicitly lists compose updates needed. (Yes)
- **CA-004 Contracts and Data Integrity**: Data/interface contract changes, provenance/timestamp impacts, and trend-alert reliability safeguards are defined. (Yes)
- **CA-005 Documentation Fidelity**: Relevant documentation is identified and will be created or updated in the same change for any impacted behavior, contracts, setup, or runbooks, including AGENTS.md when repository structure/workflows/tooling change. (Yes)
