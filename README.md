# GENERADOR DE POSTALES QSL desde archivos ADI

Genera imágenes tipo postal (QSL cards) sobreponiendo los datos de contactos de radio
sobre una foto/imagen de fondo. Cada carpeta `qsl1`–`qsl7` representa una actividad
independiente con su propia imagen de fondo, sus propios archivos ADI, y sus propias
postales generadas.

> **Resumen:** lee archivos de contactos en formato ADI, deriva el país de cada estación
> desde el prefijo del callsign (y dibuja su bandera **delante del callsign**), y genera
> una postal QSL por contacto con los datos (**bandera, callsign destinatario, nombre,
> QTH**, fecha, banda/modo, grid) más la **estación originante** (`OPERATOR`, o
> `STATION_CALLSIGN` si el ADI no trae `OPERATOR`) al inicio de la línea 2, y las casillas
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
> Las estadísticas del log completo se publican en una página independiente:
> <https://dcialdella.github.io/ia-qsls/graficos/> (27 gráficos, sin tocar las páginas
> existentes). **El flujo de trabajo diario está en §2.0.**

---

## 0. Reglas invariables (no romper)

1. **Las carpetas `qsl1`–`qsl7` de Google Drive NO se borran nunca.** Deben **existir
   siempre**, aunque estén **vacías**. Si desaparecen, hay que volver a crearlas
   (el índice web y los enlaces de descarga dependen de que existan los 7 `id`).
2. **Los archivos `.adi` son parte del proyecto: se versionan en Git y se suben al
   repo.** No contienen información sensible (datos públicos de radioaficionado:
   indicativo, nombre, grid locator, banda/modo). Van en la carpeta de su actividad
   (`qslN/*.adi`) y los de prueba en `TESTDATA/`. No deben borrarse ni excluirse
   del control de versiones. *Hoy hay 36 `.adi` en las carpetas de actividad —6 en
   `qsl1`–`qsl4`, 8 en `qsl5` y 4 en `qsl7`, entre ellos 6 de demostración y 5 de cruces adicionales— y 6 de
   ejemplo en `TESTDATA/` (§1). `qsl6/` no lleva ninguno (§1).*
3. **En `qslN/QSLS/` no se versiona ningún PNG.** Es salida generada y está en
   `.gitignore` (`qsl*/QSLS/`).
4. **La raíz de Drive `QSLs` solo contiene las 7 carpetas `qsl1`–`qsl7`**, ningún
   archivo suelto en la raíz.
5. **Tras cada generación de imágenes (parcial o total) hay que regenerar el índice
   y subir el código.** El sitio lee `qsl_index.json` desde GitHub Pages, así que
   sin push la web no ve las postcards nuevas. La forma normal de hacerlo es
   **`./run_all.sh`** (ver §2.0), que ya encadena los tres pasos:
   1. `./generar.sh --index` (o `--from-scratch` y luego `--index-only`; ambas leen
      `qslN/QSLS/`, así que no hay que esperar a que Drive suba los PNG).
   2. `git add -A && git commit && git push`.
   3. Verificar en <https://dcialdella.github.io/ia-qsls/qsl_index.json> que
      `total` y `counts` reflejan lo generado (Pages tarda ~1 min).
   El índice se construye **desde el origen local** `qslN/QSLS/` (las carpetas que
   luego se rsyncan a Drive), sin consultar el HTML público de Drive; por eso ya no
   hay que esperar a que la nube suba los PNG. Los `id` de descarga se reutilizan
   del `qsl_index.json` anterior. Para volver al modo antiguo de scraping de Drive:
   `./generar.sh --drive-index` (o `python3 drive_index.py` sin `--local`).

---

## 1. Estado actual del proyecto

> **Estado actual: en producción, con los datos reales cargados.** Las actividades
> `qsl1`–`qsl5` y `qsl7` tienen **36 `.adi` en total** (3.015 QSO de EA4HUK, EA4GHH,
> EA4IWX y EA3JAQ, incluidos 60 de los 5 `CRUZADAS-ADICIONALES-*.adi`), de los que se
> han generado **3.058 postales**, sincronizadas con
> Google Drive y publicadas en <https://dcialdella.github.io/ia-qsls/>. Los 6
> `QSL-DEMO-EG9MM.adi` de relleno siguen en el repo, pero ya no son el dataset
> publicado. El flujo diario está en §2.0. La carpeta `ADICIONALES/` guarda 9 `.adi`
> derivados para que las estaciones carguen sus QSO con EA4HUK; **no** cuenta como
> entrada del generador ni de los gráficos.
>
> Las estadísticas del log completo (3.009 QSO, sin los 6 registros demo) tienen una
> página independiente, <https://dcialdella.github.io/ia-qsls/graficos/>, con 27
> gráficos y sus miniaturas. No modifica la web de descarga ni el índice.
>
> Los datos de ejemplo que hubo antes (`estN.adi`, `stationsN.adi`, `qslN_ejemplo.adi`,
> `qslN_extra1.adi`) y las 67 postcards que generaban **se quitaron a propósito** y se
> sustituyeron primero por un `.adi` de un solo contacto y después por los ADI reales.
> Siguen recuperables con `git log -- qsl1/est1.adi` si hicieran falta, y hay copias
> completas en los backups de §9.

- ✅ Script funcional e **incremental** en `qsl_generator.py` (`GENERATOR_VERSION = "5.5"`)
- ✅ Entorno virtual `venv/` con Pillow instalado
- ✅ **Proceso diario en un comando:** `./run_all.sh` (ver §2.0)
- ✅ Las 8 carpetas con **un único** fondo cada una: qsl1 (`QSL-1.png`), qsl2 (`QSL-2.png`),
  qsl3 (`QSL-3.png`), qsl4 (`QSL-4.png`), qsl5 (`QSL-5.png`), qsl6 (`f6.png`),
  qsl7 (`f7.png`), qsl80 (`QSL-80.png`). El nombre **no** importa: el generador usa el único PNG de la raíz de
  cada carpeta y se queja si hay más de uno. Todos 1200×800 px; qsl1–qsl5 son PNG reales
  (2026-11-04) y qsl6–qsl7 JPEG con extensión `.png` (2026-10-12); detalle en
  §5 "Fondos actuales".
- ✅ **Datos reales cargados** en las actividades (36 `.adi` raíz):

  | Actividad | `.adi` | Contactos | Postales en `QSLS/` |
  |---|---|---|---|
  | `qsl1` | 6 | 565 | 565 |
  | `qsl2` | 6 | 426 | 426 |
  | `qsl3` | 6 | 628 | 628 |
  | `qsl4` | 6 | 478 | 478 |
  | `qsl5` | 8 | 852 | 852 |
  | `qsl6` | **0 (no lleva `.adi`)** | — | 43 (record) |
  | `qsl7` | 4 | 66 | 66 |
  | **Total** | **36** | **3.015** | **3.058** |

  Los 9 `.adi` de `ADICIONALES/` son derivados de los 5 `CRUZADAS-ADICIONALES`;
  no se cuentan aquí ni se procesan.

  Los 6 `QSL-DEMO-EG9MM.adi` (`CALL` = `XYZ123`, `STATION_CALLSIGN` = `EG9MM`) siguen
  entre esos 36 ficheros como relleno histórico; sus 6 contactos están incluidos en el
  total de 3.015 QSO y son los únicos que no corresponden a una estación real.
  `qsl6` **no lleva ningún `.adi`** y no debe llevar ninguno: sus postcards de record se
  derivan de los QSO ya registrados en `qsl1`–`qsl5` (ver §3.b). Por eso el manifiesto
  cuenta para `qsl6` las postcards que produce, no los `.adi` que consume; si contara los
  `.adi` daría 0 y la web excluiría la actividad entera aunque sus PNG existieran.
- ✅ `qsl_index.json` coherente con lo publicado: `total: 3058`, 1.110 indicativos
  distintos (1.109 sin contar `XYZ123`), `generated_at: 2026-11-17T20:37:14Z`; lo
  publicaron la fecha asignada a `qsl6` (`1ba3646`) y el índice local (`eb4e552`) (§9).
- ✅ Los 6 `.adi` de ejemplo siguen aparcados en `TESTDATA/` y **no se procesan**
  (el generador solo lee `qslN/*.adi`).
- ✅ Los `.adi` reales ya están incorporados: se procesan los 36 de las carpetas de
  actividad. `QSL-DEMO-EG9MM.adi` es relleno, no un sustituto de los datos reales (§1.1).
- ℹ️ **`qsl80/` es una actividad nueva e independiente** (QSO en 80 m): 1 `.adi`
  (`QSL80m.adi`, 15 contactos) y fondo `QSL-80.png`, copia de `qsl2/QSL-2.png`.
  `qsl_generator.py` la procesa igual que qsl1–qsl7 y produce 15 postales en
  `qsl80/QSLS/`. **Es solo local**: todavía no está en `qsl_index.json` ni se
  sincroniza a Drive, porque sus entradas no tienen ID de Drive asignado.
- ✅ **Proceso de ADI por actividad:** `./generar_adis.sh` genera en `qslN/ACTIVIDADES/`
  un `.adi` por actividad (TOTA/POTA/LLOTA) para subirlos a sus webs. Documentado en
  `README-ACTIVIDADES.md`. Solo procesa `qsl1`–`qsl5`.
