#!/usr/bin/env bash
# HERMES TEAM BUILDER - Desinstalador Seguro (Linux)
set -euo pipefail

echo "=========================================================="
echo "         HERMES TEAM BUILDER - DESINSTALADOR SEGURO       "
echo "=========================================================="

SPECIALISTS=(
    athena atlas tesla ada linus
    iris sherlock sentinel nova scribe arbiter
)

echo "Esta operação removerá os 11 profiles especialistas do Hermes:"
for s in "${SPECIALISTS[@]}"; do
    echo " - $s"
done
echo "O profile principal 'default' e seus projetos NÃO serão afetados."
echo ""

read -rp "Tem certeza de que deseja continuar? (s/N): " CONFIRM
if [[ "$CONFIRM" != "s" && "$CONFIRM" != "S" ]]; then
    echo "Operação cancelada pelo usuário."
    exit 0
fi

for s in "${SPECIALISTS[@]}"; do
    echo "Removendo profile '$s'..."
    hermes profile delete "$s" --yes 2>/dev/null || true
done

echo ""
echo "[+] Especialistas removidos. O profile principal default foi preservado."
