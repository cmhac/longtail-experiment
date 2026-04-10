FROM mcr.microsoft.com/devcontainers/base:debian-12

ARG PMD_VERSION="7.22.0"

ENV PATH="/usr/local/bin:/opt/uv-python/current/bin:${PATH}"
ENV UV_PYTHON_INSTALL_DIR="/opt/uv-python"

USER root

RUN set -eux; \
  apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    findutils \
    git \
    jq \
    openjdk-17-jre-headless \
    sudo \
    tar \
    unzip \
    ; \
  rm -rf /var/lib/apt/lists/*

RUN set -eux; \
  curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.noarmor.gpg -o /usr/share/keyrings/tailscale-archive-keyring.gpg; \
  curl -fsSL https://pkgs.tailscale.com/stable/debian/bookworm.tailscale-keyring.list -o /etc/apt/sources.list.d/tailscale.list; \
  apt-get update; \
  DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tailscale; \
  rm -rf /var/lib/apt/lists/*

RUN set -eux; \
  curl -LsSf https://astral.sh/uv/install.sh | sh; \
  install -m 0755 /root/.local/bin/uv /usr/local/bin/uv; \
  rm -rf /root/.local; \
  uv python install 3.12 --install-dir "${UV_PYTHON_INSTALL_DIR}"; \
  python_bin="$(find "${UV_PYTHON_INSTALL_DIR}" -type f -path '*/bin/python3.12' | head -n 1)"; \
  test -n "${python_bin}"; \
  python_home="$(dirname "$(dirname "${python_bin}")")"; \
  ln -sfn "${python_home}" /opt/uv-python/current; \
  ln -sf /opt/uv-python/current/bin/python3.12 /usr/local/bin/python3.12; \
  ln -sf /usr/local/bin/python3.12 /usr/local/bin/python3; \
  ln -sf /usr/local/bin/python3.12 /usr/local/bin/python

RUN set -eux; \
  curl -sSLo /tmp/pmd.zip "https://github.com/pmd/pmd/releases/download/pmd_releases%2F${PMD_VERSION}/pmd-dist-${PMD_VERSION}-bin.zip"; \
  unzip -q /tmp/pmd.zip -d /opt; \
  ln -sf "/opt/pmd-bin-${PMD_VERSION}/bin/pmd" /usr/local/bin/pmd; \
  rm /tmp/pmd.zip

RUN set -eux; \
  if ! id -u devcontainer-user >/dev/null 2>&1; then \
    existing_user="$(getent passwd 1000 | cut -d: -f1 || true)"; \
    if [ -n "${existing_user}" ]; then \
      if [ "${existing_user}" != "devcontainer-user" ]; then usermod -l devcontainer-user "${existing_user}"; fi; \
      existing_group="$(getent group 1000 | cut -d: -f1 || true)"; \
      if [ -n "${existing_group}" ] && [ "${existing_group}" != "devcontainer-user" ]; then groupmod -n devcontainer-user "${existing_group}" || true; fi; \
      usermod -d /home/devcontainer-user -m devcontainer-user; \
    else \
      if ! getent group 1000 >/dev/null 2>&1; then groupadd --gid 1000 devcontainer-user; fi; \
      useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash devcontainer-user; \
    fi; \
  fi; \
  usermod -aG sudo devcontainer-user; \
  echo "devcontainer-user ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/devcontainer-user; \
  chmod 0440 /etc/sudoers.d/devcontainer-user; \
  mkdir -p /var/lib/tailscale; \
  chown -R devcontainer-user:devcontainer-user /var/lib/tailscale; \
  chown -R devcontainer-user:devcontainer-user "${UV_PYTHON_INSTALL_DIR}"; \
  chmod -R g+w "${UV_PYTHON_INSTALL_DIR}"

USER devcontainer-user
