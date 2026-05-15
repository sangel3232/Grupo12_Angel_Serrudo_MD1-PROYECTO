# 📺 Simpsons ETL — Pipeline de Datos + Dashboard + Regresión Lineal

**Grupo 12 — Minería de Datos 2026**  
**Estudiante:** Angel Serrudo  
**Tecnologías:** Python · PostgreSQL · Supabase · SQLAlchemy · Streamlit · Plotly · Scikit-learn · Jupyter

---

## 🎯 Objetivo del Proyecto

Desarrollar un pipeline ETL completo sobre datos reales de Los Simpsons que permita:

- Extraer datos desde la API pública de Simpsons
- Transformar y limpiar los datos
- Cargar los datos en una base de datos PostgreSQL (local o Supabase)
- Visualizar los datos en un dashboard interactivo con Streamlit
- Aplicar un modelo de Regresión Lineal para predecir el rating IMDB de los episodios

---

## 🧱 Arquitectura del Sistema

```
Simpsons API ──► extract.py ──► transform.py ──► PostgreSQL / Supabase
                                                        │
                                                 Streamlit Dashboard
                                                        │
                                              Modelo Regresión Lineal
```

| Capa | Servicio | Función |
|---|---|---|
| Control de versiones | GitHub | Almacenamiento del código |
| Frontend / App | Streamlit | Dashboard interactivo con URL pública |
| Base de datos | PostgreSQL / Supabase | Almacenamiento de datos procesados |
| Análisis | Jupyter Notebook | EDA y modelo de regresión |

---

## 📁 Estructura del Proyecto

```
simpsons-etl/
├── config/
│   └── database.py          # Conexión a PostgreSQL / Supabase
├── dashboard/
│   ├── app.py               # Dashboard Streamlit (5 secciones)
│   └── bg.jpg               # Imagen de fondo
├── data/
│   ├── characters.csv       # Personajes exportados
│   ├── episodes.csv         # Episodios exportados
│   └── ratings.csv          # Ratings exportados
├── etl/
│   ├── extract.py           # Extracción desde la API
│   ├── transform.py         # Limpieza y transformación
│   ├── load.py              # Carga a PostgreSQL (bulk insert)
│   └── pipeline.py          # Orquestador del pipeline completo
├── notebooks/
│   └── regresion_simpsons.ipynb  # Análisis EDA + Regresión Lineal
├── scripts/
│   ├── apply_schema.py      # Crea las tablas en la BD
│   ├── seed_demo.py         # Carga datos de demo sin la API
│   └── queries.py           # Consultas SQL con filtros
├── .env.example             # Plantilla de variables de entorno
├── .streamlit/
│   ├── config.toml          # Configuración del servidor Streamlit
│   └── secrets.toml.example # Plantilla de secrets para Streamlit Cloud
├── docker-compose.yml       # PostgreSQL local con Docker
├── requirements.txt         # Dependencias del proyecto
└── README.md
```

---

## 🗄️ Base de Datos

### Tabla `dim_characters`
| Campo | Tipo | Descripción |
|---|---|---|
| character_id | INT | Identificador único |
| name | TEXT | Nombre del personaje |
| gender | TEXT | Género |
| occupation | TEXT | Ocupación |
| status | TEXT | Estado (Vivo/Fallecido) |

### Tabla `dim_episodes`
| Campo | Tipo | Descripción |
|---|---|---|
| episode_id | INT | Identificador único |
| name | TEXT | Título del episodio |
| season | INT | Número de temporada |
| air_date | DATE | Fecha de emisión |
| number_in_season | INT | Número dentro de la temporada |

### Tabla `fact_ratings`
| Campo | Tipo | Descripción |
|---|---|---|
| episode_id | INT | Referencia al episodio |
| season | INT | Temporada |
| number_in_season | INT | Número en temporada |
| viewers_millions | NUMERIC | Audiencia en millones |
| imdb_rating | NUMERIC | Rating IMDB (1-10) |
| duration_min | INT | Duración en minutos |

**Total de registros:** 1182 personajes · 768 episodios · 35 temporadas

---

## 🚀 Instalación y Ejecución