- ✅ No quedan archivos `.adi.TEST` (fueron eliminados; los renombrados pasan a `.adi`)
- ✅ **Casillas de actividades en TODAS las postales normales** (QSL1..QSL6).
- ✅ **Bandera del país delante del callsign** en la caja de datos, siempre visible
  (incluso sin nombre/QTH; ver "Banderas" más abajo y changelog v5.1/v5.2/v5.3).
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

#### Cómo se incorporaron los ADI reales (y cómo añadir otros nuevos)

`QSL-DEMO-EG9MM.adi` (un único contacto, `CALL` = `XYZ123`, repetido en `qsl1`–`qsl5` y
`qsl7`) fue el **relleno** que dejó el pipeline probado de punta a punta. Los contactos
de verdad ya están cargados en sus propios `.adi`, con los nombres que dio cada logger
(Ham2K, Smart Logger, N1MM+…), por ejemplo `ea4huk-museo.adi`,
`EA4HUK@ES-0340-20261113.adi`, `ea4iwx-poi1-20261115.adi`. El nombre es libre: el
generador detecta los `.adi` por extensión y calcula el nombre de cada PNG a partir de
él, así que **solo importa que el sufijo sea `.adi` o `.adif`**. Para añadir más
contactos basta con copiar el `.adi` a la carpeta de su actividad y correr `./run_all.sh`
(como se indicaba al principio de esta sección); no hay que quitar los que ya están.

```bash
# Así se incorporaron los ADI reales en su momento:
cp ~/loggers/ea4huk-museo.adi              qsl1/
cp ~/loggers/EA4HUK@ES-0340-20261113.adi   qsl2/
./run_all.sh    # detecta los nuevos, genera, sincroniza y publica
```

Si se quisiera volver al dataset de demostración, habría que borrar los 25 `.adi`
reales y dejar solo los 6 de relleno; no es el estado actual.

Cuatro cosas que conviene saber sobre el flujo:

- **No hace falta borrar nada ni regenerar de cero.** El generador es incremental: los
  `.adi` nuevos se procesan y las postcards viejas se podan solas (`prune_orphan_pngs`)
  en cuanto su `.adi` desaparece del log. **Lo que está en Drive y en la web es exactamente
  lo que dice el conjunto actual de `.adi`.**
- **El nombre de la PNG incluye el nombre del `.adi`** (`{indicativo}_{nombre_adi}.png`).
  Si en un `.adi` aparece dos veces el mismo indicativo, `unique_filenames()` añade un
  sufijo para que no se pisen. El índice agrupa por el campo `call`, no por el nombre del
  archivo, así que un mismo indicativo en dos `.adi` sale en una sola tarjeta.
- **El nombre del `.adi` conviene que no cambie una vez generado.** Si lo cambias, el
  generador lo trata como un `.adi` nuevo, genera las postcards con el nombre nuevo y
  poda las viejas. El resultado es el mismo, pero se procesa dos veces. Los indicativos
  que muestra la web se leen de `qsl_log.json` (§7); el nombre del PNG es solo un
  *fallback* cuando ese log no está disponible.
- **Un `.adi` corrupto o truncado no se detecta**: el parser es tolerante y salta los QSO
  que no entiende. Revisa que el número de contactos del `.adi` coincide con el que
  anuncia la salida del generador (`⚡ <archivo>.adi: N contactos -> …`) antes de dar por
  buena una corrida.

`qsl6` **no** es un destino para `.adi` reales: es la actividad de record y se deriva sola
de lo que haya en `qsl1`–`qsl5` (§3.b).

**Los `.adi` de `TESTDATA/`** son datos de ejemplo/prueba, no datos de producción, y
el generador no los toca mientras estén ahí. Si algún día quieres procesarlos, cópialos
a su actividad (la tabla del final de esta sección indica cuál) y luego bórralos de
`TESTDATA/` para no duplicar.

**Para vaciar una actividad** por completo (dejar `qsl1` sin contactos y sin
postcards), lo normal es **borrar los `.adi` y correr `./run_all.sh`**. Es decir: **lo que
está en Drive y en la web es exactamente lo que dice el conjunto actual de `.adi`**.

> **Ojo, vaciarla tiene dos pasos, no uno.** `prune_orphan_pngs()` —la rutina que borra
> los PNG que el log ya no referencia— **solo se llama desde dentro de `process_folder()` y
> de `process_act6()`**. Si borras los `.adi` y la carpeta se queda **sin ninguno**, `main()`
> hace `continue` justo después de `find_adi_files()` (`qsl_generator.py:1138-1140`) y nunca
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

> `update_adi_dates.py` fue un ayudante de una sola vez que reasignó fechas y horas
> distintas a los `.adi` (ver cambio 22), ya aplicado. **Se eliminó** por no formar parte
> del flujo diario (volver a ejecutarlo desplazaría las horas de todos los ADI); queda en
> el historial de git por si hiciera falta.

Para provar el generador de punta a punta puedes generar postcards de prueba a partir de
ellos: copia solo los que te interesen a la carpeta de su actividad y bórralos de
`TESTDATA/` para no duplicar. Contenido actual de `TESTDATA/` (contactos según `<CALL:`):

```bash
# --- 1) Copiar los .adi de ejemplo a sus actividades ---
cp "TESTDATA/activo2.adi"                 qsl2/     # actividad 2
cp "TESTDATA/actividad3.adi"              qsl3/     # actividad 3
cp "TESTDATA/probe.adi"                   qsl4/     # 1 contacto (EA4HUK)
cp "TESTDATA/probe.adi"                   qsl5/     # 1 contacto (EA4HUK)
cp "TESTDATA/TOTA2222-delta-20260909-1145.adi" \
   "TESTDATA/faro-echo-20260909-1821.adi" \
   "TESTDATA/pota1111-delta-20260909-1417.adi" qsl1/   # actividad 1 (1+4+4)
cp "TESTDATA/ejemplo.adi"                 qsl7/     # actividad 7 (carpeta DMR)

# --- 2) Probar en local SIN tocar Google Drive ni la web ---
./generar.sh --no-sync-drive
# revisa qslN/QSLS/*.png a ojo

# --- 3) Cuando el resultado te guste: sincronizar + reindexar la web ---
./generar.sh --index
```

Ojo con los nombres que llevan **espacio** (`TESTDATA/probe copy.adi`): entrecomíllalos.

> Ojo también: `lugar1-delta1-2026-10-04.adi` (2 contactos) es una alternativa a los tres
> ficheros de qsl1, no un cuarto. Si copias los cuatro a la misma actividad tendrás
> contactos duplicados en la web.

### 1.2 Derivado `ea4huk-eg9-todo.adi` (Escritorio, fuera del repo)

`~/Desktop/ea4huk-eg9-todo.adi` reúne los **954 QSO propios de EA4HUK** de los 31
`.adi` raíz (qsl1: 256, qsl2: 174, qsl3: 130, qsl4: 87, qsl5: 261, qsl7: 46;
qsl6 no tiene `.adi` raíz). Sustituye en alcance al anterior `ea4huk9.adi`
(841 QSO, solo qsl1–qsl5). Es un agregado de trabajo, **no una entrada del
generador**: no se copia a ninguna carpeta `qslN/`, no suma postales ni cambia
`qsl_index.json` (3.058).

Normalización aplicada a los 954 registros:

| Campo | Valor final | Valor en los ADI raíz |
|---|---|---|
| `STATION_CALLSIGN` | `EA4HUK/9` | `EA4HUK` en todos |
| `MY_GRIDSQUARE` | `IM85` | `IM85` (256), `IM85MH` (391), `IM85MG` (261), ausente (46) |
| `CQZ` | `14` | ausente en los 954 |
| `ITUZ` | `37` | ausente en los 954 |
| `DXCC` | `32` | ausente en los 954 |
| `OPERATOR` | `EA4HUK` | sin cambios |

El `/9` indica que la operación se hizo desde Melilla (distrito EA9); `CQZ=14` e
`ITUZ=37` son las zonas CQ e ITU de la propia estación y `DXCC=32` (España) se
fija en todos los registros por decisión expresa, no se calcula del `CALL`.
El resto de campos (`CALL`, `FREQ`, `BAND`, `MODE`, `DISTANCE`, `TIME_ON`…) se
conserva tal cual.
No se incluyen los 73 QSO en los que EA4HUK es el corresponsal de otro log:
tienen `MY_GRIDSQUARE` de otra estación y no son QSO propios.

Verificación: 954 `<EOR>`, un solo `<EOH>`, 0 longitudes declaradas incorrectas,
0 duplicados por `CALL`+fecha+hora+banda+modo, fechas 20261113–20261115,
905 SSB, 3 FM y 46 DIGITALVOICE.

El otro derivado del Escritorio, `~/Desktop/todos-contactos.csv`, se regenera
desde los mismos 36 `.adi` raíz e incluye **todos** los QSO (3.015 filas más la
cabecera, 13 columnas, CRLF), también los 6 registros demo `EG9MM`/`XYZ123`.
No se versiona ni alimenta la web; es solo un volcado de trabajo.

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
     bandera errónea). Ocurre solo si el callsign no resuelve a ningún país; ya están
     todas las banderas de `country_map.json` (ver §5).
