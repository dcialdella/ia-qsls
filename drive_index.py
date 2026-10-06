#!/usr/bin/env python3
"""Genera qsl_index.json leyendo el HTML publico de la carpeta de Google Drive.

No usa la API de Drive ni credenciales: parsea los <a> que Drive renderiza en
la vista publica de la carpeta. Por eso mismo es fragil: si Drive cambia ese
HTML, el parseo puede devolver 0 ficheros. Por eso el script se niega a
escribir un indice que sea poorer que el que ya hay en disco.

Tambien acepta un manifiesto local (qsl_manifest.json) para descartar las
actividades que ya no tienen ningun .adi, de modo que la web no ofrezca
postcards de actividades vaciadas. Sin manifiesto, se comporta como antes.
"""
import argparse
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_FOLDER_ID = "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy"
FOLDER_URL = "https://drive.google.com/drive/folders/{id}"
DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id={id}"
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
TIMEOUT = 45
FETCH_RETRIES = 3
SIZE_WORKERS = 8
FOLDER_MIME = "application/vnd.google-apps.folder"
ENTRY_HEAD = (r'\[null,"([A-Za-z0-9_-]{25,44})"\]'
              r'(?:(?!\[null,"[A-Za-z0-9_-]{25,44}"\]).{0,400}?)')
FOLDER_ENTRY_RE = re.compile(ENTRY_HEAD + re.escape(FOLDER_MIME), re.DOTALL)
FILE_ENTRY_RE = re.compile(ENTRY_HEAD + r'"image/(?:png|jpeg|webp)"', re.DOTALL)
LABEL_RE = re.compile(r'\[\[\["(qsl\d+)"')
FILENAME_RE = re.compile(r'"([^"]+\.(?:png|jpg|jpeg|webp))"')

# Las 7 actividades reales del proyecto. Un qsl8 en Drive no se publica.
ACTIVITY_TITLES = {f"qsl{i}": f"Actividad {i}" for i in range(1, 8)}
# Orden canónico de publicación.
ACTIVITY_ORDER = [f"qsl{i}" for i in range(1, 8)]

SCRIPT_DIR = Path(__file__).resolve().parent
MANIFEST_NAME = "qsl_manifest.json"
INDEX_NAME = "qsl_index.json"


class FetchError(RuntimeError):
    """Fallo de red al pedir una pagina de Drive (distinto de un parseo vacio)."""


def fetch(url):
    """Descarga `url` con reintentos. Lanza FetchError si no hay forma de obtenerla.

    Importante: relanza la excepcion original en lugar de SystemExit, para que
    quien llama pueda decidir si continua o aborta.
    """
    last = None
    for attempt in range(1, FETCH_RETRIES + 1):
        req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:  # noqa: BLE001 - se reintenta y luego se propaga
            last = e
            if attempt < FETCH_RETRIES:
                continue
    raise FetchError(f"{url}: {last}") from last


def split_blocks(html, entry_re):
    m = list(entry_re.finditer(html))
    b = []
    for i, x in enumerate(m):
        end = m[i + 1].start() if i + 1 < len(m) else len(html)
        b.append((x.group(1), x.start(), end))
    return b


def parse_folders(html):
    """Devuelve [(actividad, id_de_carpeta)] para las 7 actividades conocidas."""
    pairs = []
    seen_id = set()
    for fid, s, e in split_blocks(html, FOLDER_ENTRY_RE):
        if fid in seen_id:
            continue
        seen_id.add(fid)
        lab = LABEL_RE.search(html[s:e])
        if not lab:
            continue
        act = lab.group(1).lower()
        if act not in ACTIVITY_TITLES:
            continue  # qsl8, carpetas ajenas: no se publican
        pairs.append((act, fid))
    pairs.sort(key=lambda x: ACTIVITY_ORDER.index(x[0]))
    return pairs


def parse_files(html):
    files = []
    seen = set()
    for fid, s, e in split_blocks(html, FILE_ENTRY_RE):
        if fid in seen:
            continue
        nm = FILENAME_RE.search(html[s:e])
        if not nm:
            continue
        seen.add(fid)
        files.append({'id': fid, 'name': nm.group(1)})
    return files


def fsize(fid):
    """Tamano en bytes via HEAD (no descarga el cuerpo).

    Drive responde con el tamano real, pero en algunos casos (p.ej. el aviso
    de "can't scan for viruses" en ficheros grandes) sirve una pagina HTML de
    intersticio: se detecta comprobando el Content-Type y se devuelve 0.
    """
    url = DOWNLOAD_URL.format(id=fid)
    for attempt in range(1, FETCH_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT}, method='HEAD')
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                ctype = r.headers.get('Content-Type') or ''
                if not ctype.startswith('image/'):
                    return 0
                return int(r.headers.get('Content-Length') or 0)
        except Exception:  # noqa: BLE001 - un tamano desconocido no es fatal
            if attempt < FETCH_RETRIES:
                continue
    return 0


