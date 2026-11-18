# Gráficos del log completo

Publicados en <https://dcialdella.github.io/ia-qsls/graficos/> (página nueva, sin
modificar la web de descarga de postales ni `qsl_index.json`).

Generados con los scripts de `~/Downloads/adif-graficando-cositas`
(`analizar_adi_grafico.py` y `analizar_por_operador.py`) a partir de
`graficos/TODOS.adi`.

## Datos de entrada

`graficos/TODOS.adi` — 3.009 QSO, todos los contactos de las cuatro estaciones
(EA4HUK, EA4GHH, EA4IWX, EA3JAQ) en qsl1–qsl7.

- Origen: los 36 `.adi` raíz de cada POI (ni `ACTIVIDADES/` ni `ADICIONALES/`, que son
  derivados y duplicarían registros), incluidos los 5 `CRUZADAS-ADICIONALES-*.adi`.
- Excluidos los 6 registros de demostración `QSL-DEMO-EG9MM.adi`.
- **Tampoco entra `qsl80/`: es una actividad de postal, no una estadística nueva.**
  Sus 18 QSO en 80 m desde Melilla se solapan con los ya registrados en qsl1–qsl7
  (15 del ADI original y 3 contactos locales del 13/11). Por eso los gráficos
  siguen generándose solo con los 36 `.adi` de qsl1–qsl7 (3.009 QSO tras quitar
  los 6 demo), aunque el repo tenga ya 37 `.adi` raíz y 3.033 QSO en total.
- `STATION_CALLSIGN` normalizado (sin espacios finales) y `OPERATOR`
  completado a partir de la estación en los 626 registros de EA3JAQ, que no
  traían el campo.
- Cada QSO aparece tal como lo registró su estación: un contacto entre dos de
  nuestras estaciones está dos veces (una por cada log).

## Contenido

- 17 gráficos generales: `grafico_*.png`
- 10 gráficos por operador: `operador_*.png`
- 27 miniaturas de 720 px en `graficos/thumbs/*.png`, usadas por la galería; al
  pulsar una imagen se abre su versión completa.
- `estadisticas_adi.json`: cifras que alimentan los gráficos.
- La regeneración del 17/11 produjo 27 imágenes idénticas a las ya publicadas.

No se incluye `grafico_qrz_lookups.png`: en el proyecto original ese gráfico
usa una tabla de lookups de QRZ.com escrita a mano para otro log, no datos de
estos contactos.

Cifras del análisis: **1.109 indicativos únicos**, **33 entidades DXCC**,
8 bandas, 6 modos, distancia media **802,6 km** y máxima **13.955 km**. Hora pico:
**09:00 UTC** (841 QSO).

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