9. **Regeneración total de QSL6 en cada ejecución:** `process_act6` borra TODAS las
   postales de `qsl6/QSLS/` al empezar y las regenera siempre con la información actual
   (nombres, grids, banderas, versión del generador) y con la fecha fija `2026-11-15`
   (`ACT6_RECORD_DATE`, también forzada por `drive_index.py`). No es incremental.
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
     es un **espejo exacto** de la local: `rsync -a --update --delete` copia lo
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
23. **Nuevo diseño de la caja de texto (v5).** Rediseño completo de la zona de datos:
      - Caja fija en posición `x=220–1175, y=594–686` (955×92 px), sombra 4px, fondo gris semitransparente `(80,80,80,150)`, borde dorado `#C28C24`.
      - **2 líneas de texto** (separadores `-` en lugar de `|`):
        - Línea 1 (34pt bold): callsign dorado + bandera país + nombre + QTH.
        - Línea 2 (24pt): origen - fecha - hora - banda - modo - grid (desde v5.3).
      - Texto centrado verticalmente en la caja + offset 16px.
      - Checkboxes ACT alineados a la derecha (26×26 px, 6 casillas).
      - QSL1–5/7: tilde en su actividad; QSL6: tildes 1–5 + bandera España en casilla 6; QSL7: texto "DMR Confirmated" sin checkboxes.
      - Fuentes y `compose` / `compose_act6` reescritos.
      - **Generador v5**: subida de versión para forzar regeneración incremental de todas las actividades.
24. **PENDIENTE: Modificación futura de QSL específica** — ver notas en issue/roadmap para ajustes adicionales en el diseño de alguna actividad concreta.
25. **QSL6 texto de record, fix WSJT-X y footer web** (2026-10-06):
      - `compose_act6`: la línea 2 de la caja muestra ahora **"Todas las referencias conseguidas"** (y ` - Locator: X` si hay grid); arreglado el guion suelto de la línea 1 cuando no hay nombre.
      - `qsl_generar_adis.py`: `split_records` ahora es case-insensitive — antes no reconocía `<eoh>`/`<eor>` en minúscula y los exports de **WSJT-X** se saltaban ("sin registros QSO").
      - `index.html`: footer de créditos IA acortado a *"QSL diseñadas y retocadas con ayuda de IA mediante ChatGPT a partir de fotografías aportadas por el equipo"*.
26. **Prueba de carga de la web: 4000 entradas** (2026-10-06) — se publicó un
    `qsl_index.json` simulado con 4000 entradas (`79c5617`) y la web funcionó bien;
    se restauró el índice real de 7 (`bf2bfde`). Ver §7.
27. **Referencias TOTA reales para QSL1 y QSL2** (2026-10-11):
       - `qsl_generar_adis.py` (`CONFIG`): QSL1 pasa de `EAR-1234` a **`EAR-1901`** y
         QSL2 (Museo) de `EAR-1234` a **`EAR-1902`**. QSL1 sigue generando un único
         `-tota.adi`; QSL2 sigue generando `-tota.adi` + `-pota.adi` (`ES-0340`).
       - El cambio es **solo en el log de `ACTIVIDADES/`** (para la subida a las webs
         TOTA): ni `qsl_generator.py` ni las postales se tocan. Regenerado con
         `./generar_adis.sh` y verificado (`QSLMSG`, `MY_SIG_INFO` y cabecera con la
         referencia nueva).
       - `README-ACTIVIDADES.md`: actualizada la tabla de referencias, el ejemplo de
         campos TOTA y el ejemplo de `CONFIG`; retirada la nota de referencias
         provisionales.
28. **Limpieza y banderas completas** (2026-10-15):
       - Eliminado `update_adi_dates.py` (ayudante de una sola vez, ya aplicado; ver §1.1).
       - `FLAGS/` pasa de 249 a **253 PNG**: añadidas las 4 banderas que faltaban (`un`,
         `xi`, `xk`, `zz`). Ahora los **248** códigos de `country_map.json` tienen bandera
         y ninguna estación se queda sin ella por falta de PNG (ver §5).
29. **v5.1: la caja ya no muestra el `OPERATOR`** (2026-10-15):
       - `compose()`: el nombre de la línea 1 ya **no cae al fallback `OPERATOR`** — antes,
         al no haber campo `NAME`, la caja dibujaba el operador local (p. ej. `EA4HUK`).
         Ahora solo se muestran campos del contacto: `CALL`, `NAME` y `QTH`
         (la v5.3 reintroduce `OPERATOR` con otro significado: estación originante;
         ver punto 31).
       - La **bandera del CALL se dibuja siempre** en la caja, aunque no haya nombre ni
         QTH (antes solo se dibujaba si había nombre).
30. **v5.2: la bandera va primero en la caja** (2026-10-15):
       - El orden de la línea 1 pasa a **`[bandera] - CALL - nombre - QTH`** (antes
         `CALL - [bandera] - …`) en `compose()` y `compose_act6()`. Si el prefijo del
         CALL es desconocido no hay bandera y la línea empieza por el callsign.
       - Los indicativos se **normalizan a mayúsculas** en todo el flujo (parser,
         bandera, qsl6, nombres de PNG): `ea4hhh` y `EA4HHH` son la misma estación.
       - **`GENERATOR_VERSION = "5.2"`**: fuerza la regeneración incremental de todas las
         postales con solo correr `./run_all.sh`.
       - Demo de aquel momento: los `.adi` de relleno llevan `CALL` = `XYZ123`
         (`STATION_CALLSIGN` = `EG9MM`); entonces las 7 postcards publicadas eran
         `xyz123_*.png` y el índice web (`qsl_index.json`) listaba solo esas. Hoy el
         dataset real tiene 3.058 postales (§1). Tras purgar nombres viejos en Drive,
         repetir `./run_all.sh` un minuto después si el HTML público tarda en
         propagar el borrado (ver §2.0 y §7).
31. **v5.3: originante y destinatario en la postal** (2026-11-04):
       - La **estación destinataria** sigue siendo el `CALL` del contacto (línea 1,
         con su bandera y nombre/QTH).
       - La **estación originante** es el `OPERATOR` del ADI (una de las 4 válidas:
         `EA4HUK`, `EA4GHH`, `EA3JAQ`, `EA4IWX`) y se muestra al principio de la
         línea 2 como **`De EA4HUK - fecha - …`**, tanto en `compose()` como en
         `compose_act6()`. En la QSL6 de record se listan los operadores únicos de
         las 5 actividades.
       - `qsl_generator.py` avisa por consola si un ADI no trae `OPERATOR` o trae uno
         fuera de la lista válida (no aborta: la postal se genera igual).
       - `fit_text()` vuelve a usarse para recortar la línea 2 si no cabe en la caja.
       - `process_act6()` ya no falla si falta una carpeta `qsl1`–`qsl5`: avisa y no
         genera records (evita inventar estaciones que no contactaron en todas).
       - **Fondo único por carpeta:** `folder_backgrounds()` devuelve una sola imagen
         (el contrato del proyecto); si hay varias usa la de `mtime` más reciente y
         avisa. Se eliminaron `pick_background()` y `count_registered_pngs()` (ya no
         se alterna entre fondos).
       - El log guarda **`fondo_hash`** (sha256): si cambias el PNG de una carpeta,
         la próxima ejecución regenera sus postales automáticamente.
       - **`GENERATOR_VERSION = "5.3"`**: fuerza la regeneración incremental de todas
         las postales con solo correr `./run_all.sh`.
32. **v5.5: fallback del originante** (2026-11-17):
       - Los exports de **EA3JAQ** no traen `OPERATOR`, solo `STATION_CALLSIGN=EA3JAQ`,
         así que su línea 2 salía sin `De …`. Nueva helper `originating_station(qso)`:
         usa `OPERATOR` y, si falta, `STATION_CALLSIGN`.
       - Se aplica en `compose()` (postales normales), en los avisos de `process_folder()`
         y en la recogida de operadores de `process_act6()` (QSL6).
       - **`GENERATOR_VERSION = "5.5"`**: fuerza la regeneración de todas las postales.
 33. **Cinco ADI de cruces adicionales** (2026-11-17, commit `d0adfcf`):
        - Un `CRUZADAS-ADICIONALES-<referencia>.adi` por actividad (qsl1–qsl5), con
          12 QSO en 10 m cada uno: **+60 QSO** y +60 postales.
        - El índice pasa a `total: 3058` (conteos 565/426/628/478/852/43/66) y el
          `generated_at` a `2026-11-17T20:37:14Z`. Detalle en `RELLENO-QSO.md`.
        - Verificación de cruces: en las 5 actividades cada una de las 4 estaciones
          (`EA4HUK`, `EA3JAQ`, `EA4GHH`, `EA4IWX`) tiene al menos un QSO con cada una
          de las otras 3; no falta ningún par (§9).
 34. **Fecha de las QSL de record** (2026-11-17, commit `1ba3646`): las 43 postales de
     `qsl6` llevan `2026-11-15`; desaparece del índice el grupo `""` (sin fecha).
 35. **Índice generado en local** (2026-11-17, commit `eb4e552`): `drive_index.py --local`
     lee `qslN/QSLS/` sin acceder a Drive; `generar.sh` lo usa por defecto.
 36. **Nueve ADI derivados** (2026-11-17, commit `8ab2b1f`): `ADICIONALES/` reúne
     3 estaciones × TOTA/LLOTA/POTA con 15 QSO contra EA4HUK; no son entrada del
     generador ni de los gráficos.

