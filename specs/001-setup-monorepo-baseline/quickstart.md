# Quickstart: Initial Monorepo Baseline

## Goal

Boot a barebones Nx monorepo baseline with backend and frontend environments, strict quality gates, and affected-only execution.

## Prerequisites

- Git
- Docker (or Docker Desktop)
- Node.js 22 LTS
- pnpm
- Python 3.12
- uv

## 1. Install PMD (Pinned)

Run exactly:

```bash
$ cd $HOME
$ wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.22.0/pmd-dist-7.22.0-bin.zip
$ unzip pmd-dist-7.22.0-bin.zip
$ alias pmd="$HOME/pmd-bin-7.22.0/bin/pmd"
$ pmd check -d /usr/src -R rulesets/java/quickstart.xml -f text
```

## 2. Bootstrap Workspace

```bash
pnpm install
```

## 3. Backend Baseline Setup (uv)

```bash
uv sync --frozen
```

Backend quality commands:

```bash
uv run --project apps/backend ruff check apps/backend
uv run --project apps/backend ruff format --check apps/backend
uv run --project apps/backend ty check apps/backend
uv run --project apps/backend pytest apps/backend/tests
```

Backend `pyproject.toml` lint policy MUST include exactly:

```toml
[tool.ruff.lint]
select = [
    "E",
    "F",
    "I",
    "B",
    "D",
    "A",
    "C4",
    "UP",
    "SIM",
    "RET",
    "PTH",
    "DTZ",
    "PL",
]
ignore = ["D212", "D203"]
```

## 4. Frontend Baseline Setup (pnpm)

```bash
pnpm install --frozen-lockfile
```

Frontend quality commands:

```bash
pnpm --filter frontend exec biome check .
pnpm --filter frontend exec tsc --noEmit
pnpm --filter frontend exec vitest run
```

TypeScript contract:

- `strict: true` is mandatory.
- Additional strict flags are enabled as needed to maintain no-loose-type policy.

## 5. Cross-Repo Duplication Check

```bash
pmd cpd --minimum-tokens 50 --dir apps/backend/src --dir apps/frontend/src
```

## 6. Run Affected-Only Checks with Nx

Use Nx affected commands so checks run only for impacted projects:

```bash
pnpm nx affected -t lint
pnpm nx affected -t format
pnpm nx affected -t typecheck
pnpm nx affected -t test
pnpm nx affected -t coverage
pnpm nx affected -t duplication
```

Configuration requirements:

- `nx.json` named inputs MUST map source/test/config globs per project.
- Target defaults MUST define deterministic inputs/outputs for cache correctness.
- Workspace-level config changes MAY broaden affected scope intentionally.

## 7. Start Local Full Stack (Placeholder)

```bash
docker compose up -d
```

Verify services are healthy:

```bash
docker compose ps
```

Stop stack:

```bash
docker compose down
```

## 8. Definition of Done for This Baseline

- Backend and frontend projects are recognized by Nx.
- No business implementation is present.
- All quality gates run without suppressions.
- Coverage policy is enforced at >= 90%.
- PMD CPD runs with `--minimum-tokens 50`.
- Nx affected commands execute only relevant checks for changed projects.
- Unified local stack starts and reports healthy placeholder services.

## 9. Workspace Listing Verification

Run these commands to verify project registration and affected execution wiring:

```bash
pnpm nx show projects
pnpm nx graph --file tmp/nx-graph.html
```

## 10. Evidence Capture Template

- Full quality pipeline result: PASS/FAIL
- Affected lint runtime (seconds):
- Affected test runtime (seconds):
- Local stack startup status: PASS/FAIL
- Local stack shutdown status: PASS/FAIL

## 11. Latest Verification Evidence (2026-03-21)

Command executed:

```bash
pnpm run quality:all && bash tools/quality/local-stack/test-compose-stack.sh
```

Observed outputs summary:

- Full quality pipeline result: PASS
- Affected lint runtime (seconds): Nx cached in latest run
- Affected test runtime (seconds): Nx cached in latest run
- Local stack startup status: PASS
- Local stack shutdown status: PASS

Compose verification output excerpt:

```text
NAME                             IMAGE                SERVICE    STATUS
longtail-experiment-backend-1    python:3.12-alpine   backend    Up (health: starting)
longtail-experiment-frontend-1   node:22-alpine       frontend   Up (health: starting)
```
