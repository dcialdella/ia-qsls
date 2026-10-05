# GENERADOR DE POSTALES QSL desde archivos ADI

Genera imágenes tipo postal (QSL cards) sobreponiendo los datos de contactos de radio
sobre una foto/imagen de fondo. Cada carpeta `qsl1`–`qsl7` representa una actividad
independiente con su propia imagen de fondo, sus propios archivos ADI, y sus propias
postales generadas.

> **Resumen:** lee archivos de contactos en formato ADI, deriva el país de cada estación
> desde el prefijo del callsign (y dibuja su bandera), y genera una postal QSL por
> contacto con los datos (callsign, fecha, banda/modo, nombre, QTH, grid) y las casillas
> de las 6 actividades (con la QSL6 de "record" para quien completó las 5). Funciona en
> modo incremental (solo regenera lo que cambió).

> **Autor:** Daniel Cialdella — dcialdella@gmail.com — EA4HUK
>
> **Aviso de uso:** esta aplicación fue diseñada por Daniel Cialdella. Para su uso,
> distribución o modificación debe solicitarse permiso previo al autor.

> **Objetivo final:** el usuario ejecuta `./run_all.sh`, y para cada carpeta qslN con
> archivos `.adi` + una imagen de fondo, se generan tantas postales como contactos haya,
> guardadas en `qslN/QSLS/`. Por defecto (siempre, a menos que se use `--no-sync-drive`)
> las postales se copian automáticamente a la carpeta `QSL/QSLs/qsl1`–`qsl7` de Google
> Drive (app de escritorio sincronizada con la cuenta eg9mm), que las sube a la nube.
> Después, `run_all.sh` regenera el índice web y pushea a GitHub, de modo que las
> postcards nuevas quedan descargables en <https://dcialdella.github.io/ia-qsls/>.
> **El flujo de trabajo diario está en §2.0.**

---

## 0. Reglas invariables (no romper)

1. **Las carpetas `qsl1`–`qsl7` de Google Drive NO se borran nunca.** Deben **existir
   siempre**, aunque estén **vacías**. Si desaparecen, hay que volver a crearlas
   (el índice web y los enlaces de descarga dependen de que existan los 7 `id`).
2. **Los archivos `.adi` son parte del proyecto: se versionan en Git y se suben al
   repo.** No contienen información sensible (datos públicos de radioaficionado:
   indicativo, nombre, grid locator, banda/modo). Van en la carpeta de su actividad
   (`qslN/*.adi`) y los de prueba en `TEST DATA/`. No deben borrarse ni excluirse
   del control de versiones. *Hoy hay 6 `.adi` en las carpetas de actividad —un
   `TEST.adi` en `qsl1`–`qsl5` y `qsl7`— y los 10 de ejemplo en `TEST DATA/` (§1).
   `qsl6/` no lleva ninguno (§1).*
3. **En `qslN/QSLS/` no se versiona ningún PNG.** Es salida generada y está en
   `.gitignore` (`qsl*/QSLS/`).
4. **La raíz de Drive `QSLs` solo contiene las 7 carpetas `qsl1`–`qsl7`**, ningún
   archivo suelto en la raíz.
5. **Tras cada generación de imágenes (parcial o total) hay que regenerar el índice
   y subir el código.** El sitio lee `qsl_index.json` desde GitHub Pages, así que
   sin push la web no ve las postcards nuevas. La forma normal de hacerlo es
   **`./run_all.sh`** (ver §2.0), que ya encadena los tres pasos:
   1. `./generar.sh --index` (o `--from-scratch` y luego `--index-only` si hay que
      esperar a que Drive suba los PNG a la nube).
   2. `git add -A && git commit && git push`.
   3. Verificar en <https://dcialdella.github.io/ia-qsls/qsl_index.json> que
      `total` y `counts` reflejan lo generado (Pages tarda ~1 min).
   Ojo: `drive_index.py` lee la nube, no el disco local; si se indexa antes de que
   Drive suba los ficheros, el JSON sale sin las postcards nuevas (no necesariamente
   con `total: 0`). Se arregla repitiendo `./run_all.sh` al minuto.

---

## 1. Estado actual del proyecto

> **Estado actual: en producción, con datos de prueba reducidos.** Las actividades
> `qsl1`–`qsl5` y `qsl7` tienen **un único `.adi` cada una** (`TEST.adi`, la estación
> `EG9MM`), y las 7 postcards resultantes están sincronizadas con Google Drive y
> publicadas en <https://dcialdella.github.io/ia-qsls/>. El flujo diario está en §2.0.
>
> Los datos de ejemplo que hubo antes (`estN.adi`, `stationsN.adi`, `qslN_ejemplo.adi`,
> `qslN_extra1.adi`) y las 67 postcards que generaban **se quitaron a propósito** y se
> sustituyeron por el `TEST.adi` de un solo contacto. Siguen recuperables con
> `git log -- qsl1/est1.adi` si hicieran falta, y hay una copia completa en
> `../ia-qsls-backup-20261005-110936`.

- ✅ Script funcional e **incremental** en `qsl_generator.py` (`GENERATOR_VERSION = "4"`)
- ✅ Entorno virtual `venv/` con Pillow instalado
- ✅ **Proceso diario en un comando:** `./run_all.sh` (ver §2.0)
- ✅ Las 7 carpetas con su fondo: qsl1 (`f1.png`), qsl2 (`f2.png`), qsl3 (`f3.png`),
  qsl4 (`f4.png`), qsl5 (`f5.png`), qsl6 (`f6.png`), qsl7 (`f7.png`) — la convención es
  `f<n>.png`, el número coincide con la actividad
- ✅ **Datos reducidos a un `.adi` de prueba por actividad:**

  | Actividad | `.adi` | Contactos | Postcards en `QSLS/` |
  |---|---|---|---|
  | `qsl1` | 1 (`TEST.adi`) | 1 | 1 |
  | `qsl2` | 1 (`TEST.adi`) | 1 | 1 |
  | `qsl3` | 1 (`TEST.adi`) | 1 | 1 |
  | `qsl4` | 1 (`TEST.adi`) | 1 | 1 |
  | `qsl5` | 1 (`TEST.adi`) | 1 | 1 |
  | `qsl6` | **0 (no lleva `.adi`)** | — | 1 (record) |
  | `qsl7` | 1 (`TEST.adi`) | 1 | 1 |
  | **Total** | **6** | **6** | **7** |

  `qsl6` **no lleva ningún `.adi`** y no debe llevar ninguno: sus postcards de record se
  derivan de los QSO ya registrados en `qsl1`–`qsl5` (ver §3.b). Por eso el manifiesto
  cuenta para `qsl6` las postcards que produce, no los `.adi` que consume; si contara los
  `.adi` daría 0 y la web excluiría la actividad entera aunque sus PNG existieran.