### Estructura actual en disco

```
ia-qsls/
├── qsl_generator.py       <- Script principal (todo en un archivo)
├── run_all.sh             <- PROCESO DIARIO: generar + Drive + índice web + git push
├── generar.sh             <- Script de ejecución autónoma (bash), con --auto
├── generar_adis.sh         <- ADI por actividad: corre qsl_generar_adis.py (§ README-ACTIVIDADES.md)
├── qsl_generar_adis.py     <- Genera qslN/ACTIVIDADES/*.adi (TOTA/POTA/LLOTA)
├── drive_index.py         <- Genera qsl_index.json para la web (§7)
├── index.html             <- Página web de descarga (GitHub Pages)
├── qsl_index.json         <- Índice web (total 3058, 1110 indicativos)
├── graficos/              <- Página NUEVA de estadísticas (GitHub Pages)
│   ├── index.html         <- Galería de 27 gráficos, con miniaturas
│   ├── TODOS.adi          <- 3009 QSO de entrada (36 .adi raíz, sin 6 demo)
│   ├── *.png              <- 27 gráficos a resolución completa
│   ├── thumbs/*.png       <- 27 miniaturas de 720 px
│   ├── estadisticas_adi.json
│   └── LEEME.md
├── qsl_manifest.json      <- nº de fuentes por actividad (generado, ignorado por git)
├── country_map.json       <- Prefijos de indicativo -> ISO2 (845, longest-match)
├── FLAGS/                 <- Banderas oficiales (PNG ~80x53, flagcdn). 253 países
├── ADICIONALES/          <- 9 .adi derivados (3 estaciones × TOTA/LLOTA/POTA; NO se procesan)
├── TESTDATA/             <- 6 .adi de muestra de formato (NO se procesan aquí)
├── .gitignore             <- Excluye venv/, __pycache__, qsl*/QSLS/, qsl*/qsl_log.json
├── venv/                  <- Entorno virtual (Pillow), creado automáticamente
├── README.md
├── README-ACTIVIDADES.md  <- Documentación del proceso de ADI por actividad
├── LICENSE                <- Todos los derechos reservados
├── qsl1/  QSL-1.png + 6 .adi (565 QSO) + ACTIVIDADES/ + QSLS/ (565 PNG) + qsl_log.json
├── qsl2/  QSL-2.png + 6 .adi (426 QSO) + ACTIVIDADES/ + QSLS/ (426 PNG) + qsl_log.json
├── qsl3/  QSL-3.png + 6 .adi (628 QSO) + ACTIVIDADES/ + QSLS/ (628 PNG) + qsl_log.json
├── qsl4/  QSL-4.png + 6 .adi (478 QSO) + ACTIVIDADES/ + QSLS/ (478 PNG) + qsl_log.json
├── qsl5/  QSL-5.png + 8 .adi (852 QSO) + ACTIVIDADES/ + QSLS/ (852 PNG) + qsl_log.json
├── qsl6/  f6.png + (sin .adi) + QSLS/ (43 PNG de record, se regeneran siempre)
├── qsl7/  f7.png + 4 .adi (66 QSO) + QSLS/ (66 PNG) + qsl_log.json
└── qsl80/ QSL-80.png + 1 .adi (15 QSO) + QSLS/ (15 PNG) + qsl_log.json  [solo local]
```

Notes sobre esta estructura:

- **Cada `qslN/` tiene sus `.adi` de trabajo**, que son los que se procesan: 36 en total
  (6/6/6/6/8/0/4), con 3.015 QSO. Los 6 `QSL-DEMO-EG9MM.adi` de relleno y los 5
  `CRUZADAS-ADICIONALES-*.adi` conviven con los reales; los 6 de `TESTDATA/` siguen
  aparcados ahí y no se tocan. Los 9 `.adi` de `ADICIONALES/` viven fuera de `qslN/`
  y **no** son entrada del generador: son derivados de esos 5 cruces adicionales.
- **`qsl1`–`qsl5` tienen además `ACTIVIDADES/`**, con los `.adi` generados por
  `./generar_adis.sh` (ver `README-ACTIVIDADES.md`). Se borran y regeneran en cada
  ejecución; no se versionan como entrada del generador de imágenes.
- **`qslN/QSLS/` tiene los PNG generados** (3.058 en total). No se versionan: están en
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

### 2.0 El proceso completo: `./run_all.sh` (LO MÁS IMPORTANTE)

Este es **el único comando que necesitas** en el día a día. Todo lo demás de este README
es detalle o casos avanzados:

1. **Copiar los `.adi` nuevos a la carpeta de su actividad:** `qsl1`, `qsl2`,
   `qsl3`, `qsl4`, `qsl5` o `qsl7`. No hace falta nada más: el generador los
   detecta solo por su hash.
2. **Correr un único comando:**

   ```bash
   ./run_all.sh
   ```

   Y ya está. `run_all.sh` es una envoltura de `generar.sh --auto` que encadena
   **todo** el proceso en este orden — genera, sincroniza Drive, **regenera el índice
   web (`qsl_index.json`) desde `qslN/QSLS/` y lo pushea a GitHub** en cada corrida:

   | Paso | Qué hace |
   |---|---|
   | 1 | Detecta los `.adi` nuevos o modificados y genera sus PNG en `qslN/QSLS/` (incremental; `qsl6` se regenera siempre) |
   | 2 | Sincroniza los PNG con Google Drive (`rsync --update --delete`) |
   | 3 | Regenera `qsl_index.json` leyendo `qslN/QSLS/` (sin red; `--drive-index` para el modo antiguo) |
   | 4 | `git add -A` + `git commit` + `git push` (los `.adi` nuevos también se suben) |
   | 5 | GitHub Pages publica el sitio en ~1 min |

   Los PNG de `QSLS/` y los `qsl_log.json` **no** se commitean (están en
   `.gitignore`): viven en Drive y la web los enlaza desde ahí.

3. **Verificar** en <https://dcialdella.github.io/ia-qsls/> que el indicativo
   buscado aparece.

> **El índice ya no depende de la nube:** el paso 3 lee las carpetas locales
> `qslN/QSLS/`, así que las postcards nuevas (y los borrados) se reflejan en la
> primera pasada, sin esperar a que Drive suba nada. Solo el modo heredado
> `--drive-index` sigue sujeto al retardo del HTML público de Drive.

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
./generar.sh --index            # además regenera qsl_index.json desde qslN/QSLS (§7)
./generar.sh --index-only       # solo regenera qsl_index.json (desde qslN/QSLS)
./generar.sh --drive-index      # modo antiguo: indexa leyendo el HTML público de Drive
./generar.sh --keep-empty-drive # NO vacía en Drive las actividades sin .adi (por defecto SÍ)
./generar.sh --folder-id <ID>   # carpeta de Drive (solo con --drive-index)
./generar.sh --folder-id=<ID>   # misma cosa, forma con =
./generar.sh --force-index      # indexa aunque el recorte no cuadre con el manifiesto (§7)
```

Cualquier flag se puede pasar también a `./run_all.sh`, que los reenvía:
`./run_all.sh --keep-empty-drive`, `./run_all.sh --no-sync-drive`.

> **Ojo:** `./generar.sh` **sin `--auto`** solo genera y sincroniza con Drive: **no**
> regenera `qsl_index.json` ni pushea a GitHub. Para que la web quede correcta, el
> proceso es siempre `./run_all.sh` (o `./generar.sh --auto`, que es lo mismo).

> **Actividades vaciadas.** Por defecto, una actividad sin `.adi` **sí** se vacía en Drive
> (antes se saltaba el sync y las postcards se quedaban ahí para siempre, y la web seguía
> ofreciéndolas aunque ya no existieran en local). Con `--keep-empty-drive` se conserva lo
> que hay en Drive, pero la web deja de ofrecer esa actividad igualmente.

Salida típica cuando **nada ha cambiado** desde la última corrida (el caso habitual del
flujo diario, §2.0). Lo que ves es el setup de `generar.sh` y luego la salida del
generador. Es un **extracto**: los nombres de los `.adi` y las líneas de los 36 ficheros
se resumen con `…`.

```
============================================================
  GENERADOR QSL — setup automático
  Proyecto: /Users/danielcialdella/Downloads/ia-qsls
============================================================
→ python3 detectado: Python 3.14.10
→ venv ya existente: /Users/danielcialdella/Downloads/ia-qsls/venv
→ Pillow ya disponible: 12.3.0
→ ejecutando qsl_generator.py ...

============================================================
  GENERADOR DE POSTALES QSL (incremental)
============================================================

📂 QSL1  (fondo: QSL-1.png)
   ✓ ea4huk-museo.adi: sin cambios (256 contactos ya generados)
   ✓ Museo-ea4ghh-2026-11-14.adi: sin cambios (50 contactos ya generados)
   …  (los otros 3 .adi de qsl1)
📂 QSL6  (fondo: f6.png)
   🗑️  QSL6/QSLS: 43 postales regeneradas desde cero
   🏆 43 estación/es contactaron en las 5 actividades
   ⚡ act6: 43 record(s) -> …
