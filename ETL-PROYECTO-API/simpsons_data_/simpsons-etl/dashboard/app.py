import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
import warnings
warnings.filterwarnings("ignore")

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Los Simpsons",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

import base64

def get_bg_base64():
    bg_path = os.path.join(os.path.dirname(__file__), "bg.jpg")
    with open(bg_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_b64 = get_bg_base64()

st.markdown(f"""
<style>
.stApp {{
    background-image: url("data:image/jpg;base64,{bg_b64}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.30);
    z-index: 0;
}}
.block-container {{
    position: relative;
    z-index: 1;
    background: rgba(0, 0, 0, 0.20);
    border-radius: 12px;
    padding: 2rem;
}}
[data-testid="stSidebar"] {{
    background: rgba(15, 15, 40, 0.92) !important;
    border-right: 2px solid #FED90F;
}}
h1, h2, h3 {{
    color: #FED90F !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
}}
p, label, .stMarkdown {{
    color: #FFFFFF !important;
}}
[data-testid="stMetricValue"] {{
    color: #FED90F !important;
    font-size: 1.8rem !important;
}}
[data-testid="stMetricLabel"] {{
    color: #CCCCCC !important;
}}
.stDownloadButton > button {{
    background-color: #FED90F !important;
    color: #000000 !important;
    font-weight: bold;
    border-radius: 8px;
    border: none;
}}
.stDownloadButton > button:hover {{
    background-color: #f0c800 !important;
}}
</style>
""", unsafe_allow_html=True)

# ── Mapas de traducción de columnas ──────────────────────────────────────────
COLS_PERSONAJES = {
    "character_id": "ID",
    "name": "Nombre",
    "gender": "Género",
    "occupation": "Ocupación",
    "status": "Estado",
}
COLS_EPISODIOS = {
    "episode_id": "ID",
    "name": "Título",
    "season": "Temporada",
    "air_date": "Fecha de emisión",
    "number_in_season": "N° en temporada",
}
COLS_RATINGS = {
    "episode_id": "ID episodio",
    "season": "Temporada",
    "number_in_season": "N° en temporada",
    "viewers_millions": "Audiencia (millones)",
    "imdb_rating": "Rating IMDB",
    "duration_min": "Duración (min)",
}
GENERO_ES = {"Male": "Masculino", "Female": "Femenino", "Unknown": "Desconocido"}
ESTADO_ES = {"Alive": "Vivo/a", "Dead": "Fallecido/a", "Unknown": "Desconocido"}

# ── Conexión a BD ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    try:
        from sqlalchemy import create_engine as _ce
        db_url = st.secrets.get("DATABASE_URL", None)
        if db_url:
            return _ce(db_url, pool_pre_ping=True)
    except Exception:
        pass
    from config.database import engine
    return engine

engine = get_engine()

# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_characters():
    df = pd.read_sql("SELECT * FROM dim_characters", engine)
    df["gender"]     = df["gender"].map(GENERO_ES).fillna(df["gender"])
    df["status"]     = df["status"].map(ESTADO_ES).fillna(df["status"])
    return df.rename(columns=COLS_PERSONAJES)

@st.cache_data(ttl=300)
def load_episodes():
    df = pd.read_sql("SELECT * FROM dim_episodes", engine)
    df["air_date"] = df["air_date"].fillna("No disponible")
    return df.rename(columns=COLS_EPISODIOS)

@st.cache_data(ttl=300)
def load_ratings():
    return pd.read_sql("SELECT * FROM fact_ratings", engine).rename(columns=COLS_RATINGS)

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bc/The_Simpsons_Logo.svg/320px-The_Simpsons_Logo.svg.png",
    use_container_width=True,
)
st.sidebar.markdown("""
<div style="text-align:center; font-size:80px; line-height:1; margin: -10px 0 10px 0;
     filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.6));">
    🍩
</div>
<div style="text-align:center; color:#FED90F; font-size:13px; margin-bottom:12px;
     font-style:italic; text-shadow:1px 1px 3px black;">
    "¡Mmm... donas!"
</div>
""", unsafe_allow_html=True)
st.sidebar.title("Navegación")
seccion = st.sidebar.radio(
    "Ir a",
    ["📊 Estadísticas", "👥 Personajes", "📺 Episodios",
     "🤖 Regresión Lineal", "🌳 Árboles y Clasificación", "📥 Datos"],
)

