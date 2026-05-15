-- ─────────────────────────────────────────────────────────────────────────────
-- Simpsons Data Warehouse — Schema
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_characters (
    character_id  INT PRIMARY KEY,
    name          TEXT,
    gender        TEXT,
    occupation    TEXT,
    status        TEXT
);

CREATE TABLE IF NOT EXISTS dim_episodes (
    episode_id        INT PRIMARY KEY,
    name              TEXT,
    season            INT,
    air_date          DATE,
    number_in_season  INT
);

-- Tabla de hechos para regresión lineal
-- viewers_millions e imdb_rating son las variables clave del modelo
CREATE TABLE IF NOT EXISTS fact_ratings (
    episode_id        INT PRIMARY KEY,
    season            NUMERIC(10, 6),
    number_in_season  NUMERIC(10, 6),
    viewers_millions  NUMERIC(10, 6),
    imdb_rating       NUMERIC(10, 6),
    duration_min      NUMERIC(10, 6)
);
