import pandas as pd
import logging
from datetime import datetime

logging.basicConfig(
    filename="../logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def transformar_datos():
    try:
        logging.info("Iniciando transformación de datos...")

        df = pd.read_csv("../data/clima.csv")

        # Ejemplo de transformación
        df["temperatura_fahrenheit"] = (df["temperatura"] * 9/5) + 32
        df["fecha_transformacion"] = datetime.now()

        df.to_csv("../data/clima_transformado.csv", index=False)

        logging.info("Datos transformados correctamente.")
        print(" Transformación completada.")

    except Exception as e:
        logging.error(f"Error en transformación: {e}")
        print(" Error en transformación:", e)

if __name__ == "__main__":
    transformar_datos()