# GENERADOR DE POSTALES QSL desde archivos ADI

Genera imágenes tipo postal (QSL cards) sobreponiendo los datos de contactos de radio
sobre una foto/imagen de fondo. Cada carpeta `qsl1`–`qsl7` representa una actividad
independiente con su propia imagen de fondo, sus propios archivos ADI, y sus propias
postales generadas.

> **Objetivo final:** el usuario ejecuta el script (o el `./generar.sh`), y para cada
> carpeta qslN con archivos `.adi` + una imagen de fondo, se generan tantas postales como
> contactos haya, guardadas en `qslN/QSLS/`. Las postales se suben después a Google Drive
> manualmente.

---

## 1. Estado actual del proyecto (última sesión)

- ✅ Script funcional e **incremental** en `qsl_generator.py`
- ✅ Entorno virtual `venv/` con Pillow instalado
- ✅ Script de ejecución autónoma **`generar.sh`** (ver sección 2)
- ✅ Carpetas `qsl1`–`qsl7` creadas. Con imagen de fondo:
  - qsl1 (a1.png), qsl2 (a2.png), qsl3 (a3.png), qsl4 (f4.png), qsl6 (f6.png), qsl7 (f7.png)
- ✅ Datos de ejemplo cargados:
  - `qsl1/act1.adi` y `qsl1/act2.adi` (4 contactos c/u) → `a1.png`
  - `qsl2/activo2.adi` (4 contactos) → `a2.png`
  - `qsl3/actividad3.adi` (4 contactos) → `a3.png`
  - `qsl4/probe.adi` (1 contacto) → `f4.png`
  - `qsl7/ejemplo.adi` (3 contactos) → `f7.png`
  - `probe.adi` también en qsl1, qsl2, qsl3, qsl4 y qsl5 (estación EA4HUK), para que
    genere su QSL6 (ver sección 5.b).
- ✅ Cada carpeta con datos tiene su log `qslN/qsl_log.json` (se crea solo)
- ✅ **Casillas de actividades en TODAS las postales normales** (QSL1..QSL6).

### Cambios recientes (aplicados y verificados)

1. **Caja de datos más alta (22%).** De 17% a 22% del alto (+5%) para que entre mejor el
   texto de la estación. Antes el callsign quedaba pegado al borde superior.
2. **Texto separado del borde superior.** `inner_top` usa `pad_y + 12` en lugar de
   `pad_y + 4`; el callsign queda a ~10px del borde interior de la caja.
3. **Casillas de actividades rediseñadas:** fila alineada a la **derecha** de la caja de
   datos, con el rótulo **"ACT"** a la izquierda. Las casillas son más pequeñas
   (26×26px normales, 28×28px act6).
4. **Números dentro de las casillas.** Cada casilla muestra su número 1–6. Cuando la
   actividad está lograda, el número se **reemplaza por un tilde dorado** `(245,166,35)`.
   Se eliminaron las etiquetas "QSL1"…"QSL6" que había debajo de cada cuadro.
5. **QSL6 (record):** casillas 1–5 con tilde y la **casilla 6 con la bandera de España**
   (rojo-amarillo-rojo 1:2:1, fondos `(198,11,30)` / `(255,200,0)`) en lugar del número.
6. **QSL7 = DMR.** Las postales de la carpeta `qsl7` no muestran casillas: en su lugar
   aparece el texto **"DMR Confirmated"** alineado a la derecha en la zona inferior de la
   caja.
7. **Limpieza de código:** eliminados `load_backgrounds()` (obsoleto), el chequeo global
   de fondos, y los parámetros `my_callsign`/`label_color`/`--callsign`. El rendering usa
   solo los datos del contacto.

### Estructura actual en disco

```
ia-qsls/
├── qsl_generator.py       <- Script principal (todo en un archivo)
├── generar.sh             <- Script de ejecución autónoma (bash)
├── venv/                  <- Entorno virtual (Pillow), creado automáticamente
├── README.md
├── qsl1/
│   ├── a1.png             <- Fondo de qsl1
│   ├── act1.adi           <- Contactos actividad 1 (dia 1)
│   ├── act2.adi           <- Contactos actividad 1 (dia 2)
│   ├── probe.adi          <- EA4HUK (prueba de QSL6)
│   ├── QSLS/              <- Postales generadas
│   └── qsl_log.json       <- Log de procesado
├── qsl2/  (a2.png, activo2.adi, probe.adi, QSLS/, qsl_log.json)
├── qsl3/  (a3.png, actividad3.adi, probe.adi, QSLS/, qsl_log.json)
├── qsl4/  (f4.png, probe.adi, QSLS/, qsl_log.json)
├── qsl5/  (probe.adi con EA4HUK, QSLS/ — SIN imagen de fondo, solo cuenta para QSL6)
├── qsl6/  (f6.png, QSLS/ con ea4huk_act6.png, qsl_log.json)
└── qsl7/  (f7.png, ejemplo.adi, QSLS/ con postales DMR, qsl_log.json)
```