============================================================
  RESUMEN: 0 procesados, 1 regenerados, 36 sin cambios
  Log por carpeta: qslN/qsl_log.json
  Manifiesto: qsl_manifest.json (qsl1=6, qsl2=6, qsl3=6, qsl4=6, qsl5=8, qsl6=43, qsl7=4)
============================================================

Postales generadas por carpeta:
   qsl1   565 postales
   qsl2   426 postales
   qsl3   628 postales
   qsl4   478 postales
   qsl5   852 postales
   qsl6    43 postales
   qsl7    66 postales
```

> Ojo a la aritmética: el resumen dice **1 regenerado** (`qsl6`, que se rehace siempre)
> y **36 sin cambios** (los 36 `.adi`), pero las postales totales son 3.058 porque
> `qsl6` aporta 43 record(s) propios. El manifiesto cuenta para `qsl6` las postales
> producidas (43), no los `.adi` consumidos (0).
>
> El rótulo por carpeta es `   %-6s %s postales` (`generar.sh:163`): dice "postales"
> también para qsl6 y qsl7, que son postales de record y de DMR.

> Ojo: las líneas `Log por carpeta` y `Manifiesto` se imprimen siempre. Los ficheros se
> escriben al procesar un `.adi` real; `qsl6` se procesa siempre, aunque no tenga `.adi`
> propios.
>
> Con los flags por defecto (sin `--no-sync-drive`) se intercala además el bloque
> `→ sincronizando con Google Drive (...)`; y con `--index`, el resumen del indexado.
> Los bloques de arriba se recortan a lo que aporta `qsl_generator.py`.

La **primera** vez que se procesa un `.adi` (recién copiado de `TESTDATA/`, o uno nuevo)
se anuncia con `⚡`, no con `✓ sin cambios`. Así se vio la carga inicial de los 25 `.adi`
reales (`31` contando los 6 de relleno):

```
📂 QSL1  (fondo: QSL-1.png)
   ⚡ ea4huk-museo.adi: 256 contactos -> ea4huk_...png ... y N más
   …  (los demás .adi de qsl1)
📂 QSL6  (fondo: f6.png)
   🏆 43 estación/es contactaron en las 5 actividades
   ⚡ act6: 43 record(s) -> …
============================================================
  RESUMEN: 37 procesados, 0 regenerados, 0 sin cambios
============================================================
```

> `brief` lista como mucho los 5 primeros PNG y remata con `... y N más`.
> **El RESUMEN cuenta por archivo ADI, no por contacto**, y `qsl6` **sí cuenta** como un
> procesado: por eso son 37 (36 `.adi` + `qsl6`) y no 36. En la pasada siguiente ya no,
> porque sus 43 PNG se rehacen siempre desde cero (van a `regenerados`).

Y en la segunda, con todo ya generado:

```
📂 QSL1  (fondo: QSL-1.png)
   ✓ ea4huk-museo.adi: sin cambios (256 contactos ya generados)
   …
============================================================
  RESUMEN: 0 procesados, 1 regenerados, 36 sin cambios
