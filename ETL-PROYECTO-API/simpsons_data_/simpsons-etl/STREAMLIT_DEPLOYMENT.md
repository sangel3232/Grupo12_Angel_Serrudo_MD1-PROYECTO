# Despliegue en Streamlit Cloud — simpsons-etl

## 1. Archivo principal

```bash
streamlit run dashboard/app.py
```

## 2. Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub.
2. Ve a [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Selecciona el repo, rama `main` y archivo principal `dashboard/app.py`.
4. En **Advanced settings → Secrets**, agrega:

```toml
DATABASE_URL = "postgresql+psycopg2://postgres:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

5. Haz clic en **Deploy**.

## 3. Ejecución local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Correr el dashboard
streamlit run dashboard/app.py
```

O con Docker:

```bash
docker compose up --build
```

## 4. Secciones del dashboard

| Sección | Contenido |
|---|---|
| 📊 Estadísticas | KPIs, rating por temporada, audiencia, distribución |
| 👥 Personajes | Filtros por género/estado, gráficas de ocupación |
| 📺 Episodios | Filtros por temporada, scatter de ratings |
| 🤖 Regresión Lineal | Modelo simple y múltiple, métricas, predictor interactivo |
| 📥 Datos | Tablas completas + exportación CSV |

## 5. Variables de entorno necesarias

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL de conexión PostgreSQL/Supabase |

## 6. Notas

- El modelo de regresión predice `imdb_rating` usando `viewers_millions`, `season`, `duration_min` y `number_in_season`.
- Los datos de `fact_ratings` se generan automáticamente en el pipeline si la API no los provee.
- No subas `.env` ni `secrets.toml` a Git.
