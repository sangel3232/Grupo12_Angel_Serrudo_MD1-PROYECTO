import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
"postgresql+psycopg2://postgres:1234@host.docker.internal:5432/Simpsons_db"
)
st.title("Simpsons Data Dashboard")

characters = pd.read_sql("SELECT * FROM dim_character", engine)
episodes = pd.read_sql("SELECT * FROM dim_episode", engine)

st.subheader("Characters")
st.dataframe(characters)

st.subheader("Gender Distribution")
st.bar_chart(characters['gender'].value_counts())

st.subheader("Episodes per Season")
st.bar_chart(episodes['season'].value_counts().sort_index())