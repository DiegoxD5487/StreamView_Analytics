"""Datos y métricas del dashboard de StreamView Analytics.

Los datos de entrada provienen del proyecto académico StreamView. Las métricas de
popularidad y valoración se interpretan únicamente según su fuente, no como
estadísticas reales de uso de la plataforma.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pandas as pd

REQUIRED = {
    "content_id", "type", "release_year", "genre_principal", "country_principal",
    "language", "popularity", "vote_average", "budget", "revenue",
    "datos_financieros_validos",
}


def load_data(source: str | Path | BytesIO) -> pd.DataFrame:
    """Carga CSV exportado por ETL (UTF-8-SIG, ;, decimal coma)."""
    df = pd.read_csv(source, sep=";", decimal=",", encoding="utf-8-sig", low_memory=False)
    missing = REQUIRED.difference(df.columns)
    if missing:
        raise ValueError("Faltan columnas obligatorias: " + ", ".join(sorted(missing)))

    for col in ("release_year", "popularity", "vote_average", "budget", "revenue"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ("type", "genre_principal", "country_principal", "language"):
        df[col] = df[col].fillna("No informado").astype(str).str.strip().replace("", "No informado")
    if df["content_id"].isna().any() or df["content_id"].duplicated().any():
        raise ValueError("Se detectaron content_id nulos o duplicados.")
    return df


def filter_data(
    df: pd.DataFrame,
    types: list[str] | None = None,
    years: tuple[int, int] | None = None,
    genre: str | None = None,
    country: str | None = None,
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if types is not None:
        mask &= df["type"].isin(types)
    if years is not None:
        mask &= df["release_year"].between(years[0], years[1], inclusive="both")
    if genre and genre != "Todos":
        mask &= df["genre_principal"].eq(genre)
    if country and country != "Todos":
        mask &= df["country_principal"].eq(country)
    return df.loc[mask].copy()


def portfolio_metrics(df: pd.DataFrame) -> dict:
    valid = df.loc[
        df["type"].eq("Movie") & df["datos_financieros_validos"].eq("Sí") &
        df["budget"].gt(0) & df["revenue"].gt(0)
    ]
    budget = float(valid["budget"].sum())
    revenue = float(valid["revenue"].sum())
    return {
        "total": int(df["content_id"].nunique()),
        "movies": int(df.loc[df["type"].eq("Movie"), "content_id"].nunique()),
        "series": int(df.loc[df["type"].eq("TV Show"), "content_id"].nunique()),
        "rating": float(df["vote_average"].mean()) if not df.empty else float("nan"),
        "popularity": float(df["popularity"].mean()) if not df.empty else float("nan"),
        "revenue_budget_ratio": revenue / budget if budget > 0 else None,
        "revenue_budget_delta": revenue - budget if budget > 0 else None,
        "financial_titles": len(valid),
    }


def genre_aggregates(df: pd.DataFrame, min_titles: int = 1) -> pd.DataFrame:
    nonmissing = df.loc[df["genre_principal"].ne("No informado")]
    metrics = (nonmissing.groupby("genre_principal", observed=True)
               .agg(contenidos=("content_id", "nunique"),
                    popularidad=("popularity", "mean"),
                    valoracion=("vote_average", "mean"))
               .reset_index())
    return metrics.loc[metrics["contenidos"] >= min_titles]


def country_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    nonmissing = df.loc[df["country_principal"].ne("No informado")]
    return (nonmissing.groupby("country_principal", observed=True)
            .agg(contenidos=("content_id", "nunique"), popularidad=("popularity", "mean"))
            .reset_index())


def language_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    nonmissing = df.loc[df["language"].ne("No informado")]
    return (nonmissing.groupby("language", observed=True)
            .agg(contenidos=("content_id", "nunique"), popularidad=("popularity", "mean"))
            .reset_index())
