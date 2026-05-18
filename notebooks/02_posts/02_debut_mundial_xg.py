# %% [markdown]
# # Post #2 — "32 días para el debut: ¿Qué fue el xG?"
#
# **Concepto:** Aprovechando que falta 1 mes para el debut de Argentina en el
# Mundial 2026, recordamos cómo le fue en el último debut mundialista (ARG-SAU
# Mundial 2022) y usamos ese partido para explicar el xG.
#
# **Carrusel IG:** 5 slides 1080×1350 — Combo C aplicado.
#
# **Cómo ejecutar:** Shift+Enter celda por celda, o Run All. Generará los PNGs
# en outputs/ y los normalizados en outputs/carrusel_final/.

# %% [Setup]


import sys
import os
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
from mplsoccer import VerticalPitch, Pitch

from statsbombpy import sb
from scripts.style import (
    set_default_style, apply_branding, watermark,
    COLORS, FONTS, ROLES, PAISES_COLORS, pais_color,
    draw_card_box, draw_comparison_bar, draw_section_label,
    draw_big_number, draw_quote, place_logo,
    place_competition_icon,
)
from scripts.jugadores import display_name

set_default_style()

# Colores patrón de los países de este post (R21)
COLOR_ARG = pais_color("Argentina")        # #75AADB celeste
COLOR_SAU = pais_color("Saudi Arabia")     # #006C35 verde saudí
print(f"Color ARG: {COLOR_ARG} | Color SAU: {COLOR_SAU}")

# Paths de output
OUTPUTS = Path(REPO_ROOT) / "outputs" / "2026-05" / "post_02_debut_mundial_xg"
OUTPUTS.mkdir(parents=True, exist_ok=True)
CARRUSEL_FINAL = OUTPUTS / "carrusel_final"
CARRUSEL_FINAL.mkdir(exist_ok=True)

print(f"Outputs van a: {OUTPUTS}")

# %% [Constantes del post]
HOY = date(2026, 5, 17)  # Domingo — fecha de publicación del post
DEBUT_2026 = date(2026, 6, 16)  # Martes — Argentina vs Argelia (Mundial 2026 confirmado)
DIAS_AL_DEBUT = (DEBUT_2026 - HOY).days  # = 30 días exactos (1 mes)
print(f"Faltan {DIAS_AL_DEBUT} días para el debut del Mundial 2026")

# %% [1. Descubrir match_id de ARG-SAU Mundial 2022]
matches = sb.matches(competition_id=43, season_id=106)
arg_sau = matches[
    ((matches["home_team"] == "Argentina") & (matches["away_team"] == "Saudi Arabia")) |
    ((matches["home_team"] == "Saudi Arabia") & (matches["away_team"] == "Argentina"))
]
print(arg_sau[["match_id", "match_date", "home_team", "away_team", "home_score", "away_score"]])

MATCH_ID = int(arg_sau["match_id"].iloc[0])
print(f"\n✅ Match ID ARG-SAU: {MATCH_ID}")

# %% [2. Cargar eventos del partido]
events = sb.events(match_id=MATCH_ID)
print(f"Total eventos: {len(events)}")
print(f"Columnas disponibles: {events.shape[1]}")
print(events[["minute", "type", "team", "player"]].head(10))

# %% [3. Stats clave del partido — para los slides]

# xG totales por equipo (solo de tiros)
xg_por_equipo = events.query("type == 'Shot'").groupby("team")["shot_statsbomb_xg"].sum().round(2)
print("xG totales:")
print(xg_por_equipo)

# Tiros totales por equipo
tiros_por_equipo = events.query("type == 'Shot'").groupby("team").size()
print("\nTiros totales:")
print(tiros_por_equipo)

# Pases completados por equipo
pases_completados = events.query("type == 'Pass' and pass_outcome.isnull()", engine="python").groupby("team").size()
print("\nPases completados:")
print(pases_completados)

# Pases totales
pases_totales = events.query("type == 'Pass'").groupby("team").size()
print("\nPases totales (intentados):")
print(pases_totales)

# Goles
goles = events.query("type == 'Shot' and shot_outcome == 'Goal'").groupby("team").size()
print("\nGoles:")
print(goles)

