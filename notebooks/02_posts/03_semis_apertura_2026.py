# %% [markdown]
# # Post #3 — Semifinales Apertura 2026 (previa)
#
# **Concepto:** previa de las 2 semifinales del Apertura 2026 con datos de
# fase regular: cómo llegan River, Rosario Central, Argentinos Juniors y
# Belgrano a definir el torneo.
#
# **Carrusel IG:** 5 slides 1080×1350 — Combo C + escudos oficiales.
#
# **Datos:** FBref vía soccerdata.
#
# **Publicación target:** sábado 16/5 ~19hs (antes del primer partido).

# %% [Setup]
import sys
from pathlib import Path
from datetime import date

REPO_ROOT = r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

%load_ext autoreload
%autoreload 2

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

import soccerdata as sd
from scripts.style import (
    set_default_style, apply_branding, watermark,
    COLORS, FONTS, ROLES, PAISES_COLORS, pais_color,
    draw_card_box, draw_comparison_bar, draw_section_label,
    draw_big_number, draw_quote, place_logo,
    place_competition_icon, place_team_badge,
)

set_default_style()

# Paths de output
OUTPUTS = Path(REPO_ROOT) / "outputs" / "2026-05" / "post_03_semis_apertura"
OUTPUTS.mkdir(parents=True, exist_ok=True)
CARRUSEL_FINAL = OUTPUTS / "carrusel_final"
CARRUSEL_FINAL.mkdir(exist_ok=True)

print(f"Outputs van a: {OUTPUTS}")

# %% [Constantes del post]
HOY = date(2026, 5, 16)  # Sábado
PARTIDO_1 = "River Plate vs Rosario Central"
PARTIDO_1_DIA = "Sábado 16/5"
PARTIDO_2 = "Argentinos Juniors vs Belgrano"
PARTIDO_2_DIA = "Domingo 17/5"

# Diccionario de los 4 equipos: nombre FBref → archivo escudo + color patrón
# (FBref usa los nombres en inglés/oficiales — ajustar si las queries devuelven otro)
EQUIPOS = {
    "River Plate":       {"escudo": "river_plate.png",       "color": "#FFFFFF", "color_alt": "#C8102E"},
    "Rosario Central":   {"escudo": "rosario_central.png",   "color": "#FFD700", "color_alt": "#003C7E"},
    "Argentinos Jrs":    {"escudo": "argentinos_juniors.png","color": "#D52B1E", "color_alt": "#FFFFFF"},
    "Belgrano":          {"escudo": "belgrano.png",          "color": "#003C7E", "color_alt": "#FFFFFF"},
}

# %% [1. LanusStats — el paquete de Fede Rábanos, armado para fútbol AR]
# soccerdata.FBref y soccerdata.Sofascore NO traen Liga Argentina.
# LanusStats wrappea las mismas fuentes pero con foco en AR.
#
# Si no está instalado: pip install LanusStats
import LanusStats as ls

# Listamos qué clases/clientes expone el paquete
print("Clases disponibles en LanusStats:")
for nombre in dir(ls):
    if not nombre.startswith("_"):
        print(f"  · {nombre}")

# %% [2. Probamos FotMob — tiene Liga Profesional Argentina]
# FotMob es la fuente más completa para AR.
# IDs comunes Liga Pro Argentina: 112 (Liga Profesional)
fotmob = ls.FotMob()

# Inspeccionar métodos disponibles
print("\nMétodos del cliente FotMob:")
for m in dir(fotmob):
    if not m.startswith("_") and callable(getattr(fotmob, m, None)):
        print(f"  · {m}")

# %% [3. Descubrir el nombre EXACTO de Liga AR en FotMob]
# El docstring dice: get_available_leagues("Fotmob") devuelve los nombres válidos.
# Esa función vive a nivel módulo en LanusStats (no en el cliente FotMob).
ligas_fotmob = ls.get_available_leagues("Fotmob")
print(f"Total ligas en FotMob: {len(ligas_fotmob)}")
print("\n🔍 Ligas con 'Argentin' / 'AR':")
candidatas = [lg for lg in ligas_fotmob if "argent" in lg.lower() or "ar " in lg.lower()]
for lg in candidatas:
    print(f"  · {lg}")

if not candidatas:
    print("\n⚠️ No encontré con 'argent'. Lista completa:")
    for lg in ligas_fotmob:
        print(f"  · {lg}")

