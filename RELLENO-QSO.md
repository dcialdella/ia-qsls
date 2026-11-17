# Relleno de QSO EA4HUK ↔ {EA3JAQ, EA4GHH, EA4IWX} en 20/40/60/70/80 m y 2 m

Fecha: 2026-11-15 · Estado: aplicado a los ADI raíz, a `ACTIVIDADES/` y a `ADICIONALES/`

## Motivo

Cada log propio de EA4HUK debe contener contactos con EA3JAQ, EA4GHH y EA4IWX
en las cuatro bandas de trabajo (20 m, 40 m, 70 cm y 2 m). Antes de este relleno
faltaban 16 QSO repartidos en los cinco logs. El título incluye además 60 m y 80 m
por el bloque de 12 QSO del 2026‑11‑15 que se documenta en «Totales» y que solo
estuvo en el derivado `DME.adi`, no en los ADI raíz.

**Aviso**: estos 16 contactos **no existen en ningún log de origen** (se revisaron
también los ADI de EA3JAQ, EA4GHH y EA4IWX). Se han creado clonando el registro
del mismo operador en 70 cm del propio log (misma cuadrícula, nombre, distancia,
potencia y referencias de actividad) y sustituyendo solo `FREQ`, `BAND` y
`TIME_ON`. Las horas son consecutivas a las del resto del trío en esa actividad.

## Entradas añadidas

| Log | Estación | Banda | FREQ | TIME_ON | Hora de referencia del trío |
|---|---|---|---|---|---|
| `qsl1/ea4huk-museo.adi` | EA3JAQ | 20m | 14.250 | 1057 | 40m 1055 · 2m/70cm 1056 |
| `qsl1/ea4huk-museo.adi` | EA4GHH | 20m | 14.250 | 1057 | ídem |
| `qsl1/ea4huk-museo.adi` | EA4IWX | 20m | 14.250 | 1057 | ídem |
| `qsl2/EA4HUK@ES-0340-20261113.adi` | EA3JAQ | 40m | 7.166 | 1501 | 70cm 1500 · 2m 1457 |
| `qsl2/EA4HUK@ES-0340-20261113.adi` | EA4IWX | 40m | 7.166 | 1501 | ídem |
| `qsl3/EA4HUK@ES-0849-20261113.adi` | EA3JAQ | 40m | 7.160 | 0900 | 70cm 0859 · 2m 0857 |
| `qsl3/EA4HUK@ES-0849-20261113.adi` | EA4IWX | 40m | 7.160 | 0900 | ídem |
| `qsl4/ea4huk-pota-0850.adi` | EA3JAQ | 20m | 14.160 | 1516 | 2m/70cm 1515 · 40m 1514 |
| `qsl4/ea4huk-pota-0850.adi` | EA4GHH | 20m | 14.160 | 1516 | ídem |
| `qsl4/ea4huk-pota-0850.adi` | EA4IWX | 20m | 14.160 | 1516 | ídem |
| `qsl5/ea4huk-lles.adi` | EA3JAQ | 20m | 14.250 | 1137 | 2m 1135 · 70cm 1136 |
| `qsl5/ea4huk-lles.adi` | EA4GHH | 20m | 14.250 | 1137 | ídem |
| `qsl5/ea4huk-lles.adi` | EA4IWX | 20m | 14.250 | 1137 | ídem |
| `qsl5/ea4huk-lles.adi` | EA3JAQ | 40m | 7.194 | 1138 | ídem |
| `qsl5/ea4huk-lles.adi` | EA4GHH | 40m | 7.194 | 1138 | ídem |
| `qsl5/ea4huk-lles.adi` | EA4IWX | 40m | 7.194 | 1138 | ídem |

Frecuencias tomadas de las ya usadas en cada log para esa banda
(`qsl3` solo tenía 40 m en 7.160; `qsl5` no tenía 20 m y se usa la habitual del
resto de logs, 14.250).

