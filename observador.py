import sqlite3
from datetime import date, timedelta
import requests
import json

# Ciudades activas, leídas de ciudades.json
with open("ciudades.json", encoding="utf-8") as f:
    CIUDADES = {c["nombre"]: (c["lat"], c["lon"]) for c in json.load(f) if c["activa"]}

DIARIAS = "temperature_2m_min,temperature_2m_max,precipitation_sum,wind_speed_10m_max"

# Ventana: de hace 12 días a hace 5 días (el archivo tiene ~5 días de retraso)
hoy = date.today()
desde = (hoy - timedelta(days=12)).isoformat()
hasta = (hoy - timedelta(days=5)).isoformat()

conn = sqlite3.connect("weather.db")

# Tabla de datos ocurridos (una fila por día y ciudad)
conn.execute("""
CREATE TABLE IF NOT EXISTS observado (
  fecha         TEXT NOT NULL,
  ciudad        TEXT NOT NULL,
  temp_min      REAL,
  temp_max      REAL,
  precipitacion REAL,
  viento        REAL,
  PRIMARY KEY (fecha, ciudad)
)
""")

for ciudad, (lat, lon) in CIUDADES.items():
    r = requests.get("https://archive-api.open-meteo.com/v1/archive", params={
        "latitude": lat,
        "longitude": lon,
        "start_date": desde,
        "end_date": hasta,
        "daily": DIARIAS,
        "timezone": "America/Santiago",
    }, timeout=20)
    r.raise_for_status()
    d = r.json()["daily"]

    nuevas = 0
    for i, fecha in enumerate(d["time"]):
        cur = conn.execute("""
            INSERT OR IGNORE INTO observado
              (fecha, ciudad, temp_min, temp_max, precipitacion, viento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (fecha, ciudad,
              d["temperature_2m_min"][i],
              d["temperature_2m_max"][i],
              d["precipitation_sum"][i],
              d["wind_speed_10m_max"][i]))
        nuevas += cur.rowcount

    print(f"{ciudad}: {nuevas} filas nuevas ({desde} a {hasta})")

conn.commit()
conn.close()