# GUARDAR a archivo para revisión cómoda
debug_path = Path(REPO_ROOT) / "outputs" / "_debug_ligas_fotmob.txt"
debug_path.parent.mkdir(parents=True, exist_ok=True)
with open(debug_path, "w", encoding="utf-8") as f:
    f.write(f"Total ligas FotMob: {len(ligas_fotmob)}\n\n")
    f.write("=== TODAS las ligas ===\n")
    for lg in ligas_fotmob:
        f.write(f"  · {lg}\n")
    f.write(f"\n=== Candidatas AR ===\n")
    for lg in candidatas:
        f.write(f"  · {lg}\n")
print(f"\n📄 Guardado en: {debug_path}")

# %% [4. Descubrir seasons válidas para Liga AR]
# ⚠️ Atención: el nombre NO lleva tilde — FotMob usa "Division" en inglés.
# Importante: get_available_season_for_leagues devuelve un DICT
# con claves 'id' y 'seasons'. La lista real está en seasons['seasons'].
LIGA_AR = "Argentina Primera Division"   # ← sin tilde
LIGA_AR_ALT = "Argentina Copa de la Liga"  # alternativa si Apertura está acá

for liga in [LIGA_AR, LIGA_AR_ALT]:
    try:
        info = ls.get_available_season_for_leagues("Fotmob", liga)
        print(f"\n=== '{liga}' ===")
        print(f"id: {info.get('id')}")
        seasons_list = info.get("seasons", [])
        print(f"seasons disponibles ({len(seasons_list)}):")
        for s in seasons_list:
            print(f"  · {s}")
    except Exception as e:
        print(f"\n⚠️ '{liga}' falló: {type(e).__name__}: {e}")

# %% [5. Tabla de posiciones — fase regular Apertura 2026]
# Ahora con los nombres correctos.
SEASON_OK = "2025"  # FotMob no tiene "2026" aún — el Apertura 2026 actual está bajo "2025"

try:
    tabla = fotmob.get_season_tables(
        league=LIGA_AR,
        season=SEASON_OK,
        table=["all", "xg"],  # all + xg para ver tabla normal + tabla por xG
    )
    print(f"Tipo: {type(tabla)}")
    if hasattr(tabla, "head"):
        print(tabla.head(20))
        print("\nColumnas:", tabla.columns.tolist())
    else:
        print(tabla)
except Exception as e:
    print(f"⚠️ {type(e).__name__}: {e}")

# %% [6. Stats por equipo — recorremos los stats más útiles para el post]
# Stats válidas (vistas en el bug InvalidStat de LanusStats):
#   rating_team, goals_team_match, goals_conceded_team_match, possession...
# La lista exacta la tenemos que ver completa. Probamos uno por uno.

STATS_UTILES = [
    "rating_team",
    "goals_team_match",
    "goals_conceded_team_match",
    "possession",
    "shots_team",
    "expected_goals_team",
    "expected_goals_conceded_team",
]

resultados_stats = {}
for stat in STATS_UTILES:
    try:
        df = fotmob.get_teams_stats_season(league=LIGA_AR, season=SEASON_OK, stat=stat)
        resultados_stats[stat] = df
        print(f"✅ '{stat}' — {type(df).__name__}, shape {df.shape if hasattr(df, 'shape') else '?'}")
    except Exception as e:
        print(f"❌ '{stat}' → {type(e).__name__}: {str(e)[:120]}")

# Si "expected_goals_team" no anda, mirá el primer error InvalidStat — te lista las válidas.

# %% [6. Plan B — SofaScore directo (si FotMob falla)]
# sofa = ls.SofaScore()
# print([m for m in dir(sofa) if not m.startswith("_") and callable(getattr(sofa, m))])

# %% [7. Plan C — ThreeSixFiveScores (365scores cubre AR fuerte)]
# t365 = ls.ThreeSixFiveScores()
# print([m for m in dir(t365) if not m.startswith("_") and callable(getattr(t365, m))])

# %% [Pendiente — armar slides una vez confirmados los datos]
# Próximos pasos:
# - Slide 1: Portada — "SEMIS DEL APERTURA 2026" + logo Liga + 4 escudos en grid
# - Slide 2: Scatter peligrosidad — xG/partido vs xGA/partido (TIPO 2)
# - Slide 3: Comparativa River vs Rosario Central — 4-5 stats lado a lado (TIPO 4)
# - Slide 4: Comparativa Argentinos vs Belgrano — 4-5 stats lado a lado (TIPO 4)
# - Slide 5: Cierre — "¿Quién pasa a la final?" + handle
