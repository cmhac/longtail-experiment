# Data Model: Source-Per-Asset Migration

**Feature**: 010-source-asset-migration

## Entities

### SourceAssetRegistration

Represents a source module registered as a first-class orchestration asset.

| Field               | Type     | Required | Notes                                                          |
| ------------------- | -------- | -------- | -------------------------------------------------------------- |
| source_key          | string   | Yes      | Unique source identity used for trigger and schedule targeting |
| asset_key           | string   | Yes      | Asset identity mapped from source key                          |
| module_name         | string   | Yes      | Module providing source registration contract                  |
| registration_status | enum     | Yes      | pending, active, invalid, duplicate_rejected                   |
| validation_error    | string   | No       | Present when registration fails contract validation            |
| discovered_at       | datetime | Yes      | Discovery timestamp for deterministic startup audit            |

Validation rules:

- source_key must be globally unique within active registrations.
- registration_status=active requires no validation_error.
- registration_status=invalid or duplicate_rejected requires validation_error.

---

### SchedulingAuthorityState

Captures whether scheduling decisions are exclusively controlled by Dagster-native automation.

| Field                 | Type     | Required | Notes                                                             |
| --------------------- | -------- | -------- | ----------------------------------------------------------------- |
| state_id              | string   | Yes      | Identifier for authority state record                             |
| authority_mode        | enum     | Yes      | dagster_only or transitional                                      |
| cutover_completed_at  | datetime | No       | Populated when authority_mode becomes dagster_only                |
| legacy_paths_disabled | boolean  | Yes      | True when legacy scheduler/coordinator cadence paths are disabled |
| partial_failure_mode  | boolean  | Yes      | True if one or more sources failed in cutover window              |

Validation rules:

- authority_mode=dagster_only requires legacy_paths_disabled=true.
- cutover_completed_at is required when authority_mode=dagster_only.

---

### SourceRunOutcomeView

Operationally visible outcome record for a source run after cutover.

| Field            | Type     | Required | Notes                                           |
| ---------------- | -------- | -------- | ----------------------------------------------- |
| run_id           | string   | Yes      | Parent ingest run identifier                    |
| source_key       | string   | Yes      | Source that executed                            |
| execution_status | enum     | Yes      | succeeded, failed, deferred, locked             |
| triggered_by     | enum     | Yes      | manual or schedule                              |
| started_at       | datetime | Yes      | Execution start timestamp                       |
| finished_at      | datetime | No       | Present for terminal states                     |
| failure_summary  | string   | No       | Present when execution_status=failed            |
| visible_in_dagit | boolean  | Yes      | Indicates source-level outcome is visible in UI |

Validation rules:

- execution_status=failed requires failure_summary.
- visible_in_dagit must be true for acceptance success records.
- triggered_by=schedule is valid only when SchedulingAuthorityState.authority_mode=dagster_only after cutover.

---

### CutoverReadinessGate

Represents one decision checkpoint before one-time cutover execution.

| Field                          | Type     | Required | Notes                                                   |
| ------------------------------ | -------- | -------- | ------------------------------------------------------- |
| gate_id                        | string   | Yes      | Identifier for a cutover gate evaluation                |
| evaluated_at                   | datetime | Yes      | Evaluation timestamp                                    |
| registration_validation_passed | boolean  | Yes      | All candidate sources pass registration contract checks |
| schedule_exclusivity_verified  | boolean  | Yes      | No non-Dagster schedule path remains executable         |
| regression_suite_passed        | boolean  | Yes      | Required orchestration regression set passes            |
| go_live_decision               | enum     | Yes      | go or hold                                              |

Validation rules:

- go_live_decision=go requires all three booleans true.
- hold requires at least one boolean false and a remediation note in planning artifacts.

## Relationships

1. One SourceAssetRegistration corresponds to one logical source_key and one asset_key.
2. One SchedulingAuthorityState governs all SourceRunOutcomeView records for a runtime epoch.
3. One CutoverReadinessGate snapshot determines whether SchedulingAuthorityState may transition to dagster_only.
4. One run_id may map to multiple SourceRunOutcomeView records when multiple source assets execute in a release window.

## State Transitions

1. SourceAssetRegistration transitions pending -> active, invalid, or duplicate_rejected at startup.
2. SchedulingAuthorityState transitions transitional -> dagster_only during the release window cutover.
3. SourceRunOutcomeView transitions among succeeded, failed, deferred, or locked based on runtime execution semantics.
4. CutoverReadinessGate ends as go or hold per gate evaluation results.
