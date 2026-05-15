import psycopg2

conn = psycopg2.connect(host="localhost", port=5432, user="postgres", password="1234", dbname="Simpsons_db")
conn.autocommit = True
cur = conn.cursor()

schema = """
DROP TABLE IF EXISTS fact_ratings;
DROP TABLE IF EXISTS dim_episodes;
DROP TABLE IF EXISTS dim_characters;

CREATE TABLE dim_characters (
    character_id  INT PRIMARY KEY,
    name          TEXT,
    gender        TEXT,
    occupation    TEXT,
    status        TEXT
);

CREATE TABLE dim_episodes (
    episode_id        INT PRIMARY KEY,
    name              TEXT,
    season            INT,
    air_date          DATE,
    number_in_season  INT
);

CREATE TABLE fact_ratings (
    episode_id        INT PRIMARY KEY,
    season            NUMERIC(10, 6),
    number_in_season  NUMERIC(10, 6),
    viewers_millions  NUMERIC(10, 6),
    imdb_rating       NUMERIC(10, 6),
    duration_min      NUMERIC(10, 6)
);
"""

for stmt in [s.strip() for s in schema.split(";") if s.strip()]:
    cur.execute(stmt)
print("Schema aplicado correctamente")
cur.close()
conn.close()
