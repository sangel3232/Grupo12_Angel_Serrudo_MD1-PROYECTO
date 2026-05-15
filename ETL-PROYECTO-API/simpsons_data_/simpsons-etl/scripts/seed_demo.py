"""
Inserta datos de demo en dim_characters, dim_episodes y fact_ratings
para poder ver el dashboard sin esperar el pipeline completo.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config.database import engine

rng = np.random.default_rng(42)

# ── Personajes ────────────────────────────────────────────────────────────────
characters = pd.DataFrame([
    {"character_id": 1,  "name": "Homer Simpson",   "gender": "Male",   "occupation": "Nuclear Safety Inspector", "status": "Alive"},
    {"character_id": 2,  "name": "Marge Simpson",   "gender": "Female", "occupation": "Housewife",                "status": "Alive"},
    {"character_id": 3,  "name": "Bart Simpson",    "gender": "Male",   "occupation": "Student",                  "status": "Alive"},
    {"character_id": 4,  "name": "Lisa Simpson",    "gender": "Female", "occupation": "Student",                  "status": "Alive"},
    {"character_id": 5,  "name": "Maggie Simpson",  "gender": "Female", "occupation": "Baby",                     "status": "Alive"},
    {"character_id": 6,  "name": "Ned Flanders",    "gender": "Male",   "occupation": "Store Owner",              "status": "Alive"},
    {"character_id": 7,  "name": "Mr. Burns",       "gender": "Male",   "occupation": "CEO",                      "status": "Alive"},
    {"character_id": 8,  "name": "Apu Nahasapeemapetilon", "gender": "Male", "occupation": "Store Owner",         "status": "Alive"},
    {"character_id": 9,  "name": "Krusty the Clown","gender": "Male",   "occupation": "Entertainer",              "status": "Alive"},
    {"character_id": 10, "name": "Sideshow Bob",    "gender": "Male",   "occupation": "Criminal",                 "status": "Alive"},
    {"character_id": 11, "name": "Chief Wiggum",    "gender": "Male",   "occupation": "Police Chief",             "status": "Alive"},
    {"character_id": 12, "name": "Milhouse Van Houten", "gender": "Male", "occupation": "Student",               "status": "Alive"},
    {"character_id": 13, "name": "Nelson Muntz",    "gender": "Male",   "occupation": "Student",                  "status": "Alive"},
    {"character_id": 14, "name": "Moe Szyslak",     "gender": "Male",   "occupation": "Bartender",                "status": "Alive"},
    {"character_id": 15, "name": "Patty Bouvier",   "gender": "Female", "occupation": "DMV Employee",             "status": "Alive"},
    {"character_id": 16, "name": "Selma Bouvier",   "gender": "Female", "occupation": "DMV Employee",             "status": "Alive"},
    {"character_id": 17, "name": "Principal Skinner","gender": "Male",  "occupation": "Principal",                "status": "Alive"},
    {"character_id": 18, "name": "Groundskeeper Willie", "gender": "Male", "occupation": "Groundskeeper",        "status": "Alive"},
    {"character_id": 19, "name": "Comic Book Guy",  "gender": "Male",   "occupation": "Store Owner",              "status": "Alive"},
    {"character_id": 20, "name": "Snake Jailbird",  "gender": "Male",   "occupation": "Criminal",                 "status": "Alive"},
])

# ── Episodios (10 por temporada, 35 temporadas = 350 episodios) ───────────────
eps_rows = []
ep_id = 1
for season in range(1, 36):
    for num in range(1, 11):
        eps_rows.append({
            "episode_id": ep_id,
            "name": f"Episodio S{season:02d}E{num:02d}",
            "season": season,
            "air_date": f"{1989 + season}-01-{num:02d}",
            "number_in_season": num,
        })
        ep_id += 1

episodes = pd.DataFrame(eps_rows)

# ── Ratings ───────────────────────────────────────────────────────────────────
seasons = episodes["season"].values
base_viewers = np.clip(30 - (seasons - 1) * 0.7, 4, 30)
base_rating  = np.clip(8.0 - (seasons - 1) * 0.03, 6.0, 9.5)

ratings = pd.DataFrame({
    "episode_id":       episodes["episode_id"].values,
    "season":           seasons,
    "number_in_season": episodes["number_in_season"].values,
    "viewers_millions": np.round(base_viewers + rng.normal(0, 2, len(episodes)), 2).clip(1.0, 40.0),
    "imdb_rating":      np.round(base_rating  + rng.normal(0, 0.5, len(episodes)), 1).clip(4.0, 10.0),
    "duration_min":     rng.choice([22, 22, 22, 22, 44], len(episodes)),
})

# ── Cargar ────────────────────────────────────────────────────────────────────
for df, table in [(characters, "dim_characters"), (episodes, "dim_episodes"), (ratings, "fact_ratings")]:
    with engine.begin() as conn:
        from sqlalchemy import text
        conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE" if table != "fact_ratings" else f"TRUNCATE TABLE {table}"))
    df.to_sql(table, engine, if_exists="append", index=False, method="multi", chunksize=500)
    print(f"✅ {table}: {len(df)} registros insertados")

print("\n🎉 Demo data lista. Corre: venv\\Scripts\\streamlit.exe run dashboard/app.py")
