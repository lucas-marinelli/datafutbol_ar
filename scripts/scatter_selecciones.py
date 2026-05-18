"""scatter_selecciones — Plantilla reutilizable para scatter de selecciones.

Estilo inspirado en los visuales de DataMoroni adaptado a Combo C
(@datafutbol_ar). Cada selección se dibuja como un punto del color
patrón de su país (R21) con etiqueta al costado. Soporta destacar una
selección específica, etiquetas de cuadrantes y líneas divisorias.

Uso típico (en un notebook de post):

    from scripts.scatter_selecciones import plot_scatter_selecciones

    plot_scatter_selecciones(
        ax,
        df=df_top16,
        x_col="forma_puntos",
        y_col="puntos",
        label_col="seleccion",
        x_label="FORMA RECIENTE (pts últimos 5 partidos)",
        y_label="PUNTOS FIFA",
        highlight_label="Argentina",
        quadrant_labels={
            "tr": "EN FORMA Y TOP",
            "tl": "TRADICIÓN, MAL MOMENTO",
            "br": "EN RACHA, MENOS PESO",
            "bl": "FLOJOS",
        },
    )

Notas técnicas:
- El tamaño del punto va en puntos² (parámetro `s` de ax.scatter), por lo
  que NO depende del rango de los ejes. Antes usábamos mpatches.Circle
  con radio en unidades de datos, lo cual rompía con ejes de escala muy
  distinta (ej. eje Y de rango 0-5 vs eje X de rango 1648-1877).
- Las etiquetas se posicionan en "offset points" usando ax.annotate,
  también independiente de la escala de los ejes.
"""

from __future__ import annotations
from typing import Optional

import numpy as np
import pandas as pd

from scripts.style import (
    COLORS, FONTS, FONT_TITLE, FONT_BODY, FONT_DATA,
    pais_color,
)


