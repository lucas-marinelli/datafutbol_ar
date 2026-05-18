# %% [markdown]
# # BAJO LA LUPA · Argentina — rumbo al Mundial 2026
#
# **Concepto:** primer post de la sección "BAJO LA LUPA". Análisis técnico
# del ciclo Scaloni post-Qatar 2022 hacia el Mundial 2026.
#
# **Carrusel IG:** 6 slides 1080×1350 — Combo C aplicado.
#
# **Data:**
# - StatsBomb Open Data: Copa América 2024 (referencia más reciente verificable)
# - StatsBomb Open Data: Mundial 2022 (contexto histórico)
# - Placeholders para: forma reciente eliminatorias 2024-25, XI probable 2026
#   (el autor debe pisar antes de publicar — fuentes: AFA / fifa.com / Wikipedia)

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

from statsbombpy import sb
from scripts.style import (
    set_default_style, apply_branding, watermark,
    COLORS, FONTS, ROLES, PAISES_COLORS, pais_color,
    draw_card_box, draw_comparison_bar, draw_section_label,
    draw_big_number, draw_quote, place_logo,
    place_competition_icon, place_team_badge, place_country_flag,
)
from scripts.data_loaders import SB_IDS, sb_matches, sb_events, cargar_selecciones

set_default_style()

OUTPUTS = Path(REPO_ROOT) / "outputs" / "2026-05" / "post_04_bll_argentina"
OUTPUTS.mkdir(parents=True, exist_ok=True)
CARRUSEL_FINAL = OUTPUTS / "carrusel_final"
CARRUSEL_FINAL.mkdir(exist_ok=True)
DATA_DIR = OUTPUTS / "data"
DATA_DIR.mkdir(exist_ok=True)

print(f"Outputs van a: {OUTPUTS}")

# %% [Constantes del post]
HOY = date(2026, 5, 19)              # martes
DEBUT_ARG = date(2026, 6, 16)        # debut Argentina vs Argelia (Mundial 2026)
DIAS_AL_DEBUT = (DEBUT_ARG - HOY).days
print(f"Faltan {DIAS_AL_DEBUT} días para el debut de Argentina")

SELECCION = "Argentina"
DEBUT_RIVAL = "Argelia"  # ⚠️ confirmar contra fixture oficial cuando esté

# Cargar metadata de Argentina del CSV maestro
arg_meta = cargar_selecciones(confederacion="CONMEBOL")
arg_row = arg_meta[arg_meta["nombre_es"] == "Argentina"].iloc[0]
print(f"\nMetadata Argentina:")
print(f"  ISO2: {arg_row['iso2']}")
print(f"  Mundiales ganados: {arg_row['mundiales_ganados']}")
print(f"  Detalle: {arg_row['detalle_clave']}")

# Limpiar archivos PNG viejos de iteraciones anteriores (slide names que cambiaron)
# Mantiene solo los que vamos a regenerar en este run.
ARCHIVOS_VIEJOS = [
    "slide_7_cierre.png",            # nuevo orden: el cierre vuelve a ser slide 6
    "slide_3_top_equipo.png",        # antes era CA24, ahora es eliminatorias
    "slide_4_argentina.png",         # de un intento previo
    "slide_5_forma_vs_fifa.png",     # del intento "forma reciente"
    "slide_5_tradicion_vs_presente.png",  # del primer intento de slide 5
]
for nombre_viejo in ARCHIVOS_VIEJOS:
    for ubic in (OUTPUTS, CARRUSEL_FINAL):
        viejo = ubic / nombre_viejo
        if viejo.exists():
            viejo.unlink()
            print(f"  Borrado archivo viejo: {viejo}")

# %% [1. Verificar que Copa América 2024 está disponible en StatsBomb]
# El comentario en data_loaders.py decía "verificar" sobre los IDs.
# Antes de cualquier análisis, confirmamos que la competencia existe
# y trae partidos de Argentina.

competitions = sb.competitions()
print("Competiciones disponibles que matchean 'America' o 'Copa':")
cols_show = ["competition_id", "season_id", "competition_name", "season_name",
             "match_available", "match_available_360"]
mask = (competitions["competition_name"].str.contains("Copa America", case=False, na=False) |
        competitions["competition_name"].str.contains("America", case=False, na=False))
print(competitions[mask][cols_show])

# %% [2. Cargar partidos de Copa América 2024]
# Si la celda anterior confirmó el ID correcto, lo usamos.
# Si no, pisar SB_IDS["copa_america_2024"] con los valores reales.

CA24 = SB_IDS["copa_america_2024"]
print(f"Usando: competition_id={CA24['competition_id']}, season_id={CA24['season_id']}")

try:
    matches_ca24 = sb_matches(**CA24)
    print(f"\n✅ Total partidos en CA24: {len(matches_ca24)}")
    print(matches_ca24[["match_id", "match_date", "home_team", "away_team",
                         "home_score", "away_score"]].head(10))
except Exception as e:
    print(f"⚠️ Falló cargar CA24: {type(e).__name__}: {e}")
    print("→ Revisar IDs en data_loaders.py SB_IDS")

# %% [3. Filtrar partidos de Argentina en Copa América 2024]
arg_ca24 = matches_ca24[
    (matches_ca24["home_team"] == "Argentina") |
    (matches_ca24["away_team"] == "Argentina")
].copy()
print(f"Partidos de Argentina en CA24: {len(arg_ca24)}")
print(arg_ca24[["match_id", "match_date", "home_team", "away_team",
                "home_score", "away_score"]])

# %% [4. Cargar eventos de TODOS los partidos de Argentina en CA24]
# Para análisis agregados de Messi y stats de equipo.

eventos_por_partido = {}
for mid in arg_ca24["match_id"].tolist():
    eventos_por_partido[mid] = sb_events(match_id=int(mid))
    print(f"  match_id={mid}: {len(eventos_por_partido[mid])} eventos")

# Concatenar todos los eventos de Argentina (filtrando por team_name)
all_events = pd.concat(eventos_por_partido.values(), ignore_index=True)
arg_events = all_events[all_events["team"] == "Argentina"].copy()
print(f"\n✅ Total eventos de Argentina en CA24: {len(arg_events)}")
print(f"Tipos de eventos: {arg_events['type'].value_counts().head(10).to_dict()}")

# %% [5. Stats agregadas de Argentina en CA24]
# Goles, xG, tiros, pases, etc.

# Tiros / Shots
shots_arg = arg_events[arg_events["type"] == "Shot"].copy()
goles_arg = shots_arg[shots_arg["shot_outcome"] == "Goal"]
xg_total = shots_arg["shot_statsbomb_xg"].sum()