- ✅ `qsl_index.json` coherente con lo publicado: `total: 7`, 1 indicativo (`EG9MM`)
- ✅ Los 10 `.adi` de ejemplo siguen aparcados en `TEST DATA/` y **no se procesan**
  (el generador solo lee `qslN/*.adi`). Lo que se procesa de verdad es el `TEST.adi`
  de cada actividad, un `.adi` por QSO.
- ✅ `TEST.adi` es un **contacto de relleno**, no un dato real: en cuanto haya
  `.adi` de verdad se sustituye por ellos (§1.1). El flujo no cambia.
- ✅ No quedan archivos `.adi.TEST` (fueron eliminados; los renombrados pasan a `.adi`)
- ✅ **Casillas de actividades en TODAS las postales normales** (QSL1..QSL6).
- ✅ **Bandera del país** delante del nombre de cada estación (ver "Banderas" más abajo).
- ✅ **Sin bandera de España en la esquina** ni **sello `EG9MM`** abajo a la derecha
  (retirados en la v4; su código se borró del repo, está en el historial de git).
- ✅ Repositorio Git con remote en **GitHub** (`dcialdella/ia-qsls`, rama `main`).

### 1.1 Repoblar o vaciar una actividad

**Para añadir contactos** (el caso normal): copia el `.adi` a `qslN/` y corre
`./run_all.sh`. Nada más. Ver §2.0.

```bash
cp ~/nuevos-contactos.adi qsl1/
./run_all.sh
```

#### De los datos de prueba a los ADI reales

`TEST.adi` (un único contacto `EG9MM`, repetido en `qsl1`–`qsl5` y `qsl7`) es un
**relleno** para dejar el pipeline probado de punta a punta. Los contactos de verdad van
en sus propios `.adi`, con los nombres que dé tu logger (Ham2K, Smart Logger, N1MM+…):
`EA4HUK_20260912.adi`, `cqww-20260913.adi`, `dx-2026-10-01.adi`… El nombre es libre; el
generador detecta los `.adi` por extensión y calcula el nombre de cada PNG a partir de
él, así que **solo importa que el sufijo sea `.adi` o `.adif`**.

Para sustituir el relleno por datos reales:

```bash
# 1) Quitar el .adi de relleno (si sigue puesto)
rm qsl[1-5]/TEST.adi qsl7/TEST.adi

# 2) Copiar los .adi reales a la carpeta de su actividad
cp ~/loggers/EA4HUK_20260912.adi  qsl1/
cp ~/loggers/cqww-20260913.adi     qsl3/

# 3) Correr el flujo diario: detecta los nuevos, genera, sincroniza y publica
./run_all.sh
```

Cuatro cosas que conviene saber antes de hacerlo:

- **No hace falta borrar nada ni regenerar de cero.** El generador es incremental: los
  `.adi` nuevos se procesan y las postcards viejas se podan solas (`prune_orphan_pngs`)
  en cuanto su `.adi` desaparece del log. **Lo que está en Drive y en la web es exactamente
  lo que dice el conjunto actual de `.adi`.**
- **El nombre de la PNG incluye el nombre del `.adi`** (`{indicativo}_{nombre_adi}.png`).
  Si en un `.adi` aparece dos veces el mismo indicativo, `unique_filenames()` añade un
  sufijo para que no se pisen. El índice agrupa por el campo `call`, no por el nombre del
  archivo, así que un mismo indicativo en dos `.adi` sale en una sola tarjeta.
- **Los indicativos se leen del nombre del archivo, no de la web.** Por eso conviene que
  el nombre del `.adi` no cambie una vez generado: si lo cambias, el generador lo trata
  como un `.adi` nuevo, genera las postcards con el nombre nuevo y poda las viejas. El
  resultado es el mismo, pero se procesa dos veces.
- **Un `.adi` corrupto o truncado no se detecta**: el parser es tolerante y salta los QSO
  que no entiende. Revisa que el número de contactos del `.adi` coincide con el que
  anuncia la salida del generador (`⚡ <archivo>.adi: N contactos -> …`) antes de dar por
  buena una corrida.

`qsl6` **no** es un destino para `.adi` reales: es la actividad de record y se deriva sola
de lo que haya en `qsl1`–`qsl5` (§3.b).

**Los `.adi` de `TEST DATA/`** son datos de ejemplo/prueba, no datos de producción, y
el generador no los toca mientras estén ahí. Si algún día quieres procesarlos, cópialos
a su actividad (la tabla del final de esta sección indica cuál) y luego bórralos de
`TEST DATA/` para no duplicar.

**Para vaciar una actividad** por completo (dejar `qsl1` sin contactos y sin
postcards), lo normal es **borrar los `.adi` y correr `./run_all.sh`**. Es decir: **lo que
está en Drive y en la web es exactamente lo que dice el conjunto actual de `.adi`**.

> **Ojo, vaciarla tiene dos pasos, no uno.** `prune_orphan_pngs()` —la rutina que borra
> los PNG que el log ya no referencia— **solo se llama desde dentro de `process_folder()` y
> de `process_act6()`**. Si borras los `.adi` y la carpeta se queda **sin ninguno**, `main()`
> hace `continue` justo después de `find_adi_files()` (`qsl_generator.py:1054-1057`) y nunca
> llega a `process_folder()`: **la poda no se ejecuta y los PNG locales sobreviven.**
>
> Lo que sí ocurre es que el manifiesto deja de contar esa actividad, así que
> `drive_index.py` la excluye del índice (la web deja de ofrecerla), y el
> `rsync --delete` de la misma pasada borra los PNG de **Drive**. El resultado final es el
> correcto, pero el borrado local no lo hace el generador: lo hace el `rsync`, contra Drive.
>
> Para que no queden restos en local, borra también los PNG:
>
> ```bash
> rm -f qsl1/*.adi qsl1/QSLS/*.png
> ./run_all.sh
> ```
>
> Si la carpeta conserva **al menos un** `.adi`, entonces sí se ejecuta la poda y basta
> con borrar los `.adi` sobrantes.

Si además quieres reempezar esa actividad desde cero (sin conservar su log):