## Cobertura resultante

| Log | EA3JAQ | EA4GHH | EA4IWX |
|---|---|---|---|
| `qsl1/ea4huk-museo.adi` | 4/4 | 4/4 | 4/4 |
| `qsl2/EA4HUK@ES-0340-20261113.adi` | 4/4 | 4/4 | 4/4 |
| `qsl3/EA4HUK@ES-0849-20261113.adi` | 4/4 | 4/4 | 4/4 |
| `qsl4/ea4huk-pota-0850.adi` | 4/4 | 4/4 | 4/4 |
| `qsl5/ea4huk-lles.adi` | 4/4 | 4/4 | 4/4 |

## Corrección posterior: `<CALL:5>EAFNT` (duplicado)

En `qsl2/EA4HUK@ES-0340-20261113.adi` había un registro con indicativo inválido
`EAFNT` a las 17:31 en 40m / 7.166 sin `COUNTRY`, `GRIDSQUARE`, `NAME` ni
`DISTANCE` (entrada tecleada a mano). Cuatro minutos después, a las 17:35 y en
la misma banda y frecuencia, el mismo log tiene el registro completo de
**EA1FNT** (Ruben Lopez Alvarez, IN63TI). Se ha eliminado el registro de 17:31
por duplicado; el contacto con EA1FNT se conserva a las 17:35 (40m) y a las
17:00 (20m).

Backup previo a esta eliminación:
`/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/fnt_backup/`

## Espejos en los logs de EA3JAQ, EA4GHH y EA4IWX

A petición del operador se han creado las **entradas recíprocas** en los logs del
trío: por cada QSO de EA4HUK con EA3JAQ / EA4GHH / EA4IWX se ha añadido el
registro visto desde el otro lado, con la **misma fecha, hora, banda y
frecuencia** (`CALL=EA4HUK`, `STATION_CALLSIGN` del operador, RST 59/59).

Se han añadido al log existente de cada operador en la misma carpeta qsl
(criterio elegido por el usuario), respetando el formato de cada fichero:

- EA4GHH: Smart Logger, un campo por línea, `TIME_ON` de 4 dígitos.
- EA3JAQ: Ham2K, registro en una línea, `TIME_ON` de 6 dígitos, sin `OPERATOR`.
- EA4IWX: Ham2K Portable, `STATION_CALLSIGN=EA4IWX/9`, `OPERATOR=EA4IWX`.

Reparto (61 registros en 15 ficheros):

| Fichero destino | Espejos | Origen |
|---|---|---|
| `qsl1/EA3JAQ-20261115-en-ear-1901-dme-52001-full.adi` | 4 | `qsl1/ea4huk-museo.adi` |
| `qsl1/Museo-ea4ghh-2026-11-14.adi` | 4 | `qsl1/ea4huk-museo.adi` |
| `qsl1/ea4iwx-poi1-20261115.adi` | 4 | `qsl1/ea4huk-museo.adi` |
| `qsl2/EA3JAQ-20261114.adi` | 4 | `qsl2/EA4HUK@ES-0340-20261113.adi` |
| `qsl2/EA4GHH @ES-0340-20261113.adi` | 4 | `qsl2/EA4HUK@ES-0340-20261113.adi` |
| `qsl2/2026-11-14-EA4IWX.adi` | 4 | `qsl2/EA4HUK@ES-0340-20261113.adi` |
| `qsl3/EA3JAQ-20261114.adi` | 4 | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| `qsl3/EA4GHH @ES-0849-20261113.adi` | 4 | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| `qsl3/2026-11-14-EA4IWX.adi` | 4 | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| `qsl4/2026-11-13 EA3JAQ.adi` | 5 | `qsl4/ea4huk-pota-0850.adi` (EA3JAQ tiene 2 QSO en 40m) |
| `qsl4/EA4GHH-ES-0850-20261114.adi` | 4 | `qsl4/ea4huk-pota-0850.adi` |
| `qsl4/EA4IWX-2026-11-13.adi` | 4 | `qsl4/ea4huk-pota-0850.adi` |
| `qsl5/2026-11-13 EA3JAQ.adi` | 4 | `qsl5/ea4huk-lles.adi` |
| `qsl5/ea4ghh-llota20261115.adi` | 4 | `qsl5/ea4huk-lles.adi` |
| `qsl5/ea4iwx-poi5.adi` | 4 | `qsl5/ea4huk-lles.adi` |

