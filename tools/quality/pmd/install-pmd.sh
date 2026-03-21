#!/usr/bin/env bash
set -euo pipefail

cd "$HOME"
wget https://github.com/pmd/pmd/releases/download/pmd_releases%2F7.22.0/pmd-dist-7.22.0-bin.zip
unzip pmd-dist-7.22.0-bin.zip
alias pmd="$HOME/pmd-bin-7.22.0/bin/pmd"
pmd check -d /usr/src -R rulesets/java/quickstart.xml -f text
