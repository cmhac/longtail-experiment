#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"

cd "$REPO_ROOT"

bash tools/quality/local-stack/test-local-db-bootstrap.sh
docker compose up -d dagster_db
for _ in $(seq 1 60); do
	dagster_db_ps_json="$(docker compose ps dagster_db --format json || true)"
	dagster_db_healthy=$(printf '%s\n' "$dagster_db_ps_json" | grep -c '"Health":"healthy"' || true)
	if [[ "$dagster_db_healthy" -gt 0 ]]; then
		break
	fi
	sleep 1
done
if [[ "${dagster_db_healthy:-0}" -eq 0 ]]; then
	echo "Dagster metadata DB readiness check failed." >&2
	docker compose logs dagster_db >&2 || true
	docker compose down
	exit 1
fi
bash tools/quality/local-stack/run-db-migrations.sh
bash tools/quality/local-stack/check-db-revision.sh
bash tools/quality/local-stack/test-compose-stack.sh
