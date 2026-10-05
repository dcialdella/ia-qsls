#!/usr/bin/env bash
# Ejecuta el proceso completo: genera QSLs + sincroniza Drive + actualiza web + push a GitHub
# Uso: ./run_all.sh [opciones de generar.sh]
#   p.ej. ./run_all.sh --keep-empty-drive
#         ./run_all.sh --no-sync-drive

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Ejecutando proceso completo QSL..."
echo

# --auto primero; "$@" al final puede desactivarlo (p.ej. --no-sync-drive) o
# añadir flags como --keep-empty-drive.
./generar.sh --auto "$@"

echo
echo "✅ Proceso completo finalizado"
echo "   - QSLs generadas/actualizadas"
echo "   - Google Drive sincronizado"
echo "   - Índice web (qsl_index.json) regenerado"
echo "   - Cambios committeados y pusheados a GitHub"
echo "   - GitHub Pages se actualizará en ~1 minuto"
echo
echo "🌐 Web: https://dcialdella.github.io/ia-qsls/"