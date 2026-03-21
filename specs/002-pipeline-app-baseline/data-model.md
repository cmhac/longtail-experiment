# Data Model: Pipeline App Baseline

## Entity: PipelineWorkspaceProject

- Description: Nx project node representing the new pipeline app.
- Fields:
  - id: unique workspace project identifier (string)
  - name: project name, fixed as pipeline (string)
  - rootPath: repository-relative project root (string)
  - sourceRoot: repository-relative source path (string)
  - targets: required quality/lifecycle targets (array of strings)
  - tags: ownership and boundary labels (array of strings)
- Validation rules:
  - name MUST be unique in workspace graph.
  - targets MUST include lint, format, typecheck, test, and coverage.
  - tags MUST distinguish pipeline ownership from backend/frontend boundaries.
- Relationships:
  - PipelineWorkspaceProject has one PipelineEnvironmentProfile.
  - PipelineWorkspaceProject has many PipelineQualityGateDefinitions.

## Entity: PipelineEnvironmentProfile

- Description: Baseline runtime and setup definition for pipeline contributors.
- Fields:
  - runtimeVersion: required Python version policy (string)
  - dependencyManager: uv (string)
  - lockfilePath: committed lockfile location (string)
  - setupCommands: ordered bootstrap commands (array of strings)
  - validationCommands: ordered quality verification commands (array of strings)
- Validation rules:
  - dependencyManager MUST be uv.
  - lockfilePath MUST be committed and reproducible.
  - validationCommands MUST map to all required quality gate categories.
- Relationships:
  - PipelineEnvironmentProfile belongs to one PipelineWorkspaceProject.

## Entity: PipelineQualityGateDefinition

- Description: Quality gate contract for pipeline app checks.
- Fields:
  - gateId: unique gate key (string)
  - category: lint | format | typecheck | test | coverage (enum)
  - command: canonical command text (string)
  - threshold: optional numeric threshold (number or null)
  - suppressionPolicy: forbidden | owner-approval-required (enum)
- Validation rules:
  - coverage threshold MUST be >= 90 when category is coverage.
  - suppressionPolicy MUST NOT allow permissive bypasses.
- Relationships:
  - PipelineQualityGateDefinition belongs to one PipelineWorkspaceProject.

## Entity: PipelineBackendHandoffContract

- Description: Baseline producer/consumer boundary between pipeline and backend.
- Fields:
  - producer: pipeline placeholder producer role (string)
  - consumer: backend placeholder consumer role (string)
  - handoffPurpose: defined integration purpose statement (string)
  - verificationSignals: startup/health and contract verification outcomes (array)
  - versioningPolicy: contract evolution policy (string)
- Validation rules:
  - producer MUST remain pipeline and consumer MUST remain backend.
  - contract versioning policy MUST be documented before interface changes.
- Relationships:
  - PipelineBackendHandoffContract is referenced by LocalStackThreeAppDefinition.

## Entity: LocalStackThreeAppDefinition

- Description: Unified local stack specification for pipeline, backend, and frontend.
- Fields:
  - composeFilePath: root compose file path (string)
  - services: list of placeholder services (array)
  - healthChecks: health criteria keyed by service (map)
  - startupCommand: canonical startup command (string)
  - shutdownCommand: canonical shutdown command (string)
  - servicePorts: baseline service port mapping (map)
- Validation rules:
  - services MUST include pipeline, backend, and frontend.
  - each service MUST have a health check.
  - startup and shutdown commands MUST be documented in quickstart.
  - servicePorts MUST map pipeline=8090, backend=8080, frontend=3000.

## State Transitions

- PipelineWorkspaceProject:
  - Draft -> Registered -> GateEnabled -> LocalStackWired
- PipelineQualityGateDefinition:
  - Defined -> EnforcedLocal -> EnforcedCI
- LocalStackThreeAppDefinition:
  - Draft -> Runnable -> HealthVerified
