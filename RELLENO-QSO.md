# Relleno de QSO EA4HUK ↔ {EA3JAQ, EA4GHH, EA4IWX} en 20/40/70/2 m

Fecha: 2026-11-15 · Estado: aplicado a los ADI raíz y a `ACTIVIDADES/`

## Motivo

Cada log propio de EA4HUK debe contener contactos con EA3JAQ, EA4GHH y EA4IWX
en las cuatro bandas de trabajo (20 m, 40 m, 70 cm y 2 m). Antes de este relleno
faltaban 16 QSO repartidos en los cinco logs.

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

## Totales

- ADI raíz: 2.743 → **2.819** QSO (+16 relleno, −1 duplicado EAFNT, +61 espejos).
- `ACTIVIDADES/`: 32 ficheros, **3.144** QSO (qsl2 se replica en `pota` y `tota`).
- `audit_adi.py`: sin errores nuevos (0 sin FREQ, BAND canónica, TIME_ON de 4 caracteres,
  sin duplicados internos en los cinco logs).

## Reversión

Backup de los cinco ADI previos al cambio:

```
/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/relleno_backup_201453/
```

Script usado: `/private/var/folders/pg/zbqnb64s3c14fk26wvx_6mzw0000gn/T/opencode/rellenar_trio.py`
