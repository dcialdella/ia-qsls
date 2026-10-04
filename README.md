# GENERADOR DE POSTALES QSL desde archivos ADI

Genera imágenes tipo postal (QSL cards) sobreponiendo los datos de contactos de radio
sobre una foto/imagen de fondo. Cada carpeta `qsl1`–`qsl7` representa una actividad
independiente con su propia imagen de fondo, sus propios archivos ADI, y sus propias
postales generadas.

> **Resumen:** lee archivos de contactos en formato ADI, deriva el país de cada estación
> desde el prefijo del callsign (y dibuja su bandera), y genera una postal QSL por
> contacto con los datos (callsign, fecha, banda/modo, nombre, QTH, grid), las casillas
> de las 6 actividades (con la QSL6 de "record" para quien completó las 5) y un sello con
> la bandera de España. Funciona en modo incremental (solo regenera lo que cambió).

> **Autor:** Daniel Cialdella — dcialdella@gmail.com — EA4HUK
>
> **Aviso de uso:** esta aplicación fue diseñada por Daniel Cialdella. Para su uso,
> distribución o modificación debe solicitarse permiso previo al autor.

> **Objetivo final:** el usuario ejecuta `./generar.sh`, y para cada carpeta qslN con
> archivos `.adi` + una imagen de fondo, se generan tantas postales como contactos haya,
> guardadas en `qslN/QSLS/`. Por defecto (siempre, a menos que se use `--no-sync-drive`)
> las postales se copian automáticamente a la carpeta `QSL/QSLs/qsl1`–`qsl7` de Google
> Drive (app de escritorio sincronizada con la cuenta eg9mm), que las sube a la nube.

---

## 0. Reglas invariables (no romper)

1. **Las carpetas `qsl1`–`qsl7` de Google Drive NO se borran nunca.** Deben **existir
   siempre**, aunque estén **vacías**. Si desaparecen, hay que volver a crearlas
   (el índice web y los enlaces de descarga dependen de que existan los 7 `id`).
2. **Los archivos `.adi` son parte del proyecto: se versionan en Git y se suben al
   repo.** No contienen información sensible (datos públicos de radioaficionado:
   indicativo, nombre, grid locator, banda/modo). Van en la carpeta de su actividad
   (`qslN/*.adi`) y los de prueba en `TEST DATA/`. No deben borrarse ni excluirse
   del control de versiones. *Nota: en el estado de inicio actual no hay ninguno en
   `qslN/`; los 10 de ejemplo están en `TEST DATA/` (§1).*
3. **En `qslN/QSLS/` no se versiona ningún PNG.** Es salida generada y está en
   `.gitignore` (`qsl*/QSLS/`).
4. **La raíz de Drive `QSLs` solo contiene las 7 carpetas `qsl1`–`qsl7`**, ningún
   archivo suelto en la raíz.
5. **Tras cada generación de imágenes (parcial o total) hay que regenerar el índice
   y subir el código.** El sitio lee `qsl_index.json` desde GitHub Pages, así que
   sin push la web no ve las postcards nuevas. Secuencia obligatoria:
   1. `./generar.sh --index` (o `--from-scratch` y luego `--index-only` si hay que
      esperar a que Drive suba los PNG a la nube).
   2. `git add -A && git commit && git push`.
   3. Verificar en <https://dcialdella.github.io/ia-qsls/qsl_index.json> que
      `total` y `counts` reflejan lo generado (Pages tarda ~1 min).
   Ojo: `drive_index.py` lee la nube, no el disco local; si se indexa antes de que
   Drive suba los ficheros, el JSON sale con `total: 0`.

---

## 1. Estado actual del proyecto

> **Estado de inicio:** el generador está completo y probado, pero el árbol de datos está
> **vacío a propósito**. No hay ningún `.adi` dentro de `qsl1`–`qsl7` ni ninguna postal
> generada en `qslN/QSLS/`. Todo lo que hay es el código, los fondos y los `.adi` de
> ejemplo aparcados en `TEST DATA/`.

- ✅ Script funcional e **incremental** en `qsl_generator.py` (`GENERATOR_VERSION = "3"`)
- ✅ Entorno virtual `venv/` con Pillow instalado
- ✅ Script de ejecución autónoma **`generar.sh`** (ver sección 2)
- ✅ Carpetas `qsl1`–`qsl7` creadas y **vacías de contactos**. Todas con su fondo:
  - qsl1 (`f1.png`), qsl2 (`f2.png`), qsl3 (`f3.png`), qsl4 (`f4.png`),
    qsl5 (`f5.png`), qsl6 (`f6.png`), qsl7 (`f7.png`) — la convención es `f<n>.png`,
    el número coincide con la actividad
- ✅ `qsl1`–`qsl7`: **cero archivos `.adi`** y `QSLS/` vacío (se regenera al añadir ADIs)
- ✅ Los **10 `.adi` de ejemplo están en `TEST DATA/`**, no en las carpetas de actividad.
  No se procesan: el generador solo lee `qslN/*.adi`. Para usarlos, cópialos a su
  actividad correspondiente (ver §1.1).
- ✅ `qsl_index.json` coherente con el vacío: `total: 0` y `counts` a 0 en las 7 actividades
- ✅ No existen `qslN/qsl_log.json`: se crean solos al primer procesado real
- ✅ No quedan archivos `.adi.TEST` (fueron eliminados; los renombrados pasan a `.adi`)
- ✅ **Casillas de actividades en TODAS las postales normales** (QSL1..QSL6).
- ✅ **Bandera del país** delante del nombre de cada estación (ver "Banderas" más abajo).
- ✅ Repositorio Git con remote en **GitHub** (`dcialdella/ia-qsls`, rama `main`).

### 1.1 Cómo volver a poblar las actividades

Los `.adi` de `TEST DATA/` son datos de ejemplo/prueba, no datos de producción. Para
generar postcards de prueba, copia solo los que te interesen a la carpeta de su actividad:

```bash
# --- 1) Copiar los .adi de ejemplo a sus actividades ---
cp "TEST DATA/activo2.adi"                 qsl2/     # actividad 2
cp "TEST DATA/actividad3.adi"              qsl3/     # actividad 3
cp "TEST DATA/probe.adi"                   qsl4/     # 1 contacto (EA4HUK)
cp "TEST DATA/probe.adi"                   qsl5/     # 1 contacto (EA4HUK)
cp "TEST DATA/TOTA2222-delta-20260909-1145.adi" \
   "TEST DATA/faro-echo-20260909-1821.adi" \
   "TEST DATA/pota1111-delta-20260909-1417.adi" qsl1/   # actividad 1 (1+4+4)
cp "TEST DATA/ejemplo.adi"                 qsl7/     # actividad 7 (carpeta DMR)

# --- 2) Probar en local SIN tocar Google Drive ni la web ---
./generar.sh --no-sync-drive
# revisa qslN/QSLS/*.png a ojo

# --- 3) Cuando el resultado te guste: sincronizar + reindexar la web ---
./generar.sh --index
```