def plot_scatter_selecciones(
    ax,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    label_col: str = "seleccion",
    color_key_col: str = "color_key",
    *,
    x_label: str = "",
    y_label: str = "",
    highlight_label: Optional[str] = None,
    show_quadrants: bool = True,
    quadrant_labels: Optional[dict] = None,
    x_split: Optional[float] = None,
    y_split: Optional[float] = None,
    bg_color: Optional[str] = None,
    grid_color: Optional[str] = None,
    text_color: Optional[str] = None,
    point_size: float = 400,
    highlight_size: float = 700,
    label_offset_pts: tuple = (12, 0),
    label_fontsize: int = 11,
    highlight_fontsize: int = 13,
    jitter_at_zero: bool = True,
    jitter_strength: float = 0.06,
) -> None:
    """Dibuja el scatter de selecciones en el axes provisto.

    Args:
        ax: matplotlib Axes donde dibujar.
        df: DataFrame con las selecciones (una fila por selección).
            Debe tener al menos las columnas x_col, y_col, label_col.
        x_col, y_col: columnas numéricas para los ejes.
        label_col: columna con el nombre de la selección (default "seleccion").
        color_key_col: columna que matchea con PAISES_COLORS para el color
                       (default "color_key"). Si no existe, usa label_col.
        x_label, y_label: textos para los ejes.
        highlight_label: nombre de la selección a destacar (borde dorado, label bold).
        show_quadrants: si True dibuja líneas divisorias en las medianas.
        quadrant_labels: dict opcional con claves 'tr', 'tl', 'br', 'bl'
                         (top/bottom right/left).
        x_split, y_split: posiciones de las líneas divisorias.
                          Si None, usa las medianas.
        bg_color: color de fondo del axes (default COLORS['bg']).
        grid_color: color de las líneas auxiliares (default COLORS['primary']).
        text_color: color del texto principal (default COLORS['text']).
        point_size: tamaño del punto en puntos² (matplotlib scatter).
                    Default 400. Independiente del rango de ejes.
        highlight_size: tamaño del punto highlight (default 700).
        label_offset_pts: tupla (dx, dy) de offset de la etiqueta en puntos.
        label_fontsize: tamaño de la etiqueta normal.
        highlight_fontsize: tamaño de la etiqueta destacada.
        jitter_at_zero: si True, aplica jitter horizontal a puntos
                        amontonados en y=0 (o en cualquier valor repetido).
        jitter_strength: fracción del rango X para el jitter (default 0.06).
    """
    # Defaults de color
    bg_color = bg_color or COLORS["bg"]
    grid_color = grid_color or COLORS["primary"]
    text_color = text_color or COLORS["text"]

    # Determinar columna de color
    if color_key_col not in df.columns:
        color_key_col = label_col

    # Setup del axes
    ax.set_facecolor(bg_color)

    # Rangos con padding
    x_min, x_max = float(df[x_col].min()), float(df[x_col].max())
    y_min, y_max = float(df[y_col].min()), float(df[y_col].max())
    x_pad = (x_max - x_min) * 0.12 if x_max > x_min else 1
    y_pad = (y_max - y_min) * 0.18 if y_max > y_min else 1

    ax.set_xlim(x_min - x_pad, x_max + x_pad)
    ax.set_ylim(y_min - y_pad, y_max + y_pad)

    # Líneas divisorias (medianas) — antes de los puntos para que queden atrás
    if show_quadrants:
        x_sp = x_split if x_split is not None else float(df[x_col].median())
        y_sp = y_split if y_split is not None else float(df[y_col].median())

        ax.axvline(x_sp, color=grid_color, linestyle="--", linewidth=1,
                   alpha=0.35, zorder=1)
        ax.axhline(y_sp, color=grid_color, linestyle="--", linewidth=1,
                   alpha=0.35, zorder=1)

        if quadrant_labels:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            corners = {
                "tr": (xlim[1] - x_pad * 0.15, ylim[1] - y_pad * 0.20, "right", "top"),
                "tl": (xlim[0] + x_pad * 0.15, ylim[1] - y_pad * 0.20, "left",  "top"),
                "br": (xlim[1] - x_pad * 0.15, ylim[0] + y_pad * 0.20, "right", "bottom"),
                "bl": (xlim[0] + x_pad * 0.15, ylim[0] + y_pad * 0.20, "left",  "bottom"),
            }
            for key, label in quadrant_labels.items():
                if key in corners:
                    cx, cy, ha, va = corners[key]
                    ax.text(cx, cy, label,
                            ha=ha, va=va, fontsize=10, fontweight="bold",
                            color=COLORS["muted"], family=FONT_DATA,
                            alpha=0.75, zorder=2)

    # Jitter horizontal para puntos amontonados verticalmente
    jitter_x = np.zeros(len(df))
    if jitter_at_zero:
        rng = np.random.default_rng(seed=42)
        y_values = df[y_col].values
        # Contar cuántas filas tienen el mismo y_value
        y_counts = pd.Series(y_values).value_counts()
        amontonados = y_counts[y_counts > 1].index
        for y_val in amontonados:
            mask = (y_values == y_val)
            n = int(mask.sum())
            # Distribuir simétricamente alrededor del x original
            offsets = np.linspace(-1, 1, n) * jitter_strength * (x_max - x_min)
            # Shuffle determinístico para evitar orden por nombre
            rng.shuffle(offsets)
            jitter_x[mask] = offsets

    # Dibujar puntos
    df_iter = df.reset_index(drop=True)
    for i, row in df_iter.iterrows():
        x_data = float(row[x_col]) + jitter_x[i]
        y_data = float(row[y_col])
        nombre = str(row[label_col])
        key = str(row[color_key_col]) if color_key_col in row else nombre

        es_highlight = (highlight_label is not None and nombre == highlight_label)
        color = pais_color(key, "primary")
        s = highlight_size if es_highlight else point_size
        edgecolor = COLORS["accent"] if es_highlight else COLORS["bg"]
        linewidth = 2.5 if es_highlight else 1.2

        ax.scatter(
            x_data, y_data,
            s=s,
            c=color,
            edgecolors=edgecolor,
            linewidths=linewidth,
            alpha=0.92,
            zorder=4 if es_highlight else 3,
        )

        # Etiqueta — offset en puntos (independiente de la escala)
        fontsize = highlight_fontsize if es_highlight else label_fontsize
        fontweight = "bold" if es_highlight else "normal"
        label_color = COLORS["accent"] if es_highlight else text_color

        ax.annotate(
            nombre,
            xy=(x_data, y_data),
            xytext=label_offset_pts,
            textcoords="offset points",
            ha="left", va="center",
            fontsize=fontsize, fontweight=fontweight,
            color=label_color, family=FONT_BODY,
            zorder=5 if es_highlight else 4,
        )

    # Ejes
    if x_label:
        ax.set_xlabel(x_label, fontsize=12, color=COLORS["primary"],
                      family=FONT_DATA, labelpad=12, fontweight="bold")
    if y_label:
        ax.set_ylabel(y_label, fontsize=12, color=COLORS["primary"],
                      family=FONT_DATA, labelpad=12, fontweight="bold")

    ax.tick_params(axis="both", colors=COLORS["muted"], labelsize=10)
    for spine_name in ("top", "right"):
        ax.spines[spine_name].set_visible(False)
    for spine_name in ("left", "bottom"):
        ax.spines[spine_name].set_color(COLORS["muted"])
        ax.spines[spine_name].set_alpha(0.4)
