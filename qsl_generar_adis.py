#!/usr/bin/env python3
"""Genera archivos ADI de actividad (TOTA, POTA, DME, URE, LLOTA)
a partir de los ADI de cada carpeta QSL1..QSL5."""

import re
from pathlib import Path

BASE = Path(__file__).resolve().parent

# Configuración por QSL: lista de (formato, sig, sig_info)
# sig/sig_info = None → no se añaden campos de actividad (DME/URE)
# NOTA: los códigos TOTA cambiarán; estas referencias son provisionales hasta nuevo aviso.
CONFIG = {
    "qsl1": [
        ("tota", "TOTA", "EAR-1234"),
    ],
    "qsl2": [
        ("tota", "TOTA", "EAR-1234"),
        ("pota", "POTA", "ES-0340"),
    ],
    "qsl3": [
        ("pota", "POTA", "ES-0849"),
    ],
    "qsl4": [
        ("pota", "POTA", "ES-0850"),
    ],
    "qsl5": [
        ("llota", "LLOTA", "LLES-0214"),
    ],
}

# Estaciones URE que se añaden al final de cada archivo URE
# (pendiente de usar cuando se reactive el formato URE en CONFIG)
# URE_STATIONS = ["ea4huk", "ea3jaq", "ea4iwx", "ea4ghh"]

# Validación de estación y operador en cada QSO
REQUIRED_STATION = "EG9MM"
ALLOWED_OPERATORS = {"ea4huk", "ea4iwx", "ea4ghh", "ea3jaq"}
REVIEW_LINE = "REVISAR EL FORMATO DE OPERADOR y STATION"

ACT_FIELDS = re.compile(
    r"(?:<QSLMSG:\d+>[^<]*\s*)?"
    r"<MY_(?:SIG|POTA_REF|TOTA_REF|LLOTA_REF):\d+>[^<]*\s*"
    r"(?:<MY_SIG_INFO:\d+>[^<]*\s*)?"
    r"(?:<QSLMSG:\d+>[^<]*\s*)?",
    re.IGNORECASE,
)


def read_adi(path):
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"  ERROR: no se pudo leer {path}: {e}")
        return None


def split_records(content):
    """Devuelve (header, [record, ...]) — case-insensitive (WSJT-X usa <eoh>/<eor>)."""
    parts = re.split(r"<EOH>", content, maxsplit=1, flags=re.IGNORECASE)
    header = parts[0] + "<EOH>"
    body = parts[1] if len(parts) > 1 else ""
    records = [r.strip() for r in re.split(r"<EOR>", body, flags=re.IGNORECASE) if r.strip()]
    return header, records


def get_field(record, name):
    m = re.search(rf"<{name}:(\d+)>([^<]*)", record, re.IGNORECASE)
    return m.group(2).strip() if m else None


def validate_records(records):
    """Verifica que cada registro contenga campos ADIF mínimos."""
    errors = []
    for i, rec in enumerate(records, 1):
        if not get_field(rec, "CALL"):
            errors.append(f"registro {i}: sin CALL")
        if not get_field(rec, "QSO_DATE"):
            errors.append(f"registro {i}: sin QSO_DATE")
    return errors


def check_station_operator(records):
    """Verifica STATION_CALLSIGN=EG9MM y OPERATOR en la lista permitida.

    Devuelve lista de errores (vacía si todo OK).
    """
    errors = []
    for i, rec in enumerate(records, 1):
        station = get_field(rec, "STATION_CALLSIGN")
        if not station or station.upper() != REQUIRED_STATION:
            errors.append(
                f"registro {i}: STATION_CALLSIGN={station!r} (esperado {REQUIRED_STATION})"
            )
        operator = get_field(rec, "OPERATOR")
        if not operator or operator.lower() not in ALLOWED_OPERATORS:
            errors.append(
                f"registro {i}: OPERATOR={operator!r} "
                f"(permitidos: {', '.join(sorted(ALLOWED_OPERATORS))})"
            )
    return errors


def generate(qsl_dir, fmt_name, sig, sig_info, records):
    """Genera el contenido ADI para un formato dado.

    Quita referencias de actividad del input y agrega las del formato destino.
    """
    out_records = []

    for rec in records:
        # Quitar referencias de actividad existentes (POTA, SIG, etc.)
        r = ACT_FIELDS.sub("", rec).strip()
        # Limpiar líneas en blanco resultantes
        r = "\n".join(line for line in r.splitlines() if line.strip())

        if sig is not None and sig_info is not None:
            if sig == "TOTA":
                # TOTA: QSLMSG + MY_SIG + MY_SIG_INFO (sin MY_TOTA_REF)
                qslmsg = f"{sig} {sig_info}"
                act = (
                    f"<QSLMSG:{len(qslmsg)}>{qslmsg}\n"
                    f"<MY_SIG:{len(sig)}>{sig}\n"
                    f"<MY_SIG_INFO:{len(sig_info)}>{sig_info}\n"
                )
            else:
                # POTA/LLOTA: MY_SIG + MY_SIG_INFO + MY_XXX_REF
                ref_field = f"MY_{sig}_REF"
                act = (
                    f"<MY_SIG:{len(sig)}>{sig}\n"
                    f"<MY_SIG_INFO:{len(sig_info)}>{sig_info}\n"
                    f"<{ref_field}:{len(sig_info)}>{sig_info}\n"
                )
            r = r + "\n" + act

        out_records.append(r + "<EOR>")

    return out_records


def main():
    total = 0
    for qsl_name, formats in CONFIG.items():
        qsl_dir = BASE / qsl_name
        act_dir = qsl_dir / "ACTIVIDADES"
        if not act_dir.exists():
            print(f"  AVISO: no existe {act_dir}, se crea")
            act_dir.mkdir(parents=True, exist_ok=True)

        # Buscar ADI de entrada
        adi_files = sorted(qsl_dir.glob("*.adi"))
        if not adi_files:
            print(f"  {qsl_name}: sin archivos .adi, se omite")
            continue

        # Borrar archivos anteriores de ACTIVIDADES
        for old in act_dir.glob("*"):
            if old.is_file():
                old.unlink()

        # Procesar cada ADI por separado
        for adi in adi_files:
            content = read_adi(adi)
            if content is None:
                continue

            header, records = split_records(content)
            if not records:
                print(f"  {qsl_name}/{adi.name}: sin registros QSO")
                continue

            # Validar registros
            errors = validate_records(records)
            if errors:
                for err in errors:
                    print(f"  AVISO: {qsl_name}/{adi.name}: {err}")

            # Validar STATION_CALLSIGN y OPERATOR
            so_errors = check_station_operator(records)
            if so_errors:
                for err in so_errors:
                    print(f"  AVISO: {qsl_name}/{adi.name}: {err}")

            stem = adi.stem  # nombre sin extensión

            # Generar cada formato
            for fmt_name, sig, sig_info in formats:
                out_records = generate(qsl_dir, fmt_name, sig, sig_info, records)
                out_path = act_dir / f"{stem}-{fmt_name}.adi"
                out_content = header + "\n\n" + "\n".join(out_records) + "\n"

                # Corregir cabecera (primera línea) según formato
                first_line, sep, rest = out_content.partition("\n")
                if sig and sig_info:
                    station = get_field(records[-1], "STATION_CALLSIGN") or "EG9MM"
                    first_line = f"ADIF export for {station}: {sig.upper()} {sig_info}"
                else:
                    first_line = f"ADIF export for {fmt_name.upper()}"
                out_content = first_line + sep + rest

                # Si STATION/OPERATOR no válidos, avisar arriba de todo
                if so_errors:
                    out_content = REVIEW_LINE + "\n" + out_content
                    print(f"  {qsl_name}/{out_path.name}: añadido '{REVIEW_LINE}'")

                out_path.write_text(out_content, encoding="utf-8")
                print(f"  {qsl_name}/{out_path.name}: {len(out_records)} QSOS")
                total += 1

    print(f"\nTotal: {total} archivos generados")


if __name__ == "__main__":
    main()
