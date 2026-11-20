"""Cálculos auxiliares reproducibles para el dashboard StreamView EV3.

Todos los resultados son descriptivos de un catálogo académico; ninguna medida
se presenta como reproducciones, retención o rentabilidad de la plataforma.
"""
from __future__ import annotations

import pandas as pd
from core import genre_aggregates, country_aggregates, language_aggregates


def most_common_genre(df: pd.DataFrame) -> tuple[str, int]:
    g = genre_aggregates(df).sort_values('contenidos', ascending=False)
    return (str(g.iloc[0]['genre_principal']), int(g.iloc[0]['contenidos'])) if not g.empty else ('Sin datos', 0)


def most_common_country(df: pd.DataFrame) -> tuple[str, int]:
    c = country_aggregates(df).sort_values('contenidos', ascending=False)
    return (str(c.iloc[0]['country_principal']), int(c.iloc[0]['contenidos'])) if not c.empty else ('Sin datos', 0)


def opportunities(df: pd.DataFrame, min_titles: int = 100) -> pd.DataFrame:
    """Heurística transparente, no predicción: demanda relativa vs amplitud del catálogo."""
    out = genre_aggregates(df, min_titles=min_titles).copy()
    if out.empty:
        return pd.DataFrame(columns=['Género', 'Contenidos', 'Popularidad media', 'Valoración media',
                                     'Índice orientativo', 'Acción de revisión'])
    # Percentiles describen el grupo de géneros elegibles, y cambian con los filtros.
    pop_rank = out['popularidad'].rank(pct=True)
    rating_rank = out['valoracion'].rank(pct=True)
    low_offer_rank = 1 - out['contenidos'].rank(pct=True)
    out['indice'] = (0.5 * pop_rank + 0.3 * rating_rank + 0.2 * low_offer_rank) * 100
    mean_pop = float(out['popularidad'].mean())
    mean_count = float(out['contenidos'].mean())
    def action(row: pd.Series) -> str:
        if row['popularidad'] >= mean_pop and row['contenidos'] < mean_count:
            return 'Explorar expansión'
        if row['popularidad'] >= mean_pop:
            return 'Consolidar oferta'
        if row['contenidos'] >= mean_count:
            return 'Revisar saturación'
        return 'Monitorear'
    out['accion'] = out.apply(action, axis=1)
    return out.sort_values('indice', ascending=False).rename(columns={
        'genre_principal': 'Género', 'contenidos': 'Contenidos',
        'popularidad': 'Popularidad media', 'valoracion': 'Valoración media',
        'indice': 'Índice orientativo', 'accion': 'Acción de revisión',
    })[['Género', 'Contenidos', 'Popularidad media', 'Valoración media',
        'Índice orientativo', 'Acción de revisión']].reset_index(drop=True)


def comparable_movies(df: pd.DataFrame, min_budget: float = 1_000_000,
                      min_votes: int = 100) -> pd.DataFrame:
    """Evita multiplicadores extremos causados por presupuestos simbólicos.

    No descarta ni modifica los originales: solo filtra un gráfico de comparación.
    """
    out = df.loc[
        df['type'].eq('Movie') & df['datos_financieros_validos'].eq('Sí') &
        df['budget'].ge(min_budget) & df['revenue'].gt(0) &
        df['vote_count'].fillna(0).ge(min_votes)
    ].copy()
    if out.empty:
        return out.assign(multiplo=pd.Series(dtype='float64'))
    out['multiplo'] = out['revenue'] / out['budget']
    return out


def languages_for_chart(df: pd.DataFrame, min_titles: int = 30) -> pd.DataFrame:
    out = language_aggregates(df).query('contenidos >= @min_titles').copy()
    aliases = {
        'en':'Inglés','es':'Español','fr':'Francés','ja':'Japonés','ko':'Coreano',
        'zh':'Chino','hi':'Hindi','pt':'Portugués','ru':'Ruso','de':'Alemán',
        'ta':'Tamil','te':'Telugu','th':'Tailandés','it':'Italiano',
        'id':'Indonesio','tr':'Turco','tl':'Filipino','bn':'Bengalí',
        'ar':'Árabe','nl':'Neerlandés','cs':'Checo','el':'Griego',
        'sv':'Sueco','hu':'Húngaro','pl':'Polaco','af':'Afrikáans',
        'sk':'Eslovaco','lv':'Letón','ca':'Catalán','uk':'Ucraniano',
    }
    out['idioma_etiqueta'] = out['language'].map(lambda x: f"{aliases.get(x, x.upper())} ({x})")
    return out


