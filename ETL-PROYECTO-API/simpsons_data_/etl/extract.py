import requests
import pandas as pd

BASE_URL = "https://thesimpsonsapi.com/api"


def extract_characters():

    print("Extrayendo personajes...")

    url = f"{BASE_URL}/characters"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error al conectar con la API")

    data = response.json()

    df = pd.json_normalize(data)

    print(f"Personajes descargados: {len(df)}")

    return df


def extract_episodes():

    print("Extrayendo episodios...")

    url = f"{BASE_URL}/episodes"

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Error al conectar con la API")

    data = response.json()

    df = pd.json_normalize(data)

    print(f"Episodios descargados: {len(df)}")

    return df