Los espejos no coinciden con registros previos del mismo fichero (0 duplicados
`CALL`+fecha+hora+banda). Efecto: cada QSO pasa a existir en los dos lados, por lo
que el sitio generará una postal por cada lado (el mismo contacto aparece dos
veces, una por operador).

Backup previo a los espejos:
`/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/espejos_backup_202321/`

Script usado: `/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/espejar_qso.py`

## Cruces entre las tres estaciones del trío

Para que las cuatro estaciones tengan contacto con las cuatro en cada ronda de
banda, se han añadido los cruces que faltaban entre EA3JAQ, EA4GHH y EA4IWX:
**60 parejas / 120 registros** (cada pareja queda anotada en los dos logs).

Criterio (elegido por el usuario): **una hora común por carpeta y banda**. Por
cada carpeta y banda se toma la hora mayoritaria del trío en el log de EA4HUK
(empate → hora intermedia) y la frecuencia más usada a esa hora. Los QSO de
EA4HUK con cada estación se han dejado en su hora original.

| Carpeta | Bandas completadas (hora · freq) |
|---|---|
| qsl1 | 40m 10:55 · 7.192 — 70cm 10:56 · 443.500 — 2m 10:56 · 145.250 — 20m 10:57 · 14.250 |
| qsl2 | 20m 14:56 · 14.342 — 2m 14:57 · 145.252 — 70cm 15:00 · 434.200 — 40m 15:01 · 7.166 |
| qsl3 | 20m 08:56 · 14.323 — 2m 08:57 · 145.225 — 70cm 08:58 · 434.000 — 40m 09:00 · 7.160 |
| qsl4 | 40m 15:14 · 7.183 — 2m 15:15 · 144.525 — 70cm 15:15 · 434.000 — 20m 15:16 · 14.160 |
| qsl5 | 2m 11:35 · 145.250 — 70cm 11:36 · 434.300 — 20m 11:37 · 14.250 — 40m 11:38 · 7.194 |

Identidad usada en los registros nuevos (tomada de los logs de EA4HUK):
EA3JAQ = Eladio Muniz Fernandez / JN11HU · EA4GHH = Manuel / IN80DK ·
EA4IWX = Iñigo Merchán Pedraja / IN80CQ. `DISTANCE` calculada desde IM85mh
(JN11HU 874 km, IN80DK 574 km, IN80CQ 602 km).

Verificación: **121/121** comprobaciones OK (20 rondas × 3 cruces del trío + los
61 QSO de EA4HUK con cada estación en su hora). 0 registros duplicados.

Backup previo (15 ficheros): `/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/cruces_backup_204218/`
Script: `/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/cruzar_trio.py`

## Totales

- ADI raíz (15/11): 2.743 → **2.939** QSO (+16 relleno, −1 duplicado EAFNT, +61 espejos,
  +120 cruces del trío). La cuenta cierra: 2.743 + 16 − 1 + 61 + 120 = 2.939.
  El 17/11 se añadieron 16 espejos más (sección final), dejando el total en **2.955**,
  y después 5 `CRUZADAS-ADICIONALES-*.adi` de 12 QSO cada uno (sección siguiente),
  hasta **3.015**.
