import os
import sys
import sqlite3
import datetime as dt
import psycopg

# Ruta de la base SQLite: por defecto weather.db, o la que pases como argumento
ruta = sys.argv[1] if len(sys.argv) > 1 else "weather.db"

sq = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
pron = sq.execute(
    "SELECT fecha_recoleccion, ciudad, fecha_pronostico, temp_min, temp_max, "
    "lluvia_prob, precipitacion, viento, humedad FROM pronostico").fetchall()
obs = sq.execute(
    "SELECT fecha, ciudad, temp_min, temp_max, precipitacion, viento "
    "FROM observado").fetchall()
sq.close()

def d(texto):
    return dt.date.fromisoformat(texto)

with psycopg.connect(os.environ["SUPABASE_URL"], prepare_threshold=None) as con:
    with con.cursor() as cur:
        for f in pron:
            cur.execute("""
                INSERT INTO pronostico (fecha_recoleccion, ciudad, fecha_pronostico,
                  temp_min, temp_max, lluvia_prob, precipitacion, viento, humedad)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING""",
                (d(f[0]), f[1], d(f[2]), *f[3:]))
        for o in obs:
            cur.execute("""
                INSERT INTO observado (fecha, ciudad, temp_min, temp_max,
                  precipitacion, viento)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING""",
                (d(o[0]), o[1], *o[2:]))
        cur.execute("select count(*) from pronostico")
        n_pron = cur.fetchone()[0]
        cur.execute("select count(*) from observado")
        n_obs = cur.fetchone()[0]

print(f"SQLite: {len(pron)} pronósticos, {len(obs)} observados")
print(f"Supabase: {n_pron} pronósticos, {n_obs} observados")