# Guardar stats en dict para usar en slides
STATS = {
    "ARG": {
        "xg": float(xg_por_equipo.get("Argentina", 0)),
        "tiros": int(tiros_por_equipo.get("Argentina", 0)),
        "pases_comp": int(pases_completados.get("Argentina", 0)),
        "pases_tot": int(pases_totales.get("Argentina", 0)),
        "goles": int(goles.get("Argentina", 0)),
    },
    "SAU": {
        "xg": float(xg_por_equipo.get("Saudi Arabia", 0)),
        "tiros": int(tiros_por_equipo.get("Saudi Arabia", 0)),
        "pases_comp": int(pases_completados.get("Saudi Arabia", 0)),
        "pases_tot": int(pases_totales.get("Saudi Arabia", 0)),
        "goles": int(goles.get("Saudi Arabia", 0)),
    },
}
print(f"\nResumen final:\n{STATS}")

# %% [4. SLIDE 1 — Portada countdown]

fig, ax = plt.subplots(figsize=(8, 10), facecolor=COLORS["bg"])
ax.set_facecolor(COLORS["bg"])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# PORTADA — sin cajas, jerarquía tipográfica + líneas decorativas
# Lógica: el "32" gigante DOMINA; todo lo demás soporta esa dominancia.

# "FALTAN" arriba — fuera del rango vertical del número grande
ax.text(5, 9.0, "F A L T A N", ha="center", va="center",
        fontsize=14, fontweight="bold", color=ROLES["subtitle"],
        family=FONTS["title"])

# Número gigante — DATO CLAVE. Centrado en y=7.0, fontsize bajado a 170 para garantizar separación
# Con fontsize 170 ocupa ~2.4 unidades verticales → de y=5.8 a y=8.2 → no toca "FALTAN" en 9.0
ax.text(5, 7.0, str(DIAS_AL_DEBUT), ha="center", va="center",
        fontsize=170, fontweight="bold", color=ROLES["data_key"],
        family=FONTS["title"])

# "DÍAS PARA EL DEBUT" — bien separado del número
ax.text(5, 4.7, "D Í A S   P A R A   E L   D E B U T", ha="center", va="center",
        fontsize=20, fontweight="bold", color=ROLES["title"],
        family=FONTS["title"])

# Línea decorativa horizontal
ax.plot([3, 7], [4.2, 4.2], color=ROLES["divider"], linewidth=2, alpha=0.7)

# Bajada narrativa — sin caja, texto limpio
ax.text(5, 3.5, "Antes del Mundial 2026,", ha="center", va="center",
        fontsize=16, color=ROLES["body"], family=FONTS["body"], style="italic")
ax.text(5, 3.0, "recordamos el último debut", ha="center", va="center",
        fontsize=16, color=ROLES["body"], family=FONTS["body"], style="italic")
ax.text(5, 2.5, "mundialista de la Scaloneta.", ha="center", va="center",
        fontsize=16, color=ROLES["body"], family=FONTS["body"], style="italic")

# Marcador estilo "ticker" — líneas verticales sutiles separando elementos
ax.plot([2.0, 2.0], [1.05, 1.55], color=ROLES["caption"], linewidth=0.5, alpha=0.4)
ax.plot([8.0, 8.0], [1.05, 1.55], color=ROLES["caption"], linewidth=0.5, alpha=0.4)

ax.text(3.5, 1.3, "ARG", ha="center", va="center", fontsize=22, fontweight="bold",
        color=COLOR_ARG, family=FONTS["title"])
ax.text(5.0, 1.3, f"{STATS['ARG']['goles']} — {STATS['SAU']['goles']}",
        ha="center", va="center", fontsize=26, fontweight="bold",
        color=ROLES["body"], family=FONTS["data"])
ax.text(6.5, 1.3, "SAU", ha="center", va="center", fontsize=22, fontweight="bold",
        color=COLOR_SAU, family=FONTS["title"])

ax.text(5, 0.5, "22 nov 2022 · Lusail Stadium · Mundial Qatar",
        ha="center", va="center", fontsize=10,
        color=ROLES["caption"], family=FONTS["data"])

