# %% [markdown]
# # Ranking FIFA — Top 16 selecciones hacia el Mundial 2026
#
# **Concepto:** ranking de las 16 selecciones con más puntos FIFA yendo al
# Mundial 2026. Argentina destacada. Carrusel didáctico que explica
# cómo funciona el ranking FIFA.
#
# **Carrusel IG:** 5 slides 1080×1350 — Combo C aplicado.
#
# **Datos:** Ranking FIFA Hombres — fuente oficial fifa.com/fifa-world-ranking/men.
#
# **Nota:** los valores en `RANKING_FIFA_RAW` son hardcodeados a partir del
# último ranking publicado por FIFA. Verificar contra fifa.com antes de
# publicar el carrusel.

# %% [Setup]
import sys
import os
from pathlib import Path
from datetime import date
from io import StringIO

REPO_ROOT = r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

%load_ext autoreload
%autoreload 2

import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

from scripts.style import (
    set_default_style, apply_branding, watermark,
    COLORS, FONTS, ROLES, PAISES_COLORS, pais_color,
    draw_card_box, draw_comparison_bar, draw_section_label,
    draw_big_number, draw_quote, place_logo,
    place_competition_icon, place_country_flag,
)

set_default_style()

# Paths de output
OUTPUTS = Path(REPO_ROOT) / "outputs" / "2026-05" / "post_03_ranking_elo"
OUTPUTS.mkdir(parents=True, exist_ok=True)
CARRUSEL_FINAL = OUTPUTS / "carrusel_final"
CARRUSEL_FINAL.mkdir(exist_ok=True)

print(f"Outputs van a: {OUTPUTS}")

# %% [Constantes del post]
HOY = date(2026, 5, 17)         # Domingo
MUNDIAL_INICIO = date(2026, 6, 11)  # Apertura — México vs Sudáfrica en el Azteca
DIAS_AL_MUNDIAL = (MUNDIAL_INICIO - HOY).days
print(f"Faltan {DIAS_AL_MUNDIAL} días para que arranque el Mundial 2026")

# %% [Nota sobre verificación de datos]
# Los valores en RANKING_FIFA_RAW (celda siguiente) deben estar verificados
# contra fifa.com antes de publicar el carrusel. La verificación es parte
# del proceso editorial (no se hace desde el código).
#
# Fuente oficial: https://inside.fifa.com/es/fifa-world-ranking/men

# %% [1. Datos hardcodeados — Ranking FIFA Hombres]
# Fuente: https://inside.fifa.com/es/fifa-world-ranking/men
#
# Top 7 verificado contra fifa.com el 17/5/2026.
# Posiciones 8-20: pendientes de verificación (valores aproximados).
# Lectura: tupla = (nombre en español, puntos FIFA, código ISO-2 para banderas)

RANKING_FIFA_RAW = [
    # ── TOP 7 (verificado fifa.com 17/5/2026) ──────────────────────
    ("Francia",        1877.32, "fr"),   # ↑2 — nuevo #1
    ("España",         1876.40, "es"),   # ↓1
    ("Argentina",      1874.81, "ar"),   # ↓1 — perdió el #1 que tenía desde el Mundial 2022
    ("Inglaterra",     1825.97, "gb"),   # =
    ("Portugal",       1763.83, "pt"),   # ↑1
    ("Brasil",         1761.16, "br"),   # ↓1
    ("Países Bajos",   1757.87, "nl"),   # =

    # ── POSICIONES 8-16 (ORDEN confirmado por Lucas, puntos APROXIMADOS) ─
    # ⚠️ los puntos exactos del 8-16 falta verificarlos en fifa.com.
    # El ORDEN sí está confirmado a partir de la columna de últimos
    # resultados de la página oficial.
    ("Marruecos",      1735, "ma"),   # 8
    ("Bélgica",        1718, "be"),   # 9
    ("Alemania",       1705, "de"),   # 10
    ("Croacia",        1695, "hr"),   # 11
    ("Italia",         1685, "it"),   # 12 — NO clasificó al Mundial 2026
    ("Colombia",       1680, "co"),   # 13
    ("Senegal",        1655, "sn"),   # 14
    ("México",         1650, "mx"),   # 15
    ("EE.UU.",         1645, "us"),   # 16
]

