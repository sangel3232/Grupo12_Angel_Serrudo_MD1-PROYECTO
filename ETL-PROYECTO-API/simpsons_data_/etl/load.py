import pandas as pd
import requests
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:1234@simpsons_postgres:5432/Simpsons_db")

# API Simpsons
url = "https://api.sampleapis.com/simpsons/characters"
data = requests.get(url).json()

df = pd.json_normalize(data)

# seleccionar columnas
df_characters = df[['name', 'gender', 'occupation']]

df_characters.to_sql(
    "dim_character",
    engine,
    if_exists="replace",
    index=False
)

print("ETL completed successfully")