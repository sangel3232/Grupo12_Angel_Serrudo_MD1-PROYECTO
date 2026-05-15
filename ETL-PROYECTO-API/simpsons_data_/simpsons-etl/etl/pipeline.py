from etl.extract import extract_characters, extract_episodes
from etl.transform import transform_characters, transform_episodes, transform_ratings
from etl.load import load_csv, load_postgres_bulk


def run_pipeline():
    print("🚀 Iniciando pipeline Simpsons ETL")

    # ── Extract ──────────────────────────────
    characters_raw = extract_characters()
    episodes_raw = extract_episodes()

    # ── Transform ────────────────────────────
    characters = transform_characters(characters_raw)
    episodes = transform_episodes(episodes_raw)
    ratings = transform_ratings(episodes)

    # ── Load CSV ─────────────────────────────
    load_csv(characters, "characters")
    load_csv(episodes, "episodes")
    load_csv(ratings, "ratings")

    # ── Load PostgreSQL (bulk insert) ─────────
    load_postgres_bulk(characters, "dim_characters", chunksize=500)
    load_postgres_bulk(episodes, "dim_episodes", chunksize=500)
    load_postgres_bulk(ratings, "fact_ratings", chunksize=500)

    print("✅ Pipeline terminado exitosamente")


if __name__ == "__main__":
    run_pipeline()