Ojo con los nombres que llevan **espacio** (`TEST DATA/probe copy.adi`): entrecomíllalos.

Para deshacer la prueba y volver al estado de inicio:

```bash
find qsl[1-7] -maxdepth 1 -name '*.adi' -delete  # quita los .adi copiados de TEST DATA/
./generar.sh --from-scratch --no-sync-drive      # borra QSLS/*.png y los qsl_log.json
./generar.sh --index-only                         # deja el índice a 0 otra vez
```

> Usa `find` y no `rm qsl*/*.adi`: en zsh un glob sin coincidencias aborta el comando con
> `no matches found` en vez de ser un no-op.

> **Importante:** `--from-scratch` es obligatorio en el paso 2. Si solo borras los `.adi` y
> ejecutas el generador, las postcards **no se borran**: `main()` hace `continue` en las
> carpetas sin `.adi` y `prune_orphan_pngs` (que es lo que limpia los huérfanos) solo se
> llama desde `process_folder` y `process_act6`. Es decir, la poda no llega a ejecutarse.
> `qsl6` es la única actividad que se limpia sola en cada pasada.

`qsl6` (postales de record) no necesita `.adi` propios: se alimenta de los contactos ya
registrados en las actividades 1–5 (ver §3.b).

Contenido actual de `TEST DATA/` (contactos según `<CALL:`):

| Archivo | Contactos | Actividad destino |
|---------|-----------|-------------------|
| `TOTA2222-delta-20260909-1145.adi` | 1 | qsl1 |
| `faro-echo-20260909-1821.adi` | 4 | qsl1 |
| `pota1111-delta-20260909-1417.adi` | 4 | qsl1 |
| `lugar1-delta1-2026-10-04.adi` | 2 | qsl1 (alternativo, sustituye a los tres previos) |
| `activo2.adi` | 4 | qsl2 |
| `actividad3.adi` | 4 | qsl3 |
| `probe.adi` | 1 | qsl4, qsl5 |
| `probe copy.adi` | 1 | qsl4, qsl5 (copia de trabajo) |
| `probe copy 2.adi` | 1 | qsl4, qsl5 (copia de trabajo) |
| `ejemplo.adi` | 4 | qsl7 (los QSO son CW/SSB; lo "DMR" es el tema de la carpeta 7) |

### Cambios recientes (aplicados y verificados)

1. **Caja de datos más alta (22%).** De 17% a 22% del alto (+5%) para que entre mejor el
   texto de la estación. Antes el callsign quedaba pegado al borde superior.
2. **Texto separado del borde superior.** `inner_top` usa `pad_y + 12` en lugar de
   `pad_y + 4`; el callsign queda a ~10px del borde interior de la caja.
3. **Casillas de actividades rediseñadas:** fila alineada a la **derecha** de la caja de
   datos, con el rótulo **"ACT"** a la izquierda. Las casillas son más pequeñas
   (30×30 px en las normales —el default de `draw_activity_checkboxes`—, 28×28 px en
   act6, que sí los sobrescribe).
4. **Números dentro de las casillas.** Cada casilla muestra su número 1–6. Cuando la
   actividad está lograda, el número se **reemplaza por un tilde dorado** `(245,166,35,255)`.
   Se eliminaron las etiquetas "QSL1"…"QSL6" que había debajo de cada cuadro.
5. **QSL6 (record):** casillas 1–5 con tilde y la **casilla 6 con la bandera de España**
   (rojo-amarillo-rojo 1:2:1, fondos `(198,11,30)` / `(255,200,0)`) en lugar del número.
6. **QSL7 = DMR.** Las postales de la carpeta `qsl7` no muestran casillas: en su lugar
   aparece el texto **"DMR Confirmated"** alineado a la derecha en la zona inferior de la
   caja.
7. **Limpieza de código:** eliminados `load_backgrounds()` (obsoleto), el chequeo global
   de fondos, y los parámetros `my_callsign`/`label_color`/`--callsign`. El rendering usa
   **solo los datos del contacto** más el sello fijo de estación `STATION_TEXT`
   (`"EG9MM - Melilla"`, `qsl_generator.py:36`), que se dibuja en la esquina inferior
   derecha de todas las postcards.
8. **Bandera del país delante del nombre de cada estación:** el país se deriva del prefijo
   del callsign con `country_map.json` (845 prefijos → ISO2, mejor coincidencia por
   longest-match). La bandera se pinta con la misma altura que el texto:
   - Postales normales (`compose`, actividad 1–5/7): delante del texto *nombre • QTH • grid*.
   - Postales de record (`compose_act6`): delante del *nombre* de la estación.
   - **Sin bandera encontrada → no se dibuja nada** (cierta estación no se le pinta
     bandera errónea). Ej.: `1A0AAA` (Orden de Malta, sin PNG) no muestra bandera.
9. **Regeneración total de QSL6 en cada ejecución:** `process_act6` borra TODAS las
   postales de `qsl6/QSLS/` al empezar y las regenera siempre con la información actual
   (nombres, grids, banderas, versión del generador). No es incremental.
10. **Poda de postales huérfanas:** tras procesar, se eliminan de `qslN/QSLS/` los PNG que
    ya no referencia ningún ADI del log (al borrar contactos o ADIs).
11. **Índice por primera letra** en `country_code_for_call` (~20× más rápido en lotes de
    miles de contactos, 5 ms vs 104 ms en 5000 llamadas).
12. **Versión del generador en el log** (`generador`): si el código cambia, los ADI antiguos
    se reprocesan automáticamente sin necesidad de `--from-scratch`.
13. **Fix `--from-scratch`:** el `find` usaba `-maxdepth 2` y no alcanzaba los PNG dentro
    de `*/QSLS/` (profundidad 3); ahora se borran todas las salidas (preservando `FLAGS/`).