### Requisitos previos
- Python 3.10+
- PostgreSQL corriendo localmente o cuenta en [Supabase](https://supabase.com)
- Git

### 1. Clonar el repositorio

```bash
git clone https://github.com/sangel3232/Grupo12_Angel_Serrudo_MD1.git
cd Grupo12_Angel_Serrudo_MD1/ETL-PROYECTO-API/simpsons_data_/simpsons-etl
```

### 2. Crear y activar el entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / Mac
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar la plantilla
copy .env.example .env
```

Editar `.env` con tus credenciales:

```env
# PostgreSQL local
DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/Simpsons_db

# O Supabase
DATABASE_URL=postgresql+psycopg2://postgres.<ref>:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 5. Crear las tablas en la base de datos

```bash
venv\Scripts\python.exe scripts/apply_schema.py
```

Salida esperada:
```
Schema aplicado correctamente
```

### 6. Ejecutar el pipeline ETL

```bash
venv\Scripts\python.exe -m etl.pipeline
```

Salida esperada:
```
🚀 Iniciando pipeline Simpsons ETL
Extrayendo characters...
Total registros descargados [characters]: 1182
Extrayendo episodes...
Total registros descargados [episodes]: 768
Transformando personajes...
Personajes transformados: 1182
Transformando episodios...
Episodios transformados: 768
Generando fact_ratings...
Ratings generados: 768
✅ Tabla 'dim_characters' cargada con 1182 registros
✅ Tabla 'dim_episodes' cargada con 768 registros
✅ Tabla 'fact_ratings' cargada con 768 registros
✅ Pipeline terminado exitosamente
```

> **Nota:** Si la API tarda o no está disponible, usa los datos de demo:
> ```bash
> venv\Scripts\python.exe scripts/seed_demo.py
> ```

### 7. Ejecutar el Dashboard

```bash
venv\Scripts\python.exe -m streamlit run dashboard/app.py --server.port 8502
```

Abrir en el navegador: **`http://localhost:8502`**

### 8. Ejecutar el Notebook de Regresión

```bash
venv\Scripts\python.exe -m jupyter notebook notebooks/regresion_simpsons.ipynb
```

---

## 📊 Dashboard Interactivo

El dashboard cuenta con 5 secciones navegables:

| Sección | Contenido |
|---|---|
| 📊 Estadísticas | KPIs, rating por temporada, audiencia, distribución de ratings |
| 👥 Personajes | Filtros por género y estado, gráficas de ocupaciones |
| 📺 Episodios | Filtros por temporada, scatter de ratings por episodio |
| 🤖 Regresión Lineal | Modelos simple y múltiple, métricas, coeficientes, predictor interactivo |
| 📥 Datos | Tablas completas con exportación a CSV |

---

## 🤖 Modelo de Regresión Lineal

**Variable objetivo:** `imdb_rating` (Rating IMDB del episodio)  
**Variables predictoras:** `viewers_millions`, `season`, `duration_min`, `number_in_season`

```python
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)

model = LinearRegression()
model.fit(X_train_sc, y_train)
```

### Métricas de evaluación

| Métrica | Descripción |
|---|---|
| R² | Coeficiente de determinación — qué tan bien explica el modelo la varianza |
| RMSE | Error cuadrático medio — error promedio en puntos de rating |
| MAE | Error absoluto medio — desviación promedio de las predicciones |

El notebook incluye además:
- Análisis exploratorio (EDA) con histogramas, boxplots y mapas de correlación
- Regresión simple con el mejor predictor individual
- Regresión múltiple con todas las variables
- Cálculo de VIF para detectar multicolinealidad
- Diagnósticos: residuos, Q-Q plot, Shapiro-Wilk, Breusch-Pagan, Durbin-Watson

---

## 🔐 Seguridad

- Credenciales en variables de entorno (`.env`) — nunca en el código
- `.env` y `secrets.toml` incluidos en `.gitignore`
- Conexión cifrada con `sslmode=require` para Supabase

---

## 🌐 Despliegue en Streamlit Cloud

1. Subir el repositorio a GitHub
2. Ir a [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Seleccionar repo, rama `main`, archivo `dashboard/app.py`
4. En **Advanced settings → Secrets** agregar:

```toml
DATABASE_URL = "postgresql+psycopg2://postgres:<password>@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
```

5. Click en **Deploy**

---

## 👨‍💻 Autor

**Angel Serrudo**  
Grupo 12 — Minería de Datos · 2026  
[github.com/sangel3232](https://github.com/sangel3232)
