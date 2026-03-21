# Contract: Workspace Quality and Affected Execution

## Purpose

Define the non-negotiable quality interface for backend, frontend, and workspace-level checks in the baseline monorepo.

## Required Quality Targets

Each relevant project MUST expose these targets:

- `lint`
- `format`
- `typecheck`
- `test`
- `coverage`

Workspace MUST expose:

- `duplication` (cross-repo PMD CPD)
- `validate` (orchestrates affected quality checks)

## Backend Quality Contract

- Dependency/environment management MUST use uv.
- `pyproject.toml` and `uv.lock` MUST be present.
- Linting and formatting MUST be run with ruff.
- Type checking MUST be run with ty.
- Tests MUST be run with pytest.
- Coverage threshold MUST be >= 90%.

Backend `pyproject.toml` MUST include exactly:

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

## Frontend Quality Contract

- Package manager MUST be pnpm.
- Testing MUST use Vitest.
- Linting MUST use Biome.
- Formatting MUST use Biome.
- Type checking MUST use `tsc --noEmit`.
- TypeScript MUST have `strict: true` and stricter compiler flags as required.
- Coverage threshold MUST be >= 90%.

## Duplication Contract

- Duplication checks MUST run using PMD CPD.
- Command MUST include `--minimum-tokens 50`.
- Scan scope MUST include backend and frontend source trees.
- PMD version MUST be pinned to 7.22.0.

## PMD Installation Contract

The repository MUST codify this installation script exactly:

```bash
$ cd $HOME
$ wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.22.0/pmd-dist-7.22.0-bin.zip
$ unzip pmd-dist-7.22.0-bin.zip
$ alias pmd="$HOME/pmd-bin-7.22.0/bin/pmd"
$ pmd check -d /usr/src -R rulesets/java/quickstart.xml -f text
```

## Affected-Only Execution Contract

- All quality targets MUST be invocable through Nx affected commands.
- Affected evaluation MUST be graph-based and file-input based.
- Unrelated projects MUST NOT run quality targets for isolated changes.
- Changed workspace-level config files MAY trigger broader checks by design.

## Prohibited Actions

- Disabling or suppressing lint/type/test rules without explicit owner approval.
- Replacing required tools with alternatives without constitution amendment.
- Introducing implementation/business functionality in baseline scaffolding.
