import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://thesimpsonsapi.com/api")


def extract_all(endpoint: str) -> pd.DataFrame:
    url = f"{BASE_URL}/{endpoint}"
    all_data = []

    print(f"Extrayendo {endpoint}...")

    while url:
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            raise Exception(
                f"Error al conectar con la API [{endpoint}]: "
                f"HTTP {response.status_code}"
            )

        data = response.json()

        results = data.get("results", [])
        all_data.extend(results)

        # Paginación: "next" puede ser null/None cuando no hay más páginas
        url = data.get("next") or None

    df = pd.json_normalize(all_data)
    print(f"Total registros descargados [{endpoint}]: {len(df)}")
    return df


def extract_characters() -> pd.DataFrame:
    return extract_all("characters")


def extract_episodes() -> pd.DataFrame:
    return extract_all("episodes")
