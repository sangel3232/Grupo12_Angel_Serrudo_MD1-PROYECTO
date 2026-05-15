from etl.extract import extract_characters, extract_episodes, extract_quotes
from etl.transform import transform_characters, transform_episodes, transform_quotes
from etl.load import load_table

def run_pipeline():

    print("Extrayendo datos...")

    characters = extract_characters()
    episodes = extract_episodes()
    quotes = extract_quotes()

    print("Transformando datos...")

    dim_character = transform_characters(characters)
    dim_episode = transform_episodes(episodes)
    fact_quotes = transform_quotes(quotes)

    print("Cargando en PostgreSQL...")

    load_table(dim_character,"dim_character")
    load_table(dim_episode,"dim_episode")
    load_table(fact_quotes,"fact_quotes")

    print("Pipeline terminado")