# Logo SIMPLE arriba a la izquierda — versión coherente con el cierre (R23)
# Incluye "datafutbol Ar" integrado en su composición.
# R24: NO se cita fuente acá (portada narrativa, sin datos estadísticos)
place_logo(fig, x=0.14, y=0.92, size=0.13, alpha=0.95, variant="simple")

# Logo Mundial 2026 — contextualiza el countdown (R25)
# Alineado verticalmente con el logo @datafutbol_ar (y=0.92) para balance
# size=0.14 (un toque más grande) para llenar mejor el espacio derecho
place_competition_icon(fig, x=0.86, y=0.92, size=0.14, file="mundial_2026.png")

plt.savefig(OUTPUTS / "slide_1_portada.png", dpi=200,
            facecolor=COLORS["bg"], bbox_inches="tight", pad_inches=0.3)
plt.show()
print("✅ Slide 1 guardado")

# %% [5. SLIDE 2 — Contexto del partido]

fig, ax = plt.subplots(figsize=(8, 10), facecolor=COLORS["bg"])
ax.set_facecolor(COLORS["bg"])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# CONTEXTO — narrativa flowing + tabla con divisores (sin cajas)
# Lógica: la narrativa es texto a flujo; la tabla usa líneas + colores patrón
# para separar visualmente; los headers ARG/SAU son grandes.

# Título
ax.text(5, 9.4, "EL DEBUT QUE NADIE",
        ha="center", va="center", fontsize=24, fontweight="bold",
        color=ROLES["title"], family=FONTS["title"])
ax.text(5, 8.7, "QUIERE RECORDAR",
        ha="center", va="center", fontsize=24, fontweight="bold",
        color=ROLES["title"], family=FONTS["title"])

# Línea decorativa fina
ax.plot([3.5, 6.5], [8.2, 8.2], color=ROLES["divider"], linewidth=2, alpha=0.7)

# Narrativa — texto limpio, sin caja, con interlineado generoso
narrativa = [
    "Argentina llegaba con 36 partidos invicta.",
    "Messi venía de su mejor año.",
    "Era la favorita absoluta del grupo.",
]
y_pos = 7.6
for linea in narrativa:
    ax.text(5, y_pos, linea, ha="center", va="center", fontsize=15,
            color=ROLES["body"], family=FONTS["body"])
    y_pos -= 0.55

# Section label "EN NÚMEROS" con líneas a los lados
draw_section_label(ax, x=5, y=5.7, label="E N   N Ú M E R O S", width=6)

# Tabla comparativa — usar BANDAS LATERALES de color (no caja completa)
# Banda izquierda ARG (celeste fina vertical)
ax.plot([1.5, 1.5], [2.0, 5.2], color=COLOR_ARG, linewidth=3, alpha=0.8)
# Banda derecha SAU (verde saudí fina vertical)
ax.plot([8.5, 8.5], [2.0, 5.2], color=COLOR_SAU, linewidth=3, alpha=0.8)

# Headers
ax.text(2.6, 4.95, "ARG", ha="center", fontsize=20, fontweight="bold",
        color=COLOR_ARG, family=FONTS["title"])
ax.text(7.4, 4.95, "SAU", ha="center", fontsize=20, fontweight="bold",
        color=COLOR_SAU, family=FONTS["title"])

# Línea fina debajo de headers
ax.plot([1.8, 8.2], [4.55, 4.55], color=ROLES["subtitle"],
        linewidth=0.7, alpha=0.5)

stats_rows = [
    ("Tiros", STATS["ARG"]["tiros"], STATS["SAU"]["tiros"]),
    ("xG total", f"{STATS['ARG']['xg']:.2f}", f"{STATS['SAU']['xg']:.2f}"),
    ("Pases completos", STATS["ARG"]["pases_comp"], STATS["SAU"]["pases_comp"]),
    ("Goles", STATS["ARG"]["goles"], STATS["SAU"]["goles"]),
]

