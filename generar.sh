#!/usr/bin/env bash
# ============================================================
#  GENERADOR DE POSTALES QSL — ejecución autónoma y portable
# ============================================================
#  Uso:
#    ./generar.sh              -> incremental + sincroniza a Google Drive
#    ./generar.sh --from-scratch
#                              -> borra QSLS/*.png y qsl_log.json
#                                 y regenera TODO desde cero
#    ./generar.sh --clean      -> alias de --from-scratch
#    ./generar.sh --no-sync-drive
#                              -> NO sincroniza a Google Drive
#    ./generar.sh --index      -> regenera qsl_index.json (indice web)
#    ./generar.sh --index-only -> solo regenera qsl_index.json
#
#  El script es autocontenido:
#    * calcula su propio directorio (puede copiarse a cualquier lado)
#    * crea/usa el venv local (venv/) e instala Pillow si hace falta
#    * NO toca tus .adi ni tus fondos; solo las salidas (QSLS/ y logs)
# ============================================================
set -euo pipefail

# ---------- Localización del proyecto (portable) ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR="$SCRIPT_DIR/venv"
PY=python3

# ---------- Argumentos ----------
FROM_SCRATCH=false
SYNC_DRIVE=true
BUILD_INDEX=false
INDEX_ONLY=false
for arg in "$@"; do
  case "$arg" in
    --from-scratch|--clean) FROM_SCRATCH=true ;;
    --sync-drive) SYNC_DRIVE=true ;;
    --no-sync-drive) SYNC_DRIVE=false ;;
    --index) BUILD_INDEX=true ;;
    --index-only) BUILD_INDEX=true; INDEX_ONLY=true ;;
    *) echo "Argumento desconocido: $arg"; exit 1 ;;
  esac
done

echo "============================================================"
echo "  GENERADOR QSL — setup automático"
echo "  Proyecto: $SCRIPT_DIR"
echo "============================================================"

# ---------- 1. Comprobar python3 ----------
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "ERROR: no se encuentra python3 en el PATH." >&2
  exit 1
fi
echo "→ python3 detectado: $($PY --version 2>&1)"

# ---------- 2. Crear venv si no existe ----------
if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "→ creando venv en $VENV_DIR ..."
  "$PY" -m venv "$VENV_DIR"
else
  echo "→ venv ya existente: $VENV_DIR"
fi

PY_VENV="$VENV_DIR/bin/python"

# ---------- 3. Instalar Pillow si hace falta ----------
if ! "$PY_VENV" -c "import PIL" >/dev/null 2>&1; then
  echo "→ instalando Pillow en el venv ..."
  "$PY_VENV" -m pip install --upgrade pip
  "$PY_VENV" -m pip install Pillow
else
  echo "→ Pillow ya disponible: $($PY_VENV -c 'import PIL; print(PIL.__version__)')"
fi

# ---------- 3.b Instalar google-auth si se va a indexar Drive ----------
if [ "$BUILD_INDEX" = true ] && ! "$PY_VENV" -c "import google.auth" >/dev/null 2>&1; then
  echo "→ instalando google-auth en el venv ..."
  "$PY_VENV" -m pip install google-auth
fi

# ---------- 4. (Opcional) Regenerar todo desde cero ----------
if [ "$FROM_SCRATCH" = true ]; then
  echo "→ modo --from-scratch: borrando salidas anteriores ..."
  # Conserva .adi, fondos y el propio script; borra solo salidas
  find . -not -path './venv*' -not -path './.git*' -not -path './FLAGS*' \
    \( -name '*.png' -path '*/QSLS/*' -o -name 'qsl_log.json' \) -print -delete
fi

# ---------- 5. Sanidad mínima ----------
if [ ! -f "$SCRIPT_DIR/qsl_generator.py" ]; then
  echo "ERROR: no se encuentra qsl_generator.py junto a este script." >&2
  exit 1
fi

# ---------- 6. Ejecutar el generador ----------
if [ "$INDEX_ONLY" = false ]; then
  echo
  echo "→ ejecutando qsl_generator.py ..."
  echo
  "$PY_VENV" "$SCRIPT_DIR/qsl_generator.py"
fi

# ---------- 7. Resumen de salidas ----------
if [ "$INDEX_ONLY" = false ]; then
  echo
  echo "Postales generadas por carpeta:"
  for d in "$SCRIPT_DIR"/qsl[1-7]; do
    [ -d "$d" ] || continue
    n=$(find "$d/QSLS" -maxdepth 1 -name '*.png' 2>/dev/null | wc -l | tr -d ' ')
    printf "   %-6s %s postales\n" "$(basename "$d")" "${n:-0}"
  done
fi

# ---------- 8. Sync a Google Drive (opcional) ----------
if [ "$SYNC_DRIVE" = true ]; then
  GDRIVE_BASE="$HOME/Library/CloudStorage/GoogleDrive-eg9mm.mail@gmail.com/My Drive/QSL/QSLs"
  echo
  echo "→ sincronizando con Google Drive ($GDRIVE_BASE) ..."
  for d in "$SCRIPT_DIR"/qsl[1-7]; do
    [ -d "$d/QSLS" ] || continue
    folder_name=$(basename "$d")
    dest="$GDRIVE_BASE/$folder_name"
    mkdir -p "$dest"
    rsync -av --update --delete "$d/QSLS/" "$dest/" 2>/dev/null | grep -c '\.png$' > /dev/null 2>&1 || true
    count=$(find "$dest" -maxdepth 1 -name '*.png' 2>/dev/null | wc -l | tr -d ' ')
    printf "   %-6s -> %s/  (%s PNGs)\n" "$folder_name" "$dest" "${count:-0}"
  done
  echo "→ Google Drive sincronizará automáticamente con la nube."
fi

# ---------- 9. Índice web (opcional) ----------
if [ "$BUILD_INDEX" = true ]; then
  echo
  if [ ! -f "$SCRIPT_DIR/drive_creds.json" ]; then
    echo "→ falta drive_creds.json: no se regenera el índice web (ver README §9)."
  else
    echo "→ regenerando qsl_index.json ..."
    echo "  (si acabas de sincronizar, Drive puede tardar unos segundos en subir"
    echo "   los PNG nuevos: si faltan, repite '--index-only' en un minuto)"
    read -r -a DRIVE_INDEX_ARGS_ARR <<< "${DRIVE_INDEX_ARGS:-}"
    "$PY_VENV" "$SCRIPT_DIR/drive_index.py" "${DRIVE_INDEX_ARGS_ARR[@]+"${DRIVE_INDEX_ARGS_ARR[@]}"}"
  fi
fi

echo
echo "Listo. Busca las imágenes en cada qslN/QSLS/."
