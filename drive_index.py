#!/usr/bin/env python3
"""
Constructor del índice público de QSLs (qsl_index.json).

Los enlaces de descarga de Google Drive no se pueden construir a partir del
nombre del archivo: siempre llevan el 'file id'
(https://drive.google.com/uc?export=download&id=<ID>). Por eso este script
recorre la carpeta de Drive con la API v3 usando una *cuenta de servicio* y
guarda el nombre + el id de cada PNG.

Con ese JSON la página index.html busca por prefijo del nombre de archivo
(que empieza por el indicativo, ver unique_filenames en qsl_generator.py) y
ofrece enlaces de descarga directa.

Requisitos (una sola vez):
  1. Google Cloud > crear proyecto > IAM > Cuentas de servicio > Crear
     (sin roles de GCP).
  2. Descargar la clave JSON y guardarla en la raíz como 'drive_creds.json'
     (está en .gitignore: no se sube nunca).
  3. Compartir la carpeta de Drive 'QSL' (o 'QSLs') con el correo de la cuenta
     de servicio como Lector. Compartir por enlace NO da acceso a la API.
  4. pip install google-auth

Uso:
    python3 drive_index.py                        # usa la carpeta de EG9MM por defecto
    python3 drive_index.py --folder-id <ID>        # otra carpeta 'QSLs'
    python3 drive_index.py --parent-id <ID>        # busca 'QSLs' dentro de <ID>
    python3 drive_index.py --dry-run               # no escribe, solo informa
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"
PAGE_SIZE = 1000
DEFAULT_CREDS = "drive_creds.json"
DEFAULT_OUT = "qsl_index.json"
DEFAULT_FOLDER_NAME = "QSLs"
FOLDER_MIME = "application/vnd.google-apps.folder"
IMAGE_MIMES = ("image/png", "image/jpeg", "image/webp")

# Carpeta pública de EG9MM con las subcarpetas qsl1..qsl7:
# https://drive.google.com/drive/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy
DEFAULT_FOLDER_ID = "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy"

# Actividad -> etiqueta legible para la página web
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


def build_session(creds_path):
    """Devuelve una AuthorizedSession autenticada como la cuenta de servicio."""
    try:
        from google.auth.transport.requests import AuthorizedSession
        from google.oauth2 import service_account
    except ImportError as exc:
        raise SystemExit(
            "Falta la dependencia 'google-auth'. Instálala con:\n"
            "    pip install google-auth"
        ) from exc

    path = Path(creds_path)
    if not path.is_file():
        raise SystemExit(
            f"No encuentro las credenciales '{path}'.\n"
            "Descarga la clave JSON de la cuenta de servicio y guárdala con ese nombre."
        )

    scopes = ["https://www.googleapis.com/auth/drive.readonly"]
    creds = service_account.Credentials.from_service_account_file(
        str(path), scopes=scopes
    )
    return AuthorizedSession(creds), creds.signer_email


def api_get(session, params, label):
    """GET paginado a la API de Drive. Devuelve la lista de 'files'."""
    items = []
    page_token = None
    while True:
        query = dict(params, pageSize=PAGE_SIZE)
        if page_token:
            query["pageToken"] = page_token
        resp = session.get(DRIVE_FILES_URL, params=query, timeout=60)
        if resp.status_code != 200:
            raise SystemExit(
                f"Error {resp.status_code} de la API de Drive ({label}):\n"
                f"{resp.text[:600]}\n"
                "Comprueba que la carpeta está compartida con la cuenta de servicio."
            )
        payload = resp.json()
        items.extend(payload.get("files", []))
        page_token = payload.get("nextPageToken")
        if not page_token:
            return items


def find_child_folder(session, parent_id, name):
    """Localiza una subcarpeta por nombre exacto (case-insensitive)."""
    files = api_get(
        session,
        {
            "q": f"'{parent_id}' in parents and trashed = false",
            "fields": "nextPageToken, files(id, name, mimeType)",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        },
        f"buscando carpeta '{name}'",
    )
    for f in files:
        if f.get("mimeType") == FOLDER_MIME and f.get("name", "").lower() == name.lower():
            return f["id"]
    found = [f.get("name") for f in files if f.get("mimeType") == FOLDER_MIME]
    raise SystemExit(
        f"No encuentro la carpeta '{name}' dentro de {parent_id}.\n"
        f"Carpetas daughters encontradas: {found or '(ninguna)'}"
    )


def list_images(session, folder_id):
    """Lista los PNG/JPG de una carpeta de Drive, paginando."""
    files = api_get(
        session,
        {
            "q": f"'{folder_id}' in parents and trashed = false",
            "fields": "nextPageToken, files(id, name, mimeType, size, modifiedTime)",
            "orderBy": "name",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        },
        f"listando imágenes de {folder_id}",
    )
    return [f for f in files if f.get("mimeType") in IMAGE_MIMES]


def callsign_from_filename(name):
    """El nombre del archivo empieza por el indicativo: ea4hjz_pota1111.png -> EA4HJZ."""
    stem = name.rsplit(".", 1)[0]
    prefix = stem.split("_", 1)[0]
    return prefix.upper() or "?"


def build_index(session, qsls_id, verbose=False):
    """Recorre qsl1..qsl7 dentro de 'qsls_id' y devuelve el índice."""
    children = api_get(
        session,
        {
            "q": f"'{qsls_id}' in parents and trashed = false",
            "fields": "nextPageToken, files(id, name, mimeType)",
            "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true",
        },
        f"listando carpetas de {qsls_id}",
    )
    folders = {
        f["name"].lower(): f
        for f in children
        if f.get("mimeType") == FOLDER_MIME and f.get("name", "").lower().startswith("qsl")
    }
    if not folders:
        raise SystemExit(
            f"La carpeta {qsls_id} no contiene subcarpetas qsl1..qsl7.\n"
            "Indica --folder-id con la carpeta 'QSLs' directamente."
        )

    entries = []
    counts = {}
    for key in sorted(folders):
        folder = folders[key]
        images = list_images(session, folder["id"])
        counts[folder["name"]] = len(images)
        if verbose:
            print(f"   {folder['name']:<6} {len(images):>4} PNG")
        for img in images:
            entries.append(
                {
                    "call": callsign_from_filename(img["name"]),
                    "act": folder["name"].lower(),
                    "name": img["name"],
                    "id": img["id"],
                    "size": int(img.get("size") or 0),
                    "modified": img.get("modifiedTime", ""),
                }
            )

    entries.sort(key=lambda e: (e["call"], e["act"], e["name"]))
    return {
        "version": 1,
        "generated_at": now_iso(),
        "folder_id": qsls_id,
        "activities": {
            name: {"id": folders[name]["id"], "title": ACTIVITY_TITLES.get(name, name)}
            for name in sorted(folders)
        },
        "counts": counts,
        "total": len(entries),
        "entries": entries,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Genera qsl_index.json con los file IDs de Google Drive."
    )
    parser.add_argument("--creds", default=DEFAULT_CREDS, help="clave JSON de la cuenta de servicio")
    parser.add_argument(
        "--folder-id",
        default=DEFAULT_FOLDER_ID,
        help="ID de la carpeta con qsl1..qsl7 (por defecto, la carpeta pública de EG9MM)",
    )
    parser.add_argument("--parent-id", help="ID de la carpeta padre; se busca --folder-name dentro")
    parser.add_argument("--folder-name", default=DEFAULT_FOLDER_NAME, help="nombre de la carpeta a buscar")
    parser.add_argument("--out", default=DEFAULT_OUT, help="fichero JSON de salida")
    parser.add_argument("--dry-run", action="store_true", help="no escribe el JSON, solo informa")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    session, email = build_session(args.creds)
    print(f"→ autenticado como {email}")

    if args.parent_id:
        qsls_id = find_child_folder(session, args.parent_id, args.folder_name)
    else:
        qsls_id = args.folder_id
    print(f"→ carpeta QSLs: {qsls_id}")

    index = build_index(session, qsls_id, verbose=args.verbose)
    print(f"→ {index['total']} imagenes indexadas")
    for name, n in index["counts"].items():
        print(f"     {name:<6} {n:>4}")

    if args.dry_run:
        print("→ --dry-run: no se ha escrito ningún archivo")
        return 0

    out = Path(args.out)
    out.write_text(json.dumps(index, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"→ escrito {out} ({out.stat().st_size} bytes). Súbelo a git para publicar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