y = 4.15
for i, (label, arg_val, sau_val) in enumerate(stats_rows):
    ax.text(2.6, y, str(arg_val), ha="center", fontsize=20, fontweight="bold",
            color=ROLES["data_normal"], family=FONTS["data"])
    ax.text(5, y, label, ha="center", fontsize=12,
            color=ROLES["subtitle"], family=FONTS["body"])
    ax.text(7.4, y, str(sau_val), ha="center", fontsize=20, fontweight="bold",
            color=ROLES["data_normal"], family=FONTS["data"])
    # Línea separadora muy sutil entre filas (excepto la última)
    if i < len(stats_rows) - 1:
        ax.plot([1.8, 8.2], [y - 0.28, y - 0.28],
                color=ROLES["subtitle"], linewidth=0.3, alpha=0.25)
    y -= 0.55

# Card pedagógico: explicación de xG + ejemplos
# Card un toque más alto (1.4 vs 0.95) para sumar 2 líneas de ejemplos
draw_card_box(ax, x=0.6, y=0.55, width=8.8, height=1.35,
              facecolor=ROLES["card_bg"], edgecolor=ROLES["data_key"],
              alpha=0.55, zorder=1)

# Título card (arriba)
ax.text(5, 1.72, "¿QUÉ ES EL xG?", ha="center", va="center",
        fontsize=13, fontweight="bold",
        color=ROLES["data_key"], family=FONTS["title"], zorder=3)

# Definición — 2 líneas
ax.text(5, 1.38, "Probabilidad de que un tiro termine en gol (0 a 1).",
        ha="center", va="center", fontsize=11,
        color=ROLES["body"], family=FONTS["body"], zorder=3)
ax.text(5, 1.10, "Mide la CALIDAD del tiro, no garantiza el resultado.",
        ha="center", va="center", fontsize=11,
        color=ROLES["body"], family=FONTS["body"], zorder=3)

# Línea separadora interna sutil
ax.plot([2, 8], [0.90, 0.90], color=ROLES["caption"],
        linewidth=0.4, alpha=0.3, zorder=2)

# Ejemplos concretos (números clave para que la audiencia "vea" xG)
ax.text(5, 0.70, "Penal ≈ 0.76  ·  Tiro área ≈ 0.40  ·  Tiro lejano ≈ 0.03",
        ha="center", va="center", fontsize=11, fontweight="bold",
        color=ROLES["data_key"], family=FONTS["data"], zorder=3)

# Footer alineado: logo izq | handle centro | fuente derecha (mismo baseline)
FOOTER_Y_S2 = 0.05
place_logo(fig, x=0.08, y=FOOTER_Y_S2, size=0.06, alpha=0.95, variant="watermark")
fig.text(0.5, FOOTER_Y_S2, "@datafutbol_ar",
         ha="center", va="center", fontsize=10, fontweight="bold",
         color=COLORS["primary"], family=FONTS["data"])
fig.text(0.92, FOOTER_Y_S2, "Fuente: StatsBomb Open Data",
         ha="right", va="center", fontsize=9,
         color=COLORS["muted"], family=FONTS["data"])

plt.savefig(OUTPUTS / "slide_2_contexto.png", dpi=200,
            facecolor=COLORS["bg"], bbox_inches="tight", pad_inches=0.3)
plt.show()
print("✅ Slide 2 guardado")

# %% [6. SLIDE 3 — Shot map ARG con xG anotados]

# Filtrar tiros de Argentina y extraer coordenadas
shots_arg = events.query("type == 'Shot' and team == 'Argentina'").copy()
shots_arg["x"] = shots_arg["location"].apply(
    lambda l: l[0] if isinstance(l, (list, np.ndarray)) else None
)
shots_arg["y"] = shots_arg["location"].apply(
    lambda l: l[1] if isinstance(l, (list, np.ndarray)) else None
)
shots_arg = shots_arg.dropna(subset=["x", "y"]).reset_index(drop=True)
print(f"Tiros de Argentina con coordenadas: {len(shots_arg)}")
print(shots_arg[["minute", "player", "shot_statsbomb_xg", "shot_outcome", "x", "y"]])

