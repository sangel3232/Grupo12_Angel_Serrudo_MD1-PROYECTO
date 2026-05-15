import os
import pandas as pd
from sqlalchemy import text
from config.database import engine


def load_csv(df: pd.DataFrame, filename: str) -> None:
    os.makedirs("data", exist_ok=True)
    path = f"data/{filename}.csv"
    df.to_csv(path, index=False)
    print(f"CSV guardado en {path}")


def load_postgres_bulk(df: pd.DataFrame, table: str, chunksize: int = 1000) -> None:
    """
    Bulk insert usando method='multi' + chunksize para máxima velocidad.
    Crea la tabla si no existe; no borra datos previos (append).
    Para reinsertar desde cero usa truncate=True.
    """
    if df.empty:
        print(f"DataFrame vacío, se omite carga de {table}")
        return

    # Crear tabla si no existe (primera carga)
    with engine.begin() as conn:
        existing = conn.execute(
            text(
                "SELECT EXISTS ("
                "  SELECT 1 FROM information_schema.tables"
                "  WHERE table_name = :t"
                ")"
            ),
            {"t": table},
        ).scalar()

        if existing:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
            print(f"Tabla {table} truncada antes de la carga")

    df.to_sql(
        table,
        engine,
        if_exists="append",   # append porque ya truncamos arriba (o es nueva)
        index=False,
        method="multi",       # bulk insert — envía múltiples filas por statement
        chunksize=chunksize,
    )

    print(f"✅ Tabla '{table}' cargada con {len(df)} registros (bulk, chunksize={chunksize})")


# Alias para compatibilidad con código anterior
def load_postgres(df: pd.DataFrame, table: str) -> None:
    load_postgres_bulk(df, table)
