# Local Stack Baseline Runbook

## Start

1. Run docker compose up -d
2. Run docker compose ps

## Healthy State

- pipeline service is listed and healthy.
- backend service is listed and healthy.
- frontend service is listed and healthy.

## Troubleshooting

- If backend is unhealthy, inspect: docker compose logs backend
- If frontend is unhealthy, inspect: docker compose logs frontend
- If pipeline is unhealthy, inspect: docker compose logs pipeline
- If any service fails health checks, stop stack with docker compose down and fix configuration before retry.

## Contract Verification After Startup

1. Run pipeline contract tests: `uv run --project apps/pipeline pytest apps/pipeline/tests/contract`
2. Run backend contract tests: `uv run --project apps/backend pytest apps/backend/tests/contract`
3. Verify quality gates for affected changes:
   - `pnpm run affected:lint`
   - `pnpm run affected:test`
   - `pnpm run affected:coverage`

## Contract-Specific Troubleshooting

- If canonical validation tests fail, inspect `apps/pipeline/src/contract/schemas/canonical_observation.py` and `apps/pipeline/src/contract/normalizers/source_payload_mapper.py`.
- If provenance/revision audit tests fail, inspect `apps/pipeline/src/contract/services/revision_lineage_service.py` and `apps/backend/src/contract/query/provenance_audit_query.py`.
- If hierarchy filter tests fail, inspect `apps/pipeline/src/contract/services/taxonomy_mapping_service.py` and `apps/backend/src/contract/query/hierarchy_query.py`.