14. **`bandera_espana.png` eliminado** (ya no se usa; las banderas vienen de `FLAGS/`).
15. **(histórico) `dac1.adi` se desactivó renombrándolo a `dac1.adi.TEST`** (110 contactos,
    POTA ES-1895), igual que `eladio1/2/3.adi.TEST`. Ya no queda ningún `.TEST` (ver punto
    19), así que la regla que se establecía aquí está hoy vacía: si algún día vuelve a
    aparecer un `.adi.TEST`, es inactivo a propósito y no se renombra a `.adi` sin consultar.
16. **Sincronización con Google Drive por defecto.** `generar.sh` copia las postales
     de cada `qslN/QSLS/` a `~/Library/CloudStorage/GoogleDrive-eg9mm.mail@gmail.com/My
     Drive/QSL/QSLs/qslN` (mismas carpetas en minúsculas, creadas automáticamente). La
     sincronización ocurre **siempre**, salvo flag `--no-sync-drive`. La carpeta de Drive
     es un **espejo exacto** de la local: `rsync -av --update --delete` copia lo
     nuevo/modificado y borra en Drive los PNG que ya no están localmente. La app de
     escritorio de Google Drive sube los cambios a la nube automáticamente.
17. **Versión v3 del generador** (`GENERATOR_VERSION = "3"`). El log guarda esta
     versión; al subirla, los ADI ya registrados se reprocesan automáticamente sin
     necesidad de `--from-scratch`.
18. **Robustez en `_load_country_map`:** se validan también los ítems sin `cc` (código
     ISO2) no vacío; se descartan antes de indexarlos. Si un callsign no tiene país o
     bandera, simplemente **no se dibuja nada** (sin crash).
19. **Eliminados los `.adi.TEST`** (`eladio1/2`, `eladio3`, `dac1`): ya no existen en el
     repositorio. Los ADI activos se renombran libremente durante las pruebas (son
     volátiles); la regla de no renombrar sin consultar aplica solo a archivos `.TEST`.

### Estructura actual en disco

```
ia-qsls/
├── qsl_generator.py       <- Script principal (todo en un archivo)
├── generar.sh             <- Script de ejecución autónoma (bash)
├── drive_index.py         <- Genera qsl_index.json para la web (§7)
├── index.html             <- Página web de descarga (GitHub Pages)
├── qsl_index.json         <- Índice web (ahora vacío: total 0)
├── country_map.json       <- Prefijos de indicativo -> ISO2 (845, longest-match)
├── FLAGS/                 <- Banderas oficiales (PNG ~80x53, flagcdn). 249 países
├── TEST DATA/             <- 10 .adi de ejemplo/prueba (NO se procesan aquí)
├── .gitignore             <- Excluye venv/, __pycache__, qsl*/QSLS/, qsl*/qsl_log.json
├── venv/                  <- Entorno virtual (Pillow), creado automáticamente
├── README.md
├── LICENSE                <- Todos los derechos reservados
├── qsl1/
│   ├── f1.png             <- Fondo de qsl1
│   └── QSLS/              <- (vacía) se llena al copiar aquí los .adi y ejecutar
├── qsl2/
│   ├── f2.png
│   └── QSLS/              <- (vacía)
├── qsl3/
│   ├── f3.png
│   └── QSLS/              <- (vacía)
├── qsl4/
│   ├── f4.png
│   └── QSLS/              <- (vacía)
├── qsl5/
│   ├── f5.png             <- Fondo de qsl5
│   └── QSLS/              <- (vacía)
├── qsl6/
│   ├── f6.png
│   └── QSLS/              <- (vacía) postcards de record, se regeneran siempre
└── qsl7/
    ├── f7.png
    └── QSLS/              <- (vacía) postcards DMR
```

Notes sobre esta estructura:

- **No hay ningún `.adi` dentro de `qsl1`–`qsl7`.** Es el estado de inicio buscado.
- **No hay `qslN/qsl_log.json`.** Se crean solos la primera vez que se procesa un `.adi`
  real, y están ignorados por `.gitignore`.
- **`qslN/QSLS/` existe pero vacía** en las 7 actividades (los PNG no se versionan).
- **`qsl6/qsl6.txt` y `qsl7/qsl7.txt` ya no existen** (las notas de actividad se
  eliminaron al vaciar el árbol; la regla de la QSL6 se documenta en §3.b).
- Las carpetas `qsl1`–`qsl7` de **Google Drive** también existen, pero vacías (regla 1 de
  §0: nunca se borran).

---

## 2. Cómo ejecutar

### Opción A: uso el script autónomo `./generar.sh` (recomendado)

El script es portable: se puede copiar a cualquier lado, calcula su propio directorio,
crea el venv e instala Pillow si hace falta, y no toca tus `.adi` ni tus fondos.

```bash
./generar.sh                    # incremental + copia las postales a Google Drive (por defecto)
./generar.sh --no-sync-drive    # incremental, SIN copiar a Google Drive
./generar.sh --from-scratch     # borra QSLS/*.png y qsl_log.json y regenera TODO
./generar.sh --from-scratch --no-sync-drive  # regenera todo, sin copiar a Drive
./generar.sh --clean            # alias de --from-scratch
./generar.sh --index            # además regenera qsl_index.json (índice web, ver §7)
./generar.sh --index-only       # solo regenera qsl_index.json (no toca las postcards)
```

Salida típica en el **estado de inicio** (sin `.adi` en las carpetas, nada que generar).
Lo que ves es el setup de `generar.sh` y luego la salida del generador:

```
============================================================
  GENERADOR QSL — setup automático
  Proyecto: /Users/danielcialdella/Downloads/ia-qsls
============================================================
→ python3 detectado: Python 3.14.8
→ venv ya existente: /Users/danielcialdella/Downloads/ia-qsls/venv
→ Pillow ya disponible: 12.3.0
→ ejecutando qsl_generator.py ...

============================================================
  GENERADOR DE POSTALES QSL (incremental)
============================================================

📂 QSL1  (sin archivos .adi, nada que generar)
📂 QSL2  (sin archivos .adi, nada que generar)
📂 QSL3  (sin archivos .adi, nada que generar)
📂 QSL4  (sin archivos .adi, nada que generar)
📂 QSL5  (sin archivos .adi, nada que generar)
📂 QSL6  (fondos: f6.png)
   ℹ️  Ninguna estación contactó en las 5 actividades. Sin records que generar.
📂 QSL7  (sin archivos .adi, nada que generar)

============================================================
  RESUMEN: 0 procesados, 0 regenerados, 0 sin cambios
  Log por carpeta: qslN/qsl_log.json
============================================================

Postales generadas por carpeta:
   qsl1   0 postales
   qsl2   0 postales
   qsl3   0 postales
   qsl4   0 postales
   qsl5   0 postales
   qsl6   0 postales
   qsl7   0 postales

Listo. Busca las imágenes en cada qslN/QSLS/.
```