- **Bloque aparte (12 QSO en 40/60/80 m, 2026‑11‑15 13:00):** doce contactos en
  7.100 / 5.350 / 3.700 MHz se añadieron al derivado del Escritorio `DME.adi` (que
  contenía 2.678 QSO). **No están en los 36 `.adi` raíz ni en la web**: por eso no
  entran en el total de 3.015 ni en las 3.058 postales publicadas. `DME.adi` ya no
  estaba en el Escritorio en la última comprobación (17/11), así que este bloque solo
  consta en la documentación; si el backup `DME-backup-20261115.zip` sigue
  disponible, sería la fuente para recuperarlo. (Los `CRUZADAS-ADICIONALES-*.adi`
  que sí están en la web son contactos distintos: todos en 10 m, ver sección final.)
- **Otro derivado fuera del repo (17/11):** `~/Desktop/ea4huk-eg9-todo.adi` reúne
  954 QSO propios de EA4HUK con `STATION_CALLSIGN=EA4HUK/9`, `MY_GRIDSQUARE=IM85`,
  `CQZ=14`, `ITUZ=37` y `DXCC=32` (detalle en `README.md` §1.2). Tampoco entra en los 3.015
  QSO ni en las 3.058 postales.
- `ACTIVIDADES/`: 38 ficheros, **3.375** QSO (qsl2 se replica en `pota` y `tota`).
- `audit_adi.py`: 2 avisos de duplicado por una clave que no incluye `FREQ`
  (7.160 vs 7.150 y 7.183 vs 7.195). Son consecuencia esperada de los espejos del
  17/11: mismo `CALL`/fecha/hora/banda/modo pero frecuencias distintas en el otro log.
  No hay duplicados exactos, ni errores de FREQ, BAND o TIME_ON.

## Reversión

Backup de los cinco ADI previos al cambio:

```
/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/relleno_backup_201453/
```

Script usado: `/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/rellenar_trio.py`

## Actualización 17/11: 16 QSO unilaterales detectados en el cruce

Al cruzar de nuevo los 31 `.adi` raíz aparecieron **16 QSO que existían solo en un
log**: uno de los cuatro indicativos los había anotado y el corresponsal no. Se han
añadido como **espejos en el log contrario**, clonando un registro del mismo `CALL`
ya presente en ese fichero y sobrescribiendo `QSO_DATE`, `TIME_ON`, `BAND`, `FREQ`
y `MODE` con los del registro origen. Se respeta el formato de export de cada
destino (Smart Logger multilínea en qsl3/qsl4/ea4huk-pota, Ham2K de una línea en
qsl4/EA4IWX y en qsl7). Backup previo de los 6 ficheros destino:
`/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/adi-backup-20261117/`.
Script: `/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/add_mirrors.py`.