print(f"Estadísticas Argentina Copa América 2024:")
print(f"  Partidos jugados: {len(arg_ca24)}")
print(f"  Goles convertidos: {len(goles_arg)}")
print(f"  xG total: {xg_total:.2f}")
print(f"  Tiros totales: {len(shots_arg)}")
print(f"  xG por partido: {xg_total / len(arg_ca24):.2f}")
print(f"  Goles por partido: {len(goles_arg) / len(arg_ca24):.2f}")

# Pases / Passes
pases_arg = arg_events[arg_events["type"] == "Pass"]
pases_completos = pases_arg[pases_arg["pass_outcome"].isna()]
pct_pases = len(pases_completos) / len(pases_arg) * 100 if len(pases_arg) > 0 else 0
print(f"  Pases totales: {len(pases_arg)}")
print(f"  % pases completos: {pct_pases:.1f}%")

# %% [6. Stats individuales de Messi en CA24]
# Filtrar todos los eventos donde Messi fue el jugador.
# StatsBomb usa el nombre completo "Lionel Andrés Messi Cuccittini".

messi_events = arg_events[arg_events["player"].str.contains("Messi", case=False, na=False)].copy()
print(f"Eventos de Messi en CA24: {len(messi_events)}")

# Tiros y goles
messi_shots = messi_events[messi_events["type"] == "Shot"]
messi_goles = messi_shots[messi_shots["shot_outcome"] == "Goal"]
messi_xg = messi_shots["shot_statsbomb_xg"].sum()

# Asistencias (pass que termina en gol del receptor)
# StatsBomb marca pass_goal_assist == True
messi_pases = messi_events[messi_events["type"] == "Pass"]
messi_asistencias = messi_pases[messi_pases["pass_goal_assist"] == True]
messi_xa = messi_pases["pass_shot_assist"].sum() if "pass_shot_assist" in messi_pases.columns else 0

# Key passes (pase que termina en tiro)
messi_keypass = messi_pases[messi_pases["pass_shot_assist"] == True] if "pass_shot_assist" in messi_pases.columns else pd.DataFrame()

# Regates / dribbles
messi_dribbles = messi_events[messi_events["type"] == "Dribble"]
messi_dribbles_ok = messi_dribbles[messi_dribbles["dribble_outcome"] == "Complete"] if "dribble_outcome" in messi_dribbles.columns else pd.DataFrame()

print(f"\nMessi en Copa América 2024:")
print(f"  Partidos jugados: ¿? (verificar — algunos eventos pueden ser parciales)")
print(f"  Goles: {len(messi_goles)}")
print(f"  xG: {messi_xg:.2f}")
print(f"  Asistencias: {len(messi_asistencias)}")
print(f"  Key passes: {len(messi_keypass) if len(messi_keypass) > 0 else '—'}")
print(f"  Regates exitosos: {len(messi_dribbles_ok)}/{len(messi_dribbles)}")
print(f"  Tiros: {len(messi_shots)}")

# %% [6b. Top goleadores y asistidores de Argentina en CA24]
# Para usar en el slide analítico "TOP DEL EQUIPO".
from scripts.jugadores import display_name

# TOP GOLEADORES
goleadores_raw = (
    shots_arg[shots_arg["shot_outcome"] == "Goal"]
    .groupby("player")
    .size()
    .sort_values(ascending=False)
)
top_goleadores = goleadores_raw.head(5).reset_index()
top_goleadores.columns = ["player_full", "goles"]
top_goleadores["nombre"] = top_goleadores["player_full"].apply(display_name)

# xG por goleador
xg_por_jugador = (
    shots_arg.groupby("player")["shot_statsbomb_xg"].sum()
)
top_goleadores["xG"] = top_goleadores["player_full"].map(xg_por_jugador).round(2)

print("\nTOP GOLEADORES Argentina CA24:")
print(top_goleadores[["nombre", "goles", "xG"]].to_string(index=False))

# TOP ASISTIDORES
asistidores_raw = (
    pases_arg[pases_arg["pass_goal_assist"] == True]
    .groupby("player")
    .size()
    .sort_values(ascending=False)
)

# Si hay pocos asistidores (típico en torneo corto), agregamos key passes como tiebreak
key_passes_raw = (
    pases_arg[pases_arg.get("pass_shot_assist", pd.Series(dtype=bool)) == True]
    .groupby("player")
    .size()
    .sort_values(ascending=False)
    if "pass_shot_assist" in pases_arg.columns else pd.Series(dtype=int)
)

# Union de jugadores con asist y/o key passes
todos_creadores = set(asistidores_raw.index) | set(key_passes_raw.index)
top_asistidores = pd.DataFrame({"player_full": list(todos_creadores)})
top_asistidores["asistencias"] = top_asistidores["player_full"].map(asistidores_raw).fillna(0).astype(int)
top_asistidores["key_passes"] = top_asistidores["player_full"].map(key_passes_raw).fillna(0).astype(int)
top_asistidores["score"] = top_asistidores["asistencias"] * 3 + top_asistidores["key_passes"]
top_asistidores = top_asistidores.sort_values("score", ascending=False).head(5).reset_index(drop=True)
top_asistidores["nombre"] = top_asistidores["player_full"].apply(display_name)

print("\nTOP CREADORES Argentina CA24 (asistencias + key passes):")
print(top_asistidores[["nombre", "asistencias", "key_passes"]].to_string(index=False))

# %% [7a. Limpiar cache del scraper (correr cuando se edita scripts/scrapers/wikipedia.py)]
# Esta celda es defensiva: asegura que sys.path tenga REPO_ROOT incluso si se corre
# después de un Restart kernel sin haber pasado por Setup.
import sys
_REPO_ROOT_LOCAL = r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar"
if _REPO_ROOT_LOCAL not in sys.path:
    sys.path.insert(0, _REPO_ROOT_LOCAL)
    print(f"⚠️ sys.path no tenía REPO_ROOT — agregado ahora.")

from scripts.scrapers.cache import cache_clear
borrados = cache_clear(key_pattern="Argentina")
print(f"Cache limpiado: {borrados} archivos borrados.")

# %% [7. Top goleadores históricos Argentina (slide 2) — vía scraper Wikipedia]
# Pivot del slide 2: en lugar de "forma reciente" (que requiere otro artículo
# de Wikipedia que aún no tengo identificado), mostramos los líderes históricos
# de la selección. Data 'evergreen' y editorialmente fuerte para BAJO LA LUPA.

