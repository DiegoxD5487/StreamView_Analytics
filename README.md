# StreamView Analytics · Dashboard EV3

Dashboard web en **Streamlit + Plotly + Pandas**, construido a partir de la base académica StreamView. **No altera el proyecto original de Power BI.**

## Novedades de esta edición

- **Interfaz web nueva:** fondo limpio mediante CSS, encabezado corporativo y **tres páginas** bien diferenciadas. El fondo antiguo con cajas predibujadas no se usa porque se superponía a los componentes interactivos.
- **Navegación centrada**, con estado conservado al cambiar de pestaña.
- **Cuatro filtros compartidos**: tipo de contenido, género principal, país principal y periodo de estreno.
- **Selección de país en el gráfico de barras del Resumen Ejecutivo** que actualiza el resto de indicadores y gráficos. También está habilitada la selección de puntos en el mapa de la segunda página. En caso de que el navegador no reconozca la pulsación del mapa, usa el selector de país de la barra superior.
- Gráficos responsivos con textos visibles, paneles blancos y colores institucionales azul/morado/violeta/dorado.
- Tabla de consulta dentro de desplegables y análisis editorial con más contexto empresarial.
- Página **Decisiones estratégicas** con indicadores de cobertura de muestra, recomendaciones preliminares justificadas, benchmark financiero prudente, límites de interpretación e impacto esperado.
- En **Potencial de contenido**, los rankings de géneros exigen por defecto al menos 100 títulos y una **mediana de 10 votos por título**; los límites se pueden modificar desde los controles. Esto evita que categorías con popularidad alta pero escasísimas votaciones dominen el análisis.
- La **matriz de decisiones editoriales** presenta variables observadas (títulos, participación, popularidad, valoración y mediana de votos) y un foco descriptivo de revisión, **sin índices artificiales presentados como predicciones**.
- Los **KPI de la página estratégica comparten el mismo universo financiero**: presupuesto ≥ 1.000.000, recaudación positiva y al menos 100 votos. La cobertura se calcula sobre el número de películas de la selección filtrada.
- **Sin botones para descargar datos**: el sitio está pensado para la presentación del análisis.

## Instalación en Windows / VS Code

**Importante:** abre en VS Code la carpeta `StreamView_Streamlit` que contiene directamente `app.py` y `requirements.txt`.

```powershell
# Si ya tienes Streamlit instalado en el entorno del proyecto, omite los dos primeros comandos.
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abre `http://localhost:8501` (se abre habitualmente solo).

Si la terminal dice «no such file requirements.txt», verifica `dir`; probablemente estás en la carpeta externa del ZIP, no en la carpeta `StreamView_Streamlit`.

Para actualizar la versión antigua: realiza un respaldo, y reemplaza `app.py` y los demás archivos de esta carpeta; no es necesario copiar el entorno `.venv` desde un ZIP viejo.

## Estructura

```text
StreamView_Streamlit/
├── app.py                      # Navegación, filtros, visuales y storytelling
├── analytics.py                # Heurísticas y comparaciones de negocio
├── core.py                     # Importación, filtros, KPI y agregaciones
├── requirements.txt
├── README.md
├── .streamlit/config.toml
├── recursos/
│   ├── logo_streamview.png
│   ├── bg_resumen.png          # Referencia de diseño (no se aplica como wallpaper)
│   └── bg_potencial.png        # Referencia de diseño (no se aplica como wallpaper)
├── datos/
│   └── STREAMVIEW_POWERBI.csv
└── pruebas/
    ├── test_core.py
    └── test_analytics.py
```

## Selección cruzada de país

1. En **Resumen Ejecutivo**, haz clic en una barra del gráfico **Países con mayor presencia**.
2. El país seleccionado aparece en una cápsula sobre los gráficos y el resto de indicadores/gráficos refleja ese país.
3. Presiona **✕ Quitar país** para restablecer la vista sin país seleccionado.
4. El filtro `País principal` de la barra superior funciona en las tres páginas. Una selección manual en el desplegable reemplaza la selección que proviene del gráfico.
5. En **Potencial de contenido**, también puedes intentar seleccionar las burbujas del mapa; el filtro superior siempre está disponible.

Los gráficos Plotly permiten ver detalles al pasar el cursor. `st.plotly_chart` utiliza `on_select="rerun"`, disponible en Streamlit moderno. La interacción del clic en un gráfico depende del navegador y de la versión de Streamlit; si no se reconoce, utiliza el desplegable.

## Alcance de los datos y advertencias

El dataset contiene 31.991 títulos (16.000 películas y 15.991 series). El análisis es **académico** y no dispone de datos operativos de reproducciones, retención o suscripciones.

- `popularity` y `vote_average` son **metadatos**, no consumo real de la plataforma.
- Se utiliza el **primer género y país** registrado por título para evitar duplicidad de registros; esto limita el análisis de películas con múltiples géneros/países.
- El indicador `revenue/budget` es un **múltiplo bruto de recaudación/presupuesto**, no el ROI ni los beneficios reales de StreamView.
- La diferencia `revenue - budget` tampoco es la ganancia neta de la plataforma.
- En la tercera página, las **comparaciones de películas** solo consideran títulos con presupuesto ≥ 1.000.000 y al menos 100 votos. Esto evita que presupuestos simbólicos eleven el ranking a valores absurdos. El KPI global de recaudación/presupuesto mantiene su definición de la evaluación anterior (títulos con presupuesto e ingresos mayores a cero).
- La **matriz editorial** no es un modelo predictivo. Clasifica géneros mediante comparaciones con medianas de los géneros elegibles; un foco «Evaluar expansión» significa **investigar una alternativa**, no aprobar su adquisición. Requiere ≥100 títulos por género y ≥10 votos de mediana por título.
- «Géneros con muestra suficiente» solo exige ≥100 títulos; el número de géneros con respaldo de votos que integra la matriz puede ser menor.
- El KPI **Cobertura de la muestra financiera** es `películas comparables / total de películas filtradas`. En el catálogo completo: 3.132/16.000 = 19,6 %.
- El KPI **Recaudación/presupuesto** de **Decisiones estratégicas** es `suma(recaudación comparable) / suma(presupuesto comparable)` y vale 2,94× sin filtros. El KPI del **Resumen Ejecutivo** preserva la definición general anterior (películas con presupuesto e ingresos positivos), que da 2,92× sobre 3.540 películas. Son bases diferentes y se muestran expresamente como tales. No representan rentabilidad de StreamView.
- Los KPI editoriales y financieros se recalculan al seleccionar un tipo, país, género y período de estreno.

## Indicadores y aplicación empresarial

| Indicador | Qué mide | Uso apropiado |
|---|---|---|
| Géneros con muestra suficiente | Cantidad de géneros principales con ≥100 títulos | Determinar cuántos grupos tienen tamaño mínimo para una comparación. |
| Películas comparables | Películas con presupuesto ≥1.000.000, recaudación positiva y ≥100 votos | Crear un conjunto de referencia para análisis financiero descriptivo. |
| Cobertura de la muestra financiera | Porcentaje de películas que cumplen los requisitos de comparación | Advertir cuándo un análisis depende de una fracción reducida del catálogo. |
| Recaudación / presupuesto | Suma de ingresos cinematográficos / suma de presupuesto cinematográfico en películas comparables | Comparar magnitudes de recaudo e inversión, no beneficios de la plataforma. |

La página estratégica se organiza con la secuencia **evidencia → implicación → decisión preliminar → limitación**. Los beneficios operativos son esperados, todavía no medidos; deben validarse con mediciones antes y después.

## Validación

Desde la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Se validan recuentos, valores agregados, integridad de registros, filtrado y reglas de oportunidad/benchmark.

## Publicación en Streamlit Community Cloud

1. Sube **solo los archivos del proyecto**, sin `.venv`, a un repositorio en GitHub.
2. Asegúrate de que `requirements.txt`, `app.py`, `core.py`, `analytics.py`, `data/` y `assets/` estén presentes.
3. En https://share.streamlit.io, inicia sesión con GitHub y elige el repositorio.
4. Selecciona como archivo principal `app.py` (si subes la carpeta completa como raíz, la ruta puede ser `StreamView_Streamlit/app.py`).
5. Comprueba públicamente los filtros y la navegación antes de la defensa.

**Evaluación:** la web sirve para la demostración, pero las pautas EP5 y EP6 también solicitan el informe ejecutivo en PDF, la presentación ejecutiva en PDF/PPT y los archivos reproducibles.
