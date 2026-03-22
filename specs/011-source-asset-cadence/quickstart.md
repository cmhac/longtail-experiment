# Quickstart: Per-Source Asset Cadence

## Goal

Validate hard-cutover behavior where each source asset owns its cadence and no shared all-source schedule remains active.

## Prerequisites

- Workspace dependencies installed.
- Local runtime database available through the repository compose stack.
- Environment variables configured for active sources.

## 1. Baseline Quality Checks

1. Run affected lint checks.
2. Run affected type-checks.
3. Run affected tests for pipeline and db projects.

## 2. Local Stack Verification

1. Start local compose stack.
2. Confirm orchestration services are healthy.
3. Confirm Dagit endpoint is reachable.

## 3. Schedule Ownership Validation

1. Open Dagit deployment and catalog views.
2. Verify each active source asset appears in catalog.
3. Verify schedule definitions are source-specific and there is no shared all-source scheduled trigger.

## 4. Trigger Attribution Validation

1. Execute at least one scheduled run window for each in-scope source cadence.
2. Verify each run record includes source-level trigger attribution.
3. Verify no runs are attributed to legacy shared-cadence ownership.

## 5. On-Demand Compatibility Validation

1. Trigger on-demand execution for a specific source asset.
2. Verify source executes successfully independent of scheduled cadence timing.
3. Verify run visibility remains intact for source-level outcomes.

## 6. Legacy Artifact Interpretation Check

1. Query historical scheduling artifacts retained from pre-cutover behavior.
2. Confirm documentation and runtime behavior treat these artifacts as historical context only.
3. Confirm they do not affect active scheduled execution decisions.

## 7. Completion Criteria

- All in-scope source assets have independent schedule ownership.
- No active shared all-source schedule path exists.
- Source-level trigger attribution and run outcomes remain operator-visible.
- Quality gates pass with no suppressions or bypasses.
