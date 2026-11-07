#!/usr/bin/env bash
# HERMES TEAM BUILDER - Ponto de Entrada de Instalação (Linux / macOS)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
bash "$SCRIPT_DIR/installer/install.sh" "$@"