def calln(nm, known=None):
    """Indicativo de un PNG, usando el log local como fuente de verdad.

    Los PNG se nombran {indicativo}_{nombre_adi}.png, y `sanitize_filename_component`
    convierte en '_' todo lo que no sea alfanumerico. Eso hace el NOMBRE AMBIGUO:
    en 'ea4hjz_qsl1_ejemplo.png' no se sabe si el indicador es 'ea4hjz' o
    'ea4hjz_qsl1', y un indicativo portable como EA5/XZZ se vuelve EA5_XZZ, con un
    '_' que se confunde con el separador. Cualquier heuristica sobre la cadena
    parte mal, y asi todas las estaciones moviles de EA5 acababan agrupadas bajo
    'EA5' en la web.

    Por eso `known` (el mapa nombre -> callsign real extraido de los qsl_log.json
    locales, que guardan el indicativo sin transformar) es la via principal. Solo
    si no esta disponible se recurre a la heuristica, que al menos no inventa.
    """
    if known:
        real = known.get(nm.lower())
        if real:
            return str(real).upper()

    # Fallback: primer componente. Es la mejor aproximacion cuando no hay log
    # (p.ej. indexando Drive desde otro clon del repo).
    stem = nm.rsplit('.', 1)[0]
    call = stem.split('_', 1)[0]
    if call.count('_') == 1:
        head, _, tail = call.partition('_')
        if (re.fullmatch(r'[A-Z0-9]{1,4}', head)
                and re.fullmatch(r'[A-Z0-9]{2,6}', tail)
                and not tail.isdigit()):
            call = f"{head}/{tail}"
    return call.upper() or '?'


def load_known_calls(base):
    """Mapa {nombre_png: indicativo_real} desde los qsl_log.json locales.

    Devuelve {} si no hay logs: drive_index.py sigue funcionando contra Drive,
    pero pierde los indicativos con '/' (y solo esos).
    """
    known = {}
    for act in ACTIVITY_ORDER:          # act ya es 'qsl1'... no un número
        log = Path(base) / act / "qsl_log.json"
        if not log.exists():
            continue
        try:
            with open(log, encoding='utf-8') as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        for entry in data.values():
            if not isinstance(entry, dict):
                continue
            for c in entry.get('contactos') or []:
                if isinstance(c, dict) and c.get('archivo') and c.get('call'):
                    known[str(c['archivo']).lower()] = str(c['call'])
    return known


def load_manifest(path):
    """Carga el manifiesto de actividades activas, o None si no existe/inválido.

    El manifiesto lo escribe qsl_generator.py: Mapping {actividad: nº de .adi}.
    """
    p = Path(path)
    if not p.exists():
        return None
    try:
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    counts = data.get('adi_counts')
    if not isinstance(counts, dict):
        return None
    # Filtrar solo actividades válidas, pero mantener todo el dict para acceder a 'generador'
    filtered = {k: v for k, v in counts.items() if k in ACTIVITY_TITLES}
    # Añadir generador si existe
    if 'generador' in data:
        filtered['generador'] = data['generador']
    return filtered


def build_index(folder_id, manifest=None, base=None, generator_version=None):
    """Construye el diccionario del indice leyendo Drive.

    Si `manifest` no es None, las actividades con 0 .adi se omiten por completo
    (no se publica su id ni sus ficheros), aunque en Drive sigan estando.
    """
    html = fetch(FOLDER_URL.format(id=folder_id))
    folders = parse_folders(html)

    empty, failed = set(), []
    if manifest is not None:
        for act in ACTIVITY_ORDER:
            if int(manifest.get(act, 0) or 0) == 0:
                empty.add(act)

    known = load_known_calls(base) if base else {}

    entries = []
    counts = {}
    acts = {}
    for act, fid in folders:
        if act in empty:
            print(f"· {act}: sin .adi (manifiesto) -> no se publica")
            continue
        try:
            sh = fetch(FOLDER_URL.format(id=fid))
        except FetchError as ex:
            # Falla una actividad: se avisa y se sigue con las demas, pero la
            # actividad se marca como fallida para no publicar un indice que
            # parece completo cuando no lo es.
            print(f"ERR {act}: {ex}")
            failed.append(act)
            continue
        fl = parse_files(sh)
        counts[act] = len(fl)
        acts[act] = {'id': fid, 'title': ACTIVITY_TITLES[act]}
        for ff in fl:
            entries.append({'call': calln(ff['name'], known), 'act': act,
                            'name': ff['name'], 'id': ff['id']})

    # Los tamanos se piden en paralelo: son N peticiones HEAD independientes y
    # a ~1,4 s cada una en serie serían horas con miles de postcards.
    def with_size(e):
        e['size'] = fsize(e['id'])
        return e

    if entries:
        with ThreadPoolExecutor(max_workers=SIZE_WORKERS) as ex:
            entries = list(ex.map(with_size, entries))

    entries.sort(key=lambda e: (e['call'], e['act'], e['name']))
    result = {
        'version': 2,
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'folder_id': folder_id,
        'folder_url': FOLDER_URL.format(id=folder_id),
        'activities': acts,
        'counts': counts,
        'total': len(entries),
        'entries': entries,
    }
    if generator_version:
        result['generador'] = generator_version
    return result, failed, empty