---

## 2. Cómo ejecutar

### Opción A: uso el script autónomo `./generar.sh` (recomendado)

El script es portable: se puede copiar a cualquier lado, calcula su propio directorio,
crea el venv e instala Pillow si hace falta, y no toca tus `.adi` ni tus fondos.

```bash
./generar.sh                    # modo incremental (solo lo que cambió/falta)
./generar.sh --from-scratch     # borra QSLS/*.png y qsl_log.json y regenera TODO
./generar.sh --clean            # alias de --from-scratch
./generar.sh --help             # ayuda resumida
```

Salida típica (modo incremental, todo ya generado):

```
📂 QSL1  (fondos: a1.png)
   ✓ act1.adi: sin cambios (4 contactos ya generados)
   ...
============================================================
  RESUMEN: 0 procesados, 0 regenerados, 10 sin cambios
============================================================

Postales generadas por carpeta:
   qsl1   9 postales
   qsl2   5 postales
   ...
```

### Opción B: ejecutar el generador manualmente

```bash
cd /Users/cialdeld/Downloads/ia-qsls
source venv/bin/activate
python3 qsl_generator.py
```

IMPORTANTE: en macOS Python es “externally-managed”, por lo que **no** se usa `pip install`
globalmente; siempre activar `venv` (o usar `./generar.sh` que lo hace por ti).

---

## 3. Cómo funciona (lógica)

### Detección de archivos ADI (nombres flexibles)
`find_adi_files(folder)` recorre el contenido de la carpeta y devuelve los archivos
cuya extensión (en minúsculas) sea `.adi` o `.adif`. No usa `glob("*.adi") + glob("*.ADI")`
porque en sistemas case-insensitive (macOS) eso duplicaría el mismo archivo y se
procesaría dos veces.

### Recorrido por carpeta
1. `main()` itera `qsl1` … `qsl7`.
2. Para cada carpeta busca archivos ADI con `find_adi_files()`.
   - Si no hay → imprime "sin archivos .adi, nada que generar" y salta.
3. Toma los fondos de la carpeta: `*.png`, `*.jpg`, `*.jpeg` en la raíz de ESA carpeta
   (`folder_backgrounds`). Si no hay fondo → avisa "no tiene imagen de fondo propia"
   y **salta sin generar nada** (no se crean archivos en QSLS).
4. Con ADI + fondo → llama a `process_folder(...)` que genera/verifica las postales
   en `qslN/QSLS/`.
5. **qsl6 es especial:** no procesa sus propios ADIs sino que llama a `process_act6`
   (ver sección 3.b).

### 3.b Actividad 6 (postales de record)
`process_act6(base_dir, generator)`:
1. Recolecta los callsigns de cada actividad (qsl1..qsl5) leyendo todos sus ADIs.
   Guarda además nombre y grid locator de cada estación.
2. Calcula la **intersección** de las 5 actividades: estaciones que contactaron en
   TODAS.
3. Para cada una genera `qsl6/QSLS/{call}_act6.png` con `compose_act6` sobre el fondo
   de qsl6 (f6.png). Muestra callsign (dorado), nombre, locator y las 5 casillas
   QSL1–QSL5 tildadas + bandera de España en la casilla 6.
4. Incremental con `qsl6/qsl_log.json` (clave `act6`, sha256 de la firma del conjunto).
   Reusa las postales ya válidas; regenera solo las que falten.

### Procesado incremental (clave)
Cada carpeta tiene `qsl_log.json` con, por archivo ADI:

```json
{
  "act1.adi": {
    "sha256": "bac65c…",
    "contactos": [
      { "call": "EA4HJZ", "archivo": "ea4hjz_act1.png",
        "fondo": "a1.png", "generado_en": "2026-09-09T11:31:37Z" },
      ...
    ],
    "procesado_en": "2026-09-09T11:31:37Z"
  }
}
```