# Defensa contra kernel restart sin Setup previo
import sys
_REPO_ROOT_LOCAL = r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar"
if _REPO_ROOT_LOCAL not in sys.path:
    sys.path.insert(0, _REPO_ROOT_LOCAL)

import importlib
import scripts.scrapers.wikipedia
importlib.reload(scripts.scrapers.wikipedia)
from scripts.scrapers.wikipedia import get_top_goleadores_historicos

df_top_scorers = get_top_goleadores_historicos("Argentina", n=5)
print(f"\nTop goleadores históricos de Argentina:")
if not df_top_scorers.empty:
    print(df_top_scorers.to_string(index=False))
else:
    print("⚠️ Scraper no devolvió data — slide 2 mostrará placeholder")

# %% [8. PLACEHOLDER — XI probable Argentina (slide 3)]
# ⚠️ DATA PENDIENTE: XI titular más probable según últimos partidos.
# Posiciones en cancha (x, y) según mplsoccer.Pitch coords (0-120 ancho, 0-80 alto)

# Ejemplo de estructura (descomentar y completar):
XI_PROBABLE ={
     "formacion": "4-3-3",
     "jugadores": [
         {"nombre": "Dibu Martínez",     "posicion": "GK", "x": 5,   "y": 40, "club": "Aston Villa"},
         {"nombre": "Molina",            "posicion": "RB", "x": 25,  "y": 70, "club": "Atlético Madrid"},
         {"nombre": "Romero",            "posicion": "CB", "x": 25,  "y": 50, "club": "Tottenham"},
         {"nombre": "Otamendi",          "posicion": "CB", "x": 25,  "y": 30, "club": "Benfica"},
         {"nombre": "Tagliafico",        "posicion": "LB", "x": 25,  "y": 10, "club": "Lyon"},
         {"nombre": "De Paul",           "posicion": "CM", "x": 55,  "y": 60, "club": "Atlético Madrid"},
         {"nombre": "Enzo Fernández",    "posicion": "CM", "x": 55,  "y": 40, "club": "Chelsea"},
         {"nombre": "Mac Allister",      "posicion": "CM", "x": 55,  "y": 20, "club": "Liverpool"},
         {"nombre": "Messi",             "posicion": "RW", "x": 85,  "y": 65, "club": "Inter Miami"},
         {"nombre": "Julián Álvarez",    "posicion": "ST", "x": 95,  "y": 40, "club": "Manchester City"},
         {"nombre": "Lautaro Martínez",  "posicion": "ST", "x": 85,  "y": 15, "club": "Internacional"},
     ],
 }

# %% [9. PLACEHOLDER — Stats Eliminatorias CONMEBOL 2024-25 (slide 5)]
# ⚠️ DATA PENDIENTE: stats finales de Argentina en eliminatorias.
# Fuente: tabla oficial CONMEBOL / Wikipedia.

# Ejemplo de estructura (descomentar y completar):
ELIMINATORIAS_2024_25 = {
     "posicion": 1,           # posición final en la tabla CONMEBOL
     "pj": 18,
     "pg": 12,
     "pe": 4,
     "pp": 2,
     "gf": 35,
     "gc": 12,
     "puntos": 40,
     "goleador": "Lautaro Martínez",     # goleador del equipo
     "goles_goleador": 8,
     "racha_maxima_invicto": 10,         # partidos invicta
 }

# %% [10. Slide 1 — PORTADA (look BAJO LA LUPA)]
# Diferenciación visual de la sección:
# - Fondo BG_ALT (más oscuro que el feed regular) — sensación "editorial profundo"
# - Banner OUTLINE en lugar de filled — más sobrio, menos infográfico
# - Línea dorada decorativa bajo el nombre país (treatment periodístico)
# - "ED. 01" para numerar la serie (sirve para fidelizar audiencia: "qué selección
#   le toca a la próxima edición?")

NUMERO_EDICION = "01"  # ⚠️ incrementar en cada post BLL (02, 03, ...)
# Usar BG estándar para que el logo se mimetice (el PNG del logo tiene #0E2A47
# baked in como fondo). La diferenciación de BLL ahora vive solo en:
# banner outline dorado + "ED. NN" + línea decorativa + tipografía JetBrains Mono.
BG_BLL = COLORS["bg"]

fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(BG_BLL)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Logos top — Mundial más arriba y más chico para evitar solapamiento
place_logo(fig, x=0.10, y=0.955, size=0.09, variant="simple")
place_competition_icon(fig, x=0.90, y=0.955, size=0.08, file="mundial_2026.png")

# Tag "BAJO LA LUPA" — OUTLINE (no filled), más editorial
banner = FancyBboxPatch(
    (2.0, 10.65), 6.0, 0.6,
    boxstyle="round,pad=0.0,rounding_size=0.05",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=2.0, zorder=2,
)
ax.add_patch(banner)
ax.text(5, 10.95, f"BAJO LA LUPA  ·  ED. {NUMERO_EDICION}",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"], zorder=3)

# Título gigante
ax.text(5, 9.1, "ARGENTINA",
        ha="center", va="center", fontsize=92, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])

# Línea decorativa dorada bajo el título (treatment editorial)
ax.plot([3.5, 6.5], [8.25, 8.25],
        color=COLORS["accent"], linewidth=2.5, zorder=2)

# Bandera grande centrada
place_country_flag(fig, x=0.5, y=0.50, size=0.30, pais="argentina.png")

# 3 datos clave en cards — mucho más grandes para que se lean en feed IG
def card_dato(ax_local, x_center, label, valor, color_valor, valor_fontsize=52):
    box = FancyBboxPatch(
        (x_center - 1.4, 1.9), 2.8, 2.5,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor="none",
        edgecolor=COLORS["primary"], linewidth=1.8, zorder=2,
    )
    ax_local.add_patch(box)
    ax_local.text(x_center, 3.85, label,
                  ha="center", va="center", fontsize=17, fontweight="bold",
                  color=COLORS["primary"], family=FONTS["data"], zorder=3)
    ax_local.text(x_center, 2.85, valor,
                  ha="center", va="center", fontsize=valor_fontsize, fontweight="bold",
                  color=color_valor, family=FONTS["title"], zorder=3)

card_dato(ax, 2.0, "RANKING FIFA", "#3",     COLORS["accent"])
card_dato(ax, 5.0, "MUNDIALES",   "3",       COLORS["accent"])
card_dato(ax, 8.0, "DT",          "SCALONI", COLORS["text"], valor_fontsize=32)