def genre_evidence(df: pd.DataFrame, min_titles: int = 100) -> pd.DataFrame:
    """Cobertura y respaldo de votos por género principal de la selección activa.

    El recuento de títulos evita categorías demasiado escasas; la mediana de
    votos evita confundir una popularidad media alta con evidencia de recepción.
    """
    basic = genre_aggregates(df, min_titles=min_titles).copy()
    if basic.empty:
        return basic.assign(votos_medianos=pd.Series(dtype='float64'),
                            porcentaje_catalogo=pd.Series(dtype='float64'))
    med = (df.loc[df['genre_principal'].ne('No informado')]
           .groupby('genre_principal')['vote_count'].median())
    basic['votos_medianos'] = basic['genre_principal'].map(med).fillna(0)
    basic['porcentaje_catalogo'] = basic['contenidos'] / len(df) * 100 if len(df) else 0.0
    return basic


def genre_decision_matrix(df: pd.DataFrame, min_titles: int = 100,
                          min_median_votes: int = 10) -> pd.DataFrame:
    """Señales descriptivas para revisión editorial; NO asignación automática.

    Las reglas se basan en medianas de la selección, no en umbrales de negocio
    impuestos externamente. Los votantes medianos son por título del género.
    """
    columns = ['Género', 'Títulos', 'Participación (%)', 'Popularidad media',
               'Valoración media', 'Votos medianos', 'Foco de revisión']
    eligible = genre_evidence(df, min_titles=min_titles)
    eligible = eligible.loc[eligible['votos_medianos'].ge(min_median_votes)].copy()
    if eligible.empty:
        return pd.DataFrame(columns=columns)
    pop_middle = eligible['popularidad'].median()
    rating_middle = eligible['valoracion'].median()
    count_middle = eligible['contenidos'].median()

    def focus(row: pd.Series) -> str:
        if row['popularidad'] >= pop_middle and row['valoracion'] < rating_middle:
            return 'Revisar recepción'
        if (row['popularidad'] >= pop_middle and row['valoracion'] >= rating_middle
                and row['contenidos'] < count_middle):
            return 'Evaluar expansión'
        if row['popularidad'] >= pop_middle and row['valoracion'] >= rating_middle:
            return 'Consolidar'
        if row['contenidos'] >= count_middle:
            return 'Revisar oferta'
        return 'Monitorear'

    eligible['accion'] = eligible.apply(focus, axis=1)
    priority_order = {
        'Evaluar expansión': 0, 'Consolidar': 1, 'Revisar recepción': 2,
        'Revisar oferta': 3, 'Monitorear': 4,
    }
    eligible['orden'] = eligible['accion'].map(priority_order)
    eligible = eligible.sort_values(['orden', 'popularidad'], ascending=[True, False])
    eligible = eligible.rename(columns={
        'genre_principal': 'Género', 'contenidos': 'Títulos',
        'porcentaje_catalogo': 'Participación (%)',
        'popularidad': 'Popularidad media', 'valoracion': 'Valoración media',
        'votos_medianos': 'Votos medianos', 'accion': 'Foco de revisión',
    })
    return eligible[columns].reset_index(drop=True)


def financial_comparison_metrics(df: pd.DataFrame, min_budget: float = 1_000_000,
                                 min_votes: int = 100) -> dict:
    """Usa exactamente el mismo universo que la visualización financiera.

    Ratio = suma recaudación / suma presupuesto; nunca promedio de ratios.
    """
    comparable = comparable_movies(df, min_budget=min_budget, min_votes=min_votes)
    total_films = int(df.loc[df['type'].eq('Movie'), 'content_id'].nunique())
    eligible = int(comparable['content_id'].nunique())
    total_budget = float(comparable['budget'].sum())
    total_revenue = float(comparable['revenue'].sum())
    return {
        'eligible': eligible,
        'total_films': total_films,
        'coverage': eligible / total_films if total_films else None,
        'gross_multiple': total_revenue / total_budget if total_budget > 0 else None,
        'total_budget': total_budget,
        'total_revenue': total_revenue,
    }