```bash
find qsl[1-7] -maxdepth 1 -name '*.adi' -delete   # quita los .adi de las actividades
./generar.sh --from-scratch --no-sync-drive      # borra QSLS/*.png y los qsl_log.json
./generar.sh --index-only                         # deja el índice coherente
```

> Usa `find` y no `rm qsl*/*.adi`: en zsh un glob sin coincidencias aborta el comando con
> `no matches found` en vez de ser un no-op.

> **Importante:** `--from-scratch` es necesario solo si además quieres **borrar el log**
> de esa actividad. Si solo borras los `.adi` y ejecutas el generador, las postcards se
> podan igual. `qsl6` es la única actividad que se limpia sola en cada pasada.

> **Excepción:** si quieres conservar en Drive lo que ya no tenga `.adi` en local (p.ej.
> archivar el histórico de una actividad cerrada), usa `./run_all.sh --keep-empty-drive`:
> no vacía esa carpeta de Drive, pero la web **sí** dejará de ofrecerla.

`qsl6` (postales de record) no necesita `.adi` propios: se alimenta de los contactos ya
registrados en las actividades 1–5 (ver §3.b). Por eso **`qsl6/` no lleva ningún `.adi`**:
el que hubo allí (`qsl6_extra1.adi`) se borró, y copiarle un `.adi` no serviría de nada,
porque el generador salta a `process_act6()` para esa actividad y nunca busca ADIs propios.

`update_adi_dates.py` es un ayudante de una sola vez que reasignó fechas y horas
distintas a los `.adi` (ver cambio 22). **No forma parte del flujo diario**: si se vuelve
a ejecutar, vuelve a desplazar las horas de todos los ADI. Está versionado solo por
traza histórica de cómo se hizo.

Para provar el generador de punta a punta puedes generar postcards de prueba a partir de
ellos: copia solo los que te interesen a la carpeta de su actividad y bórralos de
`TEST DATA/` para no duplicar. Contenido actual de `TEST DATA/` (contactos según `<CALL:`):

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

> Ojo también: `lugar1-delta1-2026-10-04.adi` (2 contactos) es una alternativa a los tres
> ficheros de qsl1, no un cuarto. Si copias los cuatro a la misma actividad tendrás
> contactos duplicados en la web.

### Cambios recientes (aplicados y verificados)

1. **Caja de datos más alta (22%).** De 17% a 22% del alto (+5%) para que entre mejor el
   texto de la estación. Antes el callsign quedaba pegado al borde superior.
2. **Texto separado del borde superior.** `inner_top` usa `pad_y + 12` en lugar de
   `pad_y + 4`; el callsign queda a ~10px del borde interior de la caja.
3. **Casillas de actividades rediseñadas:** fila alineada a la **derecha** de la caja de
   datos, con el rótulo **"ACT"** a la izquierda. Las casillas son más pequeñas
   (26×26 px en las normales —el tamaño está fijado en `compose`, no es el default de
   `draw_activity_checkboxes`—, 28×28 px en act6).
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
   **solo los datos del contacto**. El sello fijo de estación `STATION_TEXT`
   (`"EG9MM - Melilla"`) se dibujaba en la esquina inferior derecha de todas las postcards,
   pero **ya no se dibuja desde la v4** (ver punto 20); en esta revisión se borraron también
   su constante y las funciones de dibujo, que quedaban muertas (`get_flag_image`,
   `draw_spanish_flag`, `draw_flag_color_text` y sus cachés, ~65 líneas). Viven en el
   historial de git si hacen falta.
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
20. **Versión v4 del generador: fuera la bandera de España y el sello de estación.**
     Se han quitado **dos elementos** de todas las postcards:
     - La **bandera de España de la esquina superior derecha** (era `draw_spanish_flag()`,
       5% x 5% de la postal) ya no se dibuja.
     - El **sello `EG9MM - Melilla` de la esquina inferior derecha** (minicaja negra con
       el texto relleno con los colores de la bandera, `draw_flag_color_text()`) ya no
       se dibuja.

     Se quitaron las llamadas y, más tarde, **el código muerto**: `draw_spanish_flag()`,
     `_draw_spanish_flag_rects()`, `draw_flag_color_text()`, `get_flag_image()` y la
     constante `STATION_TEXT` **ya no existen** en el fichero (punto 7). Si hay que
     recuperarlos están en el historial de git, en el commit anterior a esta revisión.
     *Se conservan* (no son el sello de estación): la **bandera del país** delante del
     nombre de cada estación, y la **bandera de España dentro de la casilla 6** de las
     postcards de record de QSL6.
21. **`run_all.sh`: el proceso diario en un comando.** Envoltura de `generar.sh --auto`
     que encadena generar → sync a Drive → regenerar `qsl_index.json` → `git add -A`
     → commit → push. Ver §2.0.
22. **Fechas y horas distintas en los `.adi`.** Los ADI de `qsl1`–`qsl7` usaban las
     mismas fechas y horas en varios ficheros (`20240901`/`100000` en todos los de
     qsl1, `20240902`/`100000` en todos los de qsl2, etc.), así que postcards distintas
     mostraban datos idénticos. Ahora cada actividad tiene su día (`20240901`…
     `20240907`) y cada QSO su hora, avanzando 5 minutos por contacto dentro de la
     actividad. Se regeneró todo el set.

### Estructura actual en disco

```
ia-qsls/
├── qsl_generator.py       <- Script principal (todo en un archivo)
├── run_all.sh             <- PROCESO DIARIO: generar + Drive + índice web + git push
├── generar.sh             <- Script de ejecución autónoma (bash), con --auto
├── drive_index.py         <- Genera qsl_index.json para la web (§7)
├── index.html             <- Página web de descarga (GitHub Pages)
├── qsl_index.json         <- Índice web (total 7, 1 indicativo)
├── qsl_manifest.json      <- nº de fuentes por actividad (generado, ignorado por git)
├── country_map.json       <- Prefijos de indicativo -> ISO2 (845, longest-match)
├── update_adi_dates.py    <- Ayudante de una sola vez (ya usado; ver §1.1)
├── FLAGS/                 <- Banderas oficiales (PNG ~80x53, flagcdn). 249 países
├── TEST DATA/             <- 10 .adi de ejemplo/prueba (NO se procesan aquí)
├── .gitignore             <- Excluye venv/, __pycache__, qsl*/QSLS/, qsl*/qsl_log.json
├── venv/                  <- Entorno virtual (Pillow), creado automáticamente
├── README.md
├── LICENSE                <- Todos los derechos reservados
├── qsl1/  f1.png + TEST.adi  + QSLS/ (1 PNG) + qsl_log.json
├── qsl2/  f2.png + TEST.adi  + QSLS/ (1 PNG) + qsl_log.json
├── qsl3/  f3.png + TEST.adi  + QSLS/ (1 PNG) + qsl_log.json
├── qsl4/  f4.png + TEST.adi  + QSLS/ (1 PNG) + qsl_log.json
├── qsl5/  f5.png + TEST.adi  + QSLS/ (1 PNG) + qsl_log.json
├── qsl6/  f6.png + (sin .adi) + QSLS/ (1 PNG, se regenera siempre)
└── qsl7/  f7.png + TEST.adi  + QSLS/ (1 PNG) + qsl_log.json
```

