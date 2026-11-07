#!/usr/bin/env bash
# HERMES TEAM BUILDER - Script de Reparo e Atualização de Personas (Linux)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================================="
echo "      HERMES TEAM BUILDER - REPARO E ATUALIZAÇÃO          "
echo "=========================================================="

PYTHON_BIN=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON_BIN="$(command -v "$cmd")"
        break
    fi
done

if [[ -z "$PYTHON_BIN" ]]; then
    echo "ERRO: Python 3 não foi encontrado." >&2
    exit 1
fi

"$PYTHON_BIN" - <<EOF
import sys
from pathlib import Path
sys.path.insert(0, "$PROJECT_ROOT")
from core.profile_manager import ProfileManager
from core.delegation_manager import DelegationManager

pm = ProfileManager(Path("$PROJECT_ROOT"))
results = pm.sync_all_agents(dry_run=False)
for r in results:
    print(f" -> Atualizado: {r['id'].upper()} ({r['profile']})")

dm = DelegationManager(Path("$PROJECT_ROOT"))
dm.verify_descriptions()
print('\n[+] Descrições e SOUL.md restaurados com sucesso!')
EOF

"$PYTHON_BIN" "$PROJECT_ROOT/core/validator.py"
