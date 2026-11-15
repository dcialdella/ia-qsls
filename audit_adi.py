#!/usr/bin/env python3
"""Auditoría de integridad de los ADI de qsl1-qsl5 y qsl7 (v2).

Usa los rangos de banda de ADIF 3.1.5 y comprueba: campos obligatorios,
BAND/FREQ coherentes, modo/submodo, formato de fecha/hora, referencias de
actividad, estación/operador y duplicados internos.
"""
import glob
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from qsl_generator import ADIFParser

FOLDERS = [f"qsl{n}" for n in range(1, 6)] + ["qsl7"]

# ADIF 3.1.5: nombre canónico en minúsculas y rango en MHz
BANDS = {
    "2190m": (0.1357, 0.1378), "630m": (0.472, 0.479), "560m": (0.501, 0.504),
    "160m": (1.8, 2.0), "80m": (3.5, 4.0), "60m": (5.06, 5.45), "40m": (7.0, 7.3),
    "30m": (10.1, 10.15), "20m": (14.0, 14.35), "17m": (18.068, 18.168),
    "15m": (21.0, 21.45), "12m": (24.89, 24.99), "10m": (28.0, 29.7),
    "6m": (50, 54), "4m": (68, 74), "2m": (144, 148), "1.25m": (222, 225),
    "70cm": (420, 450), "33cm": (902, 928), "23cm": (1240, 1300),
    "13cm": (2300, 2450), "9cm": (3300, 3500), "6cm": (5650, 5925),
    "3cm": (10.0, 10.5), "1.25cm": (24.0, 24.25), "6mm": (47.0, 47.2),
    "4mm": (75.5, 81.0), "2.5mm": (122.25, 123.0), "2mm": (134.0, 141.0),
    "1mm": (241.0, 250.0),
}
VALID_MODES = {
    "SSB", "CW", "FM", "AM", "RTTY", "FT8", "FT4", "MFSK", "PSK31", "PSK63",
    "DIGITALVOICE", "DSTAR", "C4FM", "JT65", "JT9", "WSPR", "OLIVIA", "DOMINO",
    "HELL", "CONTESTIA", "MT63", "PACKET", "PACTOR", "TOR", "ARDOP", "JS8",
    "ATV", "FAX", "SSTV", "MSK144", "QRA64", "FST4", "FST4W", "Q65", "FSK441",
    "JT4", "JT6M", "JT44", "ISCAT", "SIM31", "ROS", "CHIP", "THOR", "THROB",
    "CLOVER", "RTTYM", "DQPSK", "MFSK16", "MFSK32", "MFSK64", "PSK",
}
SUBMODES = {
    "SSB": {"USB", "LSB"},
    "MFSK": {"FT4", "FT2", "FST4", "FST4W", "JT4", "JT6M", "JT44", "JT65",
             "JT9", "MSK144", "Q65", "QRA64", "ISCAT", "MFSK16", "MFSK32",
             "MFSK64", "MFSK128", "T10", "JTMS"},
    "DIGITALVOICE": {"DMR", "DSTAR", "C4FM", "FUSION", "DPMR", "NXDN", "P25",
                     "TETRA", "M17"},
    "RTTY": {"ASCI", "BAUDOT", "FSK", "AMTORFEC", "NAVTEX", "SITORB", "RTTYM"},
}
CALL_RE = re.compile(r"^(?:[A-Z0-9]{1,3}/)?[A-Z0-9]{1,3}[0-9][A-Z0-9]{0,5}(?:/[A-Z0-9]{1,4})?$")

EXPECTED_SIG = {
    "qsl1": {("TOTA", "EAR-1901")},
    "qsl2": {("POTA", "ES-0340"), ("TOTA", "EAR-1902")},
    "qsl3": {("POTA", "ES-0849")},
    "qsl4": {("POTA", "ES-0850")},
    "qsl5": {("LLOTA", "LLES-0214")},
    "qsl7": None,
}


def band_from_freq(freq):
    try:
        f = float(str(freq).strip())
    except (TypeError, ValueError):
        return None
    if f > 1000:
        f /= 1000.0
    for name, (lo, hi) in BANDS.items():
        if lo <= f <= hi:
            return name
    return None


