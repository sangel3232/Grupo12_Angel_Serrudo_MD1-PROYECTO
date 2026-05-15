import streamlit as st
import pandas as pd
from config.database import engine

st.set_page_config(page_title="Simpsons Dashboard", page_icon="📺", layout="wide")
st.title("📺 Simpsons Data Dashboard")

# ── Personajes ───────────────────────────────────────────────────────────────
st.subheader("Personajes")

try:
    df_chars = pd.read_sql("SELECT * FROM dim_characters", engine)

    # Filtros interactivos
    col1, col2 = st.columns(2)
    with col1:
        gender_filter = st.multiselect(
            "Filtrar por género",
            options=df_chars["gender"].dropna().unique().tolist(),
        )
    with col2:
        status_filter = st.multiselect(
            "Filtrar por estado",
            options=df_chars["status"].dropna().unique().tolist() if "status" in df_chars.columns else [],
        )

    filtered = df_chars.copy()
    if gender_filter:
        filtered = filtered[filtered["gender"].isin(gender_filter)]
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    st.dataframe(filtered, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Personajes por género")
        st.bar_chart(filtered["gender"].value_counts())
    with col4:
        st.subheader("Top 10 ocupaciones")
        st.bar_chart(filtered["occupation"].value_counts().head(10))

except Exception as e:
    st.error(f"Error al cargar personajes: {e}")

# ── Episodios ────────────────────────────────────────────────────────────────
st.subheader("Episodios")

try:
    df_eps = pd.read_sql("SELECT * FROM dim_episodes", engine)

    season_filter = st.multiselect(
        "Filtrar por temporada",
        options=sorted(df_eps["season"].dropna().unique().tolist()) if "season" in df_eps.columns else [],
    )

    filtered_eps = df_eps.copy()
    if season_filter:
        filtered_eps = filtered_eps[filtered_eps["season"].isin(season_filter)]

    st.dataframe(filtered_eps, use_container_width=True)

    if "season" in filtered_eps.columns:
        st.subheader("Episodios por temporada")
        st.bar_chart(filtered_eps["season"].value_counts().sort_index())

except Exception as e:
    st.error(f"Error al cargar episodios: {e}")
