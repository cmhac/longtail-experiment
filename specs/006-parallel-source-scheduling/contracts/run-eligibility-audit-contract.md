# Contract: Run Eligibility and Outcome Audit

## Purpose

Define persisted run-level and source-level audit data required for operator visibility.

## Persisted Run Summary Fields

- runId
- triggerType
- startedAt
- completedAt
- outcomeState
- dueSourceCount
- executedSourceCount
- deferredSourceCount
- notDueSourceCount
- failedSourceCount

## Persisted Per-Source Eligibility Fields

- runId
- sourceKey
- eligibilityState: due, not_due, skipped_inactive, skipped_invalid_policy
- reasonCode
- evaluatedAt
- selectedForExecution

## Persisted Per-Source Outcome Fields

- runId
- sourceKey
- state: success, partial_success, failure, deferred, not_due
- acceptedCount
- quarantinedCount
- failedCount
- duplicateNoOpCount
- conflictCount
- message
- outcomeReasonCode

## Audit Guarantees

1. Every registered source evaluated for a run MUST have an eligibility record.
2. Every selected source MUST have one terminal source outcome record.
3. Every source not selected for execution MUST expose non-execution reason details.
4. Run aggregate counts MUST equal the sum of source-level classifications.

## Operator Query Expectations

- Operators MUST be able to answer all of the following from persisted records:
  - Was source X due in run Y?
  - If not executed, why not?
  - If executed, what terminal state and counts were produced?
  - Did bounded parallelism or overlap policy defer execution?
