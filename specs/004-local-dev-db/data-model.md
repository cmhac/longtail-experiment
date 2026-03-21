# Data Model: Local Development Database Readiness

## Entity: LocalDatabaseProfile

- Description: Configuration model defining how developers connect to and run the local database service.
- Fields:
  - profileName: identifier for the local profile (default `local-dev-db`)
  - host: hostname used by local services
  - port: exposed local database port
  - databaseName: target development database name
  - username: development database username
  - passwordSource: location of credential value used for local setup
  - persistenceMode: persistent-by-default setting plus explicit reset trigger
  - warningScope: explicit text describing development-only intended use
- Validation rules:
  - host and port MUST resolve to reachable local service endpoint.
  - databaseName, username, and passwordSource MUST be defined before migration commands run.
  - persistenceMode MUST default to persistent and document explicit reset path.

## Entity: MigrationBaselineState

- Description: Verification model representing expected and observed schema revision state for a local database.
- Fields:
  - expectedRevision: revision identifier required by current codebase
  - observedRevision: revision identifier detected after migration command execution
  - migrationCommand: canonical command used to apply revisions
  - statusCommand: canonical command used to read current revision
  - verificationTimestamp: time at which revision status is validated
  - outcome: success or failure state with reason code
- Validation rules:
  - observedRevision MUST equal expectedRevision for readiness success.
  - outcome MUST be failure when migration command exits non-zero.
  - statusCommand output MUST be captured for defect diagnosis on failure.

## Entity: SetupDefectRecord

- Description: Structured capture of each reproducible local setup defect discovered during implementation.
- Fields:
  - defectId: unique identifier for traceability
  - symptom: concise failure description seen by developers
  - triggerConditions: minimal reproducible preconditions
  - affectedFlow: setup, migration, verification, or reset path
  - severity: informational classification for reporting only (not for deferral)
  - rootCauseSummary: short explanation of why the defect occurs
  - fixSummary: implemented correction behavior
  - documentationUpdates: docs updated to reflect corrected behavior
  - verificationEvidence: command outputs confirming resolution
  - resolvedAt: timestamp of confirmed fix validation
- Validation rules:
  - Every reproducible defect MUST have rootCauseSummary, fixSummary, and verificationEvidence.
  - Defect records MUST be marked resolved before feature completion.

## Entity: ReadinessVerificationResult

- Description: Aggregated local-dev readiness evidence for one validation run.
- Fields:
  - setupStatus: startup and connectivity result
  - migrationApplyStatus: migration command result
  - migrationRevisionStatus: revision alignment result
  - qualityGateStatus: combined affected quality command status
  - stackHealthStatus: compose stack health result
  - runDuration: total verification duration
  - notes: additional context for failures or retries
- Validation rules:
  - Overall result is successful only when all component statuses are successful.
  - Failed component statuses MUST include actionable notes.

## State Transitions

- LocalDatabaseProfile:
  - Unconfigured -> Configured -> Running -> ResetRequested -> Running
- MigrationBaselineState:
  - Unknown -> Applying -> Verified
  - Unknown -> Applying -> Failed -> Retrying -> Verified
- SetupDefectRecord:
  - Discovered -> Reproduced -> Fixed -> Verified -> Closed
- ReadinessVerificationResult:
  - Started -> InProgress -> Passed
  - Started -> InProgress -> Failed -> Retried -> Passed