# Identificar 3 tiros para anotar (alto/medio/bajo xG)
top_xg = shots_arg.nlargest(1, "shot_statsbomb_xg").iloc[0]  # más alto (penal Messi probable)
medio_xg = shots_arg.iloc[(shots_arg["shot_statsbomb_xg"] - 0.12).abs().argsort()[:1]].iloc[0]
bajo_xg = shots_arg.nsmallest(1, "shot_statsbomb_xg").iloc[0]

print(f"\nTop xG: {top_xg['player']} ({top_xg['shot_statsbomb_xg']:.2f})")
print(f"Medio xG: {medio_xg['player']} ({medio_xg['shot_statsbomb_xg']:.2f})")
print(f"Bajo xG: {bajo_xg['player']} ({bajo_xg['shot_statsbomb_xg']:.2f})")

# Plot
fig = plt.figure(figsize=(8, 10), facecolor=COLORS["bg"])

# Pitch (mitad de cancha vertical) — usamos add_axes para controlar la posición exacta
pitch_ax = fig.add_axes((0.06, 0.18, 0.88, 0.60))
pitch = VerticalPitch(
    pitch_type="statsbomb",
    half=True,
    pitch_color=COLORS["bg"],
    line_color=COLORS["text"],
    linewidth=1.5,
    pad_top=2,
)
pitch.draw(ax=pitch_ax)
# CRÍTICO: ocultar ticks/labels que matplotlib agrega por defecto sobre el pitch
pitch_ax.set_xticks([])
pitch_ax.set_yticks([])
for spine in pitch_ax.spines.values():
    spine.set_visible(False)

# Tiros (tamaño proporcional al xG)
# Color: GOL → ROLES["goal"] (dorado, evento positivo); SIN GOL → COLOR_ARG (celeste, es ARG)
for _, shot in shots_arg.iterrows():
    color = ROLES["goal"] if shot["shot_outcome"] == "Goal" else COLOR_ARG
    pitch.scatter(
        shot["x"], shot["y"],
        s=shot["shot_statsbomb_xg"] * 1500 + 80,
        color=color, edgecolors=COLORS["text"], linewidth=1.5,
        alpha=0.85, ax=pitch_ax, zorder=3,
    )

# Anotar los 3 tiros destacados — caja celeste con texto blanco (no dorado)
def anotar(shot, etiqueta, xytext_xy):
    """
    Anota un tiro con caja semitransparente y flecha clara.
    Usa COLOR_ARG (celeste) en vez de dorado para no competir con goles.
    """
    pitch.annotate(
        f"{etiqueta}\nxG = {shot['shot_statsbomb_xg']:.2f}",
        xy=(shot["x"], shot["y"]),
        xytext=xytext_xy,
        ax=pitch_ax,
        fontsize=11, fontweight="bold",
        color=COLORS["text"], family=FONTS["data"],
        ha="center", va="center",
        bbox=dict(
            boxstyle="round,pad=0.5",
            facecolor=ROLES["card_bg"],
            edgecolor=COLOR_ARG,
            linewidth=1.5,
            alpha=0.95,
        ),
        arrowprops=dict(
            arrowstyle="-|>",
            color=COLOR_ARG,
            lw=2.0,
            shrinkA=0, shrinkB=8,
        ),
        zorder=10,
    )

# Posiciones manuales para que NO se solapen con los tiros ni entre sí
# En VerticalPitch half: x=0-120 (vertical), y=0-80 (horizontal). El arco está arriba.
anotar(top_xg, "ALTA chance\n(penal/área chica)", xytext_xy=(85, 65))
anotar(medio_xg, "MEDIA chance\n(área grande)", xytext_xy=(105, 12))
anotar(bajo_xg, "BAJA chance\n(tiro lejano)", xytext_xy=(75, 5))

# Título (R20: títulos en blanco)
fig.text(0.5, 0.94, "TODOS LOS TIROS DE ARGENTINA",
         ha="center", fontsize=20, fontweight="bold",
         color=ROLES["title"], family=FONTS["title"])
fig.text(0.5, 0.90, "El tamaño del círculo = xG (calidad de la chance)",
         ha="center", fontsize=12, color=ROLES["subtitle"],
         family=FONTS["body"], style="italic")

