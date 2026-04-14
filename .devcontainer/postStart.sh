#!/usr/bin/env bash
set -euo pipefail

docker_available="true"
tailscale_available="true"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker CLI is not installed in this devcontainer. Skipping Docker readiness checks." >&2
  docker_available="false"
fi

if ! command -v tailscaled >/dev/null 2>&1 || ! command -v tailscale >/dev/null 2>&1; then
  echo "Tailscale is not installed in this devcontainer image. Skipping Tailscale startup." >&2
  tailscale_available="false"
fi

if [[ "${docker_available}" == "true" ]]; then
  timeout_sec="${DOCKER_STARTUP_TIMEOUT_SEC:-120}"
  docker_ready="false"

  if [[ ! -S "/var/run/docker.sock" ]] && command -v dockerd >/dev/null 2>&1; then
    echo "Docker socket not found; attempting to start dockerd..." >&2
    nohup sudo dockerd >/tmp/dockerd.log 2>&1 &
  fi

  echo "Waiting for Docker daemon to be ready (timeout: ${timeout_sec}s)..." >&2
  for _ in $(seq 1 "${timeout_sec}"); do
    if docker info >/dev/null 2>&1 || sudo -n docker info >/dev/null 2>&1; then
      if docker compose version >/dev/null 2>&1; then
        docker_ready="true"
        break
      fi
    fi
    sleep 1
  done

  if [[ "${docker_ready}" != "true" ]]; then
    echo "Docker is not available inside this devcontainer after ${timeout_sec}s. Continuing without Docker-dependent startup." >&2
    echo "Debug info:" >&2
    echo "- docker version:" >&2
    docker version >&2 || true
    echo "- docker compose version:" >&2
    docker compose version >&2 || true
  fi
fi

if [[ "${tailscale_available}" == "true" ]]; then
  if ! pgrep -x tailscaled >/dev/null 2>&1; then
    echo "Starting tailscaled daemon..." >&2
    sudo mkdir -p /var/lib/tailscale
    sudo chown devcontainer-user:devcontainer-user /var/lib/tailscale
    nohup sudo tailscaled --statedir=/var/lib/tailscale >/tmp/tailscaled.log 2>&1 &
  fi

  echo "Checking Tailscale daemon status..." >&2
  if sudo tailscale status >/dev/null 2>&1; then
    echo "Tailscale daemon is running."
  else
    echo "Tailscale daemon is starting."
  fi

  echo "To authenticate manually, run: sudo tailscale up --auth-key=<tskey-...>"
fi
if ! command -v opencode >/dev/null 2>&1; then
  echo "opencode CLI is not installed yet. Rebuild the devcontainer or run: sudo npm install -g opencode-ai" >&2
  exit 0
fi

opencode_host="${OPENCODE_SERVER_HOSTNAME:-0.0.0.0}"
opencode_port="${OPENCODE_SERVER_PORT:-4096}"
opencode_log="/tmp/opencode-serve.log"

if pgrep -f "opencode serve" >/dev/null 2>&1; then
  echo "opencode serve is already running."
else
  echo "Starting opencode serve on ${opencode_host}:${opencode_port}..."
  nohup opencode serve --hostname "${opencode_host}" --port "${opencode_port}" >"${opencode_log}" 2>&1 &
fi

echo "opencode log: ${opencode_log}"
