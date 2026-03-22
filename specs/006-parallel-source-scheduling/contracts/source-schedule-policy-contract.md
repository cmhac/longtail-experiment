# Contract: Source Schedule Policy

## Purpose

Define the stable policy contract used to determine whether a source is due for scheduled execution.

## Policy Fields

- sourceKey: Stable unique source identifier
- cadenceType: One of hourly, daily, weekly, monthly, custom_interval
- cadenceValue: Positive integer required when cadenceType is custom_interval
- timezone: Timezone identifier for cadence boundary evaluation
- isActive: Boolean indicating scheduler participation
- lastSuccessfulAt: Timestamp of most recent successful source execution
- nextEligibleAt: Computed timestamp for next due execution
- priorityClass: Optional priority class for backlog fairness policy

## Validation Rules

1. sourceKey MUST match a registered source workflow key.
2. cadenceType MUST be one of the allowed values.
3. cadenceValue MUST be present and > 0 for custom_interval.
4. nextEligibleAt MUST NOT precede lastSuccessfulAt.
5. inactive sources MUST be excluded from scheduled execution.

## Eligibility Evaluation Output

For each evaluated source, the policy contract MUST produce:

- eligibilityState: due, not_due, skipped_inactive, skipped_invalid_policy
- evaluatedAt: Timestamp of evaluation
- reasonCode: Normalized reason for inclusion/exclusion
- selectedForExecution: Boolean

## Compatibility Requirements

- Unknown cadenceType values MUST be treated as invalid policy state.
- Policy defaults MUST never silently promote invalid source entries to due.
- Policy field additions MUST remain backward compatible for existing source registrations.