df_ranking = pd.DataFrame(RANKING_FIFA_RAW, columns=["seleccion", "puntos", "iso2"])
df_ranking.insert(0, "puesto", range(1, len(df_ranking) + 1))
print(f"✅ {len(df_ranking)} selecciones cargadas")
print(df_ranking.head(20))

# Guardar a CSV
df_ranking.to_csv(OUTPUTS / "ranking_fifa_17may2026.csv", index=False)
print(f"\n📄 CSV guardado en: {OUTPUTS / 'ranking_fifa_17may2026.csv'}")

# %% [2. Filtrar top 16 y datos de Argentina]
TOP_N = 16
top16 = df_ranking.head(TOP_N).copy()
print("Top 16 Ranking FIFA:")
print(top16[["puesto", "seleccion", "puntos"]])

# Posición y puntos de Argentina
arg_row = df_ranking[df_ranking["seleccion"] == "Argentina"]
ARG_PUESTO = int(arg_row.iloc[0]["puesto"])
# round() en vez de int() para mantener consistencia con el slide 3
# (1874.81 → 1875 redondeado, no 1874 truncado)
ARG_PUNTOS = round(arg_row.iloc[0]["puntos"])
print(f"\nArgentina: #{ARG_PUESTO} con {ARG_PUNTOS} puntos")

# Mapeo nombre español → nombre estilo PAISES_COLORS (sin tilde si hace falta)
# para que pais_color() encuentre el color patrón
NOMBRE_A_COLOR_KEY = {
    "Argentina": "Argentina", "Francia": "Francia", "España": "España",
    "Inglaterra": "Inglaterra", "Brasil": "Brasil", "Portugal": "Portugal",
    "Países Bajos": "Países Bajos", "Bélgica": "Bélgica", "Croacia": "Croacia",
    "Italia": "Italia", "Marruecos": "Marruecos", "Alemania": "Alemania",
    "Colombia": "Colombia", "Uruguay": "Uruguay", "Suiza": "Suiza",
    "EE.UU.": "Estados Unidos", "Senegal": "Senegal", "México": "México",
    "Japón": "Japón", "Irán": "Irán",
}
top16["color_key"] = top16["seleccion"].map(NOMBRE_A_COLOR_KEY).fillna(top16["seleccion"])

# %% [3. Slide 1 — PORTADA]
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(COLORS["bg"])  # azul profundo
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Logos
place_logo(fig, x=0.08, y=0.92, size=0.10, variant="simple")
place_competition_icon(fig, x=0.86, y=0.92, size=0.14, file="mundial_2026.png")

