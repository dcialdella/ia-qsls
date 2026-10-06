# Generación de ADI por Actividad

Proceso que lee los archivos ADI de cada carpeta `QSL1`–`QSL5` y genera archivos ADI en la subcarpeta `ACTIVIDAD/` de cada una, con el formato específico que necesita cada actividad para su subida a las webs correspondientes.

## Script

```
python3 qsl_generar_adis.py
```

## Flujo

1. **Limpia** la carpeta `ACTIVIDAD/` de cada QSL (borra todo lo anterior).
2. **Lee** todos los `.adi` de la carpeta `QSLn/` (excluyendo los de `ACTIVIDAD/`).
3. **Genera** un archivo por cada formato configurado, con nombre `<original>-<formato>.adi`.

## Formatos por actividad

| QSL | Archivos generados | Referencia |
|-----|-------------------|------------|
| QSL1 | `TEST-tota.adi`, `TEST-dme.adi` | TOTA `TO-1234`, DME |
| QSL2 | `TEST-tota.adi`, `TEST-pota.adi`, `TEST-dme.adi` | TOTA (número pendiente), POTA `ES-0340`, DME |
| QSL3 | `TEST-pota.adi`, `TEST-ure.adi` | POTA `ES-0849`, URE |
| QSL4 | `TEST-pota.adi`, `TEST-ure.adi` | POTA `ES-0850`, URE |
| QSL5 | `TEST-llota.adi`, `TEST-ure.adi` | LLOTA `LLES-0214`, URE |

## Transformaciones

### TOTA / POTA / LLOTA
- Se reemplazan los campos de actividad originales (`MY_SIG`, `MY_SIG_INFO`, `MY_POTA_REF`) por los de la actividad destino.
- Ejemplo: `POTA ES-0951` → `TOTA TO-1234`.

### DME
- Se eliminan los campos de actividad (`MY_SIG`, `MY_SIG_INFO`, `MY_POTA_REF`).
- No se añade ninguna referencia.

### URE
- Se eliminan los campos de actividad.
- Se añaden 4 estaciones al final del log usando los datos del último QSO original:
  - `ea4huk`
  - `ea3jaq`
  - `ea4iwx`
  - `ea4ghh`

## Formatos de entrada soportados

Los ADI de entrada pueden venir de cualquiera de estos programas (todos compatibles con ADIF):

| Programa | Ejemplo |
|----------|---------|
| Smart Logger | `TEST DATA/t1-smart.adi` |
| Ham2K Logger | `TEST DATA/ham2k.adi` |
| WSJT-X | `TEST DATA/wsjtdx.adi` |

## Estructura

```
qsl1/
├── TEST.adi          ← entrada
├── ACTIVIDAD/
│   ├── TEST-tota.adi ← salida
│   └── TEST-dme.adi  ← salida
├── f1.png
└── QSLS/
qsl2/
├── TEST.adi
├── ACTIVIDAD/
│   ├── TEST-tota.adi
│   ├── TEST-pota.adi
│   └── TEST-dme.adi
...
```

## Configuración

La configuración de formatos por QSL está en el diccionario `CONFIG` al inicio de `qsl_generar_adis.py`:

```python
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
    ...
}
```

- `("formato", sig, sig_info)`: si `sig` y `sig_info` son `None`, no se añaden campos de actividad.
