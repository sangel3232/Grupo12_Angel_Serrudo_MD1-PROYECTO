import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DOTENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(DOTENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

    if all([db_host, db_port, db_name, db_user, db_password]):
        DATABASE_URL = (
            f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
    else:
        missing = [
            key
            for key, value in [
                ("DB_HOST", db_host),
                ("DB_PORT", db_port),
                ("DB_NAME", db_name),
                ("DB_USER", db_user),
                ("DB_PASSWORD", db_password),
            ]
            if not value
        ]
        raise ValueError(
            "DATABASE_URL no está definida en el archivo .env. "
            f"Asegúrate de que {DOTENV_PATH} existe y contiene DATABASE_URL "
            "o las variables DB_HOST, DB_PORT, DB_NAME, DB_USER y DB_PASSWORD. "
            f"Faltan: {', '.join(missing)}."
        )

if any(token in DATABASE_URL for token in [
    "[tu-project-ref]",
    "[tu-password]",
    "postgres.[tu-project-ref]",
    "postgres.[tu-password]",
]):
    raise ValueError(
        "DATABASE_URL contiene valores de marcador de posición. "
        "Reemplaza [tu-project-ref] y [tu-password] en el archivo .env con las credenciales reales de Supabase."
    )

is_supabase = "pooler.supabase.com" in DATABASE_URL.lower()
engine = create_engine(
    DATABASE_URL,
    connect_args={"options": "-c statement_timeout=30000"} if is_supabase else {},
    pool_pre_ping=True,
)
