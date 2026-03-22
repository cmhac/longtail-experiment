# Contract: Local Dagit Operator Workflow

**Feature**: 009-dagit-local-dev  
**Audience**: Developers running local orchestration UI

## Purpose

Define the expected input, behavior, and outcomes for running Dagit locally to view existing repository definitions.

## Startup Input Contract

1. Developer runs the documented local startup command from repository root.
2. Local prerequisites are available (dependencies synced, local stack services required by definitions are healthy).
3. Required environment values for local orchestration are present.

## Startup Behavior Contract

1. Startup command begins a local UI runtime session.
2. The session exposes a local browser endpoint.
3. The workspace is loaded from existing repository definitions.
4. Startup emits developer-readable status indicating ready or failed.

## Visibility Contract

1. Landing page displays available definitions for current repository workspace.
2. Developer can navigate to at least one definition detail view.
3. Definition pages render without blocking runtime errors.

## Failure Contract

Failure outcomes MUST map to one of these categories with remediation guidance:

1. `prerequisite_missing`: local dependency, service, or configuration prerequisite is missing.
2. `endpoint_unavailable`: UI endpoint cannot be reached (for example, process failure or occupied port).
3. `workspace_load_failed`: Dagit starts but existing definitions are not loaded.
4. `partial_environment`: startup is attempted with only partially prepared local runtime.

Each failure category MUST include:

1. Observable symptom.
2. Likely root cause.
3. Recovery steps that can be executed locally.
4. Verification step confirming recovery.

## Verification Contract

A local run is considered successful only when all conditions are met:

1. Startup command completes with ready status.
2. Browser endpoint is reachable.
3. Existing definitions are visible in UI listing.
4. At least one definition detail view opens successfully.

## Out-of-Scope Contract

This feature does not define:

1. Cloud or hosted deployment workflows.
2. Infrastructure-as-code or deployment automation.
3. Production authentication and multi-tenant access patterns.