| Día | Hora | Banda | Operador | Frecuencia | CALL | Fichero ADI de origen | Fichero ADI destino |
|---|---|---|---|---|---|---|---|
| 2026-11-13 | 08:55 | 40m | EA4GHH | 7.160 | EA4IWX | `qsl4/EA4IWX-2026-11-13.adi` | `qsl3/EA4GHH @ES-0849-20261113.adi` |
| 2026-11-13 | 08:57 | 70cm | EA4GHH | 420.000 | EA3JAQ | `qsl4/2026-11-13 EA3JAQ.adi` | `qsl3/EA4GHH @ES-0849-20261113.adi` |
| 2026-11-13 | 08:55 | 70cm | EA4HUK | 430.200 | EA4IWX | `qsl4/EA4IWX-2026-11-13.adi` | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| 2026-11-13 | 08:57 | 40m | EA4HUK | 7.150 | EA4GHH | `qsl3/EA4GHH @ES-0849-20261113.adi` | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| 2026-11-13 | 08:57 | 70cm | EA4HUK | 430.320 | EA3JAQ | `qsl4/2026-11-13 EA3JAQ.adi` | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| 2026-11-13 | 09:06 | 70cm | EA4HUK | 430.200 | EA4GHH | `qsl3/EA4GHH @ES-0849-20261113.adi` | `qsl3/EA4HUK@ES-0849-20261113.adi` |
| 2026-11-13 | 08:57:00 | 40m | EA4IWX | 7.150000 | EA4GHH | `qsl3/EA4GHH @ES-0849-20261113.adi` | `qsl4/EA4IWX-2026-11-13.adi` |
| 2026-11-13 | 08:57:00 | 40m | EA4IWX | 7.000000 | EA3JAQ | `qsl4/2026-11-13 EA3JAQ.adi` | `qsl4/EA4IWX-2026-11-13.adi` |
| 2026-11-13 | 08:57:00 | 2m | EA4IWX | 145.400000 | EA3JAQ | `qsl4/2026-11-13 EA3JAQ.adi` | `qsl4/EA4IWX-2026-11-13.adi` |
| 2026-11-13 | 08:59:00 | 70cm | EA4IWX | 420.000000 | EA3JAQ | `qsl4/2026-11-13 EA3JAQ.adi` | `qsl4/EA4IWX-2026-11-13.adi` |
| 2026-11-13 | 09:07:00 | 70cm | EA4IWX | 430.200000 | EA4GHH | `qsl3/EA4GHH @ES-0849-20261113.adi` | `qsl4/EA4IWX-2026-11-13.adi` |
| 2026-11-13 | 08:57:00 | 40m | (sin `OPERATOR`) | 7.150000 | EA4GHH | `qsl3/EA4GHH @ES-0849-20261113.adi` | `qsl4/2026-11-13 EA3JAQ.adi` |
| 2026-11-13 | 09:07:00 | 70cm | (sin `OPERATOR`) | 430.200000 | EA4GHH | `qsl3/EA4GHH @ES-0849-20261113.adi` | `qsl4/2026-11-13 EA3JAQ.adi` |
| 2026-11-14 | 16:06 | 40m | EA4HUK | 7.183 | EA3JAQ | `qsl2/EA3JAQ-20261114.adi` | `qsl4/ea4huk-pota-0850.adi` |
| 2026-11-14 | 16:06 | 40m | EA4HUK | 7.195 | EA3JAQ | `qsl2/EA3JAQ-20261114.adi` | `qsl4/ea4huk-pota-0850.adi` |
| 2026-11-15 | 16:19:00 | 70cm | (sin `OPERATOR`) | 420 | EA4HUK | `qsl7/ea4huk-dmr.adi` | `qsl7/EA3JAQ-20261115-en-dmr-15-nov-full.adi` |

Los 13 espejos restantes tenían frecuencia/hora distinta en el otro log; se han
mantenido esas diferencias a propósito. Por eso `audit_adi.py` avisa de 2 duplicados
por su clave sin `FREQ`: `7.160` vs `7.150` (qsl4/EA3JAQ) y `7.183` vs `7.195`
(qsl4/ea4huk-pota). Es esperado y aceptado.

Totales tras esta actualización:

- ADI raíz: 2.939 → **2.955** QSO (+16 espejos); después **3.015** al añadir los
  5 `CRUZADAS-ADICIONALES-*.adi` (+60). QSO entre las 4 estaciones: 283 + 60,
  con **0 duplicados exactos**; longitudes ADIF correctas.
- `ACTIVIDADES/`: 38 ficheros, **3.375** QSO (regenerados con `./generar_adis.sh`).
- Postales: **3.058** generadas y sincronizadas con Drive; `qsl_index.json` con
  `total: 3058` y conteos `qsl1=565, qsl2=426, qsl3=628, qsl4=478, qsl5=852,
  qsl6=43, qsl7=66`.
- `graficos/TODOS.adi`: **3.009** QSO (36 `.adi` raíz menos los 6 registros demo),
  0 `XYZ123` y 3.009 registros con `OPERATOR` completado. 27 gráficos, 27 miniaturas
  y `estadisticas_adi.json` regenerados; hora pico 09:00 UTC con 841 QSO.

