# Gráficos del log completo

Generados con los scripts de `~/Downloads/adif-graficando-cositas`
(`analizar_adi_grafico.py` y `analizar_por_operador.py`) a partir de
`TODOS.adi`.

## Datos de entrada

`TODOS.adi` — 2.933 QSO, todos los contactos de las cuatro estaciones
(EA4HUK, EA4GHH, EA4IWX, EA3JAQ) en qsl1–qsl7.

- Origen: los `.adi` raíz de cada POI (no la carpeta `ACTIVIDADES`, que son
  derivados y duplicarían registros).
- Excluidos los 6 registros de demostración `QSL-DEMO-EG9MM.adi`.
- `STATION_CALLSIGN` normalizado (sin espacios finales) y `OPERATOR`
  completado a partir de la estación en los 608 registros de EA3JAQ, que no
  traían el campo.
- Cada QSO aparece tal como lo registró su estación: un contacto entre dos de
  nuestras estaciones está dos veces (una por cada log).

## Contenido

- 18 gráficos generales: `grafico_*.png`
- 10 gráficos por operador: `operador_*.png`
- `estadisticas_adi.json`: cifras que alimentan los gráficos

No se incluye `grafico_qrz_lookups.png`: en el proyecto original ese gráfico
usa una tabla de lookups de QRZ.com escrita a mano para otro log, no datos de
estos contactos.

## Regenerar

```bash
python3 -m venv venv_graf
venv_graf/bin/pip install "matplotlib==3.9.4" seaborn pandas numpy
cd graficos && ln -sf TODOS.adi aaa.adi
MPLBACKEND=Agg ../venv_graf/bin/python ../adif-graficando-cositas/analizar_adi_grafico.py
MPLBACKEND=Agg ../venv_graf/bin/python ../adif-graficando-cositas/analizar_por_operador.py
rm aaa.adi
```

Nota: con matplotlib ≥ 3.11 el gráfico `grafico_distancia_locator.png` falla
(`Axes.boxplot(labels=...)` fue eliminado); con 3.9.4 funciona.
