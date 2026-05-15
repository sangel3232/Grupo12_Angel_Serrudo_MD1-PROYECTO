#!/usr/bin/env python3
"""
demo_data.py
────────────
Genera datos sintéticos enriquecidos para el análisis estadístico
y los carga en PostgreSQL usando bulk insert.

Tablas generadas:
  - dim_characters  (character_id, name, gender, occupation, status)
  - dim_episodes    (episode_id, name, season, air_date, number_in_season)
  - fact_ratings    (episode_id, viewers_millions, imdb_rating, duration_min)

Uso:
    python scripts/demo_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import date
from sqlalchemy import text
from config.database import engine

np.random.seed(42)

# ── Personajes de muestra ────────────────────────────────────────────────────
CHARACTERS = [
    (1,"Homer Simpson","Male","Safety Inspector","Alive"),
    (2,"Marge Simpson","Female","Unemployed","Alive"),
    (3,"Bart Simpson","Male","Student","Alive"),
    (4,"Lisa Simpson","Female","Student","Alive"),
    (5,"Maggie Simpson","Female","Unknown","Alive"),
    (6,"Ned Flanders","Male","The Leftorium","Alive"),
    (7,"Moe Szyslak","Male","Bartender","Alive"),
    (8,"Krusty the Clown","Male","TV Personality","Alive"),
    (9,"Mr. Burns","Male","Plant Owner","Alive"),
    (10,"Apu Nahasapeemapetilon","Male","Store Owner","Alive"),
    (11,"Milhouse Van Houten","Male","Student","Alive"),
    (12,"Nelson Muntz","Male","Student","Alive"),
    (13,"Ralph Wiggum","Male","Student","Alive"),
    (14,"Chief Wiggum","Male","Police Chief","Alive"),
    (15,"Sideshow Bob","Male","Criminal","Alive"),
    (16,"Edna Krabappel","Female","Teacher","Deceased"),
    (17,"Principal Skinner","Male","Principal","Alive"),
    (18,"Groundskeeper Willie","Male","Groundskeeper","Alive"),
    (19,"Barney Gumble","Male","Helicopter Pilot","Alive"),
    (20,"Lenny Leonard","Male","Technical Supervisor","Alive"),
]

# ── Episodios sintéticos (35 temporadas, ~700 episodios) ─────────────────────
def generar_episodios():
    rows = []
    ep_id = 1
    air = date(1989, 12, 17)
    for season in range(1, 36):
        n_eps = np.random.randint(18, 24)
        for ep_num in range(1, n_eps + 1):
            rows.append({
                "episode_id": ep_id,
                "name": f"Episode S{season:02d}E{ep_num:02d}",
                "season": season,
                "air_date": air,
                "number_in_season": ep_num,
            })
            ep_id += 1
            air = date(air.year + (1 if air.month == 12 else 0),
                       (air.month % 12) + 1, air.day)
    return pd.DataFrame(rows)


# ── Ratings sintéticos (variable objetivo para regresión) ────────────────────
def generar_ratings(episodes_df: pd.DataFrame) -> pd.DataFrame:
    n = len(episodes_df)
    season = episodes_df["season"].values

    # viewers ~ 30 - 0.5*season + ruido  (declive histórico real)
    viewers = np.clip(30 - 0.5 * season + np.random.normal(0, 2, n), 2, 35)

    # imdb_rating ~ 7.5 + 0.02*(season<=10) - 0.01*season + ruido
    imdb = np.clip(
        7.5 + 0.3 * (season <= 10).astype(float)
        - 0.01 * season
        + np.random.normal(0, 0.4, n),
        4.0, 10.0,
    )

    # duration_min ~ 22 ± 2
    duration = np.clip(np.random.normal(22, 1.5, n), 18, 28)

    # number_in_season
    ep_num = episodes_df["number_in_season"].values

    return pd.DataFrame({
        "episode_id": episodes_df["episode_id"].values,
        "viewers_millions": viewers.round(2),
        "imdb_rating": imdb.round(2),
        "duration_min": duration.round(1),
        "season": season,
        "number_in_season": ep_num,
    })


def create_ratings_table():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS fact_ratings (
                id              SERIAL PRIMARY KEY,
                episode_id      INT,
                viewers_millions FLOAT,
                imdb_rating     FLOAT,
                duration_min    FLOAT,
                season          INT,
                number_in_season INT
            )
        """))


def truncate_if_exists(table: str):
    with engine.begin() as conn:
        exists = conn.execute(text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name=:t)"
        ), {"t": table}).scalar()
        if exists:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))


def main():
    print("Generando datos demo...")

    # Personajes
    df_chars = pd.DataFrame(CHARACTERS, columns=["character_id","name","gender","occupation","status"])
    truncate_if_exists("dim_characters")
    df_chars.to_sql("dim_characters", engine, if_exists="append", index=False, method="multi")
    print(f"  dim_characters: {len(df_chars)} registros")

    # Episodios
    df_eps = generar_episodios()
    truncate_if_exists("dim_episodes")
    df_eps.to_sql("dim_episodes", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"  dim_episodes: {len(df_eps)} registros")

    # Ratings
    create_ratings_table()
    df_rat = generar_ratings(df_eps)
    truncate_if_exists("fact_ratings")
    df_rat.to_sql("fact_ratings", engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"  fact_ratings: {len(df_rat)} registros")

    print("\n✅ Datos demo cargados correctamente")


if __name__ == "__main__":
    main()