# Línea decorativa
fig.add_artist(plt.Line2D([0.3, 0.7], [0.86, 0.86],
                          color=ROLES["divider"], linewidth=1.5, alpha=0.7))

# Leyenda visual — círculos reales con colores ARG (sin gol) y dorado (gol)
legend_y = 0.13
fig.text(0.25, legend_y, "GOL", ha="left", va="center", fontsize=11,
         color=ROLES["body"], family=FONTS["body"], fontweight="bold")
fig.add_artist(plt.Circle((0.22, legend_y), 0.012, color=ROLES["goal"],
                          ec=COLORS["text"], lw=1, transform=fig.transFigure))

fig.text(0.55, legend_y, "SIN GOL", ha="left", va="center", fontsize=11,
         color=ROLES["body"], family=FONTS["body"], fontweight="bold")
fig.add_artist(plt.Circle((0.52, legend_y), 0.012, color=COLOR_ARG,
                          ec=COLORS["text"], lw=1, transform=fig.transFigure))

# Footer alineado: logo izq | @datafutbol_ar centro | fuente derecha — todo en el mismo baseline vertical
FOOTER_Y = 0.05
place_logo(fig, x=0.08, y=FOOTER_Y, size=0.06, alpha=0.95, variant="watermark")
fig.text(0.5, FOOTER_Y, "@datafutbol_ar",
         ha="center", va="center", fontsize=10, fontweight="bold",
         color=COLORS["primary"], family=FONTS["data"])
fig.text(0.92, FOOTER_Y, "Fuente: StatsBomb Open Data",
         ha="right", va="center", fontsize=9,
         color=COLORS["muted"], family=FONTS["data"])

plt.savefig(OUTPUTS / "slide_3_shotmap.png", dpi=200,
            facecolor=COLORS["bg"], bbox_inches="tight", pad_inches=0.3)
plt.show()
print("✅ Slide 3 guardado")

# %% [7. SLIDE 4 — La lección del xG (comparativa)]

fig, ax = plt.subplots(figsize=(8, 10), facecolor=COLORS["bg"])
ax.set_facecolor(COLORS["bg"])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# LA LECCIÓN DEL xG — barras comparativas + número gigante + quote
# Lógica:
#  - xG ARG vs SAU → BARRAS comparativas (muy visual, sin cards)
#  - Resultado 1-2 → tipografía MASIVA con líneas arriba/abajo (sin caja)
#  - Insight → quote con comillas (variedad visual)

# Título
ax.text(5, 9.3, "LA LECCIÓN DEL xG",
        ha="center", va="center", fontsize=26, fontweight="bold",
        color=ROLES["title"], family=FONTS["title"])

# Línea decorativa
ax.plot([3, 7], [8.7, 8.7], color=ROLES["divider"], linewidth=2, alpha=0.7)

# Header del bloque comparativo
ax.text(5, 8.0, "EN xG TOTAL", ha="center", fontsize=12,
        color=ROLES["subtitle"], family=FONTS["title"], fontweight="bold")

# Big numbers comparativos — colores patrón
ax.text(2.4, 7.0, f"{STATS['ARG']['xg']:.2f}", ha="center",
        fontsize=72, fontweight="bold", color=COLOR_ARG,
        family=FONTS["data"])
ax.text(2.4, 5.7, "ARGENTINA", ha="center", fontsize=12,
        color=ROLES["body"], family=FONTS["body"], fontweight="bold")

ax.text(5, 6.6, "vs", ha="center", fontsize=22, color=ROLES["subtitle"],
        family=FONTS["title"], style="italic")

ax.text(7.6, 7.0, f"{STATS['SAU']['xg']:.2f}", ha="center",
        fontsize=72, fontweight="bold", color=COLOR_SAU,
        family=FONTS["data"])
ax.text(7.6, 5.7, "ARABIA", ha="center", fontsize=12,
        color=ROLES["body"], family=FONTS["body"], fontweight="bold")

# Separador antes del resultado (los big numbers ya muestran la diferencia, no hace falta barra)
ax.plot([2, 8], [4.7, 4.7], color=ROLES["caption"],
        linewidth=0.7, alpha=0.4)

