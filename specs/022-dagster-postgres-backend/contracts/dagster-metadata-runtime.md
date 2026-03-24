# Contract: Dagster Metadata Runtime (Local Stack)

## Interface Summary

- Interface type: Local runtime configuration and operational behavior contract
- Consumers: Pipeline developers, local-stack maintainers, verification scripts
- Providers: Docker Compose stack, Dagster runtime configuration, local runbooks/scripts

## Contract Surface

### Required runtime guarantees

1. Dagster run/event/schedule metadata persistence targets the dedicated orchestration metadata PostgreSQL role.
2. Canonical output data persistence remains mapped to its existing PostgreSQL role.
3. Orchestration startup/readiness is blocked when metadata database connectivity is missing or invalid.
4. Misconfiguration produces explicit hard failure diagnostics; no silent fallback to SQLite.

### Required configuration inputs

- Metadata database host
- Metadata database port
- Metadata database name
- Metadata database username
- Metadata database password (from configured secret source)

All required inputs must be available before orchestration services are considered ready.

## Behavioral Guarantees

1. Startup behavior is deterministic: valid configuration yields ready state, invalid configuration yields fail-fast state.
2. Metadata-store failures are observable through actionable diagnostics during startup or run launch.
3. Resetting metadata store is operationally separate from canonical output-data store reset workflows.
4. Concurrent run/event metadata writes do not rely on SQLite local file locking semantics.

## Validation Rules

- Metadata and output-data roles must be distinct logical database targets.
- Missing required metadata configuration values are contract violations.
- Readiness checks must independently verify both database roles.
- Runtime checks must reject fallback-to-default behavior for metadata persistence.

## Output Contract

### Success condition

- Local stack starts with both database roles healthy.
- Dagster run launches and run-log queries complete against PostgreSQL metadata backend.
- Concurrency validation shows no lock-protocol metadata persistence failures.

### Failure condition

- Service startup or run launch fails with explicit diagnostic reason when metadata connectivity/configuration is invalid.
- No partial-success orchestration state is reported.

### Diagnostic categories

- `metadata_config_missing`: required metadata DB inputs are missing.
- `endpoint_unavailable`: endpoint probe cannot reach Dagit.
- `workspace_load_failed`: Dagit endpoint is reachable but workspace load checks fail.

## Compatibility and Versioning

- Contract version: 1.0
- Backward compatibility requirement: Existing canonical output-data workflows continue to function without required behavior changes.
- Breaking changes to required inputs or readiness semantics must update runbooks and verification scripts in the same change.
