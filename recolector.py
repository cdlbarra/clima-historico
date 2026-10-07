import sqlite3
from datetime import date
import requests
import json

# Ciudades activas, leídas de ciudades.json
with open("ciudades.json", encoding="utf-8") as f:
    CIUDADES = {c["nombre"]: (c["lat"], c["lon"]) for c in json.load(f) if c["activa"]}

# Variables diarias que pedimos a la API
DIARIAS = ("temperature_2m_min,temperature_2m_max,"
           "precipitation_probability_max,precipitation_sum,"
           "wind_speed_10m_max,relative_humidity_2m_mean")

hoy = date.today().isoformat()   # ej. "2026-10-06"
conn = sqlite3.connect("weather.db")

for ciudad, (lat, lon) in CIUDADES.items():
    # 1. Pedir el pronóstico a la API
    r = requests.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": lat,
        "longitude": lon,
        "daily": DIARIAS,
        "timezone": "America/Santiago",
        "forecast_days": 4,          # hoy + 3 días
    }, timeout=20)
    r.raise_for_status()             # si la API falla, se detiene con error claro
    d = r.json()["daily"]

    # 2. Guardar una fila por cada día pronosticado
    nuevas = 0
    for i, fecha in enumerate(d["time"]):
        cur = conn.execute("""
            INSERT OR IGNORE INTO pronostico
              (fecha_recoleccion, ciudad, fecha_pronostico,
               temp_min, temp_max, lluvia_prob, precipitacion,
               viento, humedad)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (hoy, ciudad, fecha,
              d["temperature_2m_min"][i],
              d["temperature_2m_max"][i],
              d["precipitation_probability_max"][i],
              d["precipitation_sum"][i],
              d["wind_speed_10m_max"][i],
              d["relative_humidity_2m_mean"][i]))
        nuevas += cur.rowcount

    print(f"{ciudad}: {nuevas} filas nuevas")

conn.commit()
conn.close()