# Big title
ax.text(5, 9.4, "LAS 16",
        ha="center", va="center", fontsize=110,
        color=COLORS["accent"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 7.8, "SELECCIONES",
        ha="center", va="center", fontsize=58,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 6.8, "MÁS FUERTES",
        ha="center", va="center", fontsize=58,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 5.5, "yendo al Mundial 2026",
        ha="center", va="center", fontsize=34,
        color=COLORS["primary"],
        family=FONTS["body"], style="italic")

# Bottom hook
ax.text(5, 2.8, "Ranking ELO",
        ha="center", va="center", fontsize=44,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 2.0, f"al {HOY.strftime('%d/%m/%Y').lstrip('0')}",
        ha="center", va="center", fontsize=24,
        color=COLORS["primary"], family=FONTS["body"])

# Footer
ax.text(5, 0.6, f"FALTAN {DIAS_AL_MUNDIAL} DÍAS PARA EL INICIO",
        ha="center", va="center", fontsize=20,
        color=COLORS["accent"], fontweight="bold",
        family=FONTS["body"])

watermark(fig)

fname = OUTPUTS / "slide_1_portada.png"
fig.savefig(fname, dpi=100, facecolor=COLORS["bg"])
plt.show()
print(f"✅ {fname.name}")

# %% [4. Slide 2 — ¿CÓMO FUNCIONA EL RANKING FIFA?]
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor("#FFFFFF")  # blanco
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Banda azul superior (corta el "todo blanco")
banda = mpatches.Rectangle((0, 11.4), 10, 1.1, facecolor=COLORS["bg"], zorder=1)
ax.add_patch(banda)
ax.text(5, 11.95, "¿CÓMO SE ARMA EL RANKING?",
        ha="center", va="center", fontsize=16, fontweight="bold",
        color=COLORS["text"], family=FONTS["title"], zorder=2)

# Definición principal (compacta)
ax.text(5, 10.4, "Un sistema oficial que mide",
        ha="center", va="center", fontsize=32,
        color=COLORS["bg"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 9.7, "la fuerza actual",
        ha="center", va="center", fontsize=44,
        color=COLORS["accent"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 9.0, "de cada selección del mundo",
        ha="center", va="center", fontsize=22,
        color=COLORS["bg"], family=FONTS["body"], style="italic")

# 3 cards numeradas — sin emojis (se reemplazan con círculos numerados)
def draw_card_numerada(y_top, numero, titulo, descripcion):
    """Dibuja una card con un número circular en accent y texto al costado."""
    # Fondo de card
    draw_card_box(ax, x=0.5, y=y_top - 1.4, width=9, height=1.35,
                  facecolor=COLORS["primary"], alpha=0.10)
    # Círculo numerado al estilo lista didáctica
    circle = mpatches.Circle((1.3, y_top - 0.7), 0.45,
                              facecolor=COLORS["accent"], edgecolor="none", zorder=3)
    ax.add_patch(circle)
    ax.text(1.3, y_top - 0.7, str(numero),
            ha="center", va="center", fontsize=26, fontweight="bold",
            color=COLORS["bg"], family=FONTS["title"], zorder=4)
    # Texto
    ax.text(2.2, y_top - 0.35, titulo,
            fontsize=22, color=COLORS["bg"], fontweight="bold",
            family=FONTS["body"], va="center")
    ax.text(2.2, y_top - 1.0, descripcion,
            fontsize=17, color=COLORS["bg"], family=FONTS["body"], va="center")

draw_card_numerada(7.5, 1,
                   "Suma o resta puntos",
                   "según el resultado de cada partido oficial.")
draw_card_numerada(5.8, 2,
                   "Pesa el rival y el torneo",
                   "ganar un Mundial vale más que un amistoso.")
draw_card_numerada(4.1, 3,
                   "Mide el momento actual",
                   "no la historia: no cuenta el Mundial del 86.")

# Dato extra abajo — fact concreto para anclar
draw_card_box(ax, x=0.5, y=1.7, width=9, height=1.0,
              facecolor=COLORS["bg"], alpha=1.0)
ax.text(5, 2.45, "ACTUALIZACIÓN",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=COLORS["primary"], family=FONTS["data"])
ax.text(5, 1.95, "Se publica cada ~6 semanas en fifa.com",
        ha="center", va="center", fontsize=20, fontweight="bold",
        color=COLORS["text"], family=FONTS["body"])

# Footer
ax.text(5, 0.7, "Fuente: ranking FIFA · fifa.com/fifa-world-ranking/men",
        ha="center", va="center", fontsize=13,
        color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_2_que_es_ranking.png"
fig.savefig(fname, dpi=100, facecolor="#FFFFFF")
plt.show()
print(f"✅ {fname.name}")

# %% [5. Slide 3 — RANKING VISUAL TOP 16]
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor("#FFFFFF")  # blanco
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Section label
draw_section_label(ax, x=5, y=11.7, label="TOP 16 — RANKING FIFA", color=COLORS["bg"])
ax.text(5, 11.1, f"al {HOY.strftime('%d/%m/%Y').lstrip('0')}",
        ha="center", va="center", fontsize=18,
        color=COLORS["muted"], family=FONTS["data"])

# Barras horizontales
y_start = 10.3
y_step = 0.55
pts_max = float(top16["puntos"].max())
pts_min_chart = float(top16["puntos"].min()) - 30  # un poco menos para visual

bar_x0 = 3.0       # desde dónde arranca la barra (movido a la derecha para dejar lugar a la bandera)
bar_x_max = 9.2    # hasta dónde puede llegar
bar_width = bar_x_max - bar_x0

# Mapeo seleccion → archivo de bandera (R27, snake_case sin tildes).
# Si el archivo no existe en G:\...\banderas_paises\, place_country_flag devuelve None
# y la fila se renderiza sin bandera (degradación elegante).
BANDERA_FILE = {
    "Argentina":     "argentina.png",
    "Francia":       "francia.png",
    "España":        "espana.png",
    "Inglaterra":    "inglaterra.png",
    "Portugal":      "portugal.png",
    "Brasil":        "brasil.png",
    "Países Bajos":  "paises_bajos.png",
    "Marruecos":     "marruecos.png",
    "Bélgica":       "belgica.png",
    "Alemania":      "alemania.png",
    "Croacia":       "croacia.png",
    "Italia":        "italia.png",
    "Colombia":      "colombia.png",
    "Senegal":       "senegal.png",
    "México":        "mexico.png",
    "EE.UU.":        "estados_unidos.png",
}

for i, row in top16.iterrows():
    y = y_start - i * y_step
    es_argentina = row["seleccion"] == "Argentina"

    # Color de la barra: color patrón del país (R21)
    bar_color = pais_color(row["color_key"], "primary")
    # Argentina destacada: borde dorado adicional
    edgecolor = COLORS["accent"] if es_argentina else "none"
    edgewidth = 2.5 if es_argentina else 0

    # Texto posición
    color_pos = COLORS["accent"] if es_argentina else COLORS["bg"]
    ax.text(0.6, y, f"{int(row['puesto']):>2}",
            ha="right", va="center", fontsize=22, fontweight="bold",
            color=color_pos, family=FONTS["title"])

    # Bandera (R27) — convertimos axes coords → fig coords (axes ocupa toda la figura)
    bandera_archivo = BANDERA_FILE.get(row["seleccion"])
    if bandera_archivo:
        place_country_flag(
            fig,
            x=1.05 / 10.0,           # axes_x=1.05 → fig_x
            y=y / 12.5,              # axes_y → fig_y
            size=0.028,              # ~28 pixels de ancho a 1080px
            pais=bandera_archivo,
        )

    # Nombre selección (movido a la derecha para hacer lugar a la bandera)
    ax.text(1.5, y, row["seleccion"],
            ha="left", va="center", fontsize=15,
            color=COLORS["bg"], fontweight="bold" if es_argentina else "normal",
            family=FONTS["body"])

    # Barra escalada
    pts = float(row["puntos"])
    frac = (pts - pts_min_chart) / (pts_max - pts_min_chart)
    frac = max(0.08, min(1.0, frac))  # mínimo visible
    bar_w = bar_width * frac
    bar = FancyBboxPatch(
        (bar_x0, y - 0.18), bar_w, 0.36,
        boxstyle="round,pad=0.0,rounding_size=0.05",
        linewidth=edgewidth, edgecolor=edgecolor,
        facecolor=bar_color, alpha=0.85,
    )
    ax.add_patch(bar)

    # Puntos al final de la barra
    ax.text(bar_x0 + bar_w + 0.1, y, f"{pts:.0f}",
            ha="left", va="center", fontsize=14,
            color=COLORS["bg"], fontweight="bold" if es_argentina else "normal",
            family=FONTS["data"])

# Highlight Argentina — texto adaptado según la posición real
if ARG_PUESTO == 1:
    msg_arg = f"Argentina sigue #{ARG_PUESTO} del mundo"
elif ARG_PUESTO <= 3:
    msg_arg = f"Argentina cae al #{ARG_PUESTO} del mundo"
elif ARG_PUESTO <= 10:
    msg_arg = f"Argentina llega #{ARG_PUESTO} del mundo"
else:
    msg_arg = f"Argentina queda fuera del top 10 (#{ARG_PUESTO})"

ax.text(5, 1.0, msg_arg,
        ha="center", va="center", fontsize=22,
        color=COLORS["accent"], fontweight="bold",
        family=FONTS["title"])

# Footer
ax.text(5, 0.4, "Fuente: ranking FIFA · fifa.com",
        ha="center", va="center", fontsize=14,
        color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_3_ranking.png"
fig.savefig(fname, dpi=100, facecolor="#FFFFFF")
plt.show()
print(f"✅ {fname.name}")

# %% [6. Slide 4 — ARGENTINA EN PERSPECTIVA]
# Big number: puntos FIFA actuales + comparativa con FIFA post-Qatar 2022.
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(COLORS["bg"])  # azul profundo
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Section label
draw_section_label(ax, x=5, y=11.7, label="ARGENTINA EN EL MAPA", color=COLORS["text"])

# Big number: puntos actuales
ax.text(5, 9.3, "PUNTOS FIFA ACTUALES",
        ha="center", va="center", fontsize=22,
        color=COLORS["primary"], family=FONTS["body"])
ax.text(5, 7.7, f"{ARG_PUNTOS:.0f}",
        ha="center", va="center", fontsize=160,
        color=COLORS["accent"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 5.5, f"#{ARG_PUESTO} en el mundo",
        ha="center", va="center", fontsize=32,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["body"])

# Comparativa con post-Qatar 2022 (Argentina pasó al #1 el 22/12/2022 con 1841,3 pts)
PUNTOS_POST_QATAR = 1841  # post-final Mundial 2022, ranking FIFA 22/12/2022
diff = ARG_PUNTOS - PUNTOS_POST_QATAR
diff_color = COLORS["accent"] if diff >= 0 else "#E67E22"  # naranja si bajó
diff_signo = "+" if diff >= 0 else ""

draw_card_box(ax, x=0.5, y=2.5, width=9, height=2.2,
              facecolor=COLORS["primary"], alpha=0.15)
ax.text(5, 4.3, "vs. puntos al ganar el Mundial 2022",
        ha="center", va="center", fontsize=18,
        color=COLORS["text"], family=FONTS["body"])
ax.text(2.5, 3.4, f"{PUNTOS_POST_QATAR}",
        ha="center", va="center", fontsize=46,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["title"])
ax.text(2.5, 2.85, "(dic 2022)",
        ha="center", va="center", fontsize=14,
        color=COLORS["muted"], family=FONTS["data"])

# Flecha dibujada con annotate (en lugar del Unicode → que no renderiza)
ax.annotate("", xy=(5.6, 3.4), xytext=(4.4, 3.4),
            arrowprops=dict(arrowstyle="->", color=COLORS["primary"],
                            lw=3, mutation_scale=25))

ax.text(7.5, 3.4, f"{diff_signo}{diff:.0f}",
        ha="center", va="center", fontsize=46,
        color=diff_color, fontweight="bold",
        family=FONTS["title"])
ax.text(7.5, 2.85, "puntos",
        ha="center", va="center", fontsize=14,
        color=COLORS["muted"], family=FONTS["data"])

# Footer
ax.text(5, 0.6, "Fuente: ranking FIFA · fifa.com",
        ha="center", va="center", fontsize=14,
        color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_4_argentina.png"
fig.savefig(fname, dpi=100, facecolor=COLORS["bg"])
plt.show()
print(f"✅ {fname.name}")

# %% [7. Slide 5 — SCATTER: FORMA RECIENTE vs PUNTOS FIFA]
# Cruza el "% de puntos posibles en últimos partidos" (X) con puntos FIFA (Y).
# Cuadrantes: EN FORMA + TOP / MAL MOMENTO, ALTO PESO / EN RACHA, MENOS PESO / FLOJOS.
# Selecciones que NO clasificaron al Mundial 2026 quedan marcadas con asterisco.

from scripts.scatter_selecciones import plot_scatter_selecciones

# Resultados últimos partidos por selección (Win=W, Draw=D, Loss=L).
# Fuente: columna "Últimos Resultados" del ranking FIFA.
# Algunas selecciones tienen 5 partidos visibles, otras 6.
# Las strings se normalizan después a "% de puntos posibles".
FORMA_RECIENTE_RAW = {
    "Francia":        "DWWWW",
    "España":         "WWDWD",
    "Argentina":      "WWWWW",
    "Inglaterra":     "WWWDL",
    "Portugal":       "DLWDW",
    "Brasil":         "LWDLW",
    "Países Bajos":   "WDWWD",
    "Marruecos":      "WWWDW",
    "Bélgica":        "WDWWD",
    "Alemania":       "WWWWWW",
    "Croacia":        "WWWWWL",
    "Italia":         "WWLWL",
    "Colombia":       "DWWLL",
    "Senegal":        "WWLWW",
    "México":         "WWWDD",
    "EE.UU.":         "WWWWLL",
}

# Selecciones que NO clasificaron al Mundial 2026 (top 16 ranking pero fuera del torneo)
# ⚠️ Confirmado por Lucas: Italia no clasificó. Verificar si hay otras.
NO_JUEGAN_MUNDIAL = {"Italia"}


def calcular_forma(secuencia: str) -> dict:
    """Devuelve dict con métricas de forma: puntos, partidos, ppp, pct_pts_posibles."""
    s = "".join(c for c in secuencia.upper() if c in "WDL")
    n = len(s)
    pts = sum(3 if c == "W" else 1 if c == "D" else 0 for c in s)
    return {
        "forma_str": s,
        "forma_partidos": n,
        "forma_pts": pts,
        "forma_ppp": pts / n if n > 0 else 0,
        "forma_pct": (pts / (3 * n) * 100) if n > 0 else 0,
        "forma_wdl": (s.count("W"), s.count("D"), s.count("L")),
    }


df_slide5 = top16.copy()

# Mapear los datos de forma a cada fila
forma_data = df_slide5["seleccion"].map(FORMA_RECIENTE_RAW).apply(calcular_forma)
for col in ["forma_str", "forma_partidos", "forma_pts", "forma_ppp", "forma_pct", "forma_wdl"]:
    df_slide5[col] = forma_data.apply(lambda d: d[col])

# Marcar las que no juegan el Mundial
df_slide5["juega_mundial"] = ~df_slide5["seleccion"].isin(NO_JUEGAN_MUNDIAL)

# Agregar asterisco al nombre para visualizar las que no clasificaron
df_slide5["seleccion_display"] = df_slide5.apply(
    lambda r: r["seleccion"] + " *" if not r["juega_mundial"] else r["seleccion"],
    axis=1,
)

print("Forma reciente por selección:")
print(df_slide5[["puesto", "seleccion", "forma_str", "forma_pct", "juega_mundial"]])

# Armado del slide
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(COLORS["bg"])

# Header banda dorada
banda = mpatches.Rectangle((0, 0.94), 1, 0.06,
                            facecolor=COLORS["accent"],
                            transform=fig.transFigure,
                            zorder=10)
fig.patches.append(banda)
fig.text(0.5, 0.97, "FORMA RECIENTE vs PESO FIFA",
         ha="center", va="center",
         fontsize=16, fontweight="bold",
         color=COLORS["bg"], family=FONTS["title"], zorder=11)

fig.text(0.5, 0.90, "¿Llegan en su mejor momento?",
         ha="center", va="center", fontsize=24, fontweight="bold",
         color=COLORS["text"], family=FONTS["title"])
fig.text(0.5, 0.87, "% de puntos posibles en los últimos partidos · puntos FIFA actuales",
         ha="center", va="center", fontsize=12,
         color=COLORS["primary"], family=FONTS["body"], style="italic")

# Axes principal del scatter — más alto, dejando espacio abajo para las notas
ax = fig.add_axes([0.10, 0.22, 0.86, 0.60])

plot_scatter_selecciones(
    ax,
    df=df_slide5,
    x_col="forma_pct",
    y_col="puntos",
    label_col="seleccion_display",   # incluye asterisco para las que no juegan
    color_key_col="color_key",
    x_label="% PUNTOS POSIBLES — ÚLTIMOS PARTIDOS",
    y_label="PUNTOS FIFA",
    highlight_label="Argentina",
    quadrant_labels={
        "tr": "EN FORMA + TOP",
        "tl": "ALTO PESO, BAJA FORMA",
        "br": "EN RACHA, MENOS PESO",
        "bl": "FLOJOS",
    },
    point_size=380,
    highlight_size=650,
    label_offset_pts=(13, 0),
    jitter_at_zero=True,
    jitter_strength=0.05,
)

# Forzar xlim un poco más allá del 100% para que Argentina (que está al 100%)
# tenga aire para mostrar su etiqueta sin recorte
ax.set_xlim(-8, 118)

# Ticks de X cada 20%
ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xticklabels(["0%", "20%", "40%", "60%", "80%", "100%"])

# ───── Notas debajo del scatter ─────
# Las posiciones están coordinadas para que no se pisen entre sí ni con el
# axis label del eje X (que cae aproximadamente en y=0.17 con el axes en 0.22).

# Insight de Argentina (cerca del scatter, en dorado para destacar)
arg_row = df_slide5[df_slide5["seleccion"] == "Argentina"].iloc[0]
arg_w, arg_d, arg_l = arg_row["forma_wdl"]
arg_pct = arg_row["forma_pct"]
fig.text(0.5, 0.12,
         f"Argentina viene con {arg_w}W-{arg_d}D-{arg_l}L  ({arg_pct:.0f}% de puntos posibles)",
         ha="center", va="center", fontsize=14, fontweight="bold",
         color=COLORS["accent"], family=FONTS["body"])

# Nota del asterisco
no_juegan = sorted(df_slide5[~df_slide5["juega_mundial"]]["seleccion"].tolist())
if no_juegan:
    nota_text = "*  " + ", ".join(no_juegan) + "  —  no clasificó al Mundial 2026"
    fig.text(0.5, 0.075, nota_text,
             ha="center", va="center", fontsize=11, style="italic",
             color=COLORS["muted"], family=FONTS["body"])

# Fuente al pie
fig.text(0.5, 0.035,
         "Fuente: ranking FIFA Hombres — columna 'Últimos Resultados'",
         ha="center", va="center", fontsize=10,
         color=COLORS["muted"], family=FONTS["data"])

watermark(fig)

fname = OUTPUTS / "slide_5_forma_vs_fifa.png"
fig.savefig(fname, dpi=100, facecolor=COLORS["bg"])
plt.show()
print(f"✅ {fname.name}")

# %% [8. Slide 6 — CIERRE]
fig = plt.figure(figsize=(10.8, 13.5), dpi=100)
fig.patch.set_facecolor(COLORS["bg"])  # azul profundo
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 10)
ax.set_ylim(0, 12.5)
ax.set_axis_off()

# Logo grande arriba
place_logo(fig, x=0.5, y=0.78, size=0.30, variant="simple")

# Pregunta central
ax.text(5, 7.2, "¿Quién levantará",
        ha="center", va="center", fontsize=48,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 6.3, "la copa?",
        ha="center", va="center", fontsize=48,
        color=COLORS["accent"], fontweight="bold",
        family=FONTS["title"])

# CTA
ax.text(5, 4.8, "Dejá tu candidato en los comentarios",
        ha="center", va="center", fontsize=22,
        color=COLORS["primary"], family=FONTS["body"], style="italic")

# Handle grande
ax.text(5, 3.0, "@datafutbol_ar",
        ha="center", va="center", fontsize=42,
        color=COLORS["text"], fontweight="bold",
        family=FONTS["title"])
ax.text(5, 2.3, "fútbol con datos · español · sudamérica",
        ha="center", va="center", fontsize=18,
        color=COLORS["primary"], family=FONTS["body"])

# Footer
ax.text(5, 0.8, "Datos: ranking FIFA Hombres · fifa.com",
        ha="center", va="center", fontsize=14,
        color=COLORS["muted"], family=FONTS["data"])

fname = OUTPUTS / "slide_6_cierre.png"
fig.savefig(fname, dpi=100, facecolor=COLORS["bg"])
plt.show()
print(f"✅ {fname.name}")

# %% [9. Normalizar todos los slides a 1080×1350]
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
print("  2. slide_2_que_es_ranking.png")
print("  3. slide_3_ranking.png")
print("  4. slide_4_argentina.png")
print("  5. slide_5_forma_vs_fifa.png")
print("  6. slide_6_cierre.png")

# %% [Verificación pre-publicación]
# ⚠️ ANTES de programar en Meta, hacé estos chequeos:
#
# 1. Abrí https://www.fifa.com/fifa-world-ranking/men y compará:
#    · El #1 es Argentina con ~1886 pts? Si los puntos cambiaron, pisá el dict.
#    · Algún país del top 16 se movió? Reordená RANKING_FIFA_RAW si hace falta.
#    · La actualización más reciente del ranking FIFA es de qué fecha?
#      (FIFA actualiza cada ~6 semanas; la fecha de la actualización va en el caption.)
#
# 2. Si los datos del notebook son los más recientes:
#    · Re-corré la celda 1 después de actualizar el dict.
#    · Re-corré las celdas 3-7 para regenerar los PNG.
#    · Re-corré la celda 8 para normalizar a 1080x1350.
#
# 3. Caption sugerido para IG (ajustá según los puntos reales del día):
#
#     Las 16 selecciones más fuertes que van al Mundial 2026, según el
#     ranking FIFA actualizado.
#
#     Después de casi 3 años, Argentina perdió el #1: Francia y España la
#     superaron en la última actualización. La diferencia con el campeón
#     mundial caben en un puñado de partidos.
#
#     Faltan menos de 30 días para el debut de Argentina vs Argelia.
#
#     ¿Recupera el #1 antes del Mundial? 👇
#
#     ─────
#     Datos: ranking FIFA Hombres (actualización [pegar fecha de fifa.com])
#     Fuente: inside.fifa.com/es/fifa-world-ranking/men
#
#     #Mundial2026 #Argentina #RankingFIFA #FootballAnalytics #datafutbol

# %% [Mejoras opcionales — para siguiente iteración]
# - Sumar banderas al ranking visual (R27). Descargar de flagcdn.com:
#     https://flagcdn.com/w160/ar.png  (Argentina, .ar)
#     https://flagcdn.com/w160/fr.png  (Francia, .fr)
#     https://flagcdn.com/w160/es.png  (España, .es)
#     ... (uno por país, en G:\Mi unidad\DATAFUTBOL_AR\02_Branding\banderas_paises\)
#   Después en el loop del slide 3, agregar:
#     place_country_flag(fig, x=0.16, y=<calc>, size=0.025, pais=f"{row['iso2']}.png")
#
# - Versión "post final del Mundial" — el mismo template con los puntos actualizados,
#   pero comparando contra el actual.