# Resultado — tipografía MASIVA sin caja, con líneas arriba/abajo
ax.text(5, 3.85, "Pero el resultado fue…", ha="center", fontsize=12,
        color=ROLES["subtitle"], family=FONTS["body"], style="italic")

# El resultado es el dato clave de este slide → dorado (único)
ax.text(5, 2.9, f"{STATS['ARG']['goles']} — {STATS['SAU']['goles']}",
        ha="center", fontsize=70, fontweight="bold",
        color=ROLES["data_key"], family=FONTS["data"])

# Línea dorada decorativa debajo (subraya el dato clave)
ax.plot([3.5, 6.5], [2.4, 2.4], color=ROLES["data_key"],
        linewidth=2.5, alpha=0.7)

# Insight como quote
draw_quote(ax, x=5, y=1.5,
           text="El xG mide la CALIDAD, no garantiza goles.",
           width=8, fontsize=12, color=ROLES["highlight"])

ax.text(5, 0.65, "Argentina mereció más. Arabia fue más eficaz.",
        ha="center", fontsize=11, color=ROLES["body"],
        family=FONTS["body"], style="italic")

# Footer alineado: logo izq | handle centro | fuente derecha (mismo baseline)
FOOTER_Y_S4 = 0.05
place_logo(fig, x=0.08, y=FOOTER_Y_S4, size=0.06, alpha=0.95, variant="watermark")
fig.text(0.5, FOOTER_Y_S4, "@datafutbol_ar",
         ha="center", va="center", fontsize=10, fontweight="bold",
         color=COLORS["primary"], family=FONTS["data"])
fig.text(0.92, FOOTER_Y_S4, "Fuente: StatsBomb Open Data",
         ha="right", va="center", fontsize=9,
         color=COLORS["muted"], family=FONTS["data"])

plt.savefig(OUTPUTS / "slide_4_leccion.png", dpi=200,
            facecolor=COLORS["bg"], bbox_inches="tight", pad_inches=0.3)
plt.show()
print("✅ Slide 4 guardado")

# %% [8. SLIDE 5 — Cierre emocional]

fig, ax = plt.subplots(figsize=(8, 10), facecolor=COLORS["bg"])
ax.set_facecolor(COLORS["bg"])
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# CIERRE — distribución limpia y separada en bloques verticales:
#  · Narrativa arriba (y=8-9.5)
#  · Countdown medio (y=3.5-6)
#  · CTA (y=2.3)
#  · Footer limpio abajo: logo + marca + handle + fuente bien separados (y=0-1.5)

# ─── Narrativa (arriba) ───
ax.text(5, 9.3, "Argentina perdió ese debut.",
        ha="center", fontsize=20, color=ROLES["body"],
        family=FONTS["title"], style="italic")
ax.text(5, 8.6, "6 partidos después,",
        ha="center", fontsize=20, color=ROLES["body"],
        family=FONTS["title"], style="italic")
ax.text(5, 7.7, "era CAMPEONA del mundo.",
        ha="center", fontsize=28, fontweight="bold",
        color=ROLES["highlight"], family=FONTS["title"])

# Separador decorativo: línea celeste con punto al medio
ax.plot([3.5, 4.7], [6.8, 6.8], color=ROLES["divider"],
        linewidth=1.2, alpha=0.6)
ax.add_patch(plt.Circle((5, 6.8), 0.08, color=ROLES["data_key"], zorder=5))
ax.plot([5.3, 6.5], [6.8, 6.8], color=ROLES["divider"],
        linewidth=1.2, alpha=0.6)

# ─── Countdown (medio) ─── distribución vertical con MUCHA separación
# "AHORA FALTAN" arriba (fuera del rango del número)
ax.text(5, 6.5, "AHORA FALTAN", ha="center", va="center", fontsize=13,
        color=ROLES["subtitle"], family=FONTS["title"], fontweight="bold")

# Número grande centrado en y=4.9, fontsize=80 → ocupa ~1.1 unidades (de y=4.35 a y=5.45)
# No toca "AHORA FALTAN" (6.5) ni "DÍAS PARA EL DEBUT" (3.5)
ax.text(5, 4.9, str(DIAS_AL_DEBUT), ha="center", va="center",
        fontsize=80, fontweight="bold",
        color=ROLES["data_key"], family=FONTS["title"])

