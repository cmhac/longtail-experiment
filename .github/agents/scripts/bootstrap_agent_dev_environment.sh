#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

PMD_VERSION="7.22.0"
PMD_DIR="${HOME}/pmd-bin-${PMD_VERSION}"
UV_TOOL_BIN="${HOME}/.local/bin"

log() {
	printf '[bootstrap] %s\n' "$*"
}

add_path() {
	local path_entry="$1"
	export PATH="${path_entry}:${PATH}"

	if [[ -n "${GITHUB_PATH:-}" ]]; then
		printf '%s\n' "${path_entry}" >>"${GITHUB_PATH}"
	fi
}

require_cmd() {
	local cmd="$1"
	local install_hint="$2"

	if ! command -v "${cmd}" >/dev/null 2>&1; then
		printf '[bootstrap] Missing required command: %s. %s\n' "${cmd}" "${install_hint}" >&2
		exit 1
	fi
}

install_system_dependencies_if_possible() {
	if [[ "$(uname -s)" != "Linux" ]]; then
		log "Skipping apt-get dependency install on non-Linux host"
		return
	fi

	if ! command -v apt-get >/dev/null 2>&1; then
		log "Skipping apt-get dependency install because apt-get is unavailable"
		return
	fi

	local apt_prefix=""
	if command -v sudo >/dev/null 2>&1; then
		apt_prefix="sudo"
	fi

	log "Installing system dependencies (curl, jq, unzip, wget)"
	${apt_prefix} apt-get update
	${apt_prefix} apt-get install -y --no-install-recommends \
		curl \
		jq \
		unzip \
		wget
}

ensure_pnpm_9() {
	if ! command -v pnpm >/dev/null 2>&1; then
		require_cmd corepack "Install Node.js with corepack support."
		corepack enable
		corepack prepare pnpm@9.0.0 --activate
	fi

	local pnpm_major
	pnpm_major="$(pnpm --version | cut -d'.' -f1)"
	if [[ "${pnpm_major}" != "9" ]]; then
		require_cmd corepack "Install Node.js with corepack support."
		corepack prepare pnpm@9.0.0 --activate
	fi
}

ensure_uv() {
	if command -v uv >/dev/null 2>&1; then
		return
	fi

	require_cmd curl "Install curl to allow uv bootstrap."
	log "Installing uv"
	curl -LsSf https://astral.sh/uv/install.sh | sh
	add_path "${UV_TOOL_BIN}"
}

install_pmd() {
	require_cmd wget "Install wget to download PMD."
	require_cmd unzip "Install unzip to extract PMD."

	if [[ ! -x "${PMD_DIR}/bin/pmd" ]]; then
		log "Installing PMD ${PMD_VERSION}"
		wget -q "https://github.com/pmd/pmd/releases/download/pmd_releases%2F${PMD_VERSION}/pmd-dist-${PMD_VERSION}-bin.zip" -O /tmp/pmd.zip
		unzip -q /tmp/pmd.zip -d "${HOME}"
	fi

	add_path "${PMD_DIR}/bin"
	pmd --version
}

ensure_compose_secret_env() {
	local secrets_path="${REPO_ROOT}/docker/compose/local.secrets.env"

	if [[ ! -f "${secrets_path}" ]]; then
		log "Creating docker/compose/local.secrets.env"
		printf 'FRED_API_KEY=%s\nDAGSTER_METADATA_DB_PASSWORD=%s\n' \
			"${FRED_API_KEY:-dummy}" \
			"${DAGSTER_METADATA_DB_PASSWORD:-longtail}" >"${secrets_path}"
	fi
}

main() {
	cd "${REPO_ROOT}"

	install_system_dependencies_if_possible

	require_cmd node "Install Node.js 22.x before running this script."
	ensure_pnpm_9
	require_cmd python3 "Install Python 3.12 before running this script."
	ensure_uv
	add_path "${UV_TOOL_BIN}"

	require_cmd java "Install Java 21 (Temurin) before running this script."
	require_cmd docker "Install Docker before running this script."

	log "Verifying runtime tools"
	node --version
	pnpm --version
	python3 --version
	uv --version
	docker --version
	docker compose version

	install_pmd

	log "Installing JavaScript dependencies"
	pnpm install --frozen-lockfile

	log "Installing Python dependencies via uv"
	uv sync --project apps/backend --frozen
	uv sync --project apps/pipeline --frozen

	log "Installing pre-commit as a persistent uv tool"
	uv tool install pre-commit
	pre-commit --version
	pre-commit install-hooks

	ensure_compose_secret_env

	log "Verifying workspace configuration"
	pnpm exec nx --version
	pnpm exec nx show projects >/dev/null
	uv run --project apps/backend python -V
	uv run --project apps/pipeline python -V
	docker compose config -q

	log "Bootstrap completed successfully"
}

main "$@"
