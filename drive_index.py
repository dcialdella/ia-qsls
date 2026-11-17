#!/usr/bin/env python3
"""Genera qsl_index.json leyendo el HTML publico de la carpeta de Google Drive.

No usa la API de Drive ni credenciales: parsea el HTML que Drive renderiza en
la vista publica de la carpeta. Por eso mismo es fragil: si Drive cambia ese
HTML, el parseo puede devolver 0 ficheros. Por eso el script se niega a
escribir un indice que sea poorer que el que ya hay en disco.

Para listar los ficheros de cada actividad se usa `embeddedfolderview`, que
devuelve la carpeta completa en un unico HTML. La vista normal
(`/drive/folders/<id>`) solo incluye los primeros 50 ficheros: el resto los
carga el navegador por peticiones internas que aqui no se hacen. Con la vista
normal, una actividad con mas de 50 postcards se indexaba a medias.

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
from datetime import UTC, datetime
from html import unescape
from pathlib import Path

DEFAULT_FOLDER_ID = "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy"
FOLDER_URL = "https://drive.google.com/drive/folders/{id}"
EMBED_URL = "https://drive.google.com/embeddedfolderview?id={id}#list"
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
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.webp'}
# Vista embebida: cada fichero es <div class="flip-entry" id="entry-<id>">...
# ...<div class="flip-entry-title">nombre.png</div>
EMBED_ENTRY_RE = re.compile(
    r'<div class="flip-entry" id="entry-([A-Za-z0-9_-]{10,64})".*?'
    r'<div class="flip-entry-title">(.*?)</div>', re.DOTALL)
IMAGE_EXT_RE = re.compile(r'\.(?:png|jpe?g|webp)$', re.I)

# Las 7 actividades reales del proyecto. Un qsl8 en Drive no se publica.
ACTIVITY_TITLES = {f"qsl{i}": f"Actividad {i}" for i in range(1, 8)}
# Orden canónico de publicación.
ACTIVITY_ORDER = [f"qsl{i}" for i in range(1, 8)]
# Las QSL de record (qsl6) no son un QSO concreto: se les asigna siempre el
# último día de la expedición, aunque no haya qsl_log.json local.
ACT6_RECORD_DATE = '2026-11-15'

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


def parse_embedded_files(html):
    """Lista {id, name} del HTML de `embeddedfolderview` (carpeta completa)."""
    files = []
    seen = set()
    for fid, raw_name in EMBED_ENTRY_RE.findall(html):
        if fid in seen:
            continue
        name = unescape(raw_name).strip()
        if not IMAGE_EXT_RE.search(name):
            continue
        seen.add(fid)
        files.append({'id': fid, 'name': name})
    return files


def list_files(folder_id):
    """Devuelve TODOS los ficheros de una carpeta publica de Drive.

    `embeddedfolderview` entrega la lista completa (no pagina), mientras que la
    vista normal solo trae los primeros 50. Si la vista embebida no devolviera
    nada (cambio de Drive), se cae a la vista normal para no romper el flujo.
    """
    files = parse_embedded_files(fetch(EMBED_URL.format(id=folder_id)))
    if files:
        return files
    return parse_files(fetch(FOLDER_URL.format(id=folder_id)))


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


def iso_date(value):
    """Normaliza 20261113 / 2026-11-13 / 2026/11/13 a '2026-11-13' (o '')."""
    digits = re.sub(r'[^0-9]', '', str(value or ''))
    if len(digits) != 8:
        return ''
    return f"{digits[0:4]}-{digits[4:6]}-{digits[6:8]}"


NAME_DATE_RE = re.compile(r'(20\d{2})[-_]?(0[1-9]|1[0-2])[-_]?(0[1-9]|[12]\d|3[01])')


def date_from_name(name):
    """Fecha ISO que el nombre del PNG hereda del ADI, si la lleva.

    Es solo un respaldo para cuando no hay qsl_log.json (p.ej. otro clon):
    `..._es-0340-20261113.png` y `..._2026-11-13_...png` dan '2026-11-13'.
    """
    m = NAME_DATE_RE.search(str(name or ''))
    if not m:
        return ''
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"


def load_local_meta(base):
    """Mapas desde los qsl_log.json locales: indicativo real y fecha por PNG.

    Devuelve ({nombre_png: indicativo}, {nombre_png: fecha ISO}). Ambos vacíos
    si no hay logs: drive_index.py sigue funcionando contra Drive, pero pierde
    los indicativos con '/' y las fechas que no estén en el nombre del fichero.
    """
    known, dates = {}, {}
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
                if not isinstance(c, dict) or not c.get('archivo'):
                    continue
                key = str(c['archivo']).lower()
                if c.get('call'):
                    known[key] = str(c['call'])
                d = iso_date(c.get('fecha'))
                if d:
                    dates[key] = d
    return known, dates


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


def local_png_counts(base):
    """Nº de postcards en `<actividad>/QSLS`, por actividad.

    Drive se sincroniza desde estas carpetas con `rsync --delete`, así que los
    PNG locales son el oráculo de lo que el índice *debería* tener. Sirve para
    distinguir un recorte real (se borraron .adi y con ellos sus postcards) de
    un parseo incompleto de Drive, que es justo lo que hay que frenar. Las
    actividades sin carpeta local se omiten: no hay nada con que comparar.
    """
    counts = {}
    if not base:
        return counts
    for act in ACTIVITY_ORDER:
        d = Path(base) / act / "QSLS"
        if not d.is_dir():
            continue
        counts[act] = sum(1 for f in d.iterdir()
                          if f.is_file() and f.suffix.lower() in IMAGE_SUFFIXES)
    return counts


def check_regression(prev, idx, manifest, local):
    """Compara el índice nuevo con el anterior. Devuelve (errores, avisos).

    El índice sale de hacer scraping del HTML público de Drive: un cambio de
    HTML devolvería menos entradas (o 0) y publicaría una web incompleta. Por
    eso un recorte solo se acepta si está explicado:
      * la actividad ya no tiene ningún .adi (lo dice el manifiesto), o
      * el nuevo recuento coincide con los PNG locales, es decir, son
        postcards que rsync ya ha borrado también en Drive.

    El recorte "dentro" de una actividad que sigue activa (borrar un .adi o
    reprocesar con menos QSO) antes se confundía con un parseo fallido y
    bloqueaba el índice para siempre. Ese es el caso que cubre `local`.
    """
    errors, notes = [], []
    if not prev:
        return errors, notes

    prev_total = prev.get('total')
    prev_counts = prev.get('counts') if isinstance(prev.get('counts'), dict) else {}
    prev_acts = set(prev.get('activities') or {})
    new_acts = set(idx['activities'])
    lost = prev_acts - new_acts

    # Una actividad retirada solo es una pérdida esperada si el manifiesto la
    # declara sin .adi. Si desaparece del parseo pero el manifiesto dice que
    # sigue activa, es un fallo de lectura.
    if manifest is not None:
        unexpected_lost = {a for a in lost if int(manifest.get(a, 0) or 0) > 0}
    else:
        unexpected_lost = set()
    expected_lost = lost - unexpected_lost
    expected_drop = sum(int(prev_counts.get(a, 0) or 0) for a in expected_lost)

    # Recortes dentro de actividades que siguen activas: se dan por buenos si
    # el nuevo recuento es exactamente el de los PNG locales.
    verified_drop = 0
    verified = []
    for act, prev_n in prev_counts.items():
        if act in lost:
            continue
        prev_n = int(prev_n or 0)
        new_n = idx['counts'].get(act)
        if not isinstance(new_n, int) or new_n >= prev_n:
            continue
        if local.get(act) == new_n:
            verified_drop += prev_n - new_n
            verified.append(f"{act} {prev_n}->{new_n}")

    if verified:
        notes.append("recorte confirmado por los PNG locales: " + ", ".join(verified))
    if expected_lost:
        notes.append("actividades retiradas del índice (sin .adi según el manifiesto): "
                     f"{', '.join(sorted(expected_lost))} ({expected_drop} entradas)")
    if unexpected_lost:
        errors.append("actividades que el manifiesto da por activas pero han "
                      "desaparecido del índice: "
                      + ", ".join(sorted(unexpected_lost)) + ".")
    if (isinstance(prev_total, int)
            and idx['total'] < prev_total - expected_drop - verified_drop):
        errors.append(f"el nuevo índice tiene {idx['total']} entradas y el anterior "
                      f"{prev_total}, y solo {expected_drop + verified_drop} están "
                      "explicadas por actividades vaciadas o recortes confirmados "
                      "en el espejo local.")
    return errors, notes


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

    known, known_dates = load_local_meta(base) if base else ({}, {})

    entries = []
    counts = {}
    acts = {}
    for act, fid in folders:
        if act in empty:
            print(f"· {act}: sin .adi (manifiesto) -> no se publica")
            continue
        try:
            fl = list_files(fid)
        except FetchError as ex:
            # Falla una actividad: se avisa y se sigue con las demas, pero la
            # actividad se marca como fallida para no publicar un indice que
            # parece completo cuando no lo es.
            print(f"ERR {act}: {ex}")
            failed.append(act)
            continue
        counts[act] = len(fl)
        acts[act] = {'id': fid, 'title': ACTIVITY_TITLES[act]}
        for ff in fl:
            key = ff['name'].lower()
            entries.append({'call': calln(ff['name'], known), 'act': act,
                            'name': ff['name'], 'id': ff['id'],
                            'date': ACT6_RECORD_DATE if act == 'qsl6'
                                    else (known_dates.get(key) or date_from_name(ff['name']))})

    # Contadores por dia (clave ISO; '' = sin fecha, ya solo QSOs sin QSO_DATE).
    days = {}
    for e in entries:
        d = e.get('date') or ''
        days[d] = days.get(d, 0) + 1

    # Los tamanos se piden en paralelo: son N peticiones HEAD independientes y
    # a ~1,4 s cada una en serie serían horas con miles de postcards.
    def with_size(e):
        e['size'] = fsize(e['id'])
        return e

    if entries:
        with ThreadPoolExecutor(max_workers=SIZE_WORKERS) as pool:
            entries = list(pool.map(with_size, entries))

    entries.sort(key=lambda e: (e['call'], e['act'], e['name']))
    result = {
        'version': 2,
        'generated_at': datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'folder_id': folder_id,
        'folder_url': FOLDER_URL.format(id=folder_id),
        'activities': acts,
        'counts': counts,
        'days': {k: days[k] for k in sorted(days) if k} | ({'': days['']} if '' in days else {}),
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
        prev_acts = set(prev.get('activities') or {})
        new_acts = set(idx['activities'])

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

        errors, notes = check_regression(prev, idx, manifest,
                                         local_png_counts(SCRIPT_DIR))
        for note in notes:
            print(f"· {note}")
        if errors:
            for err in errors:
                print(f"ERROR: {err}", file=sys.stderr)
            print("       Parece un parseo fallido de Drive; no se escribe.", file=sys.stderr)
            print("       Usa --force si el recorte es intencionado.", file=sys.stderr)
            return 2

    if idx['total'] == 0 and not args.force:
        print("ERROR: 0 entradas. No se escribe un indice vacio (Drive pudo cambiar "
              "su HTML). Usa --force si de verdad quieres vaciar la web.")
        return 2

    out_path.write_text(json.dumps(idx, ensure_ascii=False, separators=(',', ':')) + '\n',
                        encoding='utf-8')
    print(f"→ {out_path}  total={idx['total']}")
    print("   Por actividad:")
    for k in ACTIVITY_ORDER:
        if k in idx['counts']:
            print(f"     {k}: {idx['counts'][k]}")
    print("   Por día:")
    for d, n in idx.get('days', {}).items():
        print(f"     {d or 'sin fecha'}: {n}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
