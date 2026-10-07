import sqlite3

# 1. Abre (o crea) el archivo weather.db en esta carpeta
conn = sqlite3.connect("weather.db")

# 2. Crea la tabla solo si no existe todavía
conn.execute("""
CREATE TABLE IF NOT EXISTS pronostico (
  fecha_recoleccion TEXT NOT NULL,
  ciudad            TEXT NOT NULL,
  fecha_pronostico  TEXT NOT NULL,
  temp_min          REAL,
  temp_max          REAL,
  lluvia_prob       REAL,
  precipitacion     REAL,
  viento            REAL,
  humedad           REAL,
  PRIMARY KEY (fecha_recoleccion, ciudad, fecha_pronostico)
)
""")

# 3. Guarda los cambios y cierra
conn.commit()
conn.close()
print("Base creada: weather.db")