| Situación | Acción |
|---|---|
| ADI **nuevo** en la carpeta | Se procesa completo (todos sus contactos) |
| ADI **modificado** (sha256 cambió) | Se reprocesa completo |
| ADI ya procesado y todos sus PNG existen | Se omite ("sin cambios") |
| ADI ya procesado pero falta algún PNG | Se regenera **solo** ese PNG (reusa su fondo previo) |
| ADI borrado de la carpeta | Se elimina del log |

Esto permite añadir 1 ADI por día sin repetir trabajo, y auto-recupera archivos borrados.
**Importante:** como los nombres ADI pueden cambiar, el log se referencia por nombre de
archivo; si renombras un ADI se tratará como nuevo (se regeneran sus postales).

### Nominación de archivos
- Formato: `{callsign}_{archivo_adi}.png` todo en minúsculas.
  - Ej: `EA4HJZ` + `act1.adi` → `ea4hjz_act1.png`
- Si el mismo callsign aparece 2+ veces en un ADI: sufijo `_2`, `_3`…
  (función `unique_filenames`)
- Actividad 6: `{callsign}_act6.png` (ej. `ea4huk_act6.png`).

### Fondos
- Cada carpeta usa **sus propios** fondos (los de su raíz). QSL1 usa a1.png, QSL2 a2.png, etc.
- Si una carpeta tiene varios fondos se alternan por contacto (`index % len(fondos)`).
- Al regenerar un faltante se **reusa el fondo** guardado en el log (`fondo`).
- **Sin imagen → no se genera nada** (ni QSLS, ni log).

---

## 4. Formato ADI (lo que entiende el parser)

```
<VERSION:5>2.0.0
<PROGRAMID:4>QSLG
<EOH>                                    <- fin de cabecera

<QSO_DATE:8>20241215                     <- REQUERIDO fecha YYYYMMDD
<TIME_ON:6>143022                        <- REQUERIDO hora HHMMSS
<CALL:6>EA4HJZ                           <- REQUERIDO callsign
<BAND:3>20M                              <- banda
<MODE:3>SSB                              <- modo
<RST_SENT:3>599                          <- RST enviado (se lee, NO se dibuja)
<RST_RCVD:3>599                          <- RST recibido (se lee, NO se dibuja)
<NAME:5>pedro                            <- nombre (opcional)
<QTH:8>madrid                            <- localidad (opcional)
<GRIDSQUARE:4>IN80                       <- grid locator (opcional)
<eor>                                    <- fin de registro
```

- Campos obligatorios: `QSO_DATE`, `TIME_ON`, `CALL` (el resto opcionales).
- El parser (`ADIFParser`) tolera la parte opcional `:TIPO` (ej. `<RST_SENT:3:number>`)
  y valores con signo (ej. RST `-10` para FT8).
- **Longitudes incorrectas toleradas:** si un tag declara más longitud de la que tiene
  (ej. `<QTH:8>madrid`), el valor se corta donde empieza el siguiente `<tag>`. Así no se
  colaba el símbolo `<` dentro del valor.
- Ignora `<VERSION>`, `<PROGRAMID>`, `<EOH>`, `<CREATED_TIMESTAMP>`.
- Registros repetidos con el mismo callsign → sufijo numérico en el archivo.

---

## 5. Diseño de las postales

Tipo | Tamaño caja | Contenido | Casillas
---|---|---|---
**Normal** (`compose`) | 22% alto × 55% ancho, inf. izquierda | callsign, fecha+UTC, banda/modo, nombre•QTH•grid | "ACT" + 6 casillas con números; tilde en la suya
**Record act6** (`compose_act6`) | 20% alto × 62% ancho, inf. izquierda | callsign (dorado), nombre, locator | "ACT" + 6 casillas; tildes QSL1..QSL5 y bandera de España en QSL6
**DMR qsl7** (`compose`, activity=7) | 22% alto × 55% ancho | igual que la normal | NO muestra casillas: texto "DMR Confirmated"

- Tamaño: `WIDTH=1200` × `HEIGHT=800` (proporción 3:2). Se puede cambiar en la clase.
- El fondo se escala con recorte centrado "cover" (nunca distorsiona).
- Caja con radio 16–18 px, fondo negro `(0,0,0,150/160)` y borde (blanco sutil o dorado
  en act6).
