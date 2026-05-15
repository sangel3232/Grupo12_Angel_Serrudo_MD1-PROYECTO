import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

conn = psycopg2.connect(host="localhost", port=5432, user="postgres", password="1234", dbname="postgres")
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname='Simpsons_db'")
exists = cur.fetchone()
if not exists:
    cur.execute('CREATE DATABASE "Simpsons_db"')
    print("Base de datos Simpsons_db creada")
else:
    print("Simpsons_db ya existe")

cur.close()
conn.close()
