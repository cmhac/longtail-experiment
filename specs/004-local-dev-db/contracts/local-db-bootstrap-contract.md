# Contract: Local DB Bootstrap

## Purpose

Define the required local database startup behavior and configuration expectations for development environments.

## Required Inputs

- Host, port, database name, username, and credential source for local database access.
- Explicit profile indicating development-local usage.
- Reset intent flag when developer requests destructive local reset.

## Required Behavior

- Startup flow MUST bring local database service to a healthy state and expose connectivity details.
- Persistence MUST be enabled by default across restarts.
- Reset MUST occur only when explicitly requested.
- Startup guidance MUST include development-only warning language.

## Validation Rules

- Missing required configuration inputs MUST fail startup with actionable message.
- Port conflicts MUST be surfaced with clear remediation steps.
- Health check output MUST indicate ready or not-ready state deterministically.

## Outputs

- Service status evidence from compose stack.
- Verified connection profile values for downstream migration flow.

## Compatibility and Evolution

- New local configuration fields must be additive and documented.
- Any change to default persistence semantics requires contract version note and quickstart update.