- El texto (callsign) queda a ~10px del borde superior de la caja (`inner_top`).
- **Casillas** (`QSLGenerator.draw_activity_checkboxes`):
  - Fila alineada a la **derecha** de la caja con rótulo **"ACT"** a la izquierda.
  - Casillas redondeadas (26×26 normales, 28×28 act6), número 1–6 dentro de cada una.
  - La casilla de la actividad lograda **reemplaza el número por un tilde dorado**
    `(245,166,35,255)` (2 trazos de 4px).
  - La casilla bandera (solo act6, casilla 6) dibuja la bandera de España en lugar del
    número: rojo `(198,11,30)` / amarillo `(255,200,0)`, franjas 1:2:1.
- **NO se dibuja** el texto RST ni la marca "QSL".

---

## 6. Referencia del código (mapa de funciones)

| Función | Qué hace |
|---|---|
| `ADIFParser.parse(filepath)` | Parsea ADI → lista de dicts de QSO (longitudes tolerantes, sin `<`) |
| `QSLGenerator.get_font(size, bold)` | Carga fuente del sistema (cacheada) |
| `QSLGenerator.cover_fit(bg, w, h)` | Escala fondo a "cover" |
| `QSLGenerator.rounded_rect(draw, xy, r, fill)` | Rectángulo redondeado |
| `QSLGenerator.draw_activity_checkboxes(draw, box, checked, …)` | Fila "ACT" + 6 casillas con número/tilde/bandera |
| `QSLGenerator.compose(bg, qso, activity=None)` | Postal normal (call, fecha, banda/modo, info + casillas; activity=7 → "DMR Confirmated") |
| `QSLGenerator.compose_act6(bg, call, name, grid)` | Postal de record (call dorado, nombre, locator + casillas con bandera) |
| `find_adi_files(folder)` | Detecta ADI/ADIF por extensión, sin duplicados, cualquier nombre |
| `folder_backgrounds(folder)` | Fondos de UNA carpeta |
| `pick_background(backgrounds, idx)` | Alterna `fondos[idx % n]` |
| `sha256_file(path)` | Hash del ADI para detectar cambios |
| `load_log(folder)` / `save_log(folder, log)` | Leer/escribir `qsl_log.json` |
| `now_iso()` | Timestamp UTC |
| `png_valid(path)` | Comprueba PNG abrible |
| `count_registered_pngs(folder)` | PNGs ya registrados (para secuencia fondos) |
| `unique_filenames(qsos, adi_stem)` | Nombres `{call}_{stem}.png` únicos |
| `process_folder(folder, gen, bgs, seq)` | Lógica incremental por carpeta |
| `process_act6(base_dir, gen)` | Detección de estaciones en las 5 actividades + QSL de record |
| `main()` | Orquesta las 7 carpetas (qsl6 especial) |

---

## 7. Tareas pendientes / próximos pasos

1. **Confirmar visualmente las postales** generadas (abrir `qslN/QSLS/*.png`) y validar
   que el diseño final (callsign separado del borde, números en casillas, tilde dorado,
   bandera en QSL6, "DMR Confirmated" en QSL7) es del agrado del usuario.
2. Sustituir los `.adi` de ejemplo por los reales del usuario en cada carpeta y re-ejecutar
   (`./generar.sh --from-scratch` para limpiar los de ejemplo).
3. **Fondo de qsl5:** colocar una imagen (ej. `f5.png`) para que la actividad 5 genere
   postales normales (EA4HUK ya cuenta para QSL6 por su ADI, pero sin fondo no hay PNG).
4. Cuando haya varias estaciones en las 5 actividades, revisar que `qsl6/QSLS/` comience
   a contener varias postales `{call}_act6.png`.
5. (Opcional) El parser trunca a la longitud declarada: `<QTH:8>palermo` daría `palerm`
   porque el ADI declara 8 pero el valor real son 7. Funciona salvo cuando la longitud
   declarada es **menor** que el valor real; se podría mejorar tomando `max(len_real, decl)`.

---

## 8. Notas de entorno

- **Mac (darwin), zsh, sin git.** El script `generar.sh` funciona también en Linux.
- **Python:** 3.14 venv; Pillow instalado (también numpy, usado solo en pruebas de debug).
- **Fuentes usadas:** Arial/Helvetica del sistema macOS (con fallback DejaVu en Linux).
- **Filesystem case-insensitive:** por eso se evitan los globs que mezclan mayúsculas.
- No hay tests automáticos; la verificación es ejecutar el script + revisar los PNG.
- `./generar.sh` es la forma recomendada de ejecutar: configura el entorno solo y, con
  `--from-scratch`, regenera todo el set de postales.