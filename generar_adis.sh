#!/usr/bin/env bash
# Genera los ADI de actividad (TOTA, POTA, LLOTA) en cada carpeta ACTIVIDADES
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================="
echo "  GENERADOR DE ADI POR ACTIVIDAD"
echo "============================================="

python3 "$SCRIPT_DIR/qsl_generar_adis.py"

echo ""
echo "✅ Proceso completado"
