#!/usr/bin/env python3
"""
Constructor del índice público de QSLs (qsl_index.json).

La carpeta de Drive es pública ('cualquier persona con el enlace'), así que no
hace falta ninguna credencial: la página de una carpeta pública trae embebidos el
nombre y el file id de cada hijo, y con ese id el enlace de descarga funciona
sin iniciar sesión:

    https://drive.google.com/uc?export=download&id=<ID>   ->  303  ->  200 image/png

Este script lee esas páginas y escribe qsl_index.json, que es lo que después
descarga index.html para buscar por indicativo.

Sin dependencias: solo la biblioteca estándar.

Uso:
    python3 drive_index.py                # usa la carpeta pública de EG9MM
    python3 drive_index.py --folder-id ID # otra carpeta
    python3 drive_index.py --dry-run      # no escribe, solo informa
    python3 drive_index.py --verbose
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Carpeta pública de EG9MM con las subcarpetas qsl1..qsl7:
# https://drive.google.com/drive/u/5/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy
DEFAULT_FOLDER_ID = "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy"
DEFAULT_OUT = "qsl_index.json"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
FOLDER_URL = "https://drive.google.com/drive/folders/{id}"
DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id={id}"
TIMEOUT = 45

FOLDER_MIME = "application/vnd.google-apps.folder"

# Cada entrada del HTML de Drive empieza por [null,"<ID>"] seguido (a menos de
# 400 caracteres) de su mime type. El nombre del archivo aparece algo después,
# dentro del mismo bloque.
ENTRY_HEAD = r'\[null,"([A-Za-z0-9_-]{25,44})"\](?:(?!\[null,"[A-Za-z0-9_-]{25,44}"\]).{0,400}?)'
FOLDER_ENTRY_RE = re.compile(ENTRY_HEAD + re.escape(FOLDER_MIME), re.S)
FILE_ENTRY_RE = re.compile(ENTRY_HEAD + r'"image/(?:png|jpeg|webp)"', re.S)
# Etiqueta que Drive adjunta a la carpeta en la página pública ("qsl1"...)
LABEL_RE = re.compile(r'\[\[\["(qsl\d)"')
FILENAME_RE = re.compile(r'"([^"]+\.(?:png|jpg|jpeg|webp))"')

ACTIVITY_TITLES = {
    "qsl1": "Actividad 1",
    "qsl2": "Actividad 2",
    "qsl3": "Actividad 3",
    "qsl4": "Actividad 4",
    "qsl5": "Actividad 5",
    "qsl6": "Actividad 6 (record)",
    "qsl7": "Actividad 7 (DMR)",
}


def now_iso():
    """Timestamp UTC en ISO-8601 con Z."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url, want_bytes=False):
    """Descarga una URL. Devuelve texto (o bytes) y lanza error con diagnóstico."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = resp.read()
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"Error {exc.code} al abrir {url}\n"
            + (
                "Si es 404, la carpeta no existe o ya no es pública."
                if exc.code == 404
                else "Revisa la conexión y que la carpeta esté compartida por enlace."
            )
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"No se pudo conectar con Drive: {exc.reason}") from exc
    return data if want_bytes else data.decode("utf-8", errors="replace")


def split_blocks(html, entry_re):
    """Parte el HTML en bloques 'entrada' y devuelve [(id, inicio, fin), ...]."""
    matches = list(entry_re.finditer(html))
    blocks = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(html)
        blocks.append((m.group(1), m.start(), end))
    return blocks


def parse_child_folders(html):
    """Devuelve {nombre_actividad: folder_id} a partir de la página pública."""
    blocks = split_blocks(html, FOLDER_ENTRY_RE)
    found = []
    for fid, start, end in blocks:
        label = LABEL_RE.search(html[start:end])
        found.append((label.group(1).lower() if label else None, fid))

    named = {name: fid for name, fid in found if name}
    if len(named) == len(found) and named:
        return named

    # Sin etiquetas legibles: Drive las ordena por nombre (qsl1..qsl7).
    fallback = {f"qsl{i + 1}": fid for i, (_, fid) in enumerate(found)}
    if fallback:
        print(
            "   aviso: no se han podido leer las etiquetas; se asigna por orden.",
            file=sys.stderr,
        )
    return fallback


def parse_files(html):
    """Devuelve [{'id':…, 'name':…}] con los archivos de imagen de la carpeta."""
    files = []
    seen = set()
    for fid, start, end in split_blocks(html, FILE_ENTRY_RE):
        if fid in seen:
            continue
        name_match = FILENAME_RE.search(html[start:end])
        if not name_match:
            continue
        seen.add(fid)
        files.append({"id": fid, "name": name_match.group(1)})
    return files


def file_size(file_id):
    """Tamaño en bytes del archivo, o 0 si no se puede averiguar."""
    try:
        req = urllib.request.Request(
            DOWNLOAD_URL.format(id=file_id),
            headers={"User-Agent": USER_AGENT},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return int(resp.headers.get("Content-Length") or 0)
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, OSError):
        return 0


def callsign_from_filename(name):
    """El nombre empieza por el indicativo: ea4hjz_pota1111.png -> EA4HJZ."""
    stem = name.rsplit(".", 1)[0]
    return stem.split("_", 1)[0].upper() or "?"


def build_index(root_id, with_sizes=True, verbose=False):
    """Recorre la carpeta pública y sus qsl1..qsl7."""
    print(f"→ leyendo {FOLDER_URL.format(id=root_id)}")
    html = fetch(FOLDER_URL.format(id=root_id))
    folders = parse_child_folders(html)
    if not folders:
        raise SystemExit(
            f"La carpeta {root_id} no parece pública o no contiene subcarpetas.\n"
            "Comprueba que el enlace 'cualquier persona con el enlace' sigue activo."
        )
    print(f"→ carpetas encontradas: {', '.join(sorted(folders))}")

    entries = []
    counts = {}
    for act in sorted(folders, key=lambda a: (len(a), a)):
        sub_id = folders[act]
        files = parse_files(fetch(FOLDER_URL.format(id=sub_id)))
        counts[act] = len(files)
        if verbose:
            print(f"   {act:<6} {len(files):>4} PNG")
        for f in files:
            entries.append(
                {
                    "call": callsign_from_filename(f["name"]),
                    "act": act,
                    "name": f["name"],
                    "id": f["id"],
                    "size": file_size(f["id"]) if with_sizes else 0,
                }
            )

    entries.sort(key=lambda e: (e["call"], e["act"], e["name"]))
    return {
        "version": 1,
        "generated_at": now_iso(),
        "folder_id": root_id,
        "folder_url": FOLDER_URL.format(id=root_id),
        "activities": {
            act: {"id": folders[act], "title": ACTIVITY_TITLES.get(act, act)}
            for act in sorted(folders, key=lambda a: (len(a), a))
        },
        "counts": counts,
        "total": len(entries),
        "entries": entries,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Genera qsl_index.json con los file IDs de la carpeta pública de Drive."
    )
    parser.add_argument("--folder-id", default=DEFAULT_FOLDER_ID, help="carpeta con qsl1..qsl7")
    parser.add_argument("--out", default=DEFAULT_OUT, help="fichero JSON de salida")
    parser.add_argument("--no-sizes", action="store_true", help="no consultar el tamaño de cada PNG")
    parser.add_argument("--dry-run", action="store_true", help="no escribe el JSON, solo informa")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    index = build_index(
        args.folder_id, with_sizes=not args.no_sizes, verbose=args.verbose
    )

    print(f"→ {index['total']} imagenes indexadas")
    for act, n in index["counts"].items():
        print(f"     {act:<6} {n:>4}")

    calls = len({e["call"] for e in index["entries"]})
    print(f"→ {calls} indicativos distintos")

    if args.dry_run:
        print("→ --dry-run: no se ha escrito ningún archivo")
        return 0

    out = Path(args.out)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"→ escrito {out} ({out.stat().st_size} bytes). Súbelo a git para publicar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