def read_existing(path):
    """Indice actual en disco, o None si no existe/no se puede leer."""
    p = Path(path)
    if not p.exists():
        return None
    try:
        with open(p, encoding='utf-8') as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--folder-id', default=DEFAULT_FOLDER_ID,
                    help='ID de la carpeta de Google Drive (por defecto, la de EG9MM).')
    ap.add_argument('--out', default=str(SCRIPT_DIR / INDEX_NAME),
                    help=f'Ruta del JSON de salida (por defecto {INDEX_NAME} junto al script).')
    ap.add_argument('--manifest', default=str(SCRIPT_DIR / MANIFEST_NAME),
                    help=f'Manifiesto de actividades activas (por defecto {MANIFEST_NAME}; '
                         'si no existe, se indexa todo lo que haya en Drive).')
    ap.add_argument('--force', action='store_true',
                    help='Escribe el indice aunque pierda entradas o actividades '
                         'respecto al que ya hay en disco.')
    args = ap.parse_args()

    out_path = Path(args.out)
    manifest = load_manifest(args.manifest)
    if manifest is None:
        print(f"AVISO: sin manifiesto válido en {args.manifest}; "
              f"se publica todo lo que haya en Drive.")

    # Extraer versión del generador del manifiesto
    generator_version = manifest.get('generador') if manifest else None

    try:
        idx, failed, _empty = build_index(args.folder_id, manifest, base=SCRIPT_DIR, generator_version=generator_version)
    except FetchError as ex:
        print(f"ERROR: no se pudo leer la carpeta de Drive: {ex}", file=sys.stderr)
        print("       Revisa el --folder-id y la conexión, y reintenta.", file=sys.stderr)
        return 2

    # --- Salvaguardas: nunca sobrescribir un indice bueno por uno peor ---
    prev = read_existing(out_path)
    if not args.force and prev:
        prev_total = prev.get('total')
        prev_counts = prev.get('counts') if isinstance(prev.get('counts'), dict) else {}
        prev_acts = set(prev.get('activities') or {})
        new_acts = set(idx['activities'])
        lost = prev_acts - new_acts

        if failed:
            print(f"ERROR: fallo de red en {', '.join(failed)}; no se escribe el indice.")
            print("       Reintenta en unos segundos, o usa --force si es intencionado.")
            return 2

        if idx['total'] == 0:
            print("ERROR: 0 entradas. No se escribe un indice vacio: lo mas probable es "
                  "que Drive haya cambiado el HTML que se hace scraping.")
            print("       Revisa drive_index.py y usa --force solo si de verdad "
                  "quieres vaciar la web.")
            return 2

        # Perder TODAS las actividades no puede ser un vaciado intencionado.
        if prev_acts and not new_acts:
            print(f"ERROR: el indice anterior tenia {len(prev_acts)} actividades y el nuevo "
                  f"ninguna. No se escribe.")
            return 2

        # Lo que el manifiesto declara vaciado es una perdida esperada: no cuenta
        # como parseo fallido. Sin esto, vaciar una actividad a proposito haria
        # que el indice se negase a actualizarse nunca mas.
        expected_drop = sum(int(prev_counts.get(a, 0) or 0) for a in lost)
        if isinstance(prev_total, int) and idx['total'] < prev_total - expected_drop:
            print(f"ERROR: el nuevo indice tiene {idx['total']} entradas y el anterior "
                  f"{prev_total}, y solo {expected_drop} son de actividades vaciadas por "
                  f"manifiesto. Parece un parseo fallido de Drive; no se escribe.")
            print("       Usa --force si el recorte es intencionado.")
            return 2

        if lost:
            print(f"· actividades retiradas del indice (sin .adi segun el manifiesto): "
                  f"{', '.join(sorted(lost))} ({expected_drop} entradas)")

    if idx['total'] == 0 and not args.force:
        print("ERROR: 0 entradas. No se escribe un indice vacio (Drive pudo cambiar "
              "su HTML). Usa --force si de verdad quieres vaciar la web.")
        return 2

    out_path.write_text(json.dumps(idx, ensure_ascii=False, separators=(',', ':')) + '\n',
                        encoding='utf-8')
    print(f"→ {out_path}  total={idx['total']}")
    for k in ACTIVITY_ORDER:
        if k in idx['counts']:
            print(f"   {k}: {idx['counts'][k]}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