Notes sobre esta estructura:

- **Cada `qslN/` tiene sus `.adi` de trabajo**, que son los que se procesan; ahora uno por
  actividad, `TEST.adi` (1 QSO, `EG9MM`), a la espera de los `.adi` reales. Los 10 de
  `TEST DATA/` siguen aparcados ahí y no se tocan.
- **`qslN/QSLS/` tiene los PNG generados** (7 en total). No se versionan: están en
  `.gitignore`. La copia que se publica vive en Google Drive.
- **`qslN/qsl_log.json` existe** en las 7 actividades (se crean solos al primer procesado
  real). También ignorado por `.gitignore`.
- **`qsl6/` no tiene ni `.adi` ni processing propio:** `main()` salta a `process_act6()`
  para `i == 6` y nunca busca ADIs. La actividad de record se alimenta de `qsl1`–`qsl5`.
  Su PNG sí se regenera en cada pasada, porque depende de qué estaciones hayan contactado.
- **`qsl6/qsl6.txt` y `qsl7/qsl7.txt` ya no existen** (las notas de actividad se
  eliminaron al vaciar el árbol; la regla de la QSL6 se documenta en §3.b).
- Las carpetas `qsl1`–`qsl7` de **Google Drive** existen y están pobladas (regla 1 de §0:
  nunca se borran).

---

## 2. Cómo ejecutar

### 2.0 El proceso diario normal (lo de cada día)

Este es el flujo de trabajo de rutina:

1. **Copiar los `.adi` nuevos a la carpeta de su actividad:** `qsl1`, `qsl2`,
   `qsl3`, `qsl4`, `qsl5` o `qsl7`. No hace falta nada más: el generador los
   detecta solo por su hash.
2. **Correr un único comando:**

   ```bash
   ./run_all.sh
   ```

   Y ya está. `run_all.sh` es una envoltura de `generar.sh --auto` que encadena
   todo el proceso en este orden:

   | Paso | Qué hace |
   |---|---|
   | 1 | Detecta los `.adi` nuevos o modificados y genera sus PNG en `qslN/QSLS/` (incremental; `qsl6` se regenera siempre) |
   | 2 | Sincroniza los PNG con Google Drive (`rsync --update --delete`) |
   | 3 | Regenera `qsl_index.json` leyendo la carpeta pública de Drive |
   | 4 | `git add -A` + `git commit` + `git push` (los `.adi` nuevos también se suben) |
   | 5 | GitHub Pages publica el sitio en ~1 min |

   Los PNG de `QSLS/` y los `qsl_log.json` **no** se commitean (están en
   `.gitignore`): viven en Drive y la web los enlaza desde ahí.

3. **Verificar** en <https://dcialdella.github.io/ia-qsls/> que el indicativo
   buscado aparece.

> **Importante — el retardo de Drive:** el paso 3 indexa lo que hay **en la nube**,
> y Google Drive sube los ficheros de forma asíncrona. Si corres `./run_all.sh` en
> el mismo momento en que copias el `.adi`, las postcards nuevas todavía no están
> en Drive y **no aparecerán en la web** hasta la siguiente pasada.
>
> **Solución: repetir `./run_all.sh` un minuto después.** Reindexa y pushea
> siempre (la marca de tiempo `generated_at` cambia en cada corrida), así que la
> segunda pasada recoge lo que la primera se dejó por subir.

> **`qsl6` no recibe `.adi`.** Es la actividad de *record* y se alimenta sola de las
> estaciones que contactaron en `qsl1`–`qsl5`. Por eso el flujo diario usa las
> carpetas 1, 2, 3, 4, 5 y 7, y `qsl6/` no tiene ningún `.adi` que copiar.

### Opción A: usar el script autónomo `./generar.sh` (avanzado)

El script es portable: se puede copiar a cualquier lado, calcula su propio directorio,
crea el venv e instala Pillow si hace falta, y no toca tus `.adi` ni tus fondos.
`./run_all.sh` es la forma recomendada para el día a día; `generar.sh` directamente
sirve para casos puntuales (regenerar todo, probar sin tocar Drive, etc.).

```bash
./generar.sh                    # incremental + copia las postales a Google Drive (por defecto)
./generar.sh --auto             # igual que ./run_all.sh (además indexa y pushea)
./generar.sh --sync-drive       # explícito; es el default, sirve para dejarlo claro
./generar.sh --no-sync-drive    # incremental, SIN copiar a Google Drive
./generar.sh --from-scratch     # borra QSLS/*.png y qsl_log.json y regenera TODO
./generar.sh --from-scratch --no-sync-drive  # regenera todo, sin copiar a Drive
./generar.sh --clean            # alias de --from-scratch
./generar.sh --index            # además regenera qsl_index.json (índice web, ver §7)
./generar.sh --index-only       # solo regenera qsl_index.json (no toca las postcards)
./generar.sh --keep-empty-drive # NO vacía en Drive las actividades sin .adi (por defecto SÍ)
./generar.sh --folder-id <ID>   # indexa otra carpeta de Google Drive
./generar.sh --folder-id=<ID>   # misma cosa, forma con =
./generar.sh --force-index      # indexa aunque el recorte no cuadre con el manifiesto (§7)
```

Cualquier flag se puede pasar también a `./run_all.sh`, que los reenvía:
`./run_all.sh --keep-empty-drive`, `./run_all.sh --no-sync-drive`.

> **Actividades vaciadas.** Por defecto, una actividad sin `.adi` **sí** se vacía en Drive
> (antes se saltaba el sync y las postcards se quedaban ahí para siempre, y la web seguía
> ofreciéndolas aunque ya no existieran en local). Con `--keep-empty-drive` se conserva lo
> que hay en Drive, pero la web deja de ofrecer esa actividad igualmente.

