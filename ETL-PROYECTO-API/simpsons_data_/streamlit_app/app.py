import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="Simpsons Data Dashboard", layout="wide")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = os.getenv(
        "STREAMLIT_DATABASE_URL",
        "postgresql://postgres:1234@localhost:5432/Simpsons_db",
    )

engine = create_engine(DATABASE_URL)

st.title("Simpsons Data Dashboard")

@st.cache_data(ttl=300)
def load_data(query: str) -> pd.DataFrame:
    return pd.read_sql(query, engine)

try:
    characters = load_data("SELECT * FROM dim_characters")
    episodes = load_data("SELECT * FROM dim_episodes")

    st.subheader("Characters")
    st.dataframe(characters)

    st.subheader("Gender Distribution")
    st.bar_chart(characters["gender"].value_counts())

    st.subheader("Episodes per Season")
    st.bar_chart(episodes["season"].value_counts().sort_index())

except Exception as e:
    st.error("Database connection error:")
    st.exception(e)
    st.markdown(
        "---\n"
        "### Solución rápida\n"
        "1. Usa `DATABASE_URL` en el entorno de despliegue de Streamlit.\n"
        "2. Si estás usando Docker local, define `DATABASE_URL` o `STREAMLIT_DATABASE_URL`.\n"
        "3. Asegúrate de que las tablas `dim_characters` y `dim_episodes` existen."
    )