> Todo lo anterior es **literal**. El rótulo del resumen es `   %-6s %s postales`
> (`generar.sh:112`): dice "postales" también para qsl6 y qsl7, que son postcards de record
> y de DMR.

> Ojo: la línea `Log por carpeta: qslN/qsl_log.json` se imprime siempre, pero en el
> estado de inicio esos ficheros **no se crean** (solo se escriben al procesar un `.adi`
> real). `qsl6` se procesa siempre, aunque no tenga `.adi` propios.
>
> Con los flags por defecto (sin `--no-sync-drive`) se intercala además el bloque
> `→ sincronizando con Google Drive (...)`; y con `--index`, el resumen del indexado.
> Los bloques de arriba se recortan a lo que aporta `qsl_generator.py`.

La **primera** vez que se procesa un `.adi` (recién copiado de `TEST DATA/`) se anuncia con
`⚡`, no con `✓ sin cambios`. En la **segunda** ejecución, si nada ha cambiado:

```
📂 QSL1  (fondos: f1.png)
   ⚡ TOTA2222-delta-20260909-1145.adi: 1 contactos -> ea4huk_tota2222-delta-20260909-1145.png
   ⚡ faro-echo-20260909-1821.adi: 4 contactos -> ea4hjz_faro-echo-20260909-1821.png, df5bnl_faro-echo-20260909-1821.png, it9rki_faro-echo-20260909-1821.png, f5len_faro-echo-20260909-1821.png
   ⚡ pota1111-delta-20260909-1417.adi: 4 contactos -> ea3jaq_pota1111-delta-20260909-1417.png, ea4hjz_pota1111-delta-20260909-1417.png, df5bnl_pota1111-delta-20260909-1417.png, f5len_pota1111-delta-20260909-1417.png
   ...
============================================================
  RESUMEN: 8 procesados, 0 regenerados, 0 sin cambios
  Log por carpeta: qslN/qsl_log.json
============================================================
```

> `brief` lista como mucho los 5 primeros PNG y remata con `... y N más`.
> **El RESUMEN cuenta por archivo ADI, no por contacto**: los 8 son los 8 `.adi` del
> §1.1 (3 en qsl1 + 1 en qsl2, qsl3, qsl4, qsl5 y qsl7). `qsl6` aporta 0 mientras ninguna
> estación haya contactado en las 5 actividades.

Y en una tercera, ya con todo generado:

```
📂 QSL1  (fondos: f1.png)
   ✓ TOTA2222-delta-20260909-1145.adi: sin cambios (1 contactos ya generados)
   ✓ faro-echo-20260909-1821.adi: sin cambios (4 contactos ya generados)
   ✓ pota1111-delta-20260909-1417.adi: sin cambios (4 contactos ya generados)
   ...
============================================================
  RESUMEN: 0 procesados, 0 regenerados, 8 sin cambios
============================================================
```

### Opción B: ejecutar el generador manualmente

```bash
cd /Users/danielcialdella/Downloads/ia-qsls
source venv/bin/activate
python3 qsl_generator.py
```

IMPORTANTE: en macOS Python es “externally-managed”, por lo que **no** se usa `pip install`
globalmente; siempre activar `venv` (o usar `./generar.sh` que lo hace por ti).

### Sincronización automática con Google Drive (por defecto, desactivable)

La sincronización ocurre **siempre** que ejecutas `./generar.sh`. Solo se desactiva con
`--no-sync-drive`. Al terminar de generar, el script copia las postales a la carpeta local
sincronizada por la app de Google Drive:

```
~/Library/CloudStorage/GoogleDrive-eg9mm.mail@gmail.com/My Drive/QSL/QSLs/
├── qsl1/   <- qsl1/QSLS/*.png
├── qsl2/   <- qsl2/QSLS/*.png
├── …
└── qsl7/   <- qsl7/QSLS/*.png
```

- Cada carpeta local `qslN` se copia a su carpeta `qslN` (mismo nombre, en minúsculas)
  dentro de `QSL/QSLs`. Si la carpeta destino no existe, se crea automáticamente.
- La carpeta de Drive es un **espejo exacto** de `qslN/QSLS/`: se usa
  `rsync -av --update --delete`, que copia lo nuevo/modificado **y borra** en Drive los
  PNGs que ya no existen localmente (postales huérfanas eliminadas).
- Después la **app de escritorio de Google Drive** detecta los archivos y los sube a la
  nube automáticamente (no hace falta nada más).
- Preprequisito: tener la app "Google Drive" de escritorio instalada y con la cuenta de
  **eg9mm.mail@gmail.com**; la ruta del CloudStorage debe existir (la carpeta `QSL/QSLs`
  con las subcarpetas qsl1–qsl7 se crea sola la primera vez que se sincroniza).
- Para generar **sin** sincronizar Drive: `./generar.sh --no-sync-drive`.

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
   de qsl6 (f6.png). Muestra callsign (dorado), bandera + nombre, locator y las 5
   casillas QSL1–QSL5 tildadas + bandera de España en la casilla 6.
4. **No es incremental:** antes de generar se borran TODAS las postales de `qsl6/QSLS/`
   para que cada ejecución refleje la información actual. `qsl6/qsl_log.json` guarda la
   firma (sha256) del conjunto solo con fines informativos.

### Procesado incremental (clave)
Cada carpeta tiene `qsl_log.json` con, por archivo ADI:

