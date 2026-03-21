# Data Model: Initial Monorepo Baseline

## Entity: WorkspaceProject

- Description: Project node registered in the Nx workspace graph.
- Fields:
  - id: unique project identifier (string)
  - name: project name (string)
  - role: backend | frontend | quality-tooling | infra
  - rootPath: repository-relative root path (string)
  - sourceRoot: repository-relative source path (string)
  - targets: list of quality and lifecycle targets (array of strings)
  - tags: boundary and ownership tags (array of strings)
- Validation rules:
  - name MUST be unique in workspace graph.
  - rootPath MUST exist and map to exactly one project.
  - targets MUST include lint, format, typecheck, test, and coverage where applicable.
- Relationships:
  - WorkspaceProject has many QualityGateDefinitions.

## Entity: EnvironmentProfile

- Description: Tooling/runtime definition for a project role.
- Fields:
  - profileId: unique profile key (string)
  - projectRole: backend | frontend
  - runtime: runtime family and version policy (string)
  - dependencyManager: uv | pnpm
  - lockfilePath: lockfile location (string)
  - setupCommands: ordered setup commands (array of strings)
  - validationCommands: ordered validation commands (array of strings)
- Validation rules:
  - dependencyManager MUST match project role policy.
  - lockfilePath MUST be present and committed for reproducibility.
  - validationCommands MUST include lint, format, typecheck, and test.
- Relationships:
  - EnvironmentProfile belongs to one WorkspaceProject role template.

## Entity: QualityGateDefinition

- Description: Gate specification enforced in local checks and CI.
- Fields:
  - gateId: unique gate key (string)
  - category: lint | format | typecheck | test | coverage | duplication
  - command: canonical command string (string)
  - scope: backend | frontend | workspace
  - threshold: optional numeric threshold (number or null)
  - suppressionPolicy: forbidden | owner-approval-required
- Validation rules:
  - coverage gates MUST have threshold >= 90.
  - duplication gate MUST enforce minimumTokens = 50.
  - suppressionPolicy MUST NOT be permissive.
- Relationships:
  - QualityGateDefinition belongs to one or more WorkspaceProjects.

## Entity: DuplicationCheckConfig

- Description: PMD CPD configuration for cross-repo duplication checks.
- Fields:
  - toolVersion: pinned PMD version string
  - minimumTokens: integer threshold
  - includePaths: list of scanned source paths
  - excludePaths: list of excluded paths
  - installScriptPath: path to PMD installation script
  - runScriptPath: path to CPD execution script
- Validation rules:
  - minimumTokens MUST equal 50.
  - includePaths MUST cover both backend and frontend sources.
  - toolVersion MUST be pinned.

## Entity: LocalStackDefinition

- Description: Unified local stack contract for baseline startup.
- Fields:
  - composeFilePath: path to compose file
  - services: list of placeholder services
  - healthChecks: list of service health criteria
  - startupCommand: canonical startup command
  - shutdownCommand: canonical shutdown command
- Validation rules:
  - services MUST include backend and frontend placeholders.
  - all services MUST define health checks.
  - startup and shutdown commands MUST be documented in quickstart.

## State Transitions

- WorkspaceProject:
  - Draft -> Registered -> GateEnabled -> LocalStackWired
- QualityGateDefinition:
  - Defined -> EnforcedLocal -> EnforcedCI
- LocalStackDefinition:
  - Draft -> Runnable -> HealthVerified
