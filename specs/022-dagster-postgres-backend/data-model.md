# Data Model: Dagster Metadata Postgres Migration

## Overview

This feature introduces and formalizes local runtime entities for orchestration metadata persistence using PostgreSQL while preserving the existing canonical output data store.

## Entities

### 1. OrchestrationMetadataDatabase

- Description: Dedicated local persistence boundary for Dagster control-plane state.
- Fields:
  - role_name (string, required): Identifier for metadata database role.
  - host (string, required)
  - port (integer, required)
  - database_name (string, required)
  - username (string, required)
  - password_source (enum, required): env_file or environment.
  - readiness_status (enum): unknown, ready, unreachable.
- Validation rules:
  - Connection attributes must be complete at runtime.
  - Role must be distinct from canonical output data role.
  - Unreachable status blocks orchestration readiness.

### 2. CanonicalOutputDatabase

- Description: Existing local persistence boundary for dataset entities and observations.
- Fields:
  - role_name (string, required)
  - host (string, required)
  - port (integer, required)
  - database_name (string, required)
  - readiness_status (enum): unknown, ready, unreachable.
- Validation rules:
  - Must remain independently reachable and operational after metadata-store migration.
  - Must not be overwritten or repurposed by orchestration metadata configuration.

### 3. DagsterStorageConfiguration

- Description: Runtime configuration mapping Dagster metadata responsibilities to PostgreSQL backend.
- Fields:
  - run_storage_target (string, required)
  - event_log_storage_target (string, required)
  - schedule_storage_target (string, required)
  - fallback_mode (enum, required): disabled.
  - validation_state (enum): valid, invalid.
- Validation rules:
  - All storage targets must resolve to the orchestration metadata database role.
  - Fallback mode must remain disabled for missing credentials/configuration.

### 4. LocalStackReadinessCheck

- Description: Executable verification record for startup and post-start checks.
- Fields:
  - check_name (string, required)
  - target (enum, required): orchestration_metadata_db, canonical_output_db, dagster_runtime.
  - result (enum, required): pass, fail.
  - timestamp (datetime, required)
  - diagnostic_message (string, optional)
- Validation rules:
  - Failing orchestration metadata checks block orchestration-ready status.
  - Diagnostic message must be present for failures.

### 5. ConcurrencyValidationRun

- Description: Repeated local run execution used to validate metadata persistence reliability.
- Fields:
  - run_id (string, required)
  - attempt_number (integer, required)
  - terminal_status (enum, required): success, failure, canceled.
  - lock_error_detected (boolean, required)
  - metadata_events_recorded (integer, required)
- Validation rules:
  - lock_error_detected must be false for successful acceptance runs.
  - metadata_events_recorded must be greater than zero for completed runs.

## Relationships

- DagsterStorageConfiguration maps 1-to-1 to OrchestrationMetadataDatabase.
- LocalStackReadinessCheck validates both OrchestrationMetadataDatabase and CanonicalOutputDatabase independently.
- ConcurrencyValidationRun depends on valid DagsterStorageConfiguration and successful OrchestrationMetadataDatabase connectivity.

## State Transitions

### Orchestration metadata readiness lifecycle

1. unconfigured: runtime settings incomplete.
2. configured: runtime settings resolved.
3. ready: connectivity and startup checks pass.
4. degraded: connectivity lost after ready state.
5. failed: startup/runtime blocked due to invalid or unreachable metadata database.

### Concurrency validation lifecycle

1. planned: workload and attempts defined.
2. running: concurrent runs actively executing.
3. passed: required attempts complete with no lock-protocol errors.
4. failed: one or more attempts detect lock-protocol or metadata persistence failure.
