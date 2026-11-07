#!/usr/bin/env bash
# HERMES TEAM BUILDER - Instalador Automatizado para Linux / WSL2 / macOS
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=========================================================="
echo "          HERMES TEAM BUILDER - INSTALADOR LINUX          "
echo "=========================================================="

# 1. Localizar Python
PYTHON_BIN=""
for cmd in python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
        PYTHON_BIN="$(command -v "$cmd")"
        break
    fi
done

if [[ -z "$PYTHON_BIN" ]]; then
    echo "ERRO: Python 3 não foi encontrado no PATH. Instale o python3." >&2
    exit 1
fi
echo "[+] Python detectado: $PYTHON_BIN"

# 2. Executar Detecção de Ambiente
echo "[+] Analisando ambiente e instalação do Hermes..."
"$PYTHON_BIN" "$PROJECT_ROOT/core/detect_environment.py"

# 3. Executar Sincronização dos Perfis e SOUL.md
echo ""
echo "[+] Instalando os 12 perfis especializados e personas SOUL.md..."
"$PYTHON_BIN" - <<EOF
import sys
from pathlib import Path
sys.path.insert(0, "$PROJECT_ROOT")
from core.profile_manager import ProfileManager

pm = ProfileManager(Path("$PROJECT_ROOT"))
results = pm.sync_all_agents(dry_run=False)
for r in results:
    status = '[CRIADO]' if r['created'] else '[EXISTENTE]'
    soul = '[SOUL OK]' if r['soul_installed'] else '[SOUL PENDENTE]'
    print(f" -> {r['id'].upper():<10} Profile: {r['profile']:<10} {status} {soul}")

print('\n[+] Perfis e personas sincronizados com sucesso!')
EOF

# 4. Diagnóstico Final
echo ""
echo "[+] Executando auditoria final de instalação..."
"$PYTHON_BIN" "$PROJECT_ROOT/core/validator.py"

echo "=========================================================="
echo " Instalação concluída com sucesso!                        "
echo " Você já pode conversar com o HERMES pelo profile default:"
echo "   hermes chat                                            "
echo "=========================================================="
