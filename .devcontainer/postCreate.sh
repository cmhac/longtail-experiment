#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed or not on PATH." >&2
  exit 1
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is not installed or not on PATH." >&2
  exit 1
fi

if ! command -v pnpm >/dev/null 2>&1; then
  corepack enable
  corepack prepare pnpm@9.0.0 --activate
fi

if [[ -f "docker/compose/local.secrets.env.example" ]] && [[ ! -f "docker/compose/local.secrets.env" ]]; then
  cp docker/compose/local.secrets.env.example docker/compose/local.secrets.env
  echo "Created docker/compose/local.secrets.env from example."
fi

echo "Installing Node workspace dependencies..."
pnpm install

if ! command -v opencode >/dev/null 2>&1; then
  echo "Installing opencode CLI..."
  npm_bin="$(command -v npm || true)"
  if [[ -z "${npm_bin}" ]]; then
    echo "npm is not installed or not on PATH." >&2
    exit 1
  fi

  if ! "${npm_bin}" install -g opencode-ai; then
    sudo "${npm_bin}" install -g opencode-ai
  fi
fi

echo "opencode version: $(opencode --version)"

echo "Syncing Python project environments..."
mapfile -t pyprojects < <(find apps libs -mindepth 2 -maxdepth 2 -name pyproject.toml | sort)

for pyproject in "${pyprojects[@]}"; do
  project_dir="$(dirname "${pyproject}")"
  echo "- uv sync --project ${project_dir}"
  uv sync --project "${project_dir}" --frozen
done

echo "Installing pre-commit hooks (best effort)..."
uvx --from pre-commit pre-commit install --install-hooks || true

echo "Devcontainer bootstrap complete."
