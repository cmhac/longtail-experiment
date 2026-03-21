# Contract: Source Workflow Registration and Execution

## Purpose

Define the bounded contract for adding source-specific ingest workflows without modifying existing workflow implementations.

## Version

- Contract: source-workflow
- Version: v1
- Status: Draft for implementation planning

## Registration Contract

Each source workflow registration MUST provide:

- workflowId
- sourceKey
- owner
- supportedTriggerModes
- expectedInputShape reference
- outputOutcomeShape reference
- status

## Input Contract

A source workflow execution request MUST include:

- runId
- sourceKey
- triggerType
- executionWindowStart
- executionWindowEnd
- runContext metadata

## Output Contract

A source workflow execution result MUST include:

- sourceKey
- status (success, partial_success, failure)
- acceptedCount
- quarantinedCount
- failedCount
- duplicateNoOpCount
- conflictCount
- optional message

## Behavioral Requirements

- Workflow execution MUST use shared canonical validation rules before persistence.
- Exact duplicate records for same series-period-value MUST be treated as no-op outcomes.
- Non-matching duplicates for same series-period MUST emit conflict outcomes and conflict persistence events.
- Workflow failure MUST not alter already persisted accepted outcomes from other source workflows.

## Validation Rules

- sourceKey MUST map to one active registration at run start.
- output counts MUST be non-negative integers.
- status MUST be consistent with count totals and terminal execution behavior.

## Compatibility and Evolution

- Input/output field additions are additive.
- Required field removals or semantic changes require contract version bump.
