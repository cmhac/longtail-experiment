# Data Model: Local Dagit Access

**Feature**: 009-dagit-local-dev

## Entities

### LocalDagitSession

Represents one developer-initiated local Dagit runtime session.

| Field              | Type     | Required | Notes                                          |
| ------------------ | -------- | -------- | ---------------------------------------------- |
| `session_id`       | string   | Yes      | Stable identifier for one startup attempt      |
| `started_at`       | datetime | Yes      | Local time when startup begins                 |
| `status`           | enum     | Yes      | `starting`, `ready`, `failed`, `stopped`       |
| `endpoint`         | string   | Yes      | Local UI URL used for browser access           |
| `workspace_loaded` | boolean  | Yes      | Indicates whether definitions workspace loaded |
| `failure_reason`   | string   | No       | High-level startup failure classification      |

Validation rules:

- `endpoint` must be non-empty and reachable when `status=ready`.
- `workspace_loaded` must be true for acceptance success.
- `failure_reason` is required when `status=failed`.

---

### DefinitionVisibilitySnapshot

Captures what the developer can see in the local UI for existing definitions.

| Field                    | Type     | Required | Notes                                             |
| ------------------------ | -------- | -------- | ------------------------------------------------- |
| `snapshot_id`            | string   | Yes      | Identifier for one visibility check               |
| `session_id`             | string   | Yes      | Associated `LocalDagitSession`                    |
| `checked_at`             | datetime | Yes      | Time visibility check was run                     |
| `jobs_visible`           | integer  | Yes      | Count of listed jobs                              |
| `assets_visible`         | integer  | Yes      | Count of listed assets                            |
| `schedules_visible`      | integer  | Yes      | Count of listed schedules                         |
| `detail_view_accessible` | boolean  | Yes      | Whether at least one definition detail view opens |

Validation rules:

- At least one definition category count must be greater than zero for a valid existing-workspace visibility check.
- `detail_view_accessible` must be true for end-to-end acceptance.

---

### StartupVerificationResult

Represents the pass/fail result of the local startup verification flow.

| Field                   | Type    | Required | Notes                                                 |
| ----------------------- | ------- | -------- | ----------------------------------------------------- |
| `verification_id`       | string  | Yes      | Identifier for one verification execution             |
| `session_id`            | string  | Yes      | Associated local runtime session                      |
| `result`                | enum    | Yes      | `pass` or `fail`                                      |
| `checks_passed`         | integer | Yes      | Number of completed checks                            |
| `checks_failed`         | integer | Yes      | Number of failed checks                               |
| `remediation_reference` | string  | No       | Link or section reference to troubleshooting guidance |

Validation rules:

- `result=pass` requires `checks_failed=0`.
- `result=fail` requires at least one troubleshooting remediation reference.

## Relationships

1. One `LocalDagitSession` can have multiple `DefinitionVisibilitySnapshot` records.
2. One `LocalDagitSession` can have one or more `StartupVerificationResult` records.
3. `StartupVerificationResult` summarizes checks that include at least one visibility snapshot.

## State Transitions

1. Session starts in `starting`.
2. If process launches and endpoint responds, transition to `ready`; otherwise transition to `failed`.
3. While `ready`, definitions visibility checks run and produce snapshots.
4. Verification computes `pass` or `fail` based on startup plus visibility outcomes.
5. Session ends in `stopped` when process is terminated.