============================================================
```

> Los tres contadores suman 32, y el único que cambia entre pasadas es `regenerados`:
> es `qsl6`, que se rehace en cada corrida. Con datos reales la cifra de "sin cambios"
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
  `rsync -a --update --delete`, que copia lo nuevo/modificado **y borra** en Drive los
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
{ "generated_at": "2026-11-15T19:52:07Z", "generador": "5.4",
  "adi_counts": {"qsl1": 5, "qsl2": 5, "qsl3": 5, "qsl4": 5,
                 "qsl5": 7, "qsl6": 43, "qsl7": 4} }
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
3. Toma el fondo de la carpeta: busca `*.png` en la raíz de ESA carpeta; si no hay,
   prueba `*.jpg`/`*.jpeg` (`folder_backgrounds`). Contrato: **una sola imagen de fondo
   por carpeta**. Si encuentra varias usa la de `mtime` más reciente y avisa por consola.
   Si no hay fondo → avisa "no tiene imagen de fondo propia" y **salta sin generar nada**
   (no se crean archivos en QSLS).
4. Con ADI + fondo → llama a `process_folder(folder, generator, backgrounds)` que
   genera/verifica las postales en `qslN/QSLS/`.
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
   casillas QSL1–QSL5 tildadas + bandera de España en la casilla 6. El log
   `qsl6/qsl_log.json` guarda `fecha: 2026-11-15` para cada postal (`ACT6_RECORD_DATE`).
4. **No es incremental:** antes de generar se borran TODAS las postales de `qsl6/QSLS/`
   para que cada ejecución refleje la información actual. `qsl6/qsl_log.json` guarda la
   firma (sha256) del conjunto (informativa) y la fecha fija de cada postal.

### Procesado incremental (clave)
Cada carpeta tiene `qsl_log.json` con, por archivo ADI:

```json
{
  "pota1111-delta-20260909-1417.adi": {
    "sha256": "bac65c…",
    "generador": "5.4",
    "fondo_hash": "0197e7…",
    "contactos": [
      { "call": "EA4HJZ", "archivo": "ea4hjz_pota1111-delta-20260909-1417.png",
        "fondo": "QSL-1.png", "generado_en": "2026-09-09T11:31:37Z" },
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
| **Fondo cambiado** (`fondo_hash` distinto) | Se reprocesa completo con el nuevo fondo |
| ADI ya procesado y todos sus PNG existen | Se omite ("sin cambios") |
| ADI ya procesado pero falta algún PNG | Se regenera **solo** ese PNG con el fondo actual |
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
- **Una carpeta = un fondo.** Cada actividad usa la **única** imagen que haya en la raíz
  de su carpeta. El generador busca `*.png` (`folder_backgrounds`); si no hay, prueba
  `*.jpg`/`*.jpeg`. El nombre **no** importa: `QSL-1.png`, `f6.png` o `mi-foto.png`
  funcionan igual.
- Si por error hay **varias** imágenes, se usa la de `mtime` más reciente y se avisa por
  consola (`⚠️ qsl1: hay 2 imágenes de fondo ...; se usa la más reciente`). No se alterna
  entre fondos.
- El log guarda `fondo_hash` (sha256 del fondo). Si cambias la imagen, el próximo
  `./generar.sh` **reprocesa** todas las postales de esa carpeta automáticamente.
- Al regenerar un PNG faltante se usa el fondo **actual** de la carpeta (no el histórico).
- **Sin imagen → no se genera nada** (ni QSLS, ni log).

#### Fondos actuales

| Fondo | Fichero | Formato real | Tamaño |
|---|---|---|---|
| qsl1 | `QSL-1.png` | PNG 1200×800 RGB | 2,2 MB |
| qsl2 | `QSL-2.png` | PNG 1200×800 RGB | 1,9 MB |
| qsl3 | `QSL-3.png` | PNG 1200×800 RGB | 2,1 MB |
| qsl4 | `QSL-4.png` | PNG 1200×800 RGB | 2,1 MB |
| qsl5 | `QSL-5.png` | PNG 1200×800 RGB | 2,2 MB |
| qsl6 | `f6.png` | JPEG 1200×800 (ext. `.png`) | 457 KB |
| qsl7 | `f7.png` | JPEG 1200×800 (ext. `.png`) | 422 KB |
| **Total** | | | **≈11 MB** |

- qsl1–qsl5: PNG reales incorporados el **2026-11-04**; el generador los usa solos.
- qsl6–qsl7: siguen siendo los de 2026-10-12, **codificados en JPEG** aunque la extensión
  sea `.png` (Pillow los abre por contenido, no por extensión).
- Todos miden 1200×800 (3:2), así que `cover_fit()` los deja **sin recorte**.
- Los antiguos `f1.png`…`f5.png` se borraron el **2026-11-04**; ahora cada carpeta
  qsl1–qsl5 tiene exactamente **una** imagen de fondo y el generador no avisa.

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
**Normal** (`compose`) | 22% alto × 55% ancho, inf. izquierda | **bandera del CALL + callsign destinatario** (dorado) + nombre•QTH (si el ADI los trae); 2ª línea: **`De OPERATOR`** (o `De STATION_CALLSIGN` si falta) + fecha+UTC, banda/modo, grid | "ACT" + 6 casillas con números; tilde en la suya
**Record act6** (`compose_act6`) | 20% alto × 62% ancho, inf. izquierda | **bandera del CALL + callsign destinatario** (dorado) + nombre; 2ª línea: **`De OPERATOR`** (o `De STATION_CALLSIGN` si falta) + "Todas las referencias conseguidas" + locator | "ACT" + 6 casillas; tildes QSL1..QSL5 y bandera de España en QSL6
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

### Banderas de país (delante del callsign)

- **Posición (v5.2):** en la caja de datos la bandera va **primero**, seguida de ` - `
  y el callsign: `[bandera] - CALL - nombre - QTH`. Se dibuja **siempre** que el
  prefijo resuelva a un país, incluso sin nombre ni QTH. Si no resuelve, la línea
  empieza directamente por el callsign.
- El país se deriva del **prefijo** del callsign (`ADIFParser` no lee campo COUNTRY;
  el `CALL` se normaliza a mayúsculas, así que `ea4hhh` y `EA4HHH` resuelven igual).
  `country_map.json` mapea 845 prefijos → código ISO2 (fuente: ADIF DXCC, campo `prefix`,
  con corrección manual del prefijo `E` → España). Solo se contemplan entidades no
  eliminadas y códigos de país de 2 letras.
- Resolución por **longest-match** (el prefijo más largo que coincida gana; ej.
  `EA4HJZ`→ES, `LU1AA`→AR, `E7ABC`→BA, `ZL2TAL`→NZ). Índice por primera letra para
  resolver rápido con muchos contactos.
- `station_flag(call, height)` carga el PNG de `FLAGS/{cc}.png` (nombre en minúsculas) y
  lo reescala a `altura = la del texto`. Cacheado por `(cc, height)`.
- **Si no existe bandera para ese país (o la estación no tiene país), NO se dibuja nada**:
  el callsign simplemente arranca en la posición original (sin el ` - ` inicial). Así
  nunca se pinta una bandera incorrecta.
- Banderas en `FLAGS/`: 253 PNG, en su mayoría de flagcdn, en principio ~80×53 px pero en
  la práctica **varios tamaños distintos** (el reescalado a la altura del texto los
  normaliza todos, así que da igual). `country_map.json` tiene 248 códigos ISO2 distintos
  y **los 248 tienen bandera**: además de las de flagcdn se añadieron las 4 que faltaban
  (`un` sede de la UIT, `xi` Irlanda del Norte —de `flagcdn` `gb-nir`—, `xk` Kosovo y `zz`
  Orden Soberana de Malta —de Wikimedia Commons—). Los 5 PNG extra que no usa
  `country_map` (`bl`, `gs`, `mf`, `nf`, `re`) resuelven a otros códigos por prefijo
  (`GP`/`FR`).
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
| `QSLGenerator.fmt_date(qso)` / `fmt_time(qso)` | Formatean fecha (`----` si falta) y hora (`''` si falta; el rótulo `--:--` lo pone `compose`, no `fmt_time`). En `qsl6` la fecha nunca falta: se fuerza a `2026-11-15` |
| `QSLGenerator.band_from_freq(freq)` | Banda desde la frecuencia, vía `BAND_RANGES` (`qsl_generator.py:72`) |
| `QSLGenerator._load_country_map()` | Carga country_map.json indexado por 1ª letra |
| `QSLGenerator.country_code_for_call(call)` | ISO2 desde prefijo (longest-match, ignora placeholders) |
| `QSLGenerator.station_flag(call, height)` | PNG de FLAGS/{cc}.png reescalado o None |
| `QSLGenerator.draw_station_flag(overlay, call, x, cy, height)` | Dibuja bandera del CALL delante del callsign; sin bandera no cambia x |
| `QSLGenerator.compose(bg, qso, activity=None)` | Postal normal (call, fecha, banda/modo, bandera+info + casillas; activity=7 → "DMR Confirmated") |
| `QSLGenerator.compose_act6(bg, call, name, grid)` | Postal de record (bandera del CALL + call dorado, locator + casillas con bandera) |
| `find_adi_files(folder)` | Detecta ADI/ADIF por extensión, sin duplicados, cualquier nombre |
| `folder_backgrounds(folder)` | Devuelve el fondo único de UNA carpeta (avisa si hay varios y usa el más reciente) |
| `sanitize_filename_component(text)` | Limpia un componente de nombre de archivo |
| `sha256_file(path)` | Hash del ADI (y del fondo) para detectar cambios |
| `load_log(folder)` / `save_log(folder, log)` | Leer/escribir `qsl_log.json` |
| `now_iso()` | Timestamp UTC |
| `png_valid(path)` | Comprueba PNG abrible |
| `prune_orphan_pngs(folder, log, label)` | Poda PNG de QSLS/ no referenciados en el log |
| `unique_filenames(qsos, adi_stem)` | Nombres `{call}_{stem}.png` únicos |
| `process_folder(folder, gen, bgs)` | Lógica incremental por carpeta (usa `bgs[0]` y `fondo_hash`) |
| `process_act6(base_dir, gen)` | Limpia QSL6/QSLS + detecta estaciones en las 5 actividades + genera QSL de record |
| `main()` | Orquesta las 7 carpetas (qsl6 especial) y escribe `qsl_manifest.json` |
| `drive_index.py` → `fetch/split_blocks/parse_folders/parse_files/fsize/calln/main` | Modo heredado `--drive-index`: **scraping del HTML público** de Drive con `urllib` (sin API, sin credenciales) para obtener los *file ids* |
| `drive_index.py` → `list_local_files/load_drive_ids/load_local_meta/local_png_counts/check_regression` | Vía normal `--local`: lista los PNG de `qslN/QSLS/`, reutiliza los ids del índice anterior, lee indicativos/fechas de los logs y valida el resultado antes de escribir |
| `drive_index.py` → `load_known_calls/read_existing/load_manifest/build_index` | `load_known_calls` lee los indicativos ya conocidos de índices previos; `read_existing` carga el JSON en disco; `load_manifest` lee `qsl_manifest.json`; `build_index` aplica las **salvaguardas** (nunca índice vacío ni recorte no justificado) y solo entonces escribe |

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
> `drive_index.py`, tal como lo llama `generar.sh`, recorre `qslN/QSLS/` (**sin red, sin
> API, sin credenciales y sin dependencias extra** — la `venv` solo tiene Pillow), reutiliza
> los *file ids* del índice anterior y escribe `qsl_index.json` con nombre + id de cada PNG.
> Ese JSON se sube a git y es lo que la página descarga con `fetch`. El modo heredado
> `--drive-index` sí hace *scraping* del HTML público de Drive.

> Histórico: antes se usaba la API v3 con una cuenta de servicio y `drive_creds.json`.
> Ese enfoque se abandonó por el scraping del HTML público (más simple, cero secretos que
> guardar). Las referencias a `drive_creds.json` que quedan en `.gitignore` son inofensivas.

### Carpeta de origen

La fuente por defecto es el **origen local** `qslN/QSLS/` (las carpetas que luego se
rsyncan a Drive). No hace falta red para indexar.

- `My Drive/QSL/QSLs` → <https://drive.google.com/drive/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy>
  es el **destino** de la sincronización. Solo se lee si se pide `--drive-index`.
- ID de la carpeta: `1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy`, hardcodeado en `DEFAULT_FOLDER_ID`
  de `drive_index.py`. Se puede cambiar con `./generar.sh --drive-index --folder-id <ID>`.
- Contiene `qsl1`…`qsl7`. Dentro de cada una, los PNG se llaman
  `{indicativo}_{nombre_adi}.png`, así que **el prefijo del nombre es el indicativo**.
- Para el modo `--drive-index` el enlace público (*Cualquier persona con el enlace* →
  Lector, ya verificado) sigue siendo imprescindible: sin él el scraping devuelve 0 ficheros.

### Puesta en marcha

No hay nada que preparar: **no hacen falta credenciales, ni cuenta de servicio, ni
dependencias, ni acceso a Google Drive**. Con las carpetas `qslN/QSLS/` en local basta:

```bash
./generar.sh --index-only              # ejecuta drive_index.py y escribe qsl_index.json
```

`drive_index.py` **parsea argumentos de verdad** (`argparse`, `main()` en
`drive_index.py:469`) y **solo escribe el archivo si el resultado es sano**:

| Flag | Efecto |
|---|---|
| `--local` | Indexa `qslN/QSLS/` sin red (lo usa `generar.sh` por defecto) |
| `--drive-index` | Modo heredado: scraping del HTML público de Drive |
| `--folder-id <ID>` | Otra carpeta de Drive (solo con `--drive-index`) |
| `--out <ruta>` | Escribe el índice donde quieras (por defecto `qsl_index.json` en la raíz) |
| `--manifest <ruta>` | Usa otro manifiesto (por defecto `qsl_manifest.json`) |
| `--force` | Escribe el índice aunque la salvaguarda lo pidiera bloquear |

`generar.sh` pasa `--local` por defecto, propaga `--folder-id` y añade `--force` cuando
le pasas `--force-index` (`FORCE_INDEX=true` → `INDEX_ARGS+=("--force")`,
`generar.sh:91-93`), así que desde el flujo diario no hace falta tocar código.

> **Por qué existe `--force`.** Al vaciar actividades **a propósito** (o al sustituirlas
> por datos de prueba), la salvaguarda ve un recorte grande del que el manifiesto no da
> cuenta y se niega a escribir, por si las postcards locales se borraron por error:
>
> ```
> ERROR: el nuevo indice tiene 7 entradas y el anterior 28, y solo 0 son de
> actividades vaciadas por manifiesto. Parece un parseo fallido de Drive; no se escribe.
>        Usa --force si el recorte es intencionado.
> ```
>
> Si has revisado que el recorte es real, `--force-index` es lo correcto:
> `./generar.sh --index-only --force-index`. Si no lo es, **no lo uses** — el JSON bueno
> en disco sigue intacto. Con `--local`, comprueba los PNG de `qslN/QSLS/`; con
> `--drive-index`, revisa el HTML de Drive.

Después, sube el índice y activa GitHub Pages (Settings → Pages → *Deploy from a branch*
→ `main` / raíz). La página queda en **https://dcialdella.github.io/ia-qsls/** y la
 de gráficos, en **https://dcialdella.github.io/ia-qsls/graficos/**.

### Uso diario

```bash
./run_all.sh                    # postcards + sync a Drive + índice + commit + push
./generar.sh --index          # postcards + sync a Drive + regenera qsl_index.json
./generar.sh --index-only     # solo regenera el índice (no toca las postcards)
./generar.sh                  # no toca el índice (hay que pedirlo con --index)
```

Lo normal es `./run_all.sh` (§2.0). Los flags de abajo sirven para casos puntuales.

> **El índice no espera a la nube:** se construye desde `qslN/QSLS/`, así que las
> postcards nuevas y los borrados se reflejan en la misma corrida. El retardo de
> Drive solo afecta al modo heredado `--drive-index`.

### Formato de `qsl_index.json`

`folder_id` se rellena siempre, y `activities` trae las 7 con su `id` y su `title`
("Actividad 1"… "Actividad 7") mientras la actividad esté publicada. La excepción son las
que el propio indexado decide dejar fuera: una actividad con **0 en el manifiesto** se
omite por completo (no aparece en `activities` ni en `counts`, y se avisa por pantalla con
`· qslN: sin .adi (manifiesto) -> no se publica`). En modo `--drive-index`, además,
una actividad cuyo HTML no se puede leer se marca como fallida. Las carpetas existen
siempre; lo que puede no publicarse es su contenido.

Estado actual del repo: índice **completo**, con `total: 3058`, 1.110 `call` distintos
(1.109 sin contar `XYZ123`) y `generated_at: 2026-11-17T20:37:14Z`. Lo publicaron la
fecha asignada a `qsl6` (`1ba3646`) y la regeneración del índice local (`eb4e552`) (§9).
Si algún día saliera vacío (`total: 0`), la web lo mostraría sin errores visibles — ver
§7 "Seguridad". **Nunca se publica un índice incompleto**: las salvaguardas de
`drive_index.py` exigen que los PNG locales y el manifiesto cuadren antes de escribir
el JSON (§7 "Puesta en marcha").

```json
{
  "version": 2,
  "generated_at": "2026-11-17T20:37:14Z",
  "folder_id": "1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy",
  "folder_url": "https://drive.google.com/drive/folders/1bknLSlpI2qJnQfAod7N1GujfJ4p1gTAy",
  "activities": {"qsl1": {"id": "1XyZ...", "title": "Actividad 1"}},
  "counts": {"qsl1": 565, "qsl2": 426, "qsl3": 628, "qsl4": 478,
             "qsl5": 852, "qsl6": 43, "qsl7": 66},
  "total": 3058,
  "days": {"2026-11-15": 966, "2026-11-14": 965,
           "2026-11-13": 1121, "2026-10-06": 6},
  "entries": [
    {"call": "IV3LDZ", "act": "qsl2",
     "name": "iv3ldz_ea4huk_es-0340-20261113.png",
     "id": "1sZ-YgsqKUut8Ram2IsX1-dPshcOnUOH6", "size": 1468204}
  ]
}
```

- La `version` del índice es **2**. La 1 ya traía las 7 `activities`; el salto refleja
  el formato de `entries` que consume hoy la web.
- `days` cuenta las postales por fecha: `2026-11-15: 966`, `2026-11-14: 965`,
  `2026-11-13: 1121`, `2026-10-06: 6`. Ya no existe la clave `""` (sin fecha):
  las 43 QSL de record de `qsl6` llevan `2026-11-15`.
- El ejemplo abrevia `activities` a una sola clave, pero el archivo real trae **las 7**
  con su `id` y su `title`, salvo las que se omiten por manifiesto vacío (o por fallo
  de fetch en modo `--drive-index`, ver arriba).
- `call` se toma de `qsl_log.json` (fuente principal, indicativo sin transformar); solo
  si el log no existe se deduce del nombre del PNG (`{call}_{stem}.png`). Así los
  indicativos con `/` no se confunden con guiones bajos del nombre del `.adi`.
- `entries` **no lleva `modified`**: ninguna de las dos fuentes lo expone. El tamaño
  (`size`) se lee con `stat()` en modo `--local`; con `--drive-index`, vía la
  redirección `uc?export=download`.
- La web usa `lh3.googleusercontent.com/d/<id>` para las miniaturas y
  `drive.google.com/uc?export=download&id=<id>` para la descarga.
- ✅ **Probado con 4000 entradas** (2026-10-06): se publicó un `qsl_index.json` simulado
  con `total: 4000` (commits `79c5617` → restaurado en `bf2bfde`) y la web funcionó
  bien — carga, listado y rendimiento sin problemas. El índice real tiene 3.058 entradas.
- ✅ **Página nueva de gráficos** (commit `f7bb4c6`): <https://dcialdella.github.io/ia-qsls/graficos/>,
  27 PNG generados desde `graficos/TODOS.adi` (3.009 QSO, sin los 6 registros demo).
  La regeneración del 17/11 produjo 27 imágenes idénticas a las ya publicadas.

### Seguridad

- **No hay secretos que gestionar.** `drive_index.py` no usa la API de Drive ni credenciales:
  en modo `--local` ni siquiera accede a la red, y con `--drive-index` solo lee el HTML
  de la carpeta pública. `drive_creds.json` ya no hace falta para nada (las entradas que
  lo ignoran en `.gitignore` son una precaución inofensiva).
- La web es estática: no habla con Drive en ningún momento, solo carga `qsl_index.json`
  desde GitHub Pages.
- Con la carpeta pública, cualquiera que conozca el enlace puede ver todos los PNG.
  Es coherente con que las QSL son públicas, pero tenlo en cuenta si añades
  datos personales (nombre/QTH) que no quieras exponer.
- Solo en modo `--drive-index`: si algún día Drive deja de renderizar esos `<a>` en su
  HTML, el parseo devolvería 0 ficheros. `drive_index.py` **se niega a escribir** un índice
  con 0 entradas, o con menos entradas que el anterior sin que el manifiesto justifique la
  pérdida, y avisa por stderr: el JSON bueno en disco no se pisa. Si ves ese error, mira
  primero los PNG locales (`--local`); el HTML de Drive es la segunda opción.
- La web no inserta el `id` de Drive sin más: `index.html` lo valida contra
  `/^[A-Za-z0-9_-]{10,64}$/` y lo mete en las URLs con `encodeURIComponent`, y escapa
  `name`, `call` y `act` con `escapeHtml`. Una entrada con un id inesperado se descarta en
  vez de inyectarse en un atributo.
- En modo `--drive-index` los tamaños se piden con peticiones **HEAD** en paralelo (8 a la
  vez), no con GET: a ~1,4 s por fichero en serie, 5000 postcards serían unas 2 horas.
  En modo `--local` son `stat()` de los PNG, sin red. Drive puede
  responder con una página HTML de intersticio en lugar de la imagen; se detecta
  comprobando el `Content-Type` y se guarda tamaño `0`.

---

## 8. Tareas pendientes / próximos pasos

Las primeras tareas del proyecto (prueba de humo, sincronización a Drive, verificación
de la web) ya están **hechas**: las 3.058 postales están generadas, sincronizadas y
publicadas a partir de los 36 `.adi` reales (3.015 QSO). La galería de gráficos también
está publicada en su propia página (§7). Queda pendiente:

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
3. ~~**Cavar con el retardo de Drive en el flujo diario.**~~ — **resuelto** (`eb4e552`):
   el índice se genera desde `qslN/QSLS/` sin red, así que ya no hace falta repetir
   `./run_all.sh` al minuto ni reintentar el indexado.
4. ~~**Limpieza de `update_adi_dates.py`.**~~ — **hecho**: el ayudante de una sola vez
   (ya aplicado; volver a ejecutarlo desplazaría las horas de todos los `.adi`) se eliminó
   del repo; queda en el historial de git.
5. **Ordenar los QSOs por fecha dentro de cada `.adi`.** Ahora la secuencia horaria sigue
   el orden en que aparecen en el fichero, no el cronológico. Cosmético, pero si algún día
   se quiere que las horas simulen una sesión real habría que ordenarlos.
6. ~~**Bug latente al pasar `--folder-id` a `drive_index.py`**~~ — **resuelto**:
   `drive_index.py` acepta ahora `--folder-id` de verdad (`argparse` propio, `main()` en
   `drive_index.py:469`) y `generar.sh` lo propaga con su propio `--folder-id` (y
   `--folder-id=<ID>`), así que ya no hace falta editar `DEFAULT_FOLDER_ID`.
7. ~~(Opcional) Añadir banderas para los 4 códigos sin PNG en `FLAGS/`.~~ — **hecho**: se
   añadieron `un` (sede de la UIT, prefijo `4U`), `xi` (Irlanda del Norte, de `flagcdn`
   `gb-nir`), `xk` (Kosovo) y `zz` (Orden Soberana de Malta, de Wikimedia Commons). Ya no
   hay estaciones sin bandera por falta de PNG.
8. **Tests.** El proyecto no tiene ninguno, y los arreglos de este ciclo (poda de PNG
   huérfanos, parser ADIF, derivación del indicativo) son justo lo que un test debería
   proteger. El candidato más barato: un test que ejecute el generador sobre `TESTDATA/`
   y compare el `qsl_log.json` resultante con un esperado.

---

### Cobertura de cruces entre las 4 estaciones (verificado 17/11)

Auditoría de los 32 `.adi` raíz de qsl1–qsl5 (2.949 QSO; excluidos
`ACTIVIDADES/`, `TESTDATA/` y los 6 registros `XYZ123`). Para cada actividad se
comprobó, con dos parsers independientes, que cada una de las 4 estaciones tiene
**al menos un QSO con cada una de las otras 3**. Resultado: **12/12 pares dirigidos
presentes en qsl1, qsl2, qsl3, qsl4 y qsl5; no falta ninguno**.

Número de QSO por par (filas = estación propia según `OPERATOR` o, si falta,
`STATION_CALLSIGN`; columnas = `CALL` del corresponsal):

| Actividad | HUK→JAQ | HUK→GHH | HUK→IWX | JAQ→HUK | JAQ→GHH | JAQ→IWX | GHH→HUK | GHH→JAQ | GHH→IWX | IWX→HUK | IWX→JAQ | IWX→GHH |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qsl1 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| qsl2 | 5 | 5 | 5 | 7 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |
| qsl3 | 6 | 7 | 6 | 5 | 5 | 5 | 8 | 9 | 9 | 5 | 5 | 5 |
| qsl4 | 8 | 5 | 5 | 9 | 10 | 8 | 5 | 5 | 5 | 8 | 8 | 8 |
| qsl5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 |

Notas: en los `CRUZADAS-ADICIONALES-*.adi` hay estaciones propias con
`STATION_CALLSIGN=EA4IWX/9` o sin `OPERATOR` (se normaliza al indicativo base),
y en qsl4 aparecen dos pares duplicados por `CALL`+fecha+hora+banda+modo con
frecuencias distintas; no afectan a la cobertura. Detalle en `RELLENO-QSO.md`.

---

## 9. Notas de entorno

- **Mac (darwin), zsh.** El script `generar.sh` funciona también en Linux.
- **Python:** 3.14 venv con **solo Pillow** (12.3.0) + `pip`. Ni numpy ni google-auth:
  el generador no los usa y `drive_index.py` va con la `urllib` de la stdlib.
  El `python3` del sistema es 3.15.2. Los gráficos se generan en un entorno aparte con
  **matplotlib 3.9.4**, seaborn, pandas y numpy (3.11 rompe `boxplot(labels=)`); ver
  `graficos/LEEME.md`.
- **Fuentes usadas:** Arial → Helvetica → Verdana → DejaVu, en ese orden de preferencia
  (`get_font`, `qsl_generator.py:300`). En macOS suelen salir Arial o Helvetica; DejaVu es
  el fallback para Linux.
- **Filesystem case-insensitive:** por eso se evitan los globs que mezclan mayúsculas.
- No hay tests automáticos; la verificación es ejecutar el script + revisar los PNG.
- **`./run_all.sh` es la forma recomendada de ejecutar** (§2.0): genera, sincroniza con
  Drive, reindexa la web desde `qslN/QSLS/` (sin acceder a Drive) y pushea. `generar.sh`
  directamente sirve para casos puntuales
  (regenerar todo con `--from-scratch`, probar con `--no-sync-drive`, etc.).
- **Git/GitHub:** el proyecto está en `git` (rama `main`) con remote `origin` →
  https://github.com/dcialdella/ia-qsls.git. `qsl*/QSLS/` y los `qsl_log.json` están
  ignorados por `.gitignore` (no se suben). Se commitean los fondos, los `.adi` (tanto los
  de `TESTDATA/` como los de `qslN/`), `index.html`, `qsl_index.json`,
  `country_map.json`, `FLAGS/`, el código y el README.
- **Estado Git:** `main` en sync con `origin/main`. Commits recientes, del más nuevo al más
  antiguo:
  - *(este commit)* — *"Actualiza toda la documentación"*
    (fecha de `qsl6`, índice local, carpeta `ADICIONALES/` y gráficos; detalle en los 4 `.md`)
  - `8ab2b1f` — *"Añade 9 ADI de contactos adicionales con EA4HUK por estación y actividad"*
    (3 estaciones × TOTA/LLOTA/POTA, 15 QSO; entradas en `ADICIONALES/`, no del generador)
  - `eb4e552` — *"Genera el índice web desde qslN/QSLS sin acceder a Drive"*
    (`--local` por defecto en `generar.sh`; `--drive-index` conserva el scraping)
  - `1ba3646` — *"Asigna 2026-11-15 a las 43 QSL de record (qsl6) y refresca TODOS.adi"*
    (`ACT6_RECORD_DATE`; desaparece del índice el grupo `""` sin fecha)
  - `35bc195` — *"Actualiza documentación a 3058 postales y verifica cruces QSL1-5"*
    (cifras alineadas con `d0adfcf`; verificación de las 4 estaciones en las 5 actividades)
  - `465ddc1` — *"Actualiza LEEME de gráficos a 3009 QSO y 36 ADI"*
  - `d0adfcf` — *"Actualiza derivados de EA3JAQ y el índice a 3058 postales"*
    (5 `CRUZADAS-ADICIONALES-*.adi` de 12 QSO = +60; 3.015 QSO raíz, 3.058 postales)
  - `0351d20` — *"Añade OPERATOR a logs EA3JAQ y fallback en generador v5.5"*
    (`originating_station()` usa `OPERATOR` y, si falta, `STATION_CALLSIGN`)
  - `ebe1740` — *"Completa los 16 QSO unilaterales y regenera postales, índice y gráficos"*
    (16 espejos en 6 ADI raíz; 2.955 QSO, 2.998 postales, 3.303 derivados, `TODOS.adi`
    con 2.949 QSO y derivados del Escritorio actualizados; detalle en `RELLENO-QSO.md`)
  - `f7bb4c6` — *"Página nueva de gráficos del log completo (2.933 QSO, 27 gráficos)"*
    (`graficos/index.html`, PNG y miniaturas; no toca `index.html` ni `qsl_index.json`)
  - `7faa24a` — *"Índice completo tras regenerar las 2.982 postales (2.939 QSO)"*
  - `939c867` — *"Cruza los logs del trío para que las 4 estaciones tengan contacto entre sí"*
    (120 QSO de cruce, operador y estación validados)
  - `652bd79` — *"Completa logs de EA4HUK y genera los espejos en los logs del trío"*
    (16 QSO de relleno, 61 espejos; detalle en `RELLENO-QSO.md`)
  - `a18021f` — regeneración completa + contadores por día y por actividad
  - `bfdae81` — *"QSL6 no lleva .adi: el manifiesto contaba lo que consume, no lo que
    produce"* (el fix de `qsl6`, `--force-index` y el README)
- **Copias de seguridad locales** (no están en git, son del propio repo):
  - `ia-qsls-backup-20261005-110936` — el estado de 28 `.adi` y 67 postcards, por si
    quisiera volver atrás.
  - `ia-qsls-backup-20261005-142557` — el estado `TEST.adi` de 7 postcards, justo antes de
    la commit `bfdae81`.
- **Punto de retorno guardado:** hay un tag **`inicio-fresco`** que congela el estado
  vacío (sin ADIs en `qslN/`, sin postcards, índice a 0). Ver §10. Nota: ese tag es ya
  **histórico** — volver a él significaría tirar las 3.058 postcards actuales.
---

## 10. Punto de retorno: el tag `inicio-fresco`

> ⚠️ **Este tag es histórico.** Congela el estado vacío del proyecto (sin `.adi` en
> `qslN/`, sin postcards, índice a 0), que era el punto de partida antes de poblar las
> actividades. **Volver a él descarta las 3.058 postcards actuales**, así que úsalo solo
> si de verdad quieres dejar el proyecto en blanco.

```bash
git tag -n9 inicio-fresco        # ver qué guarda
git show inicio-fresco           # contenido exacto del tag
```

### Qué estado congela

Apunta al commit `bf02d44`:

- `qsl1`–`qsl7` con **solo su fondo**: en ese commit `f1.png` … `f7.png` (convención
  `f<n>.png`). **Nota:** hoy qsl1–qsl5 usan `QSL-1.png`…`QSL-5.png`; el tag conserva los
  antiguos.
- `qslN/QSLS/` **vacía** en las 7 actividades (0 postcards)
- **Ningún** `qslN/qsl_log.json` (se crean solos al primer procesado real)
- **Cero** `.adi` dentro de `qsl1`–`qsl7`
- Los 10 `.adi` de ejemplo que había entonces en `TESTDATA/` (hoy quedan 6), sin procesar
- `qsl_index.json` válido pero vacío: `total: 0`, `counts` a 0, `entries: []`

### Cómo volver a él

> Antes de nada, ten en cuenta que esto **tira las 3.058 postcards actuales**.

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
> limita el borrado a los ficheros ignorados, así que no toca las imágenes de fondo
> (`f<n>.png`, `QSL-N.png`) ni los `.adi`.

### Lo que el tag NO guarda

- **Los PNG generados y los `qsl_log.json`**: están en `.gitignore`, así que no entran en
  ningún commit ni en el tag. Para eso está el `git clean -fdX` de arriba. (En el momento
  de crear el tag no había ninguno, así que el tag sí reproduce el estado completo.)
- **Google Drive**: la carpeta `QSL/QSLs` con sus 7 subcarpetas vive fuera de git. Hay que
  comprobarla a mano. Recuerda la regla 1 de §0: **las 7 carpetas nunca se borran**, aunque
  estén vacías. Para vaciarlas, borra los PNG de `qslN/QSLS/` y ejecuta
  `./generar.sh` (el `rsync --delete` los refleja en Drive) o bórralos allí a mano.