```json
{
  "pota1111-delta-20260909-1417.adi": {
    "sha256": "bac65c…",
    "generador": "3",
    "contactos": [
      { "call": "EA4HJZ", "archivo": "ea4hjz_pota1111-delta-20260909-1417.png",
        "fondo": "f1.png", "generado_en": "2026-09-09T11:31:37Z" },
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
| ADI con **versión de generador distinta** (`generador`) | Se reprocesa completo |
| ADI ya procesado y todos sus PNG existen | Se omite ("sin cambios") |
| ADI ya procesado pero falta algún PNG | Se regenera **solo** ese PNG (reusa su fondo previo) |
| ADI borrado de la carpeta | Se elimina del log + se podan sus PNG huérfanos |
| PNG en QSLS/ no referenciado en el log | Se elimina (poda de huérfanos) |

Esto permite añadir 1 ADI por día sin repetir trabajo, y auto-recupera archivos borrados.
**Importante:** como los nombres ADI pueden cambiar, el log se referencia por nombre de
archivo; si renombras un ADI se tratará como nuevo (se regeneran sus postales).

### Nominación de archivos
- Formato: `{callsign}_{archivo_adi}.png` todo en minúsculas.
  - Ej: `EA4HJZ` + `pota1111-delta-20260909-1417.adi` → `ea4hjz_pota1111-delta-20260909-1417.png`
- Si el mismo callsign aparece 2+ veces en un ADI: sufijo `_2`, `_3`…
  (función `unique_filenames`)
- Actividad 6: `{callsign}_act6.png` (ej. `ea4huk_act6.png`).

### Fondos
- Cada carpeta usa **sus propios** fondos (los de su raíz), con la convención **`f<n>.png`
  donde `n` es el número de actividad**: QSL1 → `f1.png`, QSL2 → `f2.png`… QSL7 → `f7.png`.
  El nombre es solo convención: el generador **no** lo hardcodea, hace
  `glob('*.png')` sobre la carpeta (`folder_backgrounds`), así que cualquier otro nombre
  funciona igual mientras sea el único PNG de la raíz.
- Si una carpeta tiene varios fondos se alternan por contacto (`index % len(fondos)`).
- Al regenerar un faltante se **reusa el fondo** guardado en el log (`fondo`). Si ese nombre
  ya no existe (p. ej. renombraste el fondo), cae con gracia a `pick_background(...)`: no
  peta, pero la postcard se rehace con otro fondo.
- **Sin imagen → no se genera nada** (ni QSLS, ni log).

---

## 4. Formato ADI (lo que entiende el parser)

```
<VERSION:5>2.0.0
<PROGRAMID:4>QSLG
<EOH>                                    <- fin de cabecera