ax.text(5, 3.5, "DÍAS PARA EL DEBUT", ha="center", va="center", fontsize=14,
        fontweight="bold", color=ROLES["title"], family=FONTS["title"])
ax.text(5, 3.05, "en el Mundial 2026", ha="center", va="center", fontsize=11,
        color=ROLES["subtitle"], family=FONTS["body"], style="italic")

# ─── CTA ───
ax.text(5, 2.2, "Seguinos para más análisis rumbo al Mundial.",
        ha="center", fontsize=12, color=ROLES["body"], family=FONTS["body"])

# ─── Línea divisoria sutil antes del bloque de cierre ───
ax.plot([2, 8], [1.55, 1.55], color=ROLES["caption"],
        linewidth=0.5, alpha=0.3)

# ─── CIERRE: logo SIMPLE (con marca textual integrada) + handle ───
# R23: portada y cierre usan logo simple (no watermark + texto separado).
# R24: NO se cita fuente acá porque este slide es narrativo (sin datos estadísticos).

# Logo simple centrado (incluye "datafutbol Ar" en su composición)
place_logo(fig, x=0.5, y=0.10, size=0.18, alpha=1.0, variant="simple")

# Handle debajo del logo
ax.text(5, 0.05, "@datafutbol_ar", ha="center", va="center",
        fontsize=11, fontweight="bold",
        color=COLORS["primary"], family=FONTS["data"])

plt.savefig(OUTPUTS / "slide_5_cierre.png", dpi=200,
            facecolor=COLORS["bg"], bbox_inches="tight", pad_inches=0.3)
plt.show()
print("✅ Slide 5 guardado")

# %% [9. Normalizar todos los slides a 1080x1350 para IG]

from scripts.normalizar_carrusel import normalizar_a_carrusel

slides = [
    "slide_1_portada.png",
    "slide_2_contexto.png",
    "slide_3_shotmap.png",
    "slide_4_leccion.png",
    "slide_5_cierre.png",
]

for slide in slides:
    normalizar_a_carrusel(
        input_path=str(OUTPUTS / slide),
        output_path=str(CARRUSEL_FINAL / slide),
    )
    print(f"✅ Normalizado: {slide}")

print(f"\nPNGs finales en: {CARRUSEL_FINAL}")
print("Subí estos 5 archivos a IG en orden.")

# %% [10. Caption sugerido para IG]

CAPTION = f"""{DIAS_AL_DEBUT} días. Exactamente UN MES para que Argentina vuelva a debutar en un Mundial.

Antes de la cita norteamericana, repasamos cómo fue el último debut mundialista de la Scaloneta: ARG 1-2 Arabia Saudita, 22 nov 2022.

Una historia que tiene MUCHO para enseñar sobre cómo se mide el fútbol moderno.

→ En el carrusel te mostramos:
· Qué pasó realmente en el partido.
· Cómo se "ven" los tiros de Argentina en un shot map.
· Qué es el Expected Goals (xG) y por qué ese partido es un ejemplo PERFECTO de cómo NO siempre el que más merece, gana.
· La paradoja: Argentina dominó. Y perdió.

¿Será diferente esta vez? Seguinos para más análisis rumbo al Mundial 2026.

────────
METODOLOGÍA
· Datos: StatsBomb Open Data (eventos del partido, xG oficial de StatsBomb).
· N: {STATS['ARG']['tiros'] + STATS['SAU']['tiros']} tiros totales en el partido.
· Visualizaciones armadas con Python + mplsoccer.

#datafutbol #FutbolArgentino #SelecciónArgentina #Mundial2026 #xG #FootballAnalytics #Scaloneta
"""

print(CAPTION)
# Guardar caption en archivo aparte para fácil copia
with open(OUTPUTS / "caption_ig.txt", "w", encoding="utf-8") as f:
    f.write(CAPTION)
print(f"\n✅ Caption guardado en: {OUTPUTS / 'caption_ig.txt'}")

# %%
