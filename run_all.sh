#!/usr/bin/env bash
# Ejecuta el proceso completo: genera QSLs + sincroniza Drive + actualiza web + push a GitHub
# Uso: ./run_all.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Ejecutando proceso completo QSL..."
echo

./generar.sh --auto

echo
echo "✅ Proceso completo finalizado"
echo "   - QSLs generadas/actualizadas"
echo "   - Google Drive sincronizado"
echo "   - Índice web (qsl_index.json) regenerado"
echo "   - Cambios committeados y pusheados a GitHub"
echo "   - GitHub Pages se actualizará en ~1 minuto"
echo
echo "🌐 Web: https://dcialdella.github.io/ia-qsls/"