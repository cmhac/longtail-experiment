# Local DB Defect Log

Track every reproducible local setup or migration defect discovered during feature 004 implementation.

## Entry Template

- Defect ID:
- Story/Task Link:
- Date Detected:
- Environment:
- Reproduction Steps:
- Observed Symptom:
- Root Cause:
- Fix Summary:
- Validation Commands:
- Validation Result:
- Status: Open | Fixed | Verified

## Logged Defects

- Defect ID: DB-001
- Story/Task Link: US2 / T031-T032
- Date Detected: 2026-03-21
- Environment: macOS local dev with host PostgreSQL already bound to 127.0.0.1:5432
- Reproduction Steps:
  1.  Start compose DB service.
  2.  Run `bash tools/quality/local-stack/run-db-migrations.sh`.
  3.  Observe role-auth failure against non-container DB instance.
- Observed Symptom: Migration command failed with `FATAL: role "longtail" does not exist`.
- Root Cause: Local DB host port default (`5432`) collided with an existing host PostgreSQL service, causing migration commands to target the wrong server.
- Fix Summary: Changed local DB host port default to `55432` in stack env, compose fallback interpolation, and shared DB settings defaults.
- Validation Commands:
  - `bash tools/quality/local-stack/test-local-db-bootstrap.sh`
  - 20 fresh-run attempts of migration + revision check sequence
- Validation Result: 20/20 successful fresh runs; revision checks passed.
- Status: Verified

- Defect ID: DB-002
- Story/Task Link: US3 / T042
- Date Detected: 2026-03-21
- Environment: macOS local dev with stack stopped
- Reproduction Steps:
  1.  Ensure local stack is stopped (`docker compose down`).
  2.  Run `bash tools/quality/local-stack/run-db-migrations.sh`.
  3.  Observe command failure due to DB service not running.
- Observed Symptom: Migration/revision scripts failed unless developers manually started the DB service first.
- Root Cause: Scripts assumed an already-running DB container and only checked health state.
- Fix Summary: Added DB service presence detection plus automatic `docker compose up -d db` bootstrap in migration and revision scripts.
- Validation Commands:
  - `docker compose down`
  - `bash tools/quality/local-stack/run-db-migrations.sh`
  - `bash tools/quality/local-stack/check-db-revision.sh`
- Validation Result: Scripts auto-started DB and completed migration + revision checks successfully.
- Status: Verified
