#!/usr/bin/env python3

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import logging

# =============================
# CONFIGURACIÓN DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# =============================
# RUTAS
# =============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "clima.csv")
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "clima_analysis.png")

# =============================
# CARGAR DATOS
# =============================
if not os.path.exists(DATA_PATH):
    logger.error("No se encontró el archivo clima.csv. Ejecuta primero extractor.py")
    exit()

df = pd.read_csv(DATA_PATH)

# =============================
# CREAR FIGURA
# =============================
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Análisis de Clima por Ciudades', fontsize=16, fontweight='bold')

# Gráfica 1: Temperaturas
ax1 = axes[0, 0]
ax1.bar(df['ciudad'], df['temperatura'])
ax1.set_title('Temperatura Actual (°C)')
ax1.set_ylabel('Temperatura (°C)')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', alpha=0.3)

# Gráfica 2: Humedad
ax2 = axes[0, 1]
ax2.bar(df['ciudad'], df['humedad'])
ax2.set_title('Humedad Relativa (%)')
ax2.set_ylabel('Humedad (%)')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', alpha=0.3)

# Gráfica 3: Velocidad del Viento
ax3 = axes[1, 0]
ax3.scatter(df['ciudad'], df['velocidad_viento'], s=200)
ax3.set_title('Velocidad del Viento (km/h)')
ax3.set_ylabel('Velocidad (km/h)')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(alpha=0.3)

# Gráfica 4: Sensación Térmica vs Temperatura
ax4 = axes[1, 1]
x = np.arange(len(df))
width = 0.35

ax4.bar(x - width/2, df['temperatura'], width, label='Temperatura')
ax4.bar(x + width/2, df['sensacion_termica'], width, label='Sensación Térmica')

ax4.set_title('Temperatura vs Sensación Térmica')
ax4.set_ylabel('Temperatura (°C)')
ax4.set_xticks(x)
ax4.set_xticklabels(df['ciudad'], rotation=45)
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_PATH, dpi=300, bbox_inches='tight')

logger.info("Gráficas guardadas en data/clima_analysis.png")

plt.show()