# ── Carga global ──────────────────────────────────────────────────────────────
try:
    df_chars = load_characters()
    df_eps   = load_episodes()
    df_rat   = load_ratings()
except Exception as e:
    st.error(f"❌ No se pudo conectar a la base de datos: {e}")
    st.info("Asegúrate de que DATABASE_URL está configurado en `.env` o en los Secrets de Streamlit Cloud.")
    st.stop()

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — ESTADÍSTICAS GENERALES
# ═════════════════════════════════════════════════════════════════════════════
if seccion == "📊 Estadísticas":
    st.title("📊 Estadísticas Generales — Los Simpsons")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de personajes", len(df_chars))
    col2.metric("Total de episodios", len(df_eps))
    col3.metric("Temporadas", int(df_eps["Temporada"].max()) if "Temporada" in df_eps.columns else "—")
    col4.metric("Rating IMDB promedio", f"{df_rat['Rating IMDB'].mean():.2f}" if not df_rat.empty else "—")

    st.divider()

    if not df_rat.empty and "Temporada" in df_rat.columns:
        avg_rating = df_rat.groupby("Temporada")["Rating IMDB"].mean().reset_index()
        fig = px.line(
            avg_rating, x="Temporada", y="Rating IMDB",
            title="Rating IMDB promedio por temporada",
            labels={"Temporada": "Temporada", "Rating IMDB": "Rating IMDB promedio"},
            markers=True, color_discrete_sequence=["#FED90F"],
        )
        fig.update_layout(plot_bgcolor="#1a1a2e", paper_bgcolor="#1a1a2e", font_color="white")
        st.plotly_chart(fig, use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if "Audiencia (millones)" in df_rat.columns:
            avg_viewers = df_rat.groupby("Temporada")["Audiencia (millones)"].mean().reset_index()
            fig2 = px.bar(
                avg_viewers, x="Temporada", y="Audiencia (millones)",
                title="Audiencia promedio por temporada (millones de espectadores)",
                labels={"Temporada": "Temporada", "Audiencia (millones)": "Millones de espectadores"},
                color="Audiencia (millones)", color_continuous_scale="YlOrRd",
            )
            fig2.update_layout(coloraxis_colorbar_title="Millones")
            st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        fig3 = px.histogram(
            df_rat, x="Rating IMDB", nbins=20,
            title="Distribución de ratings IMDB de todos los episodios",
            labels={"Rating IMDB": "Rating IMDB", "count": "Cantidad de episodios"},
            color_discrete_sequence=["#FED90F"],
        )
        fig3.update_layout(yaxis_title="Cantidad de episodios")
        st.plotly_chart(fig3, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — PERSONAJES
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "👥 Personajes":
    st.title("👥 Personajes de Los Simpsons")

    col1, col2 = st.columns(2)
    with col1:
        genero_opts = df_chars["Género"].dropna().unique().tolist()
        genero_filter = st.multiselect("Filtrar por género", options=genero_opts)
    with col2:
        estado_opts = df_chars["Estado"].dropna().unique().tolist() if "Estado" in df_chars.columns else []
        estado_filter = st.multiselect("Filtrar por estado", options=estado_opts)

    filtrado = df_chars.copy()
    if genero_filter:
        filtrado = filtrado[filtrado["Género"].isin(genero_filter)]
    if estado_filter:
        filtrado = filtrado[filtrado["Estado"].isin(estado_filter)]

    st.markdown(f"**{len(filtrado)} personajes encontrados**")
    st.dataframe(filtrado, use_container_width=True, hide_index=True)

    col3, col4 = st.columns(2)
    with col3:
        conteo_genero = filtrado["Género"].value_counts().reset_index()
        conteo_genero.columns = ["Género", "Cantidad"]
        fig = px.bar(
            conteo_genero, x="Género", y="Cantidad",
            title="Cantidad de personajes por género",
            color="Género", color_discrete_sequence=px.colors.qualitative.Set2,
            labels={"Género": "Género", "Cantidad": "Cantidad de personajes"},
        )
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        top_occ = filtrado["Ocupación"].value_counts().head(10).reset_index()
        top_occ.columns = ["Ocupación", "Cantidad"]
        fig2 = px.bar(
            top_occ, x="Cantidad", y="Ocupación", orientation="h",
            title="Top 10 ocupaciones más frecuentes",
            labels={"Ocupación": "Ocupación", "Cantidad": "Cantidad de personajes"},
            color_discrete_sequence=["#FED90F"],
        )
        st.plotly_chart(fig2, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — EPISODIOS
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "📺 Episodios":
    st.title("📺 Episodios de Los Simpsons")

    temp_opts = sorted(df_eps["Temporada"].dropna().unique().tolist()) if "Temporada" in df_eps.columns else []
    temp_filter = st.multiselect("Filtrar por temporada", options=temp_opts)

    filtrado_eps = df_eps.copy()
    if temp_filter:
        filtrado_eps = filtrado_eps[filtrado_eps["Temporada"].isin(temp_filter)]

    st.markdown(f"**{len(filtrado_eps)} episodios encontrados**")
    st.dataframe(filtrado_eps, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        if "Temporada" in filtrado_eps.columns:
            conteo_eps = filtrado_eps["Temporada"].value_counts().sort_index().reset_index()
            conteo_eps.columns = ["Temporada", "Episodios"]
            fig = px.bar(
                conteo_eps, x="Temporada", y="Episodios",
                title="Cantidad de episodios por temporada",
                labels={"Temporada": "Temporada", "Episodios": "Cantidad de episodios"},
                color_discrete_sequence=["#FED90F"],
            )
            st.plotly_chart(fig, use_container_width=True)
    with col2:
        if not df_rat.empty:
            rat_renamed = df_rat.rename(columns={"ID episodio": "ID"})
            eps_renamed = filtrado_eps.rename(columns={"ID": "ID"})
            merged = eps_renamed.merge(
                rat_renamed[["ID", "Rating IMDB", "Audiencia (millones)"]],
                on="ID", how="left"
            )
            if "Rating IMDB" in merged.columns:
                fig2 = px.scatter(
                    merged, x="Temporada", y="Rating IMDB",
                    title="Rating IMDB por episodio según temporada",
                    labels={"Temporada": "Temporada", "Rating IMDB": "Rating IMDB"},
                    hover_data=["Título"] if "Título" in merged.columns else None,
                    color="Rating IMDB", color_continuous_scale="RdYlGn",
                )
                fig2.update_layout(coloraxis_colorbar_title="Rating")
                st.plotly_chart(fig2, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — REGRESIÓN LINEAL
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "🤖 Regresión Lineal":
    st.title("🤖 Modelo de Regresión Lineal")
    st.markdown(
        "**Variable objetivo:** Rating IMDB del episodio  \n"
        "**Variables predictoras:** Audiencia (millones), Temporada, Duración (min), N° en temporada"
    )

    if df_rat.empty:
        st.warning("No hay datos disponibles. Ejecuta el pipeline primero.")
        st.stop()

    # df_rat ya tiene columnas en español gracias al rename en load_ratings()
    # Solo verificamos que existan
    FEATURES_ES = [c for c in ["Audiencia (millones)", "Temporada", "Duración (min)", "N° en temporada"] if c in df_rat.columns]
    TARGET_ES = "Rating IMDB"
    df_modelo = df_rat

    df_model = df_modelo[FEATURES_ES + [TARGET_ES]].dropna()

    if len(df_model) < 10:
        st.warning("Datos insuficientes para entrenar el modelo.")
        st.stop()

    X = df_model[FEATURES_ES]
    y = df_model[TARGET_ES]

    st.sidebar.subheader("⚙️ Parámetros del modelo")
    test_size    = st.sidebar.slider("Proporción de datos de prueba", 0.1, 0.4, 0.2, 0.05,
                                     help="Porcentaje de datos usados para evaluar el modelo")
    random_state = st.sidebar.number_input("Semilla aleatoria", value=42, step=1,
                                           help="Controla la reproducibilidad del experimento")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=int(random_state))
    scaler       = StandardScaler()
    X_train_sc   = scaler.fit_transform(X_train)
    X_test_sc    = scaler.transform(X_test)

    # Mejor predictor simple
    mejor_pred = X.corrwith(y).abs().idxmax()
    reg_simple = LinearRegression()
    reg_simple.fit(X_train[[mejor_pred]], y_train)
    y_pred_simple = reg_simple.predict(X_test[[mejor_pred]])

    # Modelo múltiple
    reg_mult = LinearRegression()
    reg_mult.fit(X_train_sc, y_train)
    y_pred_mult = reg_mult.predict(X_test_sc)

    def metricas(y_true, y_pred, nombre):
        return {
            "Modelo": nombre,
            "R² (coef. determinación)": round(r2_score(y_true, y_pred), 4),
            "RMSE (error cuadrático medio)": round(np.sqrt(mean_squared_error(y_true, y_pred)), 4),
            "MAE (error absoluto medio)": round(mean_absolute_error(y_true, y_pred), 4),
        }

    tabla = pd.DataFrame([
        metricas(y_test, y_pred_simple, f"Simple — {mejor_pred}"),
        metricas(y_test, y_pred_mult,   "Múltiple — todas las variables"),
    ])

    st.subheader("📋 Comparación de modelos")
    st.caption("R² más alto y RMSE/MAE más bajos indican mejor desempeño del modelo")
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    col1, col2, col3 = st.columns(3)
    metricas_cols = ["R² (coef. determinación)", "RMSE (error cuadrático medio)", "MAE (error absoluto medio)"]
    titulos = ["R² — Coeficiente de determinación", "RMSE — Error cuadrático medio", "MAE — Error absoluto medio"]
    for col, met, tit in zip([col1, col2, col3], metricas_cols, titulos):
        fig = go.Figure(go.Bar(
            x=["Modelo Simple", "Modelo Múltiple"],
            y=tabla[met],
            marker_color=["#2196F3", "#4CAF50"],
            text=tabla[met], textposition="outside",
        ))
        fig.update_layout(title=tit, yaxis_title="Valor", showlegend=False,
                          height=320, margin=dict(t=50, b=20))
        col.plotly_chart(fig, use_container_width=True)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader(f"Regresión Simple: Rating IMDB ~ {mejor_pred}")
        st.caption("Línea roja = recta de regresión ajustada")
        fig_s = px.scatter(
            x=X_test[mejor_pred], y=y_test,
            labels={"x": mejor_pred, "y": "Rating IMDB real"},
            opacity=0.5, color_discrete_sequence=["#2196F3"],
        )
        x_line = np.linspace(X_test[mejor_pred].min(), X_test[mejor_pred].max(), 100)
        m = reg_simple.coef_[0]; b_int = reg_simple.intercept_
        fig_s.add_scatter(x=x_line, y=m * x_line + b_int, mode="lines",
                          line=dict(color="red", width=2), name="Línea de regresión")
        fig_s.update_layout(legend_title="")
        st.plotly_chart(fig_s, use_container_width=True)

    with col_b:
        st.subheader("Rating real vs Rating Predicción — Modelo Múltiple")
        st.caption("Puntos sobre la línea roja = predicción perfecta")
        fig_m = px.scatter(
            x=y_test, y=y_pred_mult,
            labels={"x": "Rating IMDB real", "y": "Rating IMDB Predicción"},
            opacity=0.5, color_discrete_sequence=["#4CAF50"],
        )
        lim = [min(y_test.min(), y_pred_mult.min()), max(y_test.max(), y_pred_mult.max())]
        fig_m.add_scatter(x=lim, y=lim, mode="lines",
                          line=dict(color="red", dash="dash"), name="Predicción perfecta")
        fig_m.update_layout(legend_title="")
        st.plotly_chart(fig_m, use_container_width=True)

    st.subheader("Importancia de cada variable en el modelo múltiple")
    st.caption("Variables con coeficiente positivo aumentan el rating; negativo lo disminuyen")
    coef_df = pd.DataFrame({
        "Variable": FEATURES_ES,
        "Coeficiente estandarizado": reg_mult.coef_,
    }).sort_values("Coeficiente estandarizado")

    fig_coef = px.bar(
        coef_df, x="Coeficiente estandarizado", y="Variable", orientation="h",
        color="Coeficiente estandarizado", color_continuous_scale="RdYlGn",
        title="Coeficientes del modelo (estandarizados)",
        labels={"Coeficiente estandarizado": "Coeficiente", "Variable": "Variable predictora"},
    )
    fig_coef.add_vline(x=0, line_dash="dash", line_color="white")
    fig_coef.update_layout(coloraxis_colorbar_title="Valor")
    st.plotly_chart(fig_coef, use_container_width=True)

    st.divider()
    st.subheader("🔮 Predictor interactivo de Rating IMDB")
    st.markdown("Ajusta los valores y el modelo estimará el rating del episodio:")

    pred_cols = st.columns(len(FEATURES_ES))
    input_vals = {}
    defaults = {
        "Audiencia (millones)": float(df_rat["Audiencia (millones)"].mean()),
        "Temporada": int(df_rat["Temporada"].median()),
        "Duración (min)": 22,
        "N° en temporada": 10,
    }
    etiquetas = {
        "Audiencia (millones)": "Audiencia (millones)",
        "Temporada": "Temporada (1-35)",
        "Duración (min)": "Duración del episodio",
        "N° en temporada": "Número en la temporada",
    }
    for col, feat in zip(pred_cols, FEATURES_ES):
        if feat == "Duración (min)":
            input_vals[feat] = col.selectbox(etiquetas[feat], [22, 44], index=0,
                                              help="22 min = episodio normal, 44 min = especial")
        elif feat == "Temporada":
            input_vals[feat] = col.slider(etiquetas[feat], 1, 35, defaults.get(feat, 1))
        elif feat == "N° en temporada":
            input_vals[feat] = col.slider(etiquetas[feat], 1, 25, defaults.get(feat, 10))
        else:
            input_vals[feat] = col.number_input(etiquetas[feat], value=float(defaults.get(feat, 0.0)), step=0.5,
                                                 help="Millones de espectadores que vieron el episodio")

    X_input    = pd.DataFrame([input_vals])[FEATURES_ES]
    X_input_sc = scaler.transform(X_input)
    pred_rating = float(np.clip(reg_mult.predict(X_input_sc)[0], 1.0, 10.0))

    col_res1, col_res2 = st.columns([1, 3])
    col_res1.metric("⭐ Rating IMDB estimado", f"{pred_rating:.2f} / 10")
    if pred_rating >= 8.0:
        col_res2.success("🟢 Episodio con rating alto — muy bien recibido por la audiencia")
    elif pred_rating >= 6.5:
        col_res2.info("🟡 Episodio con rating medio — aceptable para la audiencia")
    else:
        col_res2.warning("🔴 Episodio con rating bajo — poco valorado por la audiencia")

# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — ÁRBOLES Y CLASIFICACIÓN
# ═════════════════════════════════════════════════════════════════════════════
elif seccion == "🌳 Árboles y Clasificación":
    st.title("🌳 Árboles de Decisión y Clasificación Binaria")

    if df_rat.empty:
        st.warning("No hay datos disponibles. Ejecuta el pipeline primero.")
        st.stop()

    FEATURES_ES = [c for c in ["Audiencia (millones)", "Temporada", "Duración (min)", "N° en temporada"] if c in df_rat.columns]
    UMBRAL = 7.5

    df_modelo = df_rat.copy()
    df_modelo["Rating alto"] = (df_modelo["Rating IMDB"] >= UMBRAL).astype(int)
    df_model = df_modelo[FEATURES_ES + ["Rating IMDB", "Rating alto"]].dropna()

    X = df_model[FEATURES_ES]
    y_reg  = df_model["Rating IMDB"]
    y_clas = df_model["Rating alto"]

    st.sidebar.subheader("⚙️ Parámetros")
    test_size    = st.sidebar.slider("Proporción de datos de prueba", 0.1, 0.4, 0.2, 0.05)
    max_depth    = st.sidebar.slider("Profundidad máxima del árbol", 2, 10, 5)
    random_state = st.sidebar.number_input("Semilla aleatoria", value=42, step=1)

    scaler = StandardScaler()

    splits = [("80/20", 0.20), ("70/30", 0.30), ("60/40", 0.40)]

    # ── Función de métricas ───────────────────────────────────────────────────
    def met_reg(y_true, y_pred, split):
        return {"Split": split,
                "R²": round(r2_score(y_true, y_pred), 4),
                "RMSE": round(np.sqrt(mean_squared_error(y_true, y_pred)), 4),
                "MAE": round(mean_absolute_error(y_true, y_pred), 4)}

    def met_clas(y_true, y_pred, y_prob, split, modelo):
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
        return {"Modelo": modelo, "Split": split,
                "Accuracy":  round(accuracy_score(y_true, y_pred), 4),
                "Precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
                "Recall":    round(recall_score(y_true, y_pred, zero_division=0), 4),
                "F1":        round(f1_score(y_true, y_pred, zero_division=0), 4),
                "ROC-AUC":   round(roc_auc_score(y_true, y_prob), 4)}

    # ══════════════════════════════════════════════════════════════════════════
    tab1, tab2, tab3 = st.tabs(["🌲 Árbol de Regresión", "🏷️ Árbol de Clasificación", "📈 Regresión Logística"])

    # ── TAB 1: Árbol de Regresión ─────────────────────────────────────────────
    with tab1:
        st.subheader("Árbol de Decisión para Regresión")
        st.markdown(f"**Variable objetivo:** Rating IMDB (continuo)  \n**Splits evaluados:** 80/20 · 70/30 · 60/40")

        res_arbol_reg = []
        for nombre, ts in splits:
            Xtr, Xte, ytr, yte = train_test_split(X, y_reg, test_size=ts, random_state=int(random_state))
            m = DecisionTreeRegressor(max_depth=3, min_samples_leaf=15, min_samples_split=20, random_state=int(random_state))
            m.fit(Xtr, ytr)
            yp = m.predict(Xte)
            res_arbol_reg.append(met_reg(yte, yp, nombre))

        df_ar = pd.DataFrame(res_arbol_reg)
        st.subheader("📋 Métricas por split")
        st.dataframe(df_ar, use_container_width=True, hide_index=True)

        col1, col2, col3 = st.columns(3)
        for col, met in zip([col1, col2, col3], ["R²", "RMSE", "MAE"]):
            fig = go.Figure(go.Bar(
                x=df_ar["Split"], y=df_ar[met],
                marker_color=["#2196F3", "#FF9800", "#4CAF50"],
                text=df_ar[met], textposition="outside"))
            fig.update_layout(title=met, height=300, showlegend=False, margin=dict(t=40,b=20))
            col.plotly_chart(fig, use_container_width=True)

        # Gráfica real vs Predicción del mejor split
        mejor_idx = df_ar["R²"].idxmax()
        mejor_ts  = splits[mejor_idx][1]
        Xtr_b, Xte_b, ytr_b, yte_b = train_test_split(X, y_reg, test_size=mejor_ts, random_state=int(random_state))
        m_best = DecisionTreeRegressor(max_depth=3, min_samples_leaf=15, min_samples_split=20, random_state=int(random_state))
        m_best.fit(Xtr_b, ytr_b)
        yp_best = m_best.predict(Xte_b)

        st.subheader(f"Real vs Predicción — Mejor split ({splits[mejor_idx][0]})")
        fig_rv = px.scatter(x=yte_b, y=yp_best,
            labels={"x": "Rating real", "y": "Rating Predicción"},
            opacity=0.5, color_discrete_sequence=["#2196F3"])
        lim = [min(yte_b.min(), yp_best.min()), max(yte_b.max(), yp_best.max())]
        fig_rv.add_scatter(x=lim, y=lim, mode="lines",
            line=dict(color="red", dash="dash"), name="Predicción perfecta")
        st.plotly_chart(fig_rv, use_container_width=True)

        # Importancia de variables
        imp_df = pd.DataFrame({"Variable": FEATURES_ES, "Importancia": m_best.feature_importances_}).sort_values("Importancia")
        fig_imp = px.bar(imp_df, x="Importancia", y="Variable", orientation="h",
            title="Importancia de variables — Árbol de Regresión",
            color="Importancia", color_continuous_scale="YlGn")
        st.plotly_chart(fig_imp, use_container_width=True)

        st.subheader("📊 Summary final")
        st.dataframe(df_ar, use_container_width=True, hide_index=True)
        mejor = df_ar.loc[df_ar["R²"].idxmax()]
        st.success(f"✅ Mejor R² = **{mejor['R²']}** con split **{mejor['Split']}** | RMSE = {mejor['RMSE']} | MAE = {mejor['MAE']}")

    # ── TAB 2: Árbol de Clasificación ─────────────────────────────────────────
    with tab2:
        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, roc_auc_score
        st.subheader("Árbol de Decisión para Clasificación Binaria")
        st.markdown(f"**Variable objetivo:** Rating alto (1 si Rating IMDB ≥ {UMBRAL}, 0 si no)  \n"
                    f"**Balance:** {y_clas.mean()*100:.1f}% episodios con rating alto")

        res_arbol_clas = []
        for nombre, ts in splits:
            Xtr, Xte, ytr, yte = train_test_split(X, y_clas, test_size=ts, random_state=int(random_state), stratify=y_clas)
            m = DecisionTreeClassifier(max_depth=3, min_samples_leaf=15, min_samples_split=20, class_weight="balanced", random_state=int(random_state))
            m.fit(Xtr, ytr)
            yp   = m.predict(Xte)
            yprob = m.predict_proba(Xte)[:, 1]
            res_arbol_clas.append(met_clas(yte, yp, yprob, nombre, "Árbol"))

        df_ac = pd.DataFrame(res_arbol_clas)
        st.subheader("📋 Métricas por split")
        st.dataframe(df_ac, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        for col, met in zip([col1, col2], ["Accuracy", "F1"]):
            fig = go.Figure(go.Bar(
                x=df_ac["Split"], y=df_ac[met],
                marker_color=["#2196F3", "#FF9800", "#4CAF50"],
                text=df_ac[met], textposition="outside"))
            fig.update_layout(title=met, height=300, showlegend=False, margin=dict(t=40,b=20))
            col.plotly_chart(fig, use_container_width=True)

        # Matriz de confusión del mejor split
        mejor_idx_c = df_ac["F1"].idxmax()
        mejor_ts_c  = splits[mejor_idx_c][1]
        Xtr_c, Xte_c, ytr_c, yte_c = train_test_split(X, y_clas, test_size=mejor_ts_c, random_state=int(random_state), stratify=y_clas)
        m_best_c = DecisionTreeClassifier(max_depth=3, min_samples_leaf=15, min_samples_split=20, class_weight="balanced", random_state=int(random_state))
        m_best_c.fit(Xtr_c, ytr_c)
        yp_c    = m_best_c.predict(Xte_c)
        yprob_c = m_best_c.predict_proba(Xte_c)[:, 1]

        st.subheader(f"Matriz de confusión — Mejor split ({splits[mejor_idx_c][0]})")
        cm = confusion_matrix(yte_c, yp_c)
        fig_cm, ax_cm = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay(cm, display_labels=["Bajo", "Alto"]).plot(ax=ax_cm, colorbar=False)
        ax_cm.set_title("Matriz de Confusión")
        st.pyplot(fig_cm)
        plt.close()

        st.subheader("📊 Summary final")
        st.dataframe(df_ac, use_container_width=True, hide_index=True)
        mejor_c = df_ac.loc[df_ac["F1"].idxmax()]
        st.success(f"✅ Mejor F1 = **{mejor_c['F1']}** con split **{mejor_c['Split']}** | Accuracy = {mejor_c['Accuracy']} | ROC-AUC = {mejor_c['ROC-AUC']}")

    # ── TAB 3: Regresión Logística ────────────────────────────────────────────
    with tab3:
        from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, roc_curve, roc_auc_score
        from sklearn.linear_model import LogisticRegression
        st.subheader("Regresión Logística — Clasificación Binaria")
        st.markdown(f"**Variable objetivo:** Rating alto (1 si Rating IMDB ≥ {UMBRAL}, 0 si no)")

        res_logit = []
        for nombre, ts in splits:
            Xtr, Xte, ytr, yte = train_test_split(X, y_clas, test_size=ts, random_state=int(random_state), stratify=y_clas)
            Xtr_sc = scaler.fit_transform(Xtr)
            Xte_sc = scaler.transform(Xte)
            m = LogisticRegression(max_iter=1000, random_state=int(random_state))
            m.fit(Xtr_sc, ytr)
            yp    = m.predict(Xte_sc)
            yprob = m.predict_proba(Xte_sc)[:, 1]
            res_logit.append(met_clas(yte, yp, yprob, nombre, "Reg. Logística"))

        df_lg = pd.DataFrame(res_logit)
        st.subheader("📋 Métricas por split")
        st.dataframe(df_lg, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        for col, met in zip([col1, col2], ["Accuracy", "ROC-AUC"]):
            fig = go.Figure(go.Bar(
                x=df_lg["Split"], y=df_lg[met],
                marker_color=["#2196F3", "#FF9800", "#4CAF50"],
                text=df_lg[met], textposition="outside"))
            fig.update_layout(title=met, height=300, showlegend=False, margin=dict(t=40,b=20))
            col.plotly_chart(fig, use_container_width=True)

        # Coeficientes del mejor split
        mejor_idx_l = df_lg["ROC-AUC"].idxmax()
        mejor_ts_l  = splits[mejor_idx_l][1]
        Xtr_l, Xte_l, ytr_l, yte_l = train_test_split(X, y_clas, test_size=mejor_ts_l, random_state=int(random_state), stratify=y_clas)
        Xtr_l_sc = scaler.fit_transform(Xtr_l)
        Xte_l_sc = scaler.transform(Xte_l)
        m_best_l = LogisticRegression(max_iter=1000, random_state=int(random_state))
        m_best_l.fit(Xtr_l_sc, ytr_l)
        yp_l    = m_best_l.predict(Xte_l_sc)
        yprob_l = m_best_l.predict_proba(Xte_l_sc)[:, 1]

        coef_df = pd.DataFrame({"Variable": FEATURES_ES, "Coeficiente": m_best_l.coef_[0]}).sort_values("Coeficiente")
        fig_coef = px.bar(coef_df, x="Coeficiente", y="Variable", orientation="h",
            color="Coeficiente", color_continuous_scale="RdYlGn",
            title=f"Coeficientes — Regresión Logística (Split {splits[mejor_idx_l][0]})")
        fig_coef.add_vline(x=0, line_dash="dash", line_color="white")
        st.plotly_chart(fig_coef, use_container_width=True)

        # Curva ROC
        fpr, tpr, _ = roc_curve(yte_l, yprob_l)
        auc_val = roc_auc_score(yte_l, yprob_l)
        fig_roc = go.Figure()
        fig_roc.add_scatter(x=fpr, y=tpr, mode="lines", name=f"ROC (AUC={auc_val:.3f})", line=dict(color="#4CAF50", width=2))
        fig_roc.add_scatter(x=[0,1], y=[0,1], mode="lines", name="Aleatorio", line=dict(color="red", dash="dash"))
        fig_roc.update_layout(title=f"Curva ROC — Split {splits[mejor_idx_l][0]}",
            xaxis_title="Tasa de Falsos Positivos", yaxis_title="Tasa de Verdaderos Positivos")
        st.plotly_chart(fig_roc, use_container_width=True)

        st.subheader("📊 Summary final")
        st.dataframe(df_lg, use_container_width=True, hide_index=True)
        mejor_l = df_lg.loc[df_lg["ROC-AUC"].idxmax()]
        st.success(f"✅ Mejor ROC-AUC = **{mejor_l['ROC-AUC']}** con split **{mejor_l['Split']}** | Accuracy = {mejor_l['Accuracy']} | F1 = {mejor_l['F1']}")


    st.title("📥 Datos completos y exportación")

    tab1, tab2, tab3 = st.tabs(["👥 Personajes", "📺 Episodios", "⭐ Ratings"])

    with tab1:
        st.markdown(f"**{len(df_chars)} personajes registrados**")
        st.dataframe(df_chars, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Descargar personajes en CSV",
            df_chars.to_csv(index=False).encode("utf-8"),
            "personajes_simpsons.csv", "text/csv",
        )
    with tab2:
        st.markdown(f"**{len(df_eps)} episodios registrados**")
        st.dataframe(df_eps, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Descargar episodios en CSV",
            df_eps.to_csv(index=False).encode("utf-8"),
            "episodios_simpsons.csv", "text/csv",
        )
    with tab3:
        st.markdown(f"**{len(df_rat)} registros de ratings**")
        st.dataframe(df_rat, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Descargar ratings en CSV",
            df_rat.to_csv(index=False).encode("utf-8"),
            "ratings_simpsons.csv", "text/csv",
        )
