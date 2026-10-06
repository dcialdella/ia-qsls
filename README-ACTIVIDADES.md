# Generación de ADI por Actividad

Proceso que lee los archivos ADI de cada carpeta `qsl1`–`qsl5` y genera archivos ADI en la subcarpeta `ACTIVIDADES/` de cada una, con el formato específico que necesita cada actividad para su subida a las webs correspondientes.

## Script

```bash
./generar_adis.sh
# o directamente:
python3 qsl_generar_adis.py
```

## Flujo

1. **Limpia** la carpeta `ACTIVIDADES/` de cada QSL (borra todo lo anterior).
2. **Lee** todos los `.adi` de la carpeta `QSLn/`.
3. **Valida** cada QSO:
   - `CALL` y `QSO_DATE` presentes.
   - `STATION_CALLSIGN` = `EG9MM`.
   - `OPERATOR` ∈ `ea4huk`, `ea4iwx`, `ea4ghh`, `ea3jaq` (sin importar mayúsculas).
4. **Genera** un archivo por cada formato configurado, con nombre `<original>-<formato>.adi`.
5. Si la validación de estación/operador falla, el archivo se genera completo pero con una primera línea:
   `REVISAR EL FORMATO DE OPERADOR y STATION`
   (además se imprime un aviso por registro en consola).

## Formatos por actividad

| QSL | Formato | Referencia |
|-----|---------|------------|
| QSL1 | TOTA | `EAR-1234` |
| QSL2 | TOTA | `EAR-1234` |
| QSL2 | POTA | `ES-0340` |
| QSL3 | POTA | `ES-0849` |
| QSL4 | POTA | `ES-0850` |
| QSL5 | LLOTA | `LLES-0214` |

> **Nota:** las referencias TOTA son provisionales hasta nuevo aviso.

## Campos de actividad por formato

Cada campo va en su propia línea, antes de `<EOR>`:

### TOTA
```
<QSLMSG:13>TOTA EAR-1234
<MY_SIG:4>TOTA
<MY_SIG_INFO:8>EAR-1234
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
- La primera línea de la cabecera se reemplaza por:
  `ADIF export for EG9MM: <FORMATO> <REFERENCIA>`

## Formatos de entrada soportados

Los ADI de entrada pueden venir de cualquiera de estos programas (todos compatibles con ADIF):

| Programa | Ejemplo en `TESTDATA/` |
|----------|------------------------|
| Smart Logger | `t1-tota-smart.adi`, `t1-pota-smart.adi`, `t1-llota-smart.adi` |
| Ham2K Logger | `t2-ham2k.adi` |
| WSJT-X | `t3-wsjtdx.adi` |

Input canónico de pruebas: `TESTDATA/input-qsl1.adi` (copiado como `input-qsl1.adi` en qsl1–qsl5).

## Estructura

```
qsl1/
├── input-qsl1.adi         ← entrada
├── ACTIVIDADES/
│   └── input-qsl1-tota.adi ← salida
├── f1.png
└── QSLS/
qsl2/
├── input-qsl1.adi
├── ACTIVIDADES/
│   ├── input-qsl1-tota.adi
│   └── input-qsl1-pota.adi
...
```

## Configuración

La configuración de formatos por QSL está en el diccionario `CONFIG` al inicio de `qsl_generar_adis.py`:

```python
CONFIG = {
    "qsl1": [
        ("tota", "TOTA", "EAR-1234"),
    ],
    "qsl2": [
        ("tota", "TOTA", "EAR-1234"),
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
