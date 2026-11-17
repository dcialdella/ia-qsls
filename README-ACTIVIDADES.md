# Generación de ADI por Actividad

Proceso que lee los archivos ADI de las carpetas `qsl1`–`qsl5` y genera, en la subcarpeta `ACTIVIDADES/` de cada una, un archivo por cada actividad configurada, con el formato específico que necesita cada una para su subida a las webs correspondientes.

**Alcance:** solo `qsl1`–`qsl5`. Las carpetas `qsl6` y `qsl7` **no se procesan** (no están en `CONFIG` y no se les borra ni crea nada).

## Script

```bash
./generar_adis.sh
# o directamente:
python3 qsl_generar_adis.py
```

## Flujo

1. **Limpia** la carpeta `ACTIVIDADES/` de cada QSL procesada (borra todo lo anterior).
2. **Lee todos** los `.adi` de la carpeta `qslN/` (ahora hay varios: 36 en total entre qsl1–qsl7; cada uno se procesa por separado).
3. **Valida** cada QSO:
   - `CALL` y `QSO_DATE` presentes.
   - `STATION_CALLSIGN` = `EG9MM` (única estación permitida en el log).
   - `OPERATOR` ∈ `ea4huk`, `ea4iwx`, `ea4ghh`, `ea3jaq` (sin importar mayúsculas).
4. **Genera** un archivo por cada formato configurado, con nombre `<nombre-del-input>-<formato>.adi`.
5. Si la validación de estación/operador falla, el archivo se genera completo pero con una primera línea:
   `REVISAR EL FORMATO DE OPERADOR y STATION`
   (además se imprime un aviso por registro en consola).

## Archivos de entrada (estado actual)

Las carpetas `qsl1`–`qsl5` (y `qsl7`, que no se procesa) contienen **36 `.adi`** con
3.015 QSO en total: 30 reales y 6 de demostración (`QSL-DEMO-EG9MM.adi`), incluidos
en esa cuenta. Cada una de qsl1–qsl5 incorpora además un `CRUZADAS-ADICIONALES-*.adi`
de 12 QSO (detalle en `RELLENO-QSO.md`). La carpeta `ADICIONALES/`, con 9 `.adi`
derivados de esos cruces, **no se procesa**: no está en `CONFIG`.

| Carpeta | `.adi` raíz | QSO | Formatos generados |
|---|---|---|---|
| `qsl1` | 6 | 565 | TOTA `EAR-1901` |
| `qsl2` | 6 | 426 | TOTA `EAR-1902` + POTA `ES-0340` |
| `qsl3` | 6 | 628 | POTA `ES-0849` |
| `qsl4` | 6 | 478 | POTA `ES-0850` |
| `qsl5` | 8 | 852 | LLOTA `LLES-0214` |
| **Total qsl1–qsl5** | **32** | **2.949** | **38 ficheros de salida, 3.375 QSO** |

`qsl6` no tiene `.adi` (postales de record); `qsl7` tiene 4 `.adi` (66 QSO, 3 reales +
1 demo) pero **no se procesa**: no está en `CONFIG`.

Salidas reales (38 ficheros en total). Un ejemplo por carpeta:

```
qsl1/ACTIVIDADES/ea4huk-museo-tota.adi
qsl2/ACTIVIDADES/EA4HUK@ES-0340-20261113-pota.adi
qsl3/ACTIVIDADES/EA3JAQ-20261114-pota.adi
qsl4/ACTIVIDADES/2026-11-13 EA3JAQ-pota.adi
qsl5/ACTIVIDADES/ea4ghh-llota20261115-llota.adi
```

> El total de QSO de salida (3.375) es mayor que el de entrada en `qsl1`–`qsl5`
> (2.949) porque cada `.adi` genera un fichero por formato y, en `qsl2`, dos (TOTA y
> POTA) con el mismo contenido de QSO.

## Formatos por actividad

| QSL | Formato | Referencia |
|-----|---------|------------|
| QSL1 | TOTA | `EAR-1901` |
| QSL2 | TOTA | `EAR-1902` |
| QSL2 | POTA | `ES-0340` |
| QSL3 | POTA | `ES-0849` |
| QSL4 | POTA | `ES-0850` |
| QSL5 | LLOTA | `LLES-0214` |

## Campos de actividad por formato

Cada campo va en su propia línea, antes de `<EOR>`:

### TOTA
```
<QSLMSG:13>TOTA EAR-1901
<MY_SIG:4>TOTA
<MY_SIG_INFO:8>EAR-1901
```
No se genera `MY_TOTA_REF`; el `QSLMSG` es solo para TOTA.

### POTA
```
<MY_SIG:4>POTA
<MY_SIG_INFO:7>ES-0340
<MY_POTA_REF:7>ES-0340
```

### LLOTA
```
<MY_SIG:5>LLOTA
<MY_SIG_INFO:9>LLES-0214
<MY_LLOTA_REF:9>LLES-0214
```

## Transformaciones

- Se **quitan** los campos de actividad existentes del input (`MY_SIG`, `MY_SIG_INFO`, `MY_POTA_REF`, `MY_TOTA_REF`, `MY_LLOTA_REF`, `QSLMSG`) y se **agregan** los del formato destino.
- Se limpian las líneas en blanco resultantes.
- La primera línea de la cabecera se reemplaza por
  `ADIF export for <STATION_CALLSIGN>: <FORMATO> <REFERENCIA>`, por ejemplo
  `ADIF export for EA4IWX/9: POTA ES-0340`. En los 6 ficheros demo sigue saliendo
  `ADIF export for EG9MM: ...`.
- Si la estación u operador no encajan con lo esperado, se añade además la línea
  `REVISAR EL FORMATO DE OPERADOR y STATION` (aparece en 32 de los 38 ficheros actuales;
  en los 6 demo no aparece). Es un aviso, no un error: los ficheros se generan igual.

## Formatos de entrada soportados

Los ADI de entrada pueden venir de cualquiera de estos programas (todos compatibles con ADIF):

| Programa | Ejemplo en `TESTDATA/` |
|----------|------------------------|
| Smart Logger | `t1-tota-smart.adi`, `t1-pota-smart.adi`, `t1-llota-smart.adi` |
| Ham2K Logger | `t2-ham2k.adi` |
| WSJT-X | `t3-wsjtdx.adi` |

Notas:

- El parser es **case-insensitive**: WSJT-X exporta `<eoh>`/`<eor>` en minúscula y los
  registros en una sola línea; se procesa igual.
- Los exports de **WSJT-X no traen `STATION_CALLSIGN` ni `OPERATOR`**, así que esos
  archivos generan el aviso por registro en consola y la línea
  `REVISAR EL FORMATO DE OPERADOR y STATION` en la salida (esperado, no es un error).

`TESTDATA/` contiene solo muestras de formato (no es un input del proceso).

## Estructura

```
qsl1/
├── 6 .adi (565 QSO)              ← entradas, entre ellos el demo EG9MM y CRUZADAS-ADICIONALES
├── ACTIVIDADES/
│   └── 6 *-tota.adi              ← salidas
├── QSL-1.png                     ← fondo único de la actividad
└── QSLS/
qsl2/
├── 6 .adi (426 QSO)
├── ACTIVIDADES/
│   ├── 6 *-tota.adi
│   └── 6 *-pota.adi
...
qsl7/
├── 4 .adi (66 QSO)               ← existen, pero NO se procesan (no están en CONFIG)
```

Cada `.adi` de entrada genera su propio conjunto de salidas (un `-tota.adi` en qsl1,
`-tota.adi` y `-pota.adi` en qsl2, etc.):

```
qsl1/
├── ea4huk-museo.adi              (256 QSO)
├── Museo-ea4ghh-2026-11-14.adi   (50 QSO)
├── ea4iwx-poi1-20261115.adi      (128 QSO)
├── EA3JAQ-...-full.adi           (118 QSO)
├── QSL-DEMO-EG9MM.adi            (1 QSO)
├── CRUZADAS-ADICIONALES-EAR-1901.adi (12 QSO)
└── ACTIVIDADES/
    ├── ea4huk-museo-tota.adi
    ├── Museo-ea4ghh-2026-11-14-tota.adi
    ├── ea4iwx-poi1-20261115-tota.adi
    ├── EA3JAQ-...-full-tota.adi
    ├── QSL-DEMO-EG9MM-tota.adi
    └── CRUZADAS-ADICIONALES-EAR-1901-tota.adi
```

## Configuración

La configuración de formatos por QSL está en el diccionario `CONFIG` al inicio de `qsl_generar_adis.py` (las claves determinan qué carpetas se procesan; `qsl6`/`qsl7` no están):

```python
CONFIG = {
    "qsl1": [
        ("tota", "TOTA", "EAR-1901"),
    ],
    "qsl2": [
        ("tota", "TOTA", "EAR-1902"),
        ("pota", "POTA", "ES-0340"),
    ],
    "qsl3": [("pota", "POTA", "ES-0849")],
    "qsl4": [("pota", "POTA", "ES-0850")],
    "qsl5": [("llota", "LLOTA", "LLES-0214")],
}
```

- `("formato", sig, sig_info)`: `formato` es el sufijo del archivo de salida; `sig`/`sig_info` son los valores de `MY_SIG` y `MY_SIG_INFO`.

## Validación de estación/operador

```python
REQUIRED_STATION = "EG9MM"
ALLOWED_OPERATORS = {"ea4huk", "ea4iwx", "ea4ghh", "ea3jaq"}
REVIEW_LINE = "REVISAR EL FORMATO DE OPERADOR y STATION"
```

Si algún QSO no cumple, el archivo se genera igualmente pero con `REVISAR EL FORMATO DE OPERADOR y STATION` arriba de todo (dentro de la cabecera ADIF, antes de `<EOH>`).
