# Trend Descriptor v2 Cutover Runbook

## Purpose

Define the local-development hard cutover procedure for Spec 050, including
reset expectations and validation criteria for v2-only trend and notification
semantics.

## Scope

- Environment: local Docker Compose stack only.
- Contract posture: v2-only canonical descriptor semantics after reset.
- Legacy trend/event/notification data is treated as disposable in this phase.

## Preconditions

- Docker daemon running.
- Local secrets available in `docker/compose/local.secrets.env`.
- Repo dependencies already installed.

## Cutover Procedure

1. Stop the running stack:
   - `docker compose down`
2. Remove persisted volumes to enforce a clean local baseline:
   - `docker compose down -v`
3. Start the required services:
   - `docker compose up -d db backend`
4. Verify backend readiness:
   - `docker compose ps`
   - `curl -fsS http://127.0.0.1:18081/api/health`
5. Run a post-reset ingest flow to repopulate trend state.

## Validation Criteria

After reset and post-reset ingest, verify all conditions:

- Legacy pre-reset rows are absent by timestamp window checks.
- `trend_canonical_descriptors` contains only post-reset rows.
- `trend_change_events` contains only post-reset rows.
- `user_trend_notifications` contains only post-reset rows.

Use the executable validator:

- `bash tools/verification/spec050_trend_v2_reset_validation.sh`

Optional custom ingest command:

- `SPEC050_RESET_INGEST_COMMAND="<your ingest command>" bash tools/verification/spec050_trend_v2_reset_validation.sh`

## Troubleshooting

- If backend health fails, inspect:
  - `docker compose logs backend`
- If migration state is unexpected, inspect:
  - `docker compose exec db psql -U "${LOCAL_DB_USER:-longtail}" -d "${LOCAL_DB_NAME:-longtail_local}" -c "SELECT version_num FROM alembic_version;"`
- If validation reports old rows, re-run reset (`docker compose down -v`) and repeat.

## Safety Notes

- This procedure is for local development only.
- Do not run destructive reset commands against non-development databases.
