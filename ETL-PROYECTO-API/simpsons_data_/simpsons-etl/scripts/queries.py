"""
scripts/queries.py
──────────────────
Consultas a la base de datos con filtros por cada campo del proyecto.
También incluye un bulk insert de ejemplo ejecutable directamente.

Uso:
    python scripts/queries.py                  # ejecuta todas las queries
    python scripts/queries.py --bulk           # ejecuta bulk insert de prueba
    python scripts/queries.py --pipeline       # ejecuta el pipeline completo
"""

import argparse
import sys
import os

# Permite importar módulos del proyecto desde cualquier directorio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import text
from config.database import engine


# ─────────────────────────────────────────────────────────────────────────────
# QUERIES CON FILTROS — dim_characters
# ─────────────────────────────────────────────────────────────────────────────

def query_characters_by_gender(gender: str) -> pd.DataFrame:
    """Filtra personajes por género (ej: 'Male', 'Female')."""
    sql = text("SELECT * FROM dim_characters WHERE gender = :gender")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"gender": gender})
    print(f"[characters] género='{gender}' → {len(df)} registros")
    return df


def query_characters_by_occupation(occupation: str) -> pd.DataFrame:
    """Filtra personajes por ocupación (búsqueda parcial, case-insensitive)."""
    sql = text(
        "SELECT * FROM dim_characters "
        "WHERE occupation ILIKE :occ"
    )
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"occ": f"%{occupation}%"})
    print(f"[characters] ocupación LIKE '%{occupation}%' → {len(df)} registros")
    return df


def query_characters_by_status(status: str) -> pd.DataFrame:
    """Filtra personajes por estado (ej: 'Alive', 'Dead')."""
    sql = text("SELECT * FROM dim_characters WHERE status = :status")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"status": status})
    print(f"[characters] estado='{status}' → {len(df)} registros")
    return df


def query_characters_by_name(name: str) -> pd.DataFrame:
    """Busca personajes cuyo nombre contenga el texto dado."""
    sql = text(
        "SELECT * FROM dim_characters "
        "WHERE name ILIKE :name"
    )
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"name": f"%{name}%"})
    print(f"[characters] nombre LIKE '%{name}%' → {len(df)} registros")
    return df


def query_characters_by_id(character_id: int) -> pd.DataFrame:
    """Obtiene un personaje por su ID."""
    sql = text("SELECT * FROM dim_characters WHERE character_id = :cid")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"cid": character_id})
    print(f"[characters] character_id={character_id} → {len(df)} registros")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# QUERIES CON FILTROS — dim_episodes
# ─────────────────────────────────────────────────────────────────────────────

def query_episodes_by_season(season: int) -> pd.DataFrame:
    """Filtra episodios por número de temporada."""
    sql = text("SELECT * FROM dim_episodes WHERE season = :season ORDER BY episode_id")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"season": season})
    print(f"[episodes] temporada={season} → {len(df)} registros")
    return df


def query_episodes_by_name(name: str) -> pd.DataFrame:
    """Busca episodios cuyo nombre contenga el texto dado."""
    sql = text(
        "SELECT * FROM dim_episodes "
        "WHERE name ILIKE :name ORDER BY season, episode_id"
    )
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"name": f"%{name}%"})
    print(f"[episodes] nombre LIKE '%{name}%' → {len(df)} registros")
    return df


def query_episodes_by_air_date_range(start: str, end: str) -> pd.DataFrame:
    """Filtra episodios por rango de fecha de emisión (formato 'YYYY-MM-DD')."""
    sql = text(
        "SELECT * FROM dim_episodes "
        "WHERE air_date BETWEEN :start AND :end "
        "ORDER BY air_date"
    )
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"start": start, "end": end})
    print(f"[episodes] air_date entre {start} y {end} → {len(df)} registros")
    return df


def query_episodes_by_id(episode_id: int) -> pd.DataFrame:
    """Obtiene un episodio por su ID."""
    sql = text("SELECT * FROM dim_episodes WHERE episode_id = :eid")
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, params={"eid": episode_id})
    print(f"[episodes] episode_id={episode_id} → {len(df)} registros")
    return df


# ─────────────────────────────────────────────────────────────────────────────
# BULK INSERT DE PRUEBA
# ─────────────────────────────────────────────────────────────────────────────

def bulk_insert_sample_characters(n: int = 100) -> None:
    """
    Inserta n personajes de prueba en dim_characters usando bulk insert
    (method='multi') para máxima velocidad.
    """
    sample = pd.DataFrame(
        [
            {
                "character_id": 90000 + i,
                "name": f"Test Character {i}",
                "gender": "Male" if i % 2 == 0 else "Female",
                "occupation": "Test Occupation",
                "status": "Alive",
            }
            for i in range(n)
        ]
    )

    sample.to_sql(
        "dim_characters",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )
    print(f"✅ Bulk insert: {n} personajes de prueba insertados en dim_characters")


def bulk_insert_sample_episodes(n: int = 50) -> None:
    """
    Inserta n episodios de prueba en dim_episodes usando bulk insert.
    """
    sample = pd.DataFrame(
        [
            {
                "episode_id": 90000 + i,
                "name": f"Test Episode {i}",
                "season": (i % 35) + 1,
                "air_date": "2024-01-01",
            }
            for i in range(n)
        ]
    )

    sample.to_sql(
        "dim_episodes",
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=500,
    )
    print(f"✅ Bulk insert: {n} episodios de prueba insertados en dim_episodes")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def run_all_queries():
    print("\n═══════════════════════════════════════")
    print("  QUERIES — dim_characters")
    print("═══════════════════════════════════════")
    query_characters_by_gender("Male")
    query_characters_by_occupation("teacher")
    query_characters_by_status("Alive")
    query_characters_by_name("Homer")
    query_characters_by_id(1)

    print("\n═══════════════════════════════════════")
    print("  QUERIES — dim_episodes")
    print("═══════════════════════════════════════")
    query_episodes_by_season(1)
    query_episodes_by_name("Homer")
    query_episodes_by_air_date_range("1990-01-01", "1995-12-31")
    query_episodes_by_id(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simpsons DB Queries & Bulk Insert")
    parser.add_argument("--bulk", action="store_true", help="Ejecuta bulk insert de prueba")
    parser.add_argument("--pipeline", action="store_true", help="Ejecuta el pipeline ETL completo")
    args = parser.parse_args()

    if args.pipeline:
        from etl.pipeline import run_pipeline
        run_pipeline()
    elif args.bulk:
        bulk_insert_sample_characters(100)
        bulk_insert_sample_episodes(50)
    else:
        run_all_queries()
