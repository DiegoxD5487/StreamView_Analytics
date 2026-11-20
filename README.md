# StreamView Analytics

**Proyecto de Visualización de Datos · ADY1104**

StreamView Analytics es un proyecto académico que busca transformar la información de un catálogo audiovisual en visualizaciones claras y útiles para la toma de decisiones.

En este caso asumimos el rol de un equipo de análisis que asesora a una plataforma de streaming ficticia. Nuestro objetivo es identificar patrones en su oferta de películas y series, comparar su popularidad y valoración, y proponer líneas de acción para las áreas de gerencia, contenidos y marketing.

La solución se desarrolló con **Python y Streamlit**, tomando como punto de partida el trabajo de preparación de datos y visualización realizado durante el semestre.

## ¿Qué problema buscamos resolver?

Un catálogo amplio no garantiza, por sí solo, que sus contenidos respondan a las prioridades del negocio. Para tomar mejores decisiones es necesario conocer qué géneros tienen mayor presencia, cómo se distribuyen los títulos por país, qué contenidos muestran mejores indicadores de popularidad y valoración, y qué límites tienen esas mediciones.

StreamView Analytics reúne estos antecedentes en un dashboard interactivo para apoyar tres preguntas:

- **Gerencia:** ¿cómo está compuesto el catálogo y qué aspectos conviene revisar?
- **Gestión de contenidos:** ¿qué géneros presentan oportunidades para profundizar el análisis de adquisición o curaduría?
- **Marketing:** ¿qué contenidos y segmentos podrían evaluarse para futuras acciones de promoción?

## Dashboard interactivo

El sitio está organizado en tres secciones:

### 1. Resumen Ejecutivo
Presenta los principales indicadores del catálogo, su distribución entre películas y series, y los géneros y países con mayor presencia. Permite observar cómo cambian estos resultados al aplicar filtros.

### 2. Potencial de contenido
Compara popularidad, valoración y presencia de los contenidos por género, idioma y país. Incluye visualizaciones para detectar diferencias entre el tamaño de la oferta y el desempeño observado en los datos.

### 3. Decisiones estratégicas
Relaciona los hallazgos con posibles decisiones editoriales y criterios de comparación financiera de películas. También presenta consideraciones metodológicas, riesgos de interpretación y propuestas de mejora.

En las tres secciones se utilizan indicadores, filtros, gráficos interactivos y textos de apoyo orientados a explicar los resultados, no solo a mostrarlos.

## Datos y alcance del análisis

La base integrada contiene **31.991 títulos: 16.000 películas y 15.991 series**. Para preparar el conjunto de datos se trabajó con información descriptiva del catálogo, como género, país, idioma y año de estreno, además de popularidad, votaciones y datos financieros disponibles para películas.

Es importante considerar que:

- La **popularidad** y la **valoración** son indicadores presentes en el dataset; no representan reproducciones, tiempo de visualización ni retención real de suscriptores.
- Para las comparaciones por género y país se utiliza una **categoría principal por título**. Esto simplifica los gráficos, pero no refleja todas las categorías asociadas a cada obra.
- Los análisis financieros se limitan a películas con datos suficientes. La relación **recaudación/presupuesto** es un múltiplo bruto, no una medida de ganancias netas ni de rentabilidad de la plataforma.
- Algunas comparaciones aplican umbrales mínimos de títulos, votos o presupuesto para evitar conclusiones basadas en muestras demasiado reducidas.

Por estas razones, las recomendaciones del dashboard se plantean como **orientaciones para la evaluación de alternativas**, no como decisiones automáticas ni resultados comerciales comprobados.

## Tecnologías utilizadas

- **Python y Pandas:** preparación, filtrado y análisis de datos.
- **Streamlit:** desarrollo de la aplicación web y sus controles interactivos.
- **Plotly:** construcción de los gráficos.
- **Git y GitHub:** organización y control de versiones del proyecto.

## Ejecutar el proyecto en Windows

Abre la carpeta `StreamView_Analytics` en Visual Studio Code. Desde su terminal, ejecuta los siguientes comandos:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Luego abre **http://localhost:8501** en el navegador.

Si ya tienes el entorno virtual creado y las dependencias instaladas, solo necesitas ejecutar el último comando.

## Organización de archivos

```text
StreamView_Analytics/
├── app.py                 # Interfaz, navegación y visualizaciones
├── analytics.py           # Análisis complementarios y criterios de comparación
├── core.py                # Lectura de datos, filtros e indicadores
├── requirements.txt       # Dependencias de Python
├── README.md
├── .streamlit/
│   └── config.toml        # Configuración de la aplicación
├── datos/
│   └── STREAMVIEW_POWERBI.csv
├── recursos/              # Logotipo, fondo e imágenes del proyecto
└── pruebas/               # Pruebas del procesamiento y análisis
```

## Contexto de la evaluación

Este proyecto forma parte del trabajo de la asignatura **Visualización de Datos (ADY1104)**. Su desarrollo considera las actividades de construcción de la solución (**EP5**) y su presentación y defensa (**EP6**).

El dashboard sirve como apoyo a la exposición y al análisis de resultados. El informe ejecutivo y la presentación formal complementan la solución, documentando las decisiones de diseño, los hallazgos, las limitaciones y las recomendaciones para StreamView Analytics.
