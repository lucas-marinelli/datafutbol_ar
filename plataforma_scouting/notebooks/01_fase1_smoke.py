# %% [markdown]
# # Fase 1 — Humo end-to-end de la plataforma
#
# Corré este notebook de arriba a abajo para construir el MVP de datos:
#
#   FBref (Big-5) → tabla ancha → normalizar → parquet → DuckDB → consultas
#
# ⚠️ La celda de ingesta abre **Chrome** la primera vez (soccerdata>=1.9 scrapea
#    FBref con navegador por Cloudflare). Tardá unos minutos la 1ra vez; después
#    queda cacheado en parquet y es instantáneo.
#
# El pipeline ya está validado offline con datos sintéticos — acá lo corrés con
# data real en tu máquina.

# %% [Setup — paths e imports]
import sys
from pathlib import Path

# Raíz del módulo plataforma_scouting (este notebook vive en su subcarpeta notebooks/)
PLAT = Path(r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar\plataforma_scouting")
for p in (str(PLAT), str(PLAT / "db")):
    if p not in sys.path:
        sys.path.insert(0, p)

%load_ext autoreload
%autoreload 2

import pandas as pd
import duckdb

from ingest.fbref_loader import cargar_todo, STAT_TYPES
from ingest.transformar import transformar, guardar
import build_db

SEASON = "2025-2026"   # si FBref se queja, probá "2526"
print("Setup OK · stat_types:", STAT_TYPES)

# %% [1. Ingesta FBref Big-5 — ABRE CHROME la primera vez]
# Descarga los stat_types (standard/shooting/misc/playing_time/keeper) y los une.
# refrescar=True fuerza re-bajar (necesario la 1ra vez tras cambiar STAT_TYPES,
# para que entre 'misc' con la data defensiva). Después podés ponerlo en False.
ancha = cargar_todo(season=SEASON, refrescar=True)
print("Tabla ancha:", ancha.shape)

# %% [2. Inspeccionar columnas reales (clave para verificar el matcheo)]
# Si en la celda 3 aparecen warnings de "columnas no encontradas", mirá esta
# lista y ajustá los candidatos en ingest/transformar.py (_find).
print(f"{len(ancha.columns)} columnas:")
for c in ancha.columns:
    print("   ", c)

# %% [3. Normalizar al esquema de la plataforma]
out = transformar(ancha, season=SEASON, anio_ref=2026)
print("Normalizado:", out.shape)
print("\nColumnas:", list(out.columns))
print("\nMuestra:")
print(out[["nombre", "nacionalidad", "pos_grupo", "club", "edad", "minutos",
           "goles_90", "asistencias_90", "tiros_90", "conversion",
           "tackles_ganados_90"]].head(10).to_string(index=False))

# %% [4. Guardar parquet procesado]
ruta = guardar(out, season=SEASON)
print("Guardado en:", ruta)

# %% [5. Construir la base DuckDB]
db_path = build_db.build()

# %% [6. Consultas de scouting de prueba]
con = duckdb.connect(str(db_path))

print("=== Cuántos jugadores por liga ===")
print(con.execute("""
    SELECT competicion, count(*) AS jugadores
    FROM v_scouting GROUP BY competicion ORDER BY jugadores DESC
""").df().to_string(index=False))

print("\n=== Top 10 sub-23 goleadores por 90 (delanteros, +900 min) ===")
print(con.execute("""
    SELECT nombre, club, edad, minutos,
           ROUND(goles_90,2) AS g90, ROUND(tiros_90,1) AS sh90,
           ROUND(conversion,2) AS g_por_tiro
    FROM v_scouting
    WHERE pos_grupo = 'DEL' AND edad <= 23 AND minutos >= 900
    ORDER BY goles_90 DESC
    LIMIT 10
""").df().to_string(index=False))

print("\n=== Top 10 creadores sub-23 (asistencias/90, +900 min) ===")
print(con.execute("""
    SELECT nombre, club, pos_grupo, edad,
           ROUND(asistencias_90,2) AS a90, ROUND(asistencias,0) AS asist
    FROM v_scouting
    WHERE edad <= 23 AND minutos >= 900
    ORDER BY asistencias_90 DESC
    LIMIT 10
""").df().to_string(index=False))

print("\n=== Argentinos en las Big-5 (cualquier edad) ===")
print(con.execute("""
    SELECT nombre, club, competicion, edad, minutos
    FROM v_scouting
    WHERE nacionalidad = 'ARG'
    ORDER BY minutos DESC
    LIMIT 15
""").df().to_string(index=False))

con.close()

# %% [7. Verificación / próximos pasos (R28)]
# ✅ Si llegaste hasta acá con datos reales: la Fase 1 está cumplida.
#
# CHEQUEOS:
# 1. ¿La celda 3 tiró warnings de columnas no encontradas? Si sí, abrí la lista
#    de la celda 2, encontrá el nombre real y agregalo como candidato en
#    ingest/transformar.py (función _find). Re-corré desde la celda 3.
# 2. ¿Los nacionalidad='ARG' son todos argentinos? FBref a veces marca doble
#    nacionalidad raro. Cruzá algún caso contra fbref.com.
# 3. ¿Los conteos por liga tienen sentido (~500-600 por liga)?
#
# PRÓXIMO (Fase 2):
# - Sumar Transfermarkt (valor de mercado) en ingest/transfermarkt_loader.py.
# - Implementar metrics/percentiles.py (percentil por posición).
# - Después: metrics/scoring_index.py + el dashboard Streamlit (Fase 3).

# %%
