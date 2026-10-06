#!/usr/bin/env python3
"""Genera archivos ADI de actividad (TOTA, POTA, DME, URE, LLOTA)
a partir de los ADI de cada carpeta QSL1..QSL5."""

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

# Configuración por QSL: lista de (formato, sig, sig_info)
# sig/sig_info = None → no se añaden campos de actividad (DME/URE)
CONFIG = {
    "qsl1": [
        ("tota", "TOTA", "TO-1234"),
        ("dme", None, None),
    ],
    "qsl2": [
        ("tota", "TOTA", None),       # número pendiente
        ("pota", "POTA", "ES-0340"),
        ("dme", None, None),
    ],
    "qsl3": [
        ("pota", "POTA", "ES-0849"),
        ("ure", None, None),
    ],
    "qsl4": [
        ("pota", "POTA", "ES-0850"),
        ("ure", None, None),
    ],
    "qsl5": [
        ("llota", "LLOTA", "LLES-0214"),
        ("ure", None, None),
    ],
}

# Estaciones URE que se añaden al final de cada archivo URE
URE_STATIONS = ["ea4huk", "ea3jaq", "ea4iwx", "ea4ghh"]

ACT_FIELDS = re.compile(
    r"<MY_SIG:\d+>[^<]*\s*"
    r"(?:<MY_SIG_INFO:\d+>[^<]*\s*)?"
    r"(?:<MY_POTA_REF:\d+>[^<]*\s*)?",
    re.IGNORECASE,
)


def read_adi(path):
    return path.read_text(encoding="utf-8", errors="replace")


def split_records(content):
    """Devuelve (header, [record, ...])."""
    parts = content.split("<EOH>", 1)
    header = parts[0] + "<EOH>"
    body = parts[1] if len(parts) > 1 else ""
    records = [r.strip() for r in body.split("<EOR>") if r.strip()]
    return header, records


def get_field(record, name):
    m = re.search(rf"<{name}:(\d+)>([^<]*)", record, re.IGNORECASE)
    return m.group(2) if m else None


def make_ure_record(template, callsign):
    """Crea un registro URE a partir de la plantilla (último QSO)."""
    rec = template
    # Reemplazar el CALL
    old_call = get_field(rec, "CALL")
    if old_call:
        rec = re.sub(
            rf"<CALL:{len(old_call)}>{re.escape(old_call)}",
            f"<CALL:{len(callsign)}>{callsign}",
            rec,
            flags=re.IGNORECASE,
        )
    # Añadir <EOR> al final si no lo tiene
    if not rec.rstrip().endswith("<EOR>"):
        rec = rec.rstrip() + "<EOR>"
    return rec


def generate(qsl_dir, fmt_name, sig, sig_info, records):
    """Genera el contenido ADI para un formato dado.

    Respeta las líneas originales y agrega las de la actividad si corresponde.
    """
    out_records = []

    for rec in records:
        r = rec.strip()

        if sig is not None and sig_info is not None:
            # Agregar campos de actividad antes del <EOR>
            act = (
                f"<MY_SIG:{len(sig)}>{sig} "
                f"<MY_SIG_INFO:{len(sig_info)}>{sig_info} "
            )
            r = r + act

        out_records.append(r + "<EOR>")

    # Para URE: añadir las 4 estaciones al final usando el último QSO
    if fmt_name == "ure" and records:
        last = records[-1]
        for call in URE_STATIONS:
            out_records.append(make_ure_record(last, call).strip())

    return out_records


def main():
    total = 0
    for qsl_name, formats in CONFIG.items():
        qsl_dir = BASE / qsl_name
        act_dir = qsl_dir / "ACTIVIDAD"
        if not act_dir.exists():
            print(f"  AVISO: no existe {act_dir}, se crea")
            act_dir.mkdir(parents=True, exist_ok=True)

        # Buscar ADI de entrada (excluir los de ACTIVIDAD)
        adi_files = sorted(
            f for f in qsl_dir.glob("*.adi")
            if "ACTIVIDAD" not in f.parts
        )
        if not adi_files:
            print(f"  {qsl_name}: sin archivos .adi, se omite")
            continue

        # Borrar archivos anteriores de ACTIVIDAD
        for old in act_dir.glob("*"):
            if old.is_file():
                old.unlink()

        # Procesar cada ADI por separado
        for adi in adi_files:
            content = read_adi(adi)
            header, records = split_records(content)
            if not records:
                print(f"  {qsl_name}/{adi.name}: sin registros QSO")
                continue

            stem = adi.stem  # nombre sin extensión

            # Generar cada formato
            for fmt_name, sig, sig_info in formats:
                out_records = generate(qsl_dir, fmt_name, sig, sig_info, records)
                out_path = act_dir / f"{stem}-{fmt_name}.adi"
                out_content = header + "\n\n" + "\n".join(out_records) + "\n"

                # Corregir cabecera según formato
                if sig and sig_info:
                    out_content = re.sub(
                        r"^.*$",
                        f"ADIF export for {get_field(records[-1], 'STATION_CALLSIGN') or 'EG9MM'}: {sig.upper()} {sig_info}",
                        out_content,
                        count=1,
                    )
                else:
                    out_content = re.sub(
                        r"^.*$",
                        f"ADIF export for {fmt_name.upper()}",
                        out_content,
                        count=1,
                    )

                out_path.write_text(out_content, encoding="utf-8")
                print(f"  {qsl_name}/{out_path.name}: {len(out_records)} QSOS")
                total += 1

    print(f"\nTotal: {total} archivos generados")


if __name__ == "__main__":
    main()