### Actualización 17/11 (tarde): 5 ADI de cruces adicionales

Se versionaron cinco ficheros `qslN/CRUZADAS-ADICIONALES-<referencia>.adi`, uno por
actividad de qsl1 a qsl5, con **12 QSO cada uno (60 en total)**, todos en 10 m
(28.340 / 28.500 / 28.576 MHz) y fechas 13–15/11. Cabecera
`PROGRAMID=CrossAdds`, `CREATED_TIMESTAMP=20261117 180000`, con la referencia de
la actividad en `QSLMSG` (algunos añaden `Custom DME 52001`). No son el bloque
DME de 40/60/80 m descrito arriba: ese sigue fuera del repo.

| Actividad | Fichero | Referencia |
|---|---|---|
| `qsl1` | `CRUZADAS-ADICIONALES-EAR-1901.adi` | `EAR-1901` |
| `qsl2` | `CRUZADAS-ADICIONALES-ES-0340.adi` | `ES-0340` |
| `qsl3` | `CRUZADAS-ADICIONALES-ES-0849.adi` | `ES-0849` |
| `qsl4` | `CRUZADAS-ADICIONALES-ES-0850.adi` | `ES-0850` |
| `qsl5` | `CRUZADAS-ADICIONALES-LLES-0214.adi` | `LLES-0214` |

Alimentan el generador de postales y el índice web: explican el paso de 2.955 a
3.015 QSO y de 2.998 a 3.058 postales, y los conteos por actividad 565/426/628/
478/852 (antes 553/414/616/466/840). Regenerados también los derivados de
`ACTIVIDADES/` y `graficos/TODOS.adi`.

### Actualización 17/11 (noche): 9 ADI derivados en `ADICIONALES/`

De los 5 `CRUZADAS-ADICIONALES` se extrajeron los QSO de cada estación con EA4HUK y
se versionaron 9 ficheros `ADICIONALES/<estacion>_<TOTA|LLOTA|POTA>.adi` (3 estaciones
× 3 actividades, **15 QSO** en total: 1 TOTA `EAR-1901`, 1 LLOTA `LLES-0214` y 3 POTA
`ES-0340`/`ES-0849`/`ES-0850` por estación). Cabecera
`CREATED_TIMESTAMP=20261117 210656 UTC`. Son derivados para que cada estación cargue
sus QSO en su propio log: **no** son entrada del generador de postales ni de los gráficos.

Cuadros de EA4GHH por día (día, hora, banda, operador, frecuencia, POI, nombre
del `.adi` de origen y corresponsal): `~/Desktop/cuadros_ea4ghh.md`. Cubren los
118 QSO entre EA4GHH y el resto del trío: 58 el 13/11, 40 el 14/11 y 20 el 15/11.

### Verificación de cruces por actividad

Revisados los 32 `.adi` raíz de qsl1–qsl5 (2.949 QSO, excluidos `ACTIVIDADES/`,
`TESTDATA/` y los 6 registros `XYZ123`). En **las 5 actividades**, cada una de las
4 estaciones (`EA4HUK`, `EA3JAQ`, `EA4GHH`, `EA4IWX`) tiene **al menos un QSO con
cada una de las otras 3**: 12/12 pares dirigidos presentes en cada actividad,
ningún par faltante. La estación propia se toma de `OPERATOR` y, si no está, de
`STATION_CALLSIGN` (normalizando sufijos como `EA4IWX/9`). El recuento se verificó
con dos parsers independientes. Matriz detallada de QSO por par en `README.md`
(§ "Cobertura de cruces entre las 4 estaciones"). Solo se observaron dos pares
duplicados en qsl4 por `CALL`+fecha+hora+banda+modo con frecuencias distintas,
heredados de los espejos; no cambian la conclusión.
