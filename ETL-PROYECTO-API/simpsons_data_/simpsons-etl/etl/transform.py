import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def transform_characters(df: pd.DataFrame) -> pd.DataFrame:
    print("Transformando personajes...")

    cols = [c for c in ["id", "name", "gender", "occupation", "status"] if c in df.columns]
    characters = df[cols].copy()

    rename_map = {"id": "character_id"}
    characters.rename(columns=rename_map, inplace=True)

    # Normalizar texto
    for col in ["name", "gender", "occupation", "status"]:
        if col in characters.columns:
            characters[col] = characters[col].astype(str).str.strip()

    characters.drop_duplicates(subset=["character_id"], inplace=True)
    characters.reset_index(drop=True, inplace=True)

    print(f"Personajes transformados: {len(characters)}")
    return characters


def transform_episodes(df: pd.DataFrame) -> pd.DataFrame:
    print("Transformando episodios...")

    cols = [c for c in ["id", "name", "season", "air_date", "number_in_season"] if c in df.columns]
    episodes = df[cols].copy()

    rename_map = {"id": "episode_id"}
    episodes.rename(columns=rename_map, inplace=True)

    if "season" in episodes.columns:
        episodes["season"] = pd.to_numeric(episodes["season"], errors="coerce")

    if "air_date" in episodes.columns:
        episodes["air_date"] = pd.to_datetime(episodes["air_date"], errors="coerce")
    else:
        episodes["air_date"] = pd.NaT

    # Calcular number_in_season si no viene de la API
    if "number_in_season" not in episodes.columns or episodes["number_in_season"].isna().all():
        episodes["number_in_season"] = (
            episodes.sort_values("episode_id")
            .groupby("season")
            .cumcount() + 1
        )

    episodes.drop_duplicates(subset=["episode_id"], inplace=True)
    episodes.reset_index(drop=True, inplace=True)

    print(f"Episodios transformados: {len(episodes)}")
    return episodes


def transform_ratings(df_episodes: pd.DataFrame) -> pd.DataFrame:
    """
    Genera la tabla fact_ratings a partir de los episodios transformados.
    Simula viewers_millions, imdb_rating y duration_min cuando la API
    no los provee directamente, usando distribuciones realistas de Los Simpsons.
    Las columnas numéricas se normalizan a rango [0, 1] con MinMaxScaler.
    """
    print("Generando fact_ratings...")

    rng = np.random.default_rng(42)
    n = len(df_episodes)

    ratings = pd.DataFrame()
    ratings["episode_id"] = df_episodes["episode_id"].values

    # Temporada
    season = df_episodes["season"].fillna(1).astype(int).values if "season" in df_episodes.columns else rng.integers(1, 36, n)
    ratings["season"] = season

    ratings["number_in_season"] = (
        df_episodes["number_in_season"].values
        if "number_in_season" in df_episodes.columns
        else rng.integers(1, 25, n)
    )

    # Viewers: temporadas tempranas ~30M, baja en temporadas recientes ~5M
    base_viewers = np.clip(30 - (season - 1) * 0.7, 4, 30)
    ratings["viewers_millions"] = np.round(
        base_viewers + rng.normal(0, 2, n), 2
    ).clip(1.0, 40.0)

    # IMDB rating: media ~7.3, ligera caída en temporadas tardías
    base_rating = np.clip(8.0 - (season - 1) * 0.03, 6.0, 9.5)
    ratings["imdb_rating"] = np.round(
        base_rating + rng.normal(0, 0.5, n), 1
    ).clip(4.0, 10.0)

    # Duración: mayoría 22 min, algunos especiales 44 min
    ratings["duration_min"] = rng.choice([22, 22, 22, 22, 44], n)

    ratings.drop_duplicates(subset=["episode_id"], inplace=True)
    ratings.reset_index(drop=True, inplace=True)

    # ── Normalización MinMax [0, 1] de columnas numéricas ─────────────────────
    cols_normalizar = ["viewers_millions", "imdb_rating", "season",
                       "number_in_season", "duration_min"]
    scaler = MinMaxScaler()
    ratings[cols_normalizar] = np.round(
        scaler.fit_transform(ratings[cols_normalizar]), 6
    )

    print(f"Ratings generados y normalizados [0,1]: {len(ratings)}")
    print(f"  viewers_millions : [{ratings['viewers_millions'].min():.4f}, {ratings['viewers_millions'].max():.4f}]")
    print(f"  imdb_rating      : [{ratings['imdb_rating'].min():.4f}, {ratings['imdb_rating'].max():.4f}]")
    print(f"  season           : [{ratings['season'].min():.4f}, {ratings['season'].max():.4f}]")
    return ratings