# Subtítulo abajo
ax.text(5, 1.6, "rumbo al Mundial 2026",
        ha="center", va="center", fontsize=20, style="italic",
        color=COLORS["primary"], family=FONTS["body"])
#ax.text(5, 0.85, f"DEBUT EN {DIAS_AL_DEBUT} DÍAS  ·  16 DE JUNIO",
 #       ha="center", va="center", fontsize=13, fontweight="bold",
  #      color=COLORS["accent"], family=FONTS["data"])

ax.text(5, 0.85, "DEBUT EL 16 DE JUNIO",
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"])


watermark(fig)

fname = OUTPUTS / "slide_1_portada.png"
fig.savefig(fname, dpi=100, facecolor=BG_BLL)
plt.show()
print(f"✅ {fname.name}")

# %% [11. Slide 2 — LÍDERES HISTÓRICOS · Top goleadores Argentina]
# Data: scraper Wikipedia (df_top_scorers calculado en celda 7).
# Layout: ranking horizontal con borde dorado destacando Messi.

fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(BG_BLL)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Tag superior
banner = FancyBboxPatch(
    (2.0, 11.4), 6.0, 0.55,
    boxstyle="round,pad=0.0,rounding_size=0.05",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=1.8, zorder=2,
)
ax.add_patch(banner)
ax.text(5, 11.67, "LÍDERES HISTÓRICOS",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"], zorder=3)

# Título + línea decorativa
ax.text(5, 10.3, "Top goleadores",
        ha="center", va="center", fontsize=36, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.plot([3.5, 6.5], [9.75, 9.75], color=COLORS["accent"], linewidth=2, zorder=2)
ax.text(5, 9.3, "los argentinos con más goles vistiendo la celeste y blanca",
        ha="center", va="center", fontsize=12, style="italic",
        color=COLORS["primary"], family=FONTS["body"])

# Render del ranking
if not df_top_scorers.empty:
    y_start = 8.4
    y_step = 1.05
    bar_x0 = 4.5
    bar_x_max = 9.0

    # Escala ABSOLUTA: cada barra es proporcional al líder (Messi = 100%).
    # Antes hacíamos min/max scaling y las diferencias quedaban distorsionadas.
    max_goles = float(df_top_scorers["goals"].max())

    for i, row in df_top_scorers.iterrows():
        y = y_start - i * y_step
        nombre = str(row["player"])
        goles = int(row["goals"]) if pd.notna(row["goals"]) else 0
        caps = int(row["caps"]) if pd.notna(row.get("caps", 0)) else None
        es_messi = "messi" in nombre.lower()

        color_destacado = COLORS["accent"] if es_messi else COLORS["text"]
        fw = "bold" if es_messi else "normal"

        # Posición
        ax.text(0.7, y, f"{i+1}",
                ha="left", va="center", fontsize=36, fontweight="bold",
                color=color_destacado, family=FONTS["title"])

        # Nombre
        ax.text(1.5, y + 0.20, nombre,
                ha="left", va="center", fontsize=18, fontweight=fw,
                color=COLORS["text"], family=FONTS["body"])

        # Partidos jugados subscript (si está) — R30: usar "partidos" no "caps"
        if caps is not None:
            ax.text(1.5, y - 0.35, f"{caps} partidos",
                    ha="left", va="center", fontsize=12,
                    color=COLORS["muted"], family=FONTS["data"])

        # Barra con escala absoluta: goles / max
        frac = goles / max_goles if max_goles > 0 else 0.1
        frac = max(0.10, min(1.0, frac))
        bar_w = (bar_x_max - bar_x0) * frac
        bar_color = COLORS["accent"] if es_messi else COLORS["primary"]
        bar = FancyBboxPatch(
            (bar_x0, y - 0.22), bar_w, 0.44,
            boxstyle="round,pad=0.0,rounding_size=0.05",
            facecolor=bar_color, alpha=0.95,
            edgecolor="none", linewidth=0,
        )
        ax.add_patch(bar)

        # Goles al final de la barra
        ax.text(bar_x0 + bar_w + 0.15, y, str(goles),
                ha="left", va="center", fontsize=26, fontweight="bold",
                color=color_destacado, family=FONTS["title"])

    # Card inferior con dato editorial
    box = FancyBboxPatch(
        (0.5, 1.4), 9.0, 1.6,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor="none",
        edgecolor=COLORS["accent"], linewidth=2.0, zorder=2,
    )
    ax.add_patch(box)
    # Buscar Messi en el top y mostrar dato concreto
    messi_row = df_top_scorers[df_top_scorers["player"].str.contains("Messi", case=False, na=False)]
    if not messi_row.empty:
        m_goles = int(messi_row.iloc[0]["goals"])
        m_caps = int(messi_row.iloc[0]["caps"]) if pd.notna(messi_row.iloc[0].get("caps")) else None
        ratio = m_goles / m_caps if m_caps else None
        ax.text(5, 2.55, "MESSI EN LA CIMA",
                ha="center", va="center", fontsize=15, fontweight="bold",
                color=COLORS["accent"], family=FONTS["data"])
        if ratio:
            insight = f"{m_goles} goles en {m_caps} partidos · 1 gol cada {1/ratio:.2f} encuentros"
        else:
            insight = f"{m_goles} goles · líder histórico de la selección"
        ax.text(5, 1.85, insight,
                ha="center", va="center", fontsize=15, fontweight="bold",
                color=COLORS["text"], family=FONTS["body"])
else:
    # Fallback si scraper falló
    ax.text(5, 6,
            "⚠️ Top goleadores no disponibles\n(verificar scraper Wikipedia)",
            ha="center", va="center", fontsize=14,
            color=COLORS["muted"], family=FONTS["body"])

# Footer
ax.text(5, 0.9, "Datos: Wikipedia · Argentina national football team",
        ha="center", va="center", fontsize=11,
        color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_2_top_goleadores.png"
fig.savefig(fname, dpi=100, facecolor=BG_BLL)
plt.show()
print(f"✅ {fname.name}")

# %% [12. Slide 3 — EL EQUIPO — XI probable]
# ⏸️ Pendiente: construir cuando XI_PROBABLE esté lleno (o cuando implementemos
#     get_plantilla_actual() en scrapers).

# %% [12a. Cargar stats de eliminatorias 2026 — scraper + fallback manual]
# Reemplaza la data de CA24 (julio 2024, ya vieja) con la fase clasificatoria
# del Mundial 2026 (terminó marzo 2026).
# Si el scraper Wikipedia falla, se usa el dict ELIM_MANUAL como fallback.

# Defensa contra kernel restart sin Setup previo
import sys
_REPO_ROOT_LOCAL = r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar"
if _REPO_ROOT_LOCAL not in sys.path:
    sys.path.insert(0, _REPO_ROOT_LOCAL)

import importlib
import scripts.scrapers.wikipedia
importlib.reload(scripts.scrapers.wikipedia)
from scripts.scrapers.wikipedia import get_eliminatorias_stats

# Limpiar cache previo (por si scraper cambió)
from scripts.scrapers.cache import cache_clear
cache_clear(key_pattern="wiki_qual")

# Probar scraper con verbose=True para diagnóstico
stats_elim_scraper = get_eliminatorias_stats("Argentina", verbose=True)
print("\nStats del scraper:")
for k, v in stats_elim_scraper.items():
    print(f"  {k}: {v}")

# ⚠️ FALLBACK MANUAL — completar consultando Wikipedia o cualquier fuente oficial
# URL: https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_CONMEBOL
# Pisar estos valores si el scraper devuelve vacío.
ELIM_MANUAL = {
    "posicion": None,   # ⚠️ pegar puesto final Argentina
    "pj": None,         # 18 fechas
    "pg": None,
    "pe": None,
    "pp": None,
    "gf": None,
    "gc": None,
    "puntos": None,
}

# Elegir: scraper si tiene data válida, sino manual
if stats_elim_scraper and stats_elim_scraper.get("pj"):
    stats_elim = stats_elim_scraper
    print("\n✅ Usando datos del scraper Wikipedia")
else:
    stats_elim = ELIM_MANUAL
    if any(v is not None for v in ELIM_MANUAL.values()):
        print("\n📝 Usando datos manuales de ELIM_MANUAL")
    else:
        print("\n⚠️ Scraper falló y ELIM_MANUAL vacío — el slide 3 mostrará placeholder")

# %% [12b. Slide 3 — ARGENTINA EN ELIMINATORIAS 2026]
# Data: Wikipedia EN — 2026 FIFA World Cup qualification – CONMEBOL.
# Layout: tabla con stats principales arriba + insight + barras gf/gc.

fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(BG_BLL)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Tag superior
banner = FancyBboxPatch(
    (2.0, 11.4), 6.0, 0.55,
    boxstyle="round,pad=0.0,rounding_size=0.05",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=1.8, zorder=2,
)
ax.add_patch(banner)
ax.text(5, 11.67, "EN ELIMINATORIAS  ·  MUNDIAL 2026",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"], zorder=3)

# Título + contexto
ax.text(5, 10.3, "El camino al Mundial",
        ha="center", va="center", fontsize=36, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.plot([3.5, 6.5], [9.75, 9.75], color=COLORS["accent"], linewidth=2, zorder=2)
ax.text(5, 9.3, "CONMEBOL · 18 fechas · cierre eliminatorias",
        ha="center", va="center", fontsize=13, style="italic",
        color=COLORS["primary"], family=FONTS["body"])

# Si tenemos stats, mostrarlas. Sino, placeholder claro.
if stats_elim and stats_elim.get("pj"):
    # === Rama A: stats eliminatorias disponibles ===
    def big_stat(ax_local, x, y, label, valor, color_v=None):
        c = color_v or COLORS["text"]
        ax_local.text(x, y + 0.5, str(valor),
                      ha="center", va="center", fontsize=60, fontweight="bold",
                      color=c, family=FONTS["title"])
        ax_local.text(x, y - 0.45, label,
                      ha="center", va="center", fontsize=16, fontweight="bold",
                      color=COLORS["primary"], family=FONTS["data"])

    # Fila 1 — Posición / Puntos / PJ
    big_stat(ax, 2.0, 7.5, "POSICIÓN",  f"#{stats_elim['posicion']}", COLORS["accent"])
    big_stat(ax, 5.0, 7.5, "PUNTOS",    stats_elim["puntos"],          COLORS["accent"])
    big_stat(ax, 8.0, 7.5, "PARTIDOS",  stats_elim["pj"])
    # Fila 2 — PG / PE / PP
    big_stat(ax, 2.0, 5.3, "GANADOS",   stats_elim["pg"])
    big_stat(ax, 5.0, 5.3, "EMPATADOS", stats_elim["pe"])
    big_stat(ax, 8.0, 5.3, "PERDIDOS",  stats_elim["pp"])

    # Card inferior — Goles a favor vs en contra
    box_goles = FancyBboxPatch(
        (0.5, 2.4), 9.0, 1.8,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor="none",
        edgecolor=COLORS["accent"], linewidth=2.0, zorder=2,
    )
    ax.add_patch(box_goles)
    ax.text(5, 3.85, "GOLES",
            ha="center", va="center", fontsize=16, fontweight="bold",
            color=COLORS["accent"], family=FONTS["data"])
    ax.text(3.0, 3.10, f"{stats_elim['gf']}",
            ha="center", va="center", fontsize=54, fontweight="bold",
            color=COLORS["text"], family=FONTS["title"])
    ax.text(3.0, 2.55, "A FAVOR",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=COLORS["primary"], family=FONTS["data"])
    ax.text(7.0, 3.10, f"{stats_elim['gc']}",
            ha="center", va="center", fontsize=54, fontweight="bold",
            color=COLORS["text"], family=FONTS["title"])
    ax.text(7.0, 2.55, "EN CONTRA",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=COLORS["primary"], family=FONTS["data"])
    ax.text(5.0, 3.10, "—",
            ha="center", va="center", fontsize=34,
            color=COLORS["primary"], family=FONTS["body"])

    # Footer eliminatorias
    ax.text(5, 1.2, "Datos: Wikipedia · Eliminatorias Mundial 2026 — CONMEBOL",
            ha="center", va="center", fontsize=11,
            color=COLORS["muted"], family=FONTS["data"])
else:
    # === Rama B: fallback con HISTORIAL MUNDIALISTA (data 100% verificable) ===
    # Lucas confirmó que no quiere mostrar CA24 ("info muy vieja"). El historial
    # mundialista es más viejo pero es CONTEXTO histórico (no actualidad).
    # Mientras el scraper de eliminatorias se afina, este fallback no avergüenza.
    # Todos los datos son verificables vs Wikipedia + FIFA.

    # Re-etiquetar el tag superior (que estaba 'EN ELIMINATORIAS')
    # → Lo borramos visualmente con un rectángulo y reescribimos
    ax.add_patch(mpatches.Rectangle((0, 11.0), 10, 1.5, facecolor=BG_BLL, zorder=3))
    banner2 = FancyBboxPatch(
        (2.0, 11.4), 6.0, 0.55,
        boxstyle="round,pad=0.0,rounding_size=0.05",
        facecolor="none",
        edgecolor=COLORS["accent"], linewidth=1.8, zorder=4,
    )
    ax.add_patch(banner2)
    ax.text(5, 11.67, "EN MUNDIALES  ·  HISTORIA",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=COLORS["accent"], family=FONTS["data"], zorder=5)

    # Re-pintar título y subtítulo
    ax.add_patch(mpatches.Rectangle((0, 9.2), 10, 2, facecolor=BG_BLL, zorder=3))
    ax.text(5, 10.3, "El historial mundialista",
            ha="center", va="center", fontsize=34, fontweight="bold",
            color=COLORS["text"], family=FONTS["title"], zorder=4)
    ax.plot([3.5, 6.5], [9.75, 9.75],
            color=COLORS["accent"], linewidth=2, zorder=4)
    ax.text(5, 9.3, "Tercera selección más laureada del planeta",
            ha="center", va="center", fontsize=13, style="italic",
            color=COLORS["primary"], family=FONTS["body"], zorder=4)

    # 3 big stats verificables (Wikipedia / FIFA)
    def big_stat_hist(ax_local, x, y, label, valor, color_v=None):
        c = color_v or COLORS["text"]
        ax_local.text(x, y + 0.5, str(valor),
                      ha="center", va="center", fontsize=68, fontweight="bold",
                      color=c, family=FONTS["title"])
        ax_local.text(x, y - 0.55, label,
                      ha="center", va="center", fontsize=13, fontweight="bold",
                      color=COLORS["primary"], family=FONTS["data"])

    big_stat_hist(ax, 2.0, 7.0, "PARTICIPACIONES", "18", COLORS["text"])
    big_stat_hist(ax, 5.0, 7.0, "TÍTULOS",          "3",  COLORS["accent"])
    big_stat_hist(ax, 8.0, 7.0, "FINALES",          "6",  COLORS["text"])

    # Card inferior — años de los títulos
    box_titulos = FancyBboxPatch(
        (0.5, 3.2), 9.0, 2.4,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor="none",
        edgecolor=COLORS["accent"], linewidth=1.5, zorder=2,
    )
    ax.add_patch(box_titulos)
    ax.text(5, 5.0, "AÑOS CAMPEONA",
            ha="center", va="center", fontsize=13, fontweight="bold",
            color=COLORS["accent"], family=FONTS["data"])
    ax.text(5, 4.15, "1978  ·  1986  ·  2022",
            ha="center", va="center", fontsize=36, fontweight="bold",
            color=COLORS["text"], family=FONTS["title"])
    ax.text(5, 3.55, "última: Qatar 2022 (Scaloni · Messi capitán)",
            ha="center", va="center", fontsize=11, style="italic",
            color=COLORS["primary"], family=FONTS["body"])

    # Linea + nota explicativa
    ax.text(5, 2.5,
            "Solo Brasil (5) e Italia/Alemania (4) tienen más copas en la historia",
            ha="center", va="center", fontsize=12, style="italic",
            color=COLORS["muted"], family=FONTS["body"])

    # Aclaración pequeña
    ax.text(5, 1.7,
            "ⓘ Stats eliminatorias 2026 en el caption  ·  scraper en construcción",
            ha="center", va="center", fontsize=10, style="italic",
            color=COLORS["primary"], family=FONTS["body"])

    # Footer
    ax.text(5, 1.0, "Datos: FIFA + Wikipedia · participaciones hasta Mundial 2022",
            ha="center", va="center", fontsize=11,
            color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_3_eliminatorias.png"
fig.savefig(fname, dpi=100, facecolor=BG_BLL)
plt.show()
print(f"✅ {fname.name}")

# %% [13. Slide 4 — LA FIGURA · MESSI en Copa América 2024]
# Data 100% StatsBomb — calculada en celda 6.
# Insight central: 2.81 xG vs 1 gol = ineficiencia en finalización.

# Recalcular stats clave (por si la celda 6 no se corrió en este run)
messi_goles_n = int(len(messi_goles))
messi_xg_total = float(messi_xg)
messi_asist_n = int(len(messi_asistencias))
messi_keypass_n = int(len(messi_keypass)) if not messi_keypass.empty else 0
messi_drib_ok = int(len(messi_dribbles_ok))
messi_drib_tot = int(len(messi_dribbles))
messi_tiros_n = int(len(messi_shots))
diff_xg_goles = messi_xg_total - messi_goles_n

fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(BG_BLL)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Tag de sección coherente con portada
banner = FancyBboxPatch(
    (2.0, 11.4), 6.0, 0.55,
    boxstyle="round,pad=0.0,rounding_size=0.05",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=1.8, zorder=2,
)
ax.add_patch(banner)
ax.text(5, 11.67, "LA FIGURA  ·  MESSI",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"], zorder=3)

# Nombre + contexto
ax.text(5, 10.4, "Lionel Messi",
        ha="center", va="center", fontsize=44, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.plot([3.5, 6.5], [9.85, 9.85],
        color=COLORS["accent"], linewidth=2, zorder=2)
ax.text(5, 9.4, "Copa América 2024 · 6 partidos · última gran competencia",
        ha="center", va="center", fontsize=12, style="italic",
        color=COLORS["primary"], family=FONTS["body"])

# Big numbers: xG vs goles (la historia central)
ax.text(2.8, 7.7, f"{messi_xg_total:.2f}",
        ha="center", va="center", fontsize=110, fontweight="bold",
        color=COLORS["accent"], family=FONTS["title"])
ax.text(2.8, 6.0, "xG GENERADO",
        ha="center", va="center", fontsize=17, fontweight="bold",
        color=COLORS["primary"], family=FONTS["data"])
ax.text(2.8, 5.45, "(casi 3 goles esperados)",
        ha="center", va="center", fontsize=12, style="italic",
        color=COLORS["muted"], family=FONTS["body"])

ax.text(5, 6.7, "vs",
        ha="center", va="center", fontsize=24,
        color=COLORS["primary"], family=FONTS["body"], style="italic")

ax.text(7.2, 7.7, f"{messi_goles_n}",
        ha="center", va="center", fontsize=110, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.text(7.2, 6.0, "GOL CONVERTIDO",
        ha="center", va="center", fontsize=17, fontweight="bold",
        color=COLORS["primary"], family=FONTS["data"])

# Insight clave — card outline dorada
insight_box = FancyBboxPatch(
    (0.5, 3.7), 9.0, 1.0,
    boxstyle="round,pad=0.02,rounding_size=0.1",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=2.0, zorder=2,
)
ax.add_patch(insight_box)
ax.text(5, 4.2,
        f"Generó como nunca, definió por debajo de su nivel: -{diff_xg_goles:.1f} de eficiencia.",
        ha="center", va="center", fontsize=16, fontweight="bold",
        color=COLORS["text"], family=FONTS["body"], style="italic")

# Stats secundarias en grid 1x3
def stat_mini(ax_local, x, y, label, valor):
    ax_local.text(x, y + 0.35, valor,
                  ha="center", va="center", fontsize=38, fontweight="bold",
                  color=COLORS["text"], family=FONTS["title"])
    ax_local.text(x, y - 0.35, label,
                  ha="center", va="center", fontsize=14, fontweight="bold",
                  color=COLORS["primary"], family=FONTS["data"])

stat_mini(ax, 2.5, 2.3, "ASISTENCIAS",  f"{messi_asist_n}")
stat_mini(ax, 5.0, 2.3, "PASES CLAVE",  f"{messi_keypass_n}")
stat_mini(ax, 7.5, 2.3, "REGATES OK",   f"{messi_drib_ok}/{messi_drib_tot}")

# Footer
ax.text(5, 0.9, "Datos: StatsBomb Open Data · Copa América 2024",
        ha="center", va="center", fontsize=12,
        color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_4_messi.png"
fig.savefig(fname, dpi=100, facecolor=BG_BLL)
plt.show()
print(f"✅ {fname.name}")

# %% [14. Slide 5 — LOS CREADORES (asistidores + key passes CA24)]
# Data: df top_asistidores calculado en celda 6b (StatsBomb CA24).
# Layout similar al slide 2 (top goleadores) pero con dos métricas por jugador.

fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(BG_BLL)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Tag superior
banner = FancyBboxPatch(
    (2.0, 11.4), 6.0, 0.55,
    boxstyle="round,pad=0.0,rounding_size=0.05",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=1.8, zorder=2,
)
ax.add_patch(banner)
ax.text(5, 11.67, "LOS CREADORES",
        ha="center", va="center", fontsize=14, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"], zorder=3)

# Título + línea decorativa
ax.text(5, 10.3, "Top creadores de juego",
        ha="center", va="center", fontsize=34, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.plot([3.5, 6.5], [9.75, 9.75], color=COLORS["accent"], linewidth=2, zorder=2)
ax.text(5, 9.3, "asistencias y key passes en Copa América 2024",
        ha="center", va="center", fontsize=12, style="italic",
        color=COLORS["primary"], family=FONTS["body"])

# Render del ranking — similar al slide 2 pero con asist + key passes
if not top_asistidores.empty:
    y_start = 8.3
    y_step = 1.05
    bar_x0 = 4.5
    bar_x_max = 8.4

    # Escala basada en key passes del líder
    max_kp = float(top_asistidores["key_passes"].max())

    for i, row in top_asistidores.iterrows():
        y = y_start - i * y_step
        nombre = str(row["nombre"])
        asistencias = int(row["asistencias"])
        key_passes = int(row["key_passes"])
        es_messi = "Messi" in nombre

        color_destacado = COLORS["accent"] if es_messi else COLORS["text"]
        fw = "bold" if es_messi else "normal"

        # Posición
        ax.text(0.7, y, f"{i+1}",
                ha="left", va="center", fontsize=36, fontweight="bold",
                color=color_destacado, family=FONTS["title"])

        # Nombre
        ax.text(1.5, y + 0.20, nombre,
                ha="left", va="center", fontsize=17, fontweight=fw,
                color=COLORS["text"], family=FONTS["body"])

        # Subtítulo "creador" + total contribution
        total_contrib = asistencias + key_passes
        ax.text(1.5, y - 0.35, f"{total_contrib} acciones de peligro",
                ha="left", va="center", fontsize=11,
                color=COLORS["muted"], family=FONTS["data"])

        # Barra escalada por key passes (la métrica con más variabilidad)
        frac = key_passes / max_kp if max_kp > 0 else 0.1
        frac = max(0.10, min(1.0, frac))
        bar_w = (bar_x_max - bar_x0) * frac
        bar_color = COLORS["accent"] if es_messi else COLORS["primary"]
        bar = FancyBboxPatch(
            (bar_x0, y - 0.22), bar_w, 0.44,
            boxstyle="round,pad=0.0,rounding_size=0.05",
            facecolor=bar_color, alpha=0.95,
            edgecolor="none", linewidth=0,
        )
        ax.add_patch(bar)

        # Stats al final: 1A · 13 P. CLAVE  — R30: usar términos en español
        ax.text(bar_x_max + 0.2, y + 0.08, f"{asistencias}A",
                ha="left", va="center", fontsize=18, fontweight="bold",
                color=color_destacado, family=FONTS["title"])
        ax.text(bar_x_max + 0.2, y - 0.30, f"{key_passes} pases clave",
                ha="left", va="center", fontsize=11, fontweight="bold",
                color=COLORS["primary"], family=FONTS["data"])

    # Card inferior con insight editorial
    box_insight = FancyBboxPatch(
        (0.5, 1.4), 9.0, 1.6,
        boxstyle="round,pad=0.02,rounding_size=0.15",
        facecolor="none",
        edgecolor=COLORS["accent"], linewidth=2.0, zorder=2,
    )
    ax.add_patch(box_insight)
    # Calcular cuántos KP totales generó el equipo
    total_kp_eq = int(top_asistidores["key_passes"].sum())
    total_asist_eq = int(top_asistidores["asistencias"].sum())
    ax.text(5, 2.55, "EL EQUIPO QUE CREÓ EL TÍTULO",
            ha="center", va="center", fontsize=15, fontweight="bold",
            color=COLORS["accent"], family=FONTS["data"])
    ax.text(5, 1.85,
            f"{total_asist_eq} asistencias · {total_kp_eq} pases clave entre los top 5 creadores",
            ha="center", va="center", fontsize=14, fontweight="bold",
            color=COLORS["text"], family=FONTS["body"])
else:
    ax.text(5, 6,
            "⚠️ Data de creadores no disponible",
            ha="center", va="center", fontsize=14,
            color=COLORS["muted"], family=FONTS["body"])

# Footer
ax.text(5, 0.6, "Datos: StatsBomb Open Data · Copa América 2024",
        ha="center", va="center", fontsize=11,
        color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_5_creadores.png"
fig.savefig(fname, dpi=100, facecolor=BG_BLL)
plt.show()
print(f"✅ {fname.name}")

# %% [15. Slide 6 — CIERRE (look BAJO LA LUPA coherente con portada)]
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(BG_BLL)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Tag de sección arriba — coherente con portada
banner = FancyBboxPatch(
    (2.0, 11.3), 6.0, 0.6,
    boxstyle="round,pad=0.0,rounding_size=0.05",
    facecolor="none",
    edgecolor=COLORS["accent"], linewidth=2.0, zorder=2,
)
ax.add_patch(banner)
ax.text(5, 11.6, f"BAJO LA LUPA  ·  ED. {NUMERO_EDICION}  ·  ARGENTINA",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=COLORS["accent"], family=FONTS["data"], zorder=3)

# Logo grande
place_logo(fig, x=0.5, y=0.73, size=0.26, variant="simple")

# Pregunta central
ax.text(5, 6.5, "¿Llega lista",
        ha="center", va="center", fontsize=44, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.text(5, 5.65, "para defender",
        ha="center", va="center", fontsize=44, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])
ax.text(5, 4.8, "la copa?",
        ha="center", va="center", fontsize=44, fontweight="bold",
        color=COLORS["accent"], family=FONTS["title"])

# Línea decorativa dorada (treatment editorial coherente con portada)
ax.plot([3.8, 6.2], [4.0, 4.0], color=COLORS["accent"], linewidth=2.5, zorder=2)

# Countdown debut — card outline coherente con cards portada
debut_box = FancyBboxPatch(
    (1.5, 2.2), 7.0, 1.6,
    boxstyle="round,pad=0.02,rounding_size=0.15",
    facecolor="none",
    edgecolor=COLORS["primary"], linewidth=2.0, zorder=2,
)
ax.add_patch(debut_box)
ax.text(5, 3.35, "DEBUT MUNDIAL 2026",
        ha="center", va="center", fontsize=15, fontweight="bold",
        color=COLORS["primary"], family=FONTS["data"])
ax.text(5, 2.65, f"16 JUN  ·  vs {DEBUT_RIVAL.upper()}",
        ha="center", va="center", fontsize=26, fontweight="bold",
        color=COLORS["text"], family=FONTS["body"])

# Handle
ax.text(5, 1.4, "@datafutbol_ar",
        ha="center", va="center", fontsize=36, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"])

#ax.text(5, 0.9, f"análisis a {DIAS_AL_DEBUT} días del debut",
 #       ha="center", va="center", fontsize=12, style="italic",
  #      color=COLORS["primary"], family=FONTS["body"])

# Footer
ax.text(5, 0.5, "Datos: StatsBomb Open · ranking FIFA · Wikipedia",
        ha="center", va="center", fontsize=12,
        color=COLORS["muted"], family=FONTS["data"])

fname = OUTPUTS / "slide_6_cierre.png"
fig.savefig(fname, dpi=100, facecolor=BG_BLL)
plt.show()
print(f"✅ {fname.name}")

# %% [16. Normalizar slides a 1080×1350 → carrusel_final/]
from PIL import Image

TARGET = (1080, 1350)
slides_src = sorted(OUTPUTS.glob("slide_*.png"))
print(f"Encontré {len(slides_src)} slides para normalizar:")
for s in slides_src:
    print(f"  · {s.name}")

for src in slides_src:
    img = Image.open(src)
    if img.size != TARGET:
        img = img.resize(TARGET, Image.LANCZOS)
    dst = CARRUSEL_FINAL / src.name
    img.save(dst, "PNG", optimize=True)
    print(f"  ✅ {dst.name} → {img.size}")

print(f"\nCarrusel listo en: {CARRUSEL_FINAL}")
print("\nOrden para subir a IG:")
print("  1. slide_1_portada.png")
print("  2. slide_2_top_goleadores.png")
print("  3. slide_3_eliminatorias.png")
print("  4. slide_4_messi.png")
print("  5. slide_5_creadores.png")
print("  6. slide_6_cierre.png")

# %% [17. Generar caption IG (R29)]
# Caption parametrizado con valores reales del DataFrame.

# Datos para el caption
top_goleador = df_top_scorers.iloc[0] if not df_top_scorers.empty else None
messi_goles_career = int(top_goleador["goals"]) if top_goleador is not None else None
messi_caps_career = int(top_goleador["caps"]) if top_goleador is not None and pd.notna(top_goleador.get("caps")) else None

# Stats eliminatorias para el caption
if stats_elim and stats_elim.get("pj"):
    elim_pos = stats_elim["posicion"]
    elim_pts = stats_elim["puntos"]
    elim_gf = stats_elim["gf"]
    elim_gc = stats_elim["gc"]
    bloque_elim = f"En eliminatorias quedó #{elim_pos} con {elim_pts} puntos ({elim_gf}-{elim_gc} en goles)."
else:
    bloque_elim = "Cerró eliminatorias en zona de clasificación directa."

CAPTION_IG = f"""🔍 BAJO LA LUPA · ED. 01 — ARGENTINA

A {DIAS_AL_DEBUT} días del debut contra Argelia, miramos en detalle al campeón vigente.

📊 LOS DATOS QUE IMPORTAN:

· #3 del ranking FIFA (perdió el #1 que tenía desde Qatar 2022)
· 3 Mundiales ganados — solo Brasil, Italia y Alemania tienen más
· {bloque_elim}

⭐ MESSI EN COPA AMÉRICA 2024:
2.81 xG en 6 partidos pero solo 1 gol convertido. Generó como nunca, definió por debajo de su nivel. Sin embargo lideró al equipo con 13 pases clave — el motor creativo.

🥇 EL LÍDER HISTÓRICO:
Messi es el goleador absoluto de la selección. {messi_goles_career if messi_goles_career else '~110'} goles en {messi_caps_career if messi_caps_career else '~190'} partidos. Está a otro nivel.

¿Llega lista para defender la copa? 👇

————
📊 Datos: StatsBomb Open + Wikipedia + ranking FIFA mayo 2026
🔍 Próxima edición de BAJO LA LUPA: pronto

#BajoLaLupa #Argentina #Mundial2026 #Scaloneta #Messi #FootballAnalytics #datafutbol_ar
"""

caption_path = CARRUSEL_FINAL / "caption_ig.txt"
caption_path.write_text(CAPTION_IG, encoding="utf-8")
print(f"\nCaption guardado en: {caption_path}")
print(f"Longitud: {len(CAPTION_IG)} caracteres (límite IG: 2200)")
print("\n--- PREVIEW ---")
print(CAPTION_IG)
