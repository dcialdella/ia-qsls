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
#    ./generar.sh --keep-empty-drive
#                              -> NO vacía en Drive las actividades sin .adi
#                                 (por defecto SÍ se vacían: es lo coherente
#                                 con los .adi actuales)
#    ./generar.sh --folder-id <ID>
#                              -> indexa otra carpeta de Google Drive
#    ./generar.sh --index      -> regenera qsl_index.json (indice web)
#    ./generar.sh --index-only -> solo regenera qsl_index.json
#    ./generar.sh --auto       -> genera + sincroniza Drive + actualiza índice web + commit + push a GitHub
#
#  El script es autocontenido:
#    * calcula su propio directorio (puede copiarse a cualquier lado)
#    * crea/usa el venv local (venv/) e instala Pillow si hace falta
#    * NO toca tus .adi ni tus fondos; solo las salidas (QSLS/ y logs)
#
#  Sincronización con Drive:
#    * rsync usa --delete, así que las postcards borradas en local se
#      propagan a Drive (podado de huérfanas incluido).
#    * Una actividad con NINGÚN .adi es una actividad vaciada a propósito:
#      sus postcards locales se borran, Drive se vacía con ellas y el índice
#      web deja de ofrecerlas (drive_index.py lee qsl_manifest.json).
#    * Para conservar en Drive lo que ya no tenga .adi en local, usa
#      --keep-empty-drive.
# ============================================================
set -euo pipefail

# Estado de la última ejecución, para el aviso de salida parcial.
SYNCED=()
STEP='inicio'
trap 'rc=$?; echo; echo "ERROR: fallo en el paso «$STEP» (código $rc)." >&2;
      if [ ${#SYNCED[@]} -gt 0 ]; then
        echo "       Ya sincronizadas en Drive: ${SYNCED[*]}" >&2
        echo "       Repite ./generar.sh --auto: rsync y el índice son incrementales." >&2
      else
        echo "       No se llegó a sincronizar nada con Drive." >&2
      fi
      echo "       No se ha commiteado nada: el repo local y Drive pueden estar desincronizados." >&2
      exit $rc' ERR

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
AUTO_PUSH=false
KEEP_EMPTY_DRIVE=false
FOLDER_ID=""
INDEX_ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --from-scratch|--clean) FROM_SCRATCH=true ;;
    --sync-drive) SYNC_DRIVE=true ;;
    --no-sync-drive) SYNC_DRIVE=false ;;
    --keep-empty-drive) KEEP_EMPTY_DRIVE=true ;;
    --folder-id) FOLDER_ID="${2:-}"; [ -n "$FOLDER_ID" ] || { echo "ERROR: --folder-id necesita un valor." >&2; exit 1; }; shift ;;
    --folder-id=*) FOLDER_ID="${1#*=}" ;;
    --index) BUILD_INDEX=true ;;
    --index-only) BUILD_INDEX=true; INDEX_ONLY=true ;;
    --auto) BUILD_INDEX=true; SYNC_DRIVE=true; AUTO_PUSH=true ;;
    *) echo "Argumento desconocido: $1" >&2; exit 1 ;;
  esac
  shift
done
[ -n "$FOLDER_ID" ] && INDEX_ARGS+=("--folder-id" "$FOLDER_ID")

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
# Cuenta los PNG de un directorio sin fallar si no existe y sin depender de find.
count_png() {
  local dir="$1"
  [ -d "$dir" ] || { echo 0; return 0; }
  local n=0 f
  for f in "$dir"/*.png; do
    [ -f "$f" ] && n=$((n + 1))
  done
  echo "$n"
}

# ---------- 7. Ejecutar el generador ----------
if [ "$INDEX_ONLY" = false ]; then
  STEP="generación de postcards"
  echo
  echo "→ ejecutando qsl_generator.py ..."
  echo
  "$PY_VENV" "$SCRIPT_DIR/qsl_generator.py"
fi

# ---------- 8. Resumen de salidas ----------
if [ "$INDEX_ONLY" = false ]; then
  echo
  echo "Postales generadas por carpeta:"
  for d in "$SCRIPT_DIR"/qsl[1-7]; do
    [ -d "$d" ] || continue
    printf "   %-6s %s postales\n" "$(basename "$d")" "$(count_png "$d/QSLS")"
  done
fi

# ---------- 9. Sync a Google Drive (opcional) ----------
if [ "$SYNC_DRIVE" = true ]; then
  GDRIVE_BASE="$HOME/Library/CloudStorage/GoogleDrive-eg9mm.mail@gmail.com/My Drive/QSL/QSLs"
  STEP="sincronización con Google Drive"
  echo
  echo "→ sincronizando con Google Drive ($GDRIVE_BASE) ..."
  for d in "$SCRIPT_DIR"/qsl[1-7]; do
    [ -d "$d/QSLS" ] || continue
    folder_name=$(basename "$d")
    dest="$GDRIVE_BASE/$folder_name"
    src_count=$(count_png "$d/QSLS")

    # Una actividad sin postcards locales solo se salta si se ha pedido
    # --keep-empty-drive. Por defecto se propaga el vaciado a Drive, para que
    # ni Drive ni la web sigan ofreciendo postcards de una actividad vaciada.
    if [ "$src_count" -eq 0 ] && [ "$KEEP_EMPTY_DRIVE" = true ]; then
      printf "   %-6s -> %s/  (%s PNGs)  [--keep-empty-drive: no se toca]\n" \
        "$folder_name" "$dest" "$(count_png "$dest")"
      continue
    fi

    mkdir -p "$dest"
    # Sin el "if !": dentro de un then, $? es el de la negación (siempre 0) y
    # el mensaje de error mentiría sobre el código real de rsync.
    if rsync -a --update --delete "$d/QSLS/" "$dest/"; then
      SYNCED+=("$folder_name")
      printf "   %-6s -> %s/  (%s PNGs)\n" "$folder_name" "$dest" "$(count_png "$dest")"
    else
      rc=$?
      echo "ERROR: rsync falló al sincronizar $folder_name (código $rc)." >&2
      exit "$rc"
    fi
  done
  echo "→ Google Drive sincronizará automáticamente con la nube."
fi

# ---------- 10. Índice web (opcional) ----------
if [ "$BUILD_INDEX" = true ]; then
  STEP="regeneración del índice web"
  echo
  echo "→ regenerando qsl_index.json (lectura HTML público, sin credenciales) ..."
  echo "  ID de carpeta: ${FOLDER_ID:-1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy}"
  if [ "$INDEX_ONLY" = true ] && [ ! -f "$SCRIPT_DIR/qsl_manifest.json" ]; then
    echo "  AVISO: no hay qsl_manifest.json (no se ha generado aún en este repo)."
    echo "         Se indexará todo lo que haya en Drive, incluidas actividades vaciadas."
  fi
  "$PY_VENV" "$SCRIPT_DIR/drive_index.py" ${INDEX_ARGS[@]+"${INDEX_ARGS[@]}"}
fi

# ---------- 10. Auto push a GitHub (opcional) ----------
if [ "$AUTO_PUSH" = true ]; then
  echo
  echo "→ commit y push a GitHub ..."
  git add -A
  if git diff --cached --quiet; then
    echo "   (sin cambios para commitear)"
  else
    git commit -m "Actualización automática: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
    git push origin main
    echo "   → GitHub Pages se actualizará en ~1 minuto"
  fi
fi

echo
echo "Listo. Busca las imágenes en cada qslN/QSLS/."