<QSO_DATE:8>20241215                     <- fecha YYYYMMDD
<TIME_ON:6>143022                        <- hora HHMMSS
<CALL:6>EA4HJZ                           <- REQUERIDO (único campo obligatorio)
<BAND:3>20M                              <- banda
<MODE:3>SSB                              <- modo
<RST_SENT:3>599                          <- RST enviado (se lee, NO se dibuja)
<RST_RCVD:3>599                          <- RST recibido (se lee, NO se dibuja)
<NAME:5>pedro                            <- nombre (opcional)
<QTH:8>madrid                            <- localidad (opcional)
<GRIDSQUARE:4>IN80                       <- grid locator (opcional)
<eor>                                    <- fin de registro
```

- **El único callsign obligatorio es `CALL`** (o, en su defecto, `DX_CALL`: `_resolve_call`
  hace `CALL or DX_CALL`, para los QSOs de FT8/FT4 que solo traen `DX_CALL`). Sin ninguno de
  los dos, el registro se descarta entero. `QSO_DATE` y `TIME_ON` **no se validan**: si
  faltan, la postcard se dibuja con `----` y `--:--`. Aun así, conviene exportarlos siempre
  desde el logger.
- El parser (`ADIFParser`) tolera la parte opcional `:TIPO` (ej. `<RST_SENT:3:number>`)
  y valores con signo (ej. RST `-10` para FT8).
- **Longitudes incorrectas toleradas:** si un tag declara más longitud de la que tiene
  (ej. `<QTH:8>madrid`), el valor se corta donde empieza el siguiente `<tag>`. Así no se
  colaba el símbolo `<` dentro del valor.
- **Cabecera ignorada** (`HEADER_KEYS`): `ADIF_VER`, `ADIFVER`, `PROGRAMID`,
  `PROGRAM_NAME`, `PROGRAMVERSION`, `EOH`, `USERDEF`, `CREATED_TIMESTAMP`,
  `GENERATED_TIMESTAMP`, `LASTUPDATED`, `SUBMITTED`, `ENDOFLOG`, `APP_ADIF_VER`.
  Ojo: **`VERSION` no está en esa lista** (el estándar ADIF usa `ADIF_VER`), así que un
  `<VERSION:5>` como el del ejemplo se guarda como un campo más del QSO. Es inofensivo
  (no se dibuja), pero es una rareza conocida del parser.
- Tolerante con exportadores que no cierran el último registro con `<EOR>`: el QSO
  pendiente se vuelca al final en lugar de perderse.
- Registros repetidos con el mismo callsign → sufijo numérico en el archivo.

---

## 5. Diseño de las postales

Tipo | Tamaño caja | Contenido | Casillas
---|---|---|---
**Normal** (`compose`) | 22% alto × 55% ancho, inf. izquierda | callsign, fecha+UTC, banda/modo, **bandera + nombre•QTH•grid** | "ACT" + 6 casillas con números; tilde en la suya
**Record act6** (`compose_act6`) | 20% alto × 62% ancho, inf. izquierda | callsign (dorado), **bandera + nombre**, locator | "ACT" + 6 casillas; tildes QSL1..QSL5 y bandera de España en QSL6
**DMR qsl7** (`compose`, activity=7) | 22% alto × 55% ancho | igual que la normal | NO muestra casillas: texto "DMR Confirmated"

- Tamaño: `WIDTH=1200` × `HEIGHT=800` (proporción 3:2). Se puede cambiar en la clase.
- El fondo se escala con recorte centrado "cover" (nunca distorsiona).
- Caja con radio 16–18 px, fondo negro `(0,0,0,150/160)` y borde (blanco sutil o dorado
  en act6).
- El texto (callsign) queda a 22 px del borde superior de la caja: `inner_top = box[1] +
  pad_y + 12`, con `pad_y = 10`.
- **Casillas** (`QSLGenerator.draw_activity_checkboxes`):
  - Fila alineada a la **derecha** de la caja con rótulo **"ACT"** a la izquierda.
  - Casillas redondeadas (30×30 normales, 28×28 act6), número 1–6 dentro de cada una.
  - La casilla de la actividad lograda **reemplaza el número por un tilde dorado**
    RGBA `(245, 166, 35, 255)` (2 trazos de 4px).
  - La casilla bandera (solo act6, casilla 6) dibuja la bandera de España en lugar del
    número: rojo `(198,11,30)` / amarillo `(255,200,0)`, franjas 1:2:1.
- **NO se dibuja** el texto RST ni la marca "QSL".
- **Sí se dibuja el sello de estación** `EG9MM - Melilla` (`STATION_TEXT`, constante en
  `qsl_generator.py:36`), en la esquina inferior derecha, con los colores de la bandera de
  España. Aparece en **las dos** composiciones (`compose` y `compose_act6`). Los ejemplos
  de postcard de esta web son de EG9MM, así que el sello es intencional.

### Banderas de país (delante del nombre)

- El país se deriva del **prefijo** del callsign (`ADIFParser` no lee campo COUNTRY).
  `country_map.json` mapea 845 prefijos → código ISO2 (fuente: ADIF DXCC, campo `prefix`,
  con corrección manual del prefijo `E` → España). Solo se contemplan entidades no
  eliminadas y códigos de país de 2 letras.
- Resolución por **longest-match** (el prefijo más largo que coincida gana; ej.
  `EA4HJZ`→ES, `LU1AA`→AR, `E7ABC`→BA, `ZL2TAL`→NZ). Índice por primera letra para
  resolver rápido con muchos contactos.
- `station_flag(call, height)` carga el PNG de `FLAGS/{cc}.png` (nombre en minúsculas) y
  lo reescala a `altura = la del texto`. Cacheado por `(cc, height)`.
- **Si no existe bandera para ese país (o la estación no tiene país), NO se dibuja nada**:
  el texto del nombre simplemente arranca en la posición original. Así nunca se pinta una
  bandera incorrecta.
- Banderas en `FLAGS/`: 249 PNG de flagcdn, en principio ~80×53 px pero en la práctica
  **24 tamaños distintos** (alturas de 31 a 98 px; solo 109 son 80×53). Da igual: el
  reescalado a la altura del texto normaliza todas. `country_map.json` tiene 248
  códigos ISO2 distintos y **faltan 4 banderas**: `un` (sede de la UIT, prefijo `4U`),
  `xi` (Irlanda del Norte, prefijos `GI`/`GN`/`2I`), `xk` (Kosovo, prefijo `Z6`) y `zz`
  (Orden Soberana de Malta, p.ej. `1A0AAA`). Esas estaciones se quedan sin bandera.
- La **esquina superior derecha** de cada postal lleva la bandera de España (`FLAGS/es.png`);
  si faltara el archivo, se dibuja igual la franja 1:2:1 como fallback.
- **`bandera_espana.png` fue eliminado**; las banderas ahora viven exclusivamente en `FLAGS/`.

---

## 6. Referencia del código (mapa de funciones)

| Función | Qué hace |
|---|---|
| `ADIFParser.parse(filepath)` | Parsea ADI → lista de dicts de QSO (longitudes tolerantes, sin `<`) |
| `ADIFParser._resolve_call(qso)` | Normaliza un QSO y descarta los que no tienen `CALL` |
| `QSLGenerator.get_font(size, bold)` | Carga fuente del sistema (cacheada) |
| `QSLGenerator.cover_fit(bg, w, h)` | Escala fondo a "cover" |
| `QSLGenerator.rounded_rect(draw, xy, r, fill)` | Rectángulo redondeado |
| `QSLGenerator.draw_activity_checkboxes(draw, box, checked, …)` | Fila "ACT" + 6 casillas con número/tilde/bandera |
| `QSLGenerator.get_flag_image()` | Bandera de España de FLAGS/es.png (esquina sup. dcha.) |
| `QSLGenerator.draw_spanish_flag(img, …)` / `_draw_spanish_flag_rects(draw, …)` | Bandera de España como imagen, o dibujada a franjas 1:2:1 como fallback |
| `QSLGenerator.draw_flag_color_text(…, text, …)` | Texto con la silueta rellena de los colores de la bandera (sello de estación) |
| `QSLGenerator.prepare_background(path, w, h)` | Carga + escala un fondo al tamaño de la postal |
| `QSLGenerator.fmt_date(qso)` / `fmt_time(qso)` | Formatean fecha (`----` si falta) y hora (`''` si falta; el rótulo `--:--` lo pone `compose`, no `fmt_time`) |
| `QSLGenerator.band_from_freq(freq)` | Banda desde la frecuencia, vía `BAND_RANGES` (`qsl_generator.py:39`) |
| `QSLGenerator._load_country_map()` | Carga country_map.json indexado por 1ª letra |
| `QSLGenerator.country_code_for_call(call)` | ISO2 desde prefijo (longest-match, ignora placeholders) |
| `QSLGenerator.station_flag(call, height)` | PNG de FLAGS/{cc}.png reescalado o None |
| `QSLGenerator.draw_station_flag(overlay, call, x, cy, height)` | Dibuja bandera delante del nombre; sin bandera no cambia x |
| `QSLGenerator.compose(bg, qso, activity=None)` | Postal normal (call, fecha, banda/modo, bandera+info + casillas; activity=7 → "DMR Confirmated") |
| `QSLGenerator.compose_act6(bg, call, name, grid)` | Postal de record (call dorado, bandera+nombre, locator + casillas con bandera) |
| `find_adi_files(folder)` | Detecta ADI/ADIF por extensión, sin duplicados, cualquier nombre |
| `folder_backgrounds(folder)` | Fondos de UNA carpeta |
| `pick_background(backgrounds, idx)` | Alterna `fondos[idx % n]` |
| `sanitize_filename_component(text)` | Limpia un componente de nombre de archivo |
| `sha256_file(path)` | Hash del ADI para detectar cambios |
| `load_log(folder)` / `save_log(folder, log)` | Leer/escribir `qsl_log.json` |
| `now_iso()` | Timestamp UTC |
| `png_valid(path)` | Comprueba PNG abrible |
| `prune_orphan_pngs(folder, log, label)` | Poda PNG de QSLS/ no referenciados en el log |
| `count_registered_pngs(folder)` | PNGs ya registrados (para secuencia fondos) |
| `unique_filenames(qsos, adi_stem)` | Nombres `{call}_{stem}.png` únicos |
| `process_folder(folder, gen, bgs, seq)` | Lógica incremental por carpeta |
| `process_act6(base_dir, gen)` | Limpia QSL6/QSLS + detecta estaciones en las 5 actividades + genera QSL de record |
| `main()` | Orquesta las 7 carpetas (qsl6 especial) |
| `drive_index.py` → `fetch/split_blocks/parse_folders/parse_files/fsize/calln/main` | **Scraping del HTML público** de la carpeta de Drive con `urllib` (sin API, sin credenciales) y escribe `qsl_index.json` con los *file ids* |

---

## 7. Página web pública de descarga de QSLs

### Qué hace

`index.html` (en la raíz del repo, servido por **GitHub Pages**) es un buscador
público: la persona escribe su **indicativo** y la página muestra sus postcards
con miniatura y dos botones, **Descargar** y **Abrir** en Google Drive. Los PNG
siguen viviendo en tu carpeta de Drive; la web solo pone los enlaces.

La búsqueda es por **inicio del nombre del archivo** (que empieza por el indicativo,
ver `unique_filenames`): escribir `EA4` lista todas las estaciones EA4, y la
coincidencia exacta se resalta y se trae arriba.

> **Por qué hace falta un índice:** los enlaces de descarga de Drive siempre llevan
> el *file id* (`.../uc?export=download&id=<ID>`), nunca el nombre del archivo.
> `drive_index.py` recorre la carpeta **pública** de Drive, hace *scraping* del HTML con
> `urllib` (**sin API v3, sin credenciales y sin dependencias extra** — la `venv` solo
> tiene Pillow) y escribe `qsl_index.json` con nombre + id de cada PNG. Ese JSON se sube
> a git y es lo que la página descarga con `fetch`.

> Histórico: antes se usaba la API v3 con una cuenta de servicio y `drive_creds.json`.
> Ese enfoque se abandonó por el scraping del HTML público (más simple, cero secretos que
> guardar). Las referencias a `drive_creds.json` que quedan en `.gitignore` son inofensivas.

### Carpeta de origen

`My Drive/QSL/QSLs` → <https://drive.google.com/drive/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy>

- ID de la carpeta: `1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy`, hardcodeado en la constante
  `DEFAULT_FOLDER_ID` de `drive_index.py`. **No hay flag para cambiarlo**: para indexar otra
  carpeta hay que editar esa constante.
- Contiene `qsl1`…`qsl7`. Dentro de cada una, los PNG se llaman
  `{indicativo}_{nombre_adi}.png`, así que **el prefijo del nombre es el indicativo**.
- Acceso: *Cualquier persona con el enlace* → Lector. **Ya está hecho** (verificado:
  la carpeta responde 200 sin iniciar sesión). Es un requisito indispensable: sin enlace
  público el scraping devuelve 0 ficheros.

### Puesta en marcha

No hay nada que preparar: **no hacen falta credenciales, ni cuenta de servicio, ni
dependencias**. Solo la carpeta de Drive compartida por enlace (ya está) y:

```bash
./generar.sh --index-only              # ejecuta drive_index.py y escribe qsl_index.json
```

`drive_index.py` **no parsea argumentos** (`argparse` está importado pero no se usa) y
siempre escribe el archivo. `main()` no acepta `--dry-run` ni `--folder-id`: cualquier
flag que le pases se ignora en silencio.

> Bug latente conocido: `generar.sh:138` invoca `drive_index.py` con
> `"${DRIVE_INDEX_ARGS_ARR[@]}"`, pero **`DRIVE_INDEX_ARGS_ARR` no se asigna en ningún
> sitio**. O sea que `DRIVE_INDEX_ARGS="--folder-id <ID>" ./generar.sh --index-only`
> tampoco funciona. Para indexar otra carpeta hay que editar `DEFAULT_FOLDER_ID` en
> `drive_index.py:6`.

Después, sube el índice y activa GitHub Pages (Settings → Pages → *Deploy from a branch*
→ `main` / raíz). La página queda en **https://dcialdella.github.io/ia-qsls/**

### Uso diario

```bash
./generar.sh --index          # postcards + sync a Drive + regenera qsl_index.json
./generar.sh --index-only     # solo regenera el índice (no toca las postcards)
./generar.sh                  # no toca el índice (hay que pedirlo con --index)
```

> **Ojo con el retardo de Drive:** Drive for Desktop sube los PNG de forma
> asíncrona. Si generas postcards nuevas y sincronizas en el mismo momento, el
> índice se construirá antes de que existan en la nube: repite `--index-only`
> un minuto después.

### Formato de `qsl_index.json`

Los 7 `id` de actividad y el `folder_id` **se rellenan siempre** (regla 1 de §0), aunque
no haya ninguna postcard. Estado actual del repo: índice **vacío pero válido**, con
`total: 0`, `counts` a 0 y `entries: []`. La web lo muestra sin errores.

```json
{
 "version": 1,
 "generated_at": "2026-10-04T10:00:00Z",
 "folder_id": "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy",
 "folder_url": "https://drive.google.com/drive/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy",
 "activities": {"qsl1": {"id": "1XyZ...", "title": "Actividad 1"}},
 "counts": {"qsl1": 12, "qsl2": 3},
 "total": 15,
 "entries": [
   {"call": "EA4HJZ", "act": "qsl1",
    "name": "ea4hjz_pota1111-delta-20260909-1417.png",
    "id": "1QwErTy...", "size": 210433}
 ]
}
```

- El ejemplo abrevia `activities` a una sola clave, pero el archivo real trae **las 7**
  con su `id` y su `title` ("Actividad 1"… "Actividad 7"), siempre, aunque estén vacías.
- `call` se deduce del nombre del archivo (`{call}_{stem}.png`), no del log.
- `entries` **no lleva `modified`**: el scraping del HTML no lo expone. El tamaño (`size`)
  sí se lee, vía la redirección `uc?export=download`.
- La web usa `lh3.googleusercontent.com/d/<id>` para las miniaturas y
  `drive.google.com/uc?export=download&id=<id>` para la descarga.

### Seguridad

- **No hay secretos que gestionar.** `drive_index.py` no usa la API de Drive ni credenciales:
  solo lee el HTML de la carpeta pública. `drive_creds.json` ya no hace falta para nada
  (las entradas que lo ignoran en `.gitignore` son una precaución inofensiva).
- La web es estática: no habla con Drive en ningún momento, solo carga `qsl_index.json`
  desde GitHub Pages.
- Con la carpeta pública, cualquiera que conozca el enlace puede ver todos los PNG.
  Es coherente con que las QSL son públicas, pero tenlo en cuenta si añades
  datos personales (nombre/QTH) que no quieras exponer.
- Corolario de usar HTML público: si algún día Drive deja de renderizar esos `<a>` en su
  HTML, el índice saldría vacío **sin error visible**. Si `total: 0` de repente, es lo
  primero a mirar.

---

## 8. Tareas pendientes / próximos pasos

Partiendo del estado de inicio (sin `.adi` en `qslN/`, sin postcards generadas):

1. **Prueba de humo del generador:** copiar 2–3 `.adi` de `TEST DATA/` a sus actividades
   (ver §1.1) y ejecutar `./generar.sh --no-sync-drive`. Debe crear postcards en
   `qslN/QSLS/` y los `qsl_log.json` correspondientes.
2. **Confirmar visualmente las postales** generadas (abrir `qslN/QSLS/*.png`) y validar
   que las banderas de país delante del nombre se ven como se espera, y que las casillas
   1–6 / el texto "DMR Confirmated" salen bien.
3. **Revisar la sincronización a Google Drive**: ejecutar `./generar.sh` y comprobar que en
   `QSL/QSLs/qsl1`–`qsl7` aparecen las postcards y que la app las sube a la nube.
4. **Verificar la web** con datos reales: `./generar.sh --index` y comprobar
   `qsl_index.json` en <https://dcialdella.github.io/ia-qsls/qsl_index.json>.
5. Cuando haya varias estaciones en las 5 actividades, revisar que `qsl6/QSLS/` comienza
   a contener varias postcards `{call}_act6.png` (se regeneran en cada ejecución).
6. Cuando quieras **activar contactos masivos** (p.ej. Eladio/DAC con Ham2K o Smart
   Logger), dejar sus `.adi` en la carpeta de su actividad y ejecutar `./generar.sh`.
7. (Resuelto) **Longitudes declaradas mal ajustadas.** El parser recorta el valor a la
   longitud `<len>` solo si el valor real es **más largo**: `<QTH:3>palermo` → `pal`. Si
   declara más de lo que tiene (`<QTH:8>palermo`), respeta la cadena entera (`palermo`),
   no se rellena ni se corta. Antes se documentaba al revés aquí; el comportamiento real
   está en §4.
8. (Opcional) Añadir banderas para los 4 códigos sin PNG en `FLAGS/`: `un` (sede de la
   UIT, prefijo `4U`), `xi` (Irlanda del Norte), `xk` (Kosovo) y `zz` (Orden de Malta).
   Hoy esas estaciones se quedan sin bandera.

---

## 9. Notas de entorno

- **Mac (darwin), zsh.** El script `generar.sh` funciona también en Linux.
- **Python:** 3.14 venv con **solo Pillow** (12.3.0) + `pip`. Ni numpy ni google-auth:
  el generador no los usa y `drive_index.py` va con la `urllib` de la stdlib.
- **Fuentes usadas:** Arial → Helvetica → Verdana → DejaVu, en ese orden de preferencia
  (`get_font`, `qsl_generator.py:266`). En macOS suelen salir Arial o Helvetica; DejaVu es
  el fallback para Linux.
- **Filesystem case-insensitive:** por eso se evitan los globs que mezclan mayúsculas.
- No hay tests automáticos; la verificación es ejecutar el script + revisar los PNG.
- `./generar.sh` es la forma recomendada de ejecutar: configura el entorno solo y, con
  `--from-scratch`, regenera todo el set de postales; por defecto además copia las
  postales a Google Drive (usa `--no-sync-drive` para evitar la copia).
- **Git/GitHub:** el proyecto está en `git` (rama `main`) con remote `origin` →
  https://github.com/dcialdella/ia-qsls.git. `qsl*/QSLS/` y los `qsl_log.json` están
  ignorados por `.gitignore` (no se suben). Se commitean los fondos, los `.adi` (los de
  `TEST DATA/` ahora, los de `qslN/` cuando los actives), `index.html`, `qsl_index.json`,
  `country_map.json`, `FLAGS/`, el código y el README.
- **Estado Git:** `main` en sync con `origin/main` (0 ahead, 0 behind). Último commit:
  `bf02d44` — *"Unificar los fondos: f1.png..f7.png en las 7 actividades"*. Antes,
  `a756881` — *"Regeneracion total sin ADIs in qsl1-qsl7: 0 postcards, indice a 0"*: el
  volcado deliberado al estado de inicio que describe §1.
- **Punto de retorno guardado:** hay un tag **`inicio-fresco`** en `bf02d44` que congela
  este estado (sin ADIs en `qslN/`, sin postcards, índice a 0). Ver §10.
---

## 10. Punto de retorno: el tag `inicio-fresco`

Hay un tag de git que congela el estado "**INICIO FRESCO sin datos generados**", por si
hay que deshacer pruebas o empezar de cero otra vez:

```bash
git tag -n9 inicio-fresco        # ver qué guarda
git show inicio-fresco           # contenido exacto del tag
```

### Qué estado congela

Apunta al commit `bf02d44`:

- `qsl1`–`qsl7` con **solo su fondo**: `f1.png` … `f7.png` (convención `f<n>.png`)
- `qslN/QSLS/` **vacía** en las 7 actividades (0 postcards)
- **Ningún** `qslN/qsl_log.json` (se crean solos al primer procesado real)
- **Cero** `.adi` dentro de `qsl1`–`qsl7`
- Los 10 `.adi` de ejemplo en `TEST DATA/`, sin procesar
- `qsl_index.json` válido pero vacío: `total: 0`, `counts` a 0, `entries: []`

### Cómo volver a él

**Para trabajar desde ahí sin perder el `main` actual** (recomendado):

```bash
git switch -c prueba-inicio-fresco inicio-fresco
```

**Para volver al estado de inicio destruyendo lo que haya ahora**:

```bash
git reset --hard inicio-fresco
git clean -fdX qsl1 qsl2 qsl3 qsl4 qsl5 qsl6 qsl7   # borra QSLS/*.png y qsl_log.json
./generar.sh --no-sync-drive                        # comprobación: 0 postcards
./generar.sh --index-only                           # deja el índice a 0
```

> `git reset --hard` **descarta** cualquier cambio sin commitear. Haz `git status` antes.
> El `git clean -fdX` solo borra lo ignorado (`QSLS/`, `qsl_log.json`); el `-X` es lo que
> limita el borrado a los ficheros ignorados, así que no toca `f<n>.png` ni los `.adi`.

### Lo que el tag NO guarda

- **Los PNG generados y los `qsl_log.json`**: están en `.gitignore`, así que no entran en
  ningún commit ni en el tag. Para eso está el `git clean -fdX` de arriba. (En el momento
  de crear el tag no había ninguno, así que el tag sí reproduce el estado completo.)
- **Google Drive**: la carpeta `QSL/QSLs` con sus 7 subcarpetas vive fuera de git. Hay que
  comprobarla a mano. Recuerda la regla 1 de §0: **las 7 carpetas nunca se borran**, aunque
  estén vacías. Para vaciarlas, borra los PNG de `qslN/QSLS/` y ejecuta
  `./generar.sh` (el `rsync --delete` los refleja en Drive) o bórralos allí a mano.