def check(path, folder):
    qsos = ADIFParser.parse(str(path))
    issues = defaultdict(list)
    for i, q in enumerate(qsos, 1):
        for tag in ("CALL", "QSO_DATE", "TIME_ON", "BAND", "MODE"):
            if not (q.get(tag) or "").strip():
                issues[f"sin {tag}"].append(i)
        band = (q.get("BAND") or "").strip()
        if band:
            if band.lower() not in BANDS:
                issues["BAND no es nombre ADIF"].append(f"{i}:{band}")
            elif band != band.lower():
                issues["BAND no canónica (minúsculas)"].append(f"{i}:{band}")
        freq = (q.get("FREQ") or "").strip()
        if freq:
            bf = band_from_freq(freq)
            if bf is None:
                issues["FREQ fuera de toda banda"].append(f"{i}:{freq}")
            elif band and bf != band.lower():
                issues["BAND≠FREQ"].append(f"{i}:{band}/{freq}→{bf}")
        mode = (q.get("MODE") or "").strip().upper()
        if mode and mode not in VALID_MODES:
            issues["MODE inválido"].append(f"{i}:{q.get('MODE')}")
        sub = (q.get("SUBMODE") or "").strip()
        if mode in SUBMODES and sub and sub.upper() not in SUBMODES[mode]:
            issues["SUBMODE no válido para MODE"].append(f"{i}:{mode}/{sub}")
        if sub and mode not in SUBMODES:
            issues["SUBMODE con MODE que no lo admite"].append(f"{i}:{mode}/{sub}")
        d = (q.get("QSO_DATE") or "").strip()
        if d:
            try:
                if len(d) != 8 or not d.isdigit():
                    raise ValueError
                datetime.strptime(d, "%Y%m%d")
            except ValueError:
                issues["QSO_DATE inválida"].append(f"{i}:{d}")
        t = (q.get("TIME_ON") or "").strip()
        if t:
            if not t.isdigit() or len(t) not in (4, 6):
                issues["TIME_ON inválida"].append(f"{i}:{t}")
            elif int(t[:2]) > 23 or int(t[2:4]) > 59 or (len(t) == 6 and int(t[4:6]) > 59):
                issues["TIME_ON fuera de rango"].append(f"{i}:{t}")
        call = (q.get("CALL") or "").strip().upper()
        if call and not CALL_RE.match(call):
            issues["CALL con formato dudoso"].append(f"{i}:{call}")
        doff = (q.get("QSO_DATE_OFF") or "").strip()
        if doff and d and doff != d:
            issues["QSO_DATE_OFF≠QSO_DATE"].append(f"{i}:{d}/{doff}")
        st = (q.get("STATION_CALLSIGN") or "").strip()
        if st and st.upper() != "EG9MM":
            issues["STATION≠EG9MM"].append(f"{i}:{st}")
        op = (q.get("OPERATOR") or "").strip()
        if op and op.lower() not in {"ea4huk", "ea4iwx", "ea4ghh", "ea3jaq"}:
            issues["OPERATOR no permitido"].append(f"{i}:{op}")

    exp = EXPECTED_SIG.get(folder)
    if exp:
        pairs = Counter(((q.get("MY_SIG") or "").strip().upper(),
                         (q.get("MY_SIG_INFO") or "").strip()) for q in qsos)
        pairs.pop(("", ""), None)
        bad = {p: n for p, n in pairs.items() if p not in exp}
        if bad:
            issues["referencia de actividad incorrecta"].append(
                ", ".join(f"{a}:{b} x{n}" for (a, b), n in bad.items()))
        for q in qsos:
            sig = (q.get("MY_SIG") or "").strip().upper()
            info = (q.get("MY_SIG_INFO") or "").strip()
            if sig and info and sig != "TOTA":
                ref = (q.get(f"MY_{sig}_REF") or "").strip()
                if ref and ref != info:
                    issues[f"MY_{sig}_REF≠MY_SIG_INFO"].append(f"{info}/{ref}")
                    break

    key = Counter((q.get("CALL"), q.get("QSO_DATE"), q.get("TIME_ON"),
                   (q.get("BAND") or "").lower(), (q.get("MODE") or "").upper())
                  for q in qsos)
    ndup = sum(v - 1 for v in key.values() if v > 1)
    if ndup:
        issues["duplicados internos"].append(f"{ndup} QSO extra")
    return qsos, issues


def main():
    rows = []
    total_qso = 0
    for folder in FOLDERS:
        for f in sorted(glob.glob(f"{folder}/*.adi")):
            qsos, issues = check(Path(f), folder)
            total_qso += len(qsos)
            nf = sum(1 for q in qsos if not (q.get("FREQ") or "").strip())
            times = Counter(len((q.get("TIME_ON") or "").strip()) for q in qsos)
            bands = Counter((q.get("BAND") or "").strip() for q in qsos)
            lower = all(b == b.lower() for b in bands if b)
            rows.append((f, len(qsos), nf, dict(times), lower, dict(issues)))

    print(f"ADIs: {len(rows)} · QSO: {total_qso}")
    print("\n--- RESUMEN POR FICHERO ---")
    print("fichero | QSO | sin FREQ | TIME_ON long | BAND canónica | incidencias")
    for f, n, nf, times, lower, issues in rows:
        inc = "; ".join(f"{k} ({len(v) if isinstance(v, list) else v})" for k, v in issues.items()) or "ok"
        print(f"{f} | {n} | {nf} | {times} | {'sí' if lower else 'no'} | {inc}")

    print("\n--- DETALLE ---")
    for f, n, nf, times, lower, issues in rows:
        if not issues:
            continue
        print(f"\n{f} ({n} QSO)")
        for k, v in sorted(issues.items()):
            v = sorted(v, key=str) if isinstance(v, (list, set)) else v
            sample = ", ".join(map(str, list(v)[:8]))
            more = f" … (+{len(v) - 8})" if isinstance(v, list) and len(v) > 8 else ""
            print(f"  - {k}: {len(v) if isinstance(v, (list, set)) else v} → {sample}{more}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
