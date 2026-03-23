# Quickstart: Frontend Dataset Discovery UI (018)

**Branch**: `018-frontend-dataset-discovery`  
**Date**: 2026-03-23

---

## Prerequisites

- Docker Compose local stack is running (backend API + database):
  ```bash
  docker compose up -d db backend
  ```
- Node.js 22 LTS and pnpm 9 installed.
- Frontend dependencies installed:
  ```bash
  pnpm install
  ```

## Environment Setup

Set the discovery API base URL for local development. Create or update
`apps/frontend/.env.local`:

```bash
DISCOVERY_API_BASE_URL=http://localhost:8080
```

> For Docker Compose internal networking (if running Next.js inside Compose),
> use `http://backend:8080` instead.

## Run the Frontend Dev Server

```bash
pnpm --dir apps/frontend dev
```

The app is served at `http://localhost:3000`.

## Pages to Verify

| Page            | URL                                           | Expected Content                  |
| --------------- | --------------------------------------------- | --------------------------------- |
| Home            | `http://localhost:3000/`                      | Search box + Recent Updates feed  |
| Home search     | `http://localhost:3000/?q=federal`            | Matching datasets returned        |
| Catalog         | `http://localhost:3000/datasets`              | All datasets list                 |
| Catalog grouped | `http://localhost:3000/datasets?group=source` | Grouped by source sections        |
| Catalog search  | `http://localhost:3000/datasets?q=rate`       | Filtered list                     |
| Detail          | `http://localhost:3000/datasets/FEDFUNDS`     | Full metadata + time series chart |
| Not found       | `http://localhost:3000/datasets/UNKNOWN`      | "Not found" page                  |

## Running Tests

```bash
# Run all frontend tests
pnpm --dir apps/frontend test

# Run with coverage (must stay ≥ 90%)
pnpm --dir apps/frontend coverage

# Run lint and format checks
pnpm --dir apps/frontend lint
pnpm --dir apps/frontend exec biome check .

# Run type checking
pnpm --dir apps/frontend typecheck
```

## Running All Affected Quality Gates

```bash
pnpm run affected:lint
pnpm run affected:format
pnpm run affected:typecheck
pnpm run affected:test
pnpm run affected:coverage
```

## Adding the Frontend to Docker Compose (Optional)

If serving the frontend via Compose, add a `frontend` service to `docker-compose.yml`:

```yaml
frontend:
  image: node:22-alpine
  working_dir: /workspace
  command:
    [
      "sh",
      "-c",
      "npm install -g pnpm && pnpm install && pnpm --dir apps/frontend dev",
    ]
  environment:
    DISCOVERY_API_BASE_URL: http://backend:8080
  ports:
    - "3000:3000"
  volumes:
    - ./:/workspace
  depends_on:
    backend:
      condition: service_healthy
```

## Execution Evidence

Environment and stack used for verification:

- `docker compose up -d db backend`
- `DISCOVERY_API_BASE_URL=http://localhost:8080 pnpm --dir apps/frontend dev`
- Next.js selected port `3002` because `3000` was already in use.

Route status verification:

```text
ROUTE STATUS
/ 200
/?q=federal 200
/datasets 200
/datasets?group=source 200
/datasets/FEDFUNDS 200
/datasets/UNKNOWN 404
```

Content verification excerpts:

```text
CONTENT CHECKS
Recent Updates
Search datasets
Group by source
Search datasets
Dataset observations
Federal Funds Effective Rate
Back to all datasets
Dataset not found
```

Frontend quality suite verification:

- `pnpm --dir apps/frontend lint` ✅
- `pnpm --dir apps/frontend exec biome check .` ✅
- `pnpm --dir apps/frontend typecheck` ✅
- `pnpm --dir apps/frontend test` ✅
- `pnpm --dir apps/frontend coverage` ✅ (overall coverage remained above the 90% threshold)

Cross-workspace affected checks note:

- `pnpm run affected:test` / `pnpm run affected:coverage` remain blocked by pre-existing backend/pipeline coverage gaps unrelated to this frontend feature.