Salida típica cuando **nada ha cambiado** desde la última corrida (el caso habitual del
flujo diario, §2.0). Lo que ves es el setup de `generar.sh` y luego la salida del
generador:

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

📂 QSL1  (fondos: f1.png)
   ✓ TEST.adi: sin cambios (1 contactos ya generados)
   …
📂 QSL6  (fondos: f6.png)
   🗑️  QSL6/QSLS: 1 postal/es regenerada/s desde cero
   🏆 1 estación/es contactaron en las 5 actividades
   ⚡ act6: 1 record(s) -> EG9MM → eg9mm_act6.png

============================================================
  RESUMEN: 0 procesados, 1 regenerados, 6 sin cambios
  Log por carpeta: qslN/qsl_log.json
  Manifiesto: qsl_manifest.json (qsl1=1, qsl2=1, qsl3=1, qsl4=1, qsl5=1, qsl6=1, qsl7=1)
============================================================

Postales generadas por carpeta:
   qsl1   1 postales
   qsl2   1 postales
   qsl3   1 postales
   qsl4   1 postales
   qsl5   1 postales
   qsl6   1 postales
   qsl7   1 postales

Listo. Busca las imágenes en cada qslN/QSLS/.
```

> Todo lo anterior es **literal**, salvo la línea `   …` que resume los cinco `TEST.adi`
> iguales. Ojo a la aritmética: el resumen dice **1 regenerado** (`qsl6`, que se rehace
> siempre) y **6 sin cambios** (los seis `TEST.adi`), pero las postcards totales son 7
> porque `eg9mm_act6.png` cuenta como una más.
>
> El rótulo por carpeta es `   %-6s %s postales` (`generar.sh:163`): dice "postales"
> también para qsl6 y qsl7, que son postcards de record y de DMR.

> Ojo: las líneas `Log por carpeta` y `Manifiesto` se imprimen siempre. Los ficheros se
> escriben al procesar un `.adi` real; `qsl6` se procesa siempre, aunque no tenga `.adi`
> propios.
>
> Con los flags por defecto (sin `--no-sync-drive`) se intercala además el bloque
> `→ sincronizando con Google Drive (...)`; y con `--index`, el resumen del indexado.
> Los bloques de arriba se recortan a lo que aporta `qsl_generator.py`.

La **primera** vez que se procesa un `.adi` (recién copiado de `TEST DATA/`, o sustituyendo
`TEST.adi` por uno real) se anuncia con `⚡`, no con `✓ sin cambios`. Tras un
`--from-scratch` completo:

```
📂 QSL1  (fondos: f1.png)
   ⚡ TEST.adi: 1 contactos -> eg9mm_test.png
   …  (igual en QSL2..QSL5 y QSL7)
📂 QSL6  (fondos: f6.png)
   🏆 1 estación/es contactaron en las 5 actividades
   ⚡ act6: 1 record(s) -> EG9MM → eg9mm_act6.png
============================================================
  RESUMEN: 7 procesados, 0 regenerados, 0 sin cambios
============================================================
```

> `brief` lista como mucho los 5 primeros PNG y remata con `... y N más`.
> **El RESUMEN cuenta por archivo ADI, no por contacto**, y `qsl6` **sí cuenta** como un
> procesado: por eso son 7 y no 6. En la pasada siguiente ya no, porque su PNG se rehace
> siempre desde cero (va a `regenerados`).

Y en la segunda, con todo ya generado:

```
📂 QSL1  (fondos: f1.png)
   ✓ TEST.adi: sin cambios (1 contactos ya generados)
   …
============================================================
  RESUMEN: 0 procesados, 1 regenerados, 6 sin cambios
============================================================
```

> Los tres contadores suman 7, y el único que cambia entre pasadas es `regenerados`: es
> `qsl6`, que se rehace en cada corrida. Con datos reales la cifra de "sin cambios"
> será la de tus `.adi` menos los que hayas tocado.

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
- Para **no vaciar** en Drive una actividad que ya no tiene `.adi`: `--keep-empty-drive`.
- Si un `rsync` falla a mitad, el script **aborta en ese instante** (`generar.sh:195-198`)
  con `ERROR: rsync falló al sincronizar qslN (código N)`, y **no llega a indexar ni a
  commitear**. Basta con repetir `./generar.sh --auto` (todo el proceso es incremental: no
  se pierde trabajo). Ese caso lleva su propio `exit` explícito, a propósito: dentro de un
  `if !`, `$?` es el de la negación (siempre 0) y el mensaje mentiría sobre el código real.
- Un `trap ERR` global (`generar.sh:42`) cubre además cualquier otro paso fallido —venv,
  Pillow, generación, `git push`— diciendo qué paso era y con qué código. Limitación
  conocida: `STEP` solo se actualiza en los pasos de sync, resumen e indexado, así que un
  fallo temprano reporta el paso como «inicio». Además `exit` **no** dispara `trap ERR`, y
  por eso el fallo de `rsync` tiene su mensaje propio y no aparece en el del trap.

### El manifiesto de actividades (`qsl_manifest.json`)

`qsl_generator.py` escribe al terminar `qsl_manifest.json` con **cuántas fuentes tiene cada
actividad**. Para `qsl1`–`qsl5` y `qsl7` eso es el número de `.adi`; para `qsl6` es el
número de **postcards de record que ha producido**, porque no consume ningún `.adi`:

```json
{ "generated_at": "…", "generador": "4",
  "adi_counts": {"qsl1": 1, "qsl2": 1, "qsl3": 1, "qsl4": 1,
                 "qsl5": 1, "qsl6": 1, "qsl7": 1} }
```

El campo se llama `adi_counts` por historia, pero **`qsl6` no cuenta `.adi`**: cuenta las
postcards que generó en esa pasada.

`drive_index.py` lo lee y **excluye del índice las actividades con 0**, aunque sus PNG
sigan todavía en Drive. Así la web no ofrece postcards de una actividad vaciada, que
era el modo en que la web ofrecía ficheros que ya no existían en local.

> **Por qué `qsl6` necesita ese matiz.** Cuando `qsl6/` llevaba su propio `.adi`, contar
> `.adi` y contar postcards daba lo mismo. Al vaciarlo de `.adi` (que es lo correcto, §1),
> el manifiesto pasó a dar `qsl6: 0` y la web **excluía la actividad entera** aunque su PNG
> estuviera en Drive: el índice salía con 6 entradas en vez de 7 y el record de `EG9MM`
> quedaba invisible. Por eso, para `qsl6`, lo que decide si la actividad se publica es lo
> que **produce**, no lo que consume.
>
> El caso inverso también se comprobó: vaciando `qsl1`–`qsl5`, `qsl6` da 0 y la actividad
> se omite, que es lo correcto — no hay contactos de donde sacar un record.

El fichero está en `.gitignore`: es salida derivada, se regenera en cada corrida y no
merece un commit propio.

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
  - Casillas redondeadas (26×26 normales, 28×28 act6), número 1–6 dentro de cada una.
  - La casilla de la actividad lograda **reemplaza el número por un tilde dorado**
    RGBA `(245, 166, 35, 255)` (2 trazos de 4px).
  - La casilla bandera (solo act6, casilla 6) dibuja la bandera de España en lugar del
    número: rojo `(198,11,30)` / amarillo `(255,200,0)`, franjas 1:2:1.
- **NO se dibuja** el texto RST ni la marca "QSL".
- **Ya NO se dibuja el sello de estación** `EG9MM - Melilla`: se retiró en la v4 y **su
  código se borró del repo**, no quedó comentado. No hay ni `STATION_TEXT` ni
  `draw_flag_color_text()`.
- **Ya NO se dibuja la bandera de España** en la esquina superior derecha: se retiró en
  la v4 y **`get_flag_image()` / `draw_spanish_flag()` / `_draw_spanish_flag_rects()`
  también se borraron**. No queda código muerto de la esquina.
- Los dos cambios son reversibles, pero volver a esa versión exige rehacer el dibujo desde
  el historial (`git log -- qsl_generator.py`, commits anteriores a `fb9a16e`).

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
- La **esquina superior derecha** de cada postal **ya no lleva** la bandera de España:
  se retiró en la v4. Antes venía de `FLAGS/es.png` con la franja 1:2:1 dibujada como
  fallback si faltara el archivo.
- La bandera de España **sí se conserva** dentro de la casilla 6 de las postcards de
  record de QSL6 (`flag_box=6`), que es otro elemento distinto.
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
| `QSLGenerator.prepare_background(path)` | Abre el fondo y lo devuelve ya escalado a "cover" y en RGBA, cacheado por ruta (`cover_fit(bg, self.WIDTH, self.HEIGHT)`; no recibe tamaño como argumento) |
| `QSLGenerator.fmt_date(qso)` / `fmt_time(qso)` | Formatean fecha (`----` si falta) y hora (`''` si falta; el rótulo `--:--` lo pone `compose`, no `fmt_time`) |
| `QSLGenerator.band_from_freq(freq)` | Banda desde la frecuencia, vía `BAND_RANGES` (`qsl_generator.py:61`) |
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
| `main()` | Orquesta las 7 carpetas (qsl6 especial) y escribe `qsl_manifest.json` |
| `drive_index.py` → `fetch/split_blocks/parse_folders/parse_files/fsize/calln/main` | **Scraping del HTML público** de la carpeta de Drive con `urllib` (sin API, sin credenciales) y escribe `qsl_index.json` con los *file ids* |
| `drive_index.py` → `load_known_calls/read_existing/load_manifest/build_index` | `load_known_calls` lee los indicativos ya conocidos de los índices previos; `read_existing` carga el JSON en disco; `load_manifest` lee `qsl_manifest.json`; `build_index` scrapingea, aplica las **salvaguardas** (nunca escribir un índice vacío ni un recorte no justificado) y solo entonces escribe |

---

## 7. Página web pública de descarga de QSLs

### Qué hace

`index.html` (en la raíz del repo, servido por **GitHub Pages**) es un buscador
público: la persona escribe su **indicativo completo** y la página muestra sus
postcards con miniatura y un único botón, **Descargar/Download**. Los PNG siguen
viviendo en tu carpeta de Drive; la web solo pone los enlaces. La miniatura sigue
siendo un enlace a la vista previa en Drive.

La búsqueda es de **coincidencia exacta** del indicativo, usando el campo `call` del
índice (no el nombre del archivo, que además incluye el nombre del ADI): escribir
`EA4XX1` muestra solo las postcards de esa estación. Si el indicativo no existe, no se
muestra ninguna postcard y se indica cuáles empiezan por lo tecleado. Con el buscador
vacío no se pinta nada: solo el contador de postcards indexadas. No hay paginación,
porque nunca se muestran más postcards que las de un indicativo.

> **Por qué el campo `call` y no el nombre del fichero.** El nombre es
> `{indicativo}_{nombre_adi}.png`, y el indicativo puede contener una `/` que el generador
> sanea a `_` al escribir el archivo (`EA5/XZZ` → `ea5_xzz_...png`). `drive_index.py` lo
> resuelve en dos pasos, con un orden de preferencia deliberado:
>
> 1. **Fuente principal: los `qsl_log.json` locales.** `load_known_calls()` construye un
>    mapa `{nombre_png → indicativo real}` leyendo los logs, que guardan el indicativo
>    **sin transformar**. Si el nombre está ahí, se usa ese valor y no se heurística nada.
> 2. **Fallback: heurística sobre el nombre**, solo si no hay log (p. ej. indexando Drive
>    desde otro clon del repo). Se parte por el **primer** `_` y, si el resto encaja como
>    sufijo portátil (`cabeza` de 1–4 alfanuméricos, `cola` de 2–6 no numérica), se
>    **reconstruye la `/`**: `ea5_xzz_...png` → `EA5/XZZ`.
>
> La fuente principal importa porque el fallback no puede distinguir `EA5_XZZ` de un
> indicativo `EA5` seguido de un `.adi` llamado `XZZ…`: por eso, sin logs, los indicativos
> portátiles se agrupan bajo el prefijo (`EA5`). Con los logs locales presentes —es el caso
> normal, porque `drive_index.py` se ejecuta desde el repo— no hay ambigüedad.

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
  `DEFAULT_FOLDER_ID` de `drive_index.py`. Se puede cambiar sin editar código:
  `./generar.sh --folder-id <ID>` (o `python3 drive_index.py --folder-id <ID>`).
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

`drive_index.py` **parsea argumentos de verdad** (`argparse`, `main()` en
`drive_index.py:292`) y **solo escribe el archivo si el resultado es sano**:

| Flag | Efecto |
|---|---|
| `--folder-id <ID>` | Indexa otra carpeta de Drive (por defecto `DEFAULT_FOLDER_ID`) |
| `--out <ruta>` | Escribe el índice donde quieras (por defecto `qsl_index.json` en la raíz) |
| `--manifest <ruta>` | Usa otro manifiesto (por defecto `qsl_manifest.json`) |
| `--force` | Escribe el índice aunque la salvaguarda lo pidiera bloquear |

`generar.sh` propaga `--folder-id` y añade `--force` cuando le pasas `--force-index`
(`FORCE_INDEX=true` → `INDEX_ARGS+=("--force")`, `generar.sh:89`), así que desde el
flujo diario no hace falta tocar código.

> **Por qué existe `--force`.** Al vaciar actividades **a propósito** (o al sustituirlas
> por datos de prueba), la salvaguarda ve un recorte grande del que el manifiesto no da
> cuenta y se niega a escribir, por si lo que pasó fue un fallo de parseo de Drive:
>
> ```
> ERROR: el nuevo indice tiene 7 entradas y el anterior 28, y solo 0 son de
> actividades vaciadas por manifiesto. Parece un parseo fallido de Drive; no se escribe.
>        Usa --force si el recorte es intencionado.
> ```
>
> Si has revisado que el recorte es real, `--force-index` es lo correcto:
> `./generar.sh --index-only --force-index`. Si no lo es, **no lo uses** — el JSON bueno
> en disco sigue intacto y el problema está en el HTML de Drive.

Después, sube el índice y activa GitHub Pages (Settings → Pages → *Deploy from a branch*
→ `main` / raíz). La página queda en **https://dcialdella.github.io/ia-qsls/**

### Uso diario

```bash
./run_all.sh                    # postcards + sync a Drive + índice + commit + push
./generar.sh --index          # postcards + sync a Drive + regenera qsl_index.json
./generar.sh --index-only     # solo regenera el índice (no toca las postcards)
./generar.sh                  # no toca el índice (hay que pedirlo con --index)
```

Lo normal es `./run_all.sh` (§2.0). Los flags de abajo sirven para casos puntuales.

> **Ojo con el retardo de Drive:** Drive for Desktop sube los PNG de forma
> asíncrona. Si generas postcards nuevas y sincronizas en el mismo momento, el
> índice se construirá antes de que existan en la nube: repite `--index-only`
> (o `./run_all.sh`) un minuto después.

### Formato de `qsl_index.json`

`folder_id` se rellena siempre, y `activities` trae las 7 con su `id` y su `title`
("Actividad 1"… "Actividad 7") mientras la actividad esté publicada. La excepción son las
que el propio indexado decide dejar fuera: una actividad con **0 en el manifiesto** se
omite por completo (no aparece en `activities` ni en `counts`, y se avisa por pantalla con
`· qslN: sin .adi (manifiesto) -> no se publica`), y también una actividad cuyo HTML de
Drive no se puede leer, que se marca como fallida. Regla 1 de §0 sigue vigente en Drive:
las carpetas existen siempre; lo que puede no publicarse es su contenido.

Estado actual del repo: índice **poblado**, con `total: 7`, `counts` a 1 en cada una de
las 7 actividades y `entries` con una entrada por postcard (las 6 de `EG9MM` en
`qsl1`–`qsl5`/`qsl7` más `eg9mm_act6.png`). Si algún día saliera vacío (`total: 0`), la
web lo mostraría sin errores visibles — ver §7 "Seguridad".

```json
{
  "version": 2,
  "generated_at": "2026-10-05T12:23:02Z",
  "folder_id": "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy",
  "folder_url": "https://drive.google.com/drive/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy",
  "activities": {"qsl1": {"id": "1XyZ...", "title": "Actividad 1"}},
  "counts": {"qsl1": 1, "qsl2": 1, "qsl3": 1, "qsl4": 1, "qsl5": 1, "qsl6": 1, "qsl7": 1},
  "total": 7,
  "entries": [
    {"call": "EG9MM", "act": "qsl1",
     "name": "eg9mm_test.png",
     "id": "1QwErTy...", "size": 210433}
  ]
}
```

- La `version` del índice es **2**. La 1 ya traía las 7 `activities`; el salto reflects
  el formato de `entries` que consume hoy la web.
- El ejemplo abrevia `activities` a una sola clave, pero el archivo real trae **las 7**
  con su `id` y su `title`, salvo las que se omiten por manifiesto vacío o por fallo de
  fetch (ver arriba).
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
  HTML, el parseo devolvería 0 ficheros. `drive_index.py` **se niega a escribir** un índice
  con 0 entradas, o con menos entradas que el anterior sin que el manifiesto justifique la
  pérdida, y avisa por stderr: el JSON bueno en disco no se pisa. Si ves ese error, lo
  de arriba a mirar es el HTML de Drive, no las postcards.
- La web no inserta el `id` de Drive sin más: `index.html` lo valida contra
  `/^[A-Za-z0-9_-]{10,64}$/` y lo mete en las URLs con `encodeURIComponent`, y escapa
  `name`, `call` y `act` con `escapeHtml`. Una entrada con un id inesperado se descarta en
  vez de inyectarse en un atributo.
- Los tamaños del índice se piden con peticiones **HEAD** en paralelo (8 a la vez), no con
  GET: a ~1,4 s por fichero en serie, 5000 postcards serían unas 2 horas. Drive puede
  responder con una página HTML de intersticio en lugar de la imagen; se detecta
  comprobando el `Content-Type` y se guarda tamaño `0`.

---

## 8. Tareas pendientes / próximos pasos

Las primeras tareas del proyecto (prueba de humo, revisión visual, sincronización a
Drive, verificación de la web) ya están **hechas**: las 7 postcards están generadas,
sincronizadas y publicadas. El dataset es ahora mínimo a propósito (un solo contacto
`EG9MM`), a la espera de los `.adi` reales. Queda pendiente:

1. ~~**Repaso visual de las postcards tras la v4.**~~ La v4 quitó la bandera de España de
   la esquina y el sello `EG9MM`; falta abrir unas cuantas para confirmar el encuadre.
2. **Proteger `qsl_log.json` contra corrupción.** `load_log()` captura el
   `JSONDecodeError` de un JSON truncado (un corte de luz a mitad de escritura, o un merge
   a medias) y **devuelve `{}`**, es decir, "aquí no hay nada registrado". El `.adi` se
   reprocesa y `save_log()` reconstruye el log, así que **con los `.adi` intactos el
   daño es mínimo**: se regeneran sus PNG y se recupera el log. Comprobado.

   El problema aparece cuando el log corrupto **se junta con un `.adi` que ya no está**,
   porque entonces los PNG de ese `.adi` no tienen de dónde regenerarse y `prune_orphan_pngs()`
   los poda. Reproducido en una copia de prueba:
   ```
   🧹 qsl1: 1 postal/es huérfana/s eliminadas
   ```
   Y a partir de ahí el `rsync --delete` propaga el borrado a Drive y la web deja de
   ofrecerlas. Sigue siendo **parcial y acotado** (solo las actividades con el log
   corrupto, y solo las postcard de los `.adi` que ya no están), no un borrado masivo: si
   la carpeta se queda sin ningún `.adi`, `main()` hace `continue` y no se poda nada (§1.1).

   Mitigación barata y de bajo riesgo: validar el JSON al leerlo y, si no parsea, **abortar
   con un aviso** en vez de devolver `{}`. Así un log dañado se ve y se repara a mano,
   en lugar de que el sistema reinvente la verdad.
3. **Cavar con el retardo de Drive en el flujo diario.** De momento la solución es
   repetir `./run_all.sh` al minuto. Si molesta, se podría hacer que `run_all.sh`
   reintentara el indexado automáticamente hasta que `total` coincida con el número de
   PNG locales.
4. **Limpieza de `update_adi_dates.py`.** Es un ayudante de una sola vez, ya aplicado, y
   volver a ejecutarlo desplazaría las horas de todos los `.adi`. Podría borrarse.
5. **Ordenar los QSOs por fecha dentro de cada `.adi`.** Ahora la secuencia horaria sigue
   el orden en que aparecen en el fichero, no el cronológico. Cosmético, pero si algún día
   se quiere que las horas simulen una sesión real habría que ordenarlos.
6. ~~**Bug latente al pasar `--folder-id` a `drive_index.py`**~~ — **resuelto**:
   `drive_index.py` acepta ahora `--folder-id` de verdad (`argparse` propio, `main()` en
   `drive_index.py:292`) y `generar.sh` lo propaga con su propio `--folder-id` (y
   `--folder-id=<ID>`), así que ya no hace falta editar `DEFAULT_FOLDER_ID`.
7. (Opcional) Añadir banderas para los 4 códigos sin PNG en `FLAGS/`: `un` (sede de la
   UIT, prefijo `4U`), `xi` (Irlanda del Norte), `xk` (Kosovo) y `zz` (Orden de Malta).
   Hoy esas estaciones se quedan sin bandera.
8. **Tests.** El proyecto no tiene ninguno, y los arreglos de este ciclo (poda de PNG
   huérfanos, parser ADIF, derivación del indicativo) son justo lo que un test debería
   proteger. El candidato más barato: un test que ejecute el generador sobre `TEST DATA/`
   y compare el `qsl_log.json` resultante con un esperado.

---

## 9. Notas de entorno

- **Mac (darwin), zsh.** El script `generar.sh` funciona también en Linux.
- **Python:** 3.14 venv con **solo Pillow** (12.3.0) + `pip`. Ni numpy ni google-auth:
  el generador no los usa y `drive_index.py` va con la `urllib` de la stdlib.
- **Fuentes usadas:** Arial → Helvetica → Verdana → DejaVu, en ese orden de preferencia
  (`get_font`, `qsl_generator.py:289`). En macOS suelen salir Arial o Helvetica; DejaVu es
  el fallback para Linux.
- **Filesystem case-insensitive:** por eso se evitan los globs que mezclan mayúsculas.
- No hay tests automáticos; la verificación es ejecutar el script + revisar los PNG.
- **`./run_all.sh` es la forma recomendada de ejecutar** (§2.0): genera, sincroniza con
  Drive, reindexa la web y pushea. `generar.sh` directamente sirve para casos puntuales
  (regenerar todo con `--from-scratch`, probar con `--no-sync-drive`, etc.).
- **Git/GitHub:** el proyecto está en `git` (rama `main`) con remote `origin` →
  https://github.com/dcialdella/ia-qsls.git. `qsl*/QSLS/` y los `qsl_log.json` están
  ignorados por `.gitignore` (no se suben). Se commitean los fondos, los `.adi` (tanto los
  de `TEST DATA/` como los de `qslN/`), `index.html`, `qsl_index.json`,
  `country_map.json`, `FLAGS/`, el código y el README.
- **Estado Git:** `main` en sync con `origin/main`. Commits recientes, del más nuevo al más
  antiguo:
  - `bfdae81` — *"QSL6 no lleva .adi: el manifiesto contaba lo que consume, no lo que
    produce"* (el fix de `qsl6`, `--force-index`, el dataset `TEST.adi` y este README)
  - `0e94987` — *"Actualización automática"* (reindexado a 7 entradas)
  - `47c385b` — *"Actualización automática"* (los `.adi` reales de prueba, 28 `.adi`
    y 67 postcards)
  - `39dcaf2` — reindexado automático
  - `5ef0691` — el ciclo de arreglos grande (manifesto, salvaguardas, escapado de HTML,
    flags, traps)
  - `d9f1791` / `57aebfa` / `0bd6c33` — la web: sin lista al cargar, coincidencia exacta
    de indicativo, único botón de descarga
- **Copias de seguridad locales** (no están en git, son del propio repo):
  - `ia-qsls-backup-20261005-110936` — el estado de 28 `.adi` y 67 postcards, por si
    quisiera volver atrás.
  - `ia-qsls-backup-20261005-142557` — el estado `TEST.adi` de 7 postcards, justo antes de
    la commit `bfdae81`.
- **Punto de retorno guardado:** hay un tag **`inicio-fresco`** que congela el estado
  vacío (sin ADIs en `qslN/`, sin postcards, índice a 0). Ver §10. Nota: ese tag es ya
  **histórico** — volver a él significaría tirar las 7 postcards actuales.
---

## 10. Punto de retorno: el tag `inicio-fresco`

> ⚠️ **Este tag es histórico.** Congela el estado vacío del proyecto (sin `.adi` en
> `qslN/`, sin postcards, índice a 0), que era el punto de partida antes de poblar las
> actividades. **Volver a él descarta las 7 postcards actuales**, así que úsalo solo
> si de verdad quieres dejar el proyecto en blanco.

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

> Antes de nada, ten en cuenta que esto **tira las 7 postcards actuales**.

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
