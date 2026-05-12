"""
shot_map.py — Mapas de tiros con identidad visual @datafutbol_ar

Función reutilizable para generar shot maps con la paleta Combo C.
Los tiros se grafican como círculos cuyo tamaño representa el xG y
el color indica si fue gol (lleno) o no (con borde).

Datos esperados: DataFrame de eventos de StatsBomb con columnas:
    - location (lista [x, y]) o location_x, location_y
    - shot_statsbomb_xg (float)
    - shot_outcome (str, "Goal" o cualquier otro)
    - team (str), player (str), minute, second
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import VerticalPitch

from scripts.style import (
    BG, PRIMARY, ACCENT, TEXT, MUTED,
    FONT_TITLE, FONT_BODY, FONT_DATA,
    apply_branding, watermark,
)
from scripts.jugadores import display_name


def _extract_coord(loc, idx: int):
    """Saca la coordenada `idx` (0 = x, 1 = y) de location.

    `location` puede venir como:
    - list / tuple: [x, y]
    - numpy.ndarray: array([x, y])
    - string: "[x, y]"  (raro pero pasa)
    - None / NaN: cuando no se sabe

    Devuelve None si no se puede extraer.
    """
    if loc is None:
        return None
    # NaN check (pd.isna falla con arrays; usar try/except)
    try:
        if pd.isna(loc):
            return None
    except (TypeError, ValueError):
        pass
    # list, tuple, ndarray, etc. — todo lo indexable con len
    try:
        if len(loc) >= idx + 1:
            return float(loc[idx])
    except (TypeError, IndexError, ValueError):
        pass
    return None


def _normalizar_location(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura que el DataFrame tenga columnas `x` e `y` con coordenadas float.

    Si existe la columna `location`, SIEMPRE recalculamos x, y desde ahí
    (no confiamos en columnas x/y preexistentes porque pueden venir de otro
    evento o estar en NaN). Soporta location como list, tuple, ndarray o string.
    """
    df = df.copy()

    if "location" in df.columns:
        df["x"] = df["location"].apply(lambda loc: _extract_coord(loc, 0))
        df["y"] = df["location"].apply(lambda loc: _extract_coord(loc, 1))
        return df

    if "x" in df.columns and "y" in df.columns:
        return df

    raise ValueError(
        "El DataFrame debe tener columna `location` o columnas `x`, `y`."
    )


def _calcular_stats(shots: pd.DataFrame) -> dict:
    """Calcula stats agregadas de un set de tiros para el panel informativo."""
    total = len(shots)
    goles = int((shots["shot_outcome"] == "Goal").sum())
    xg_total = float(shots["shot_statsbomb_xg"].sum()) if "shot_statsbomb_xg" in shots else 0.0
    xg_por_tiro = xg_total / total if total else 0.0

    # Top tirador (por cantidad de tiros, desempata por xG)
    top_jugador, top_tiros, top_xg = None, 0, 0.0
    if total and "player" in shots.columns:
        by_player = (
            shots.groupby("player")
            .agg(tiros=("player", "count"), xg=("shot_statsbomb_xg", "sum"))
            .sort_values(["tiros", "xg"], ascending=False)
        )
        if not by_player.empty:
            top_jugador = by_player.index[0]
            top_tiros = int(by_player.iloc[0]["tiros"])
            top_xg = float(by_player.iloc[0]["xg"])

    return {
        "total": total,
        "goles": goles,
        "xg_total": xg_total,
        "xg_por_tiro": xg_por_tiro,
        "top_jugador": top_jugador,
        "top_tiros": top_tiros,
        "top_xg": top_xg,
    }


def _dibujar_panel_stats(fig: plt.Figure, stats: dict, y_base: float = 0.18) -> None:
    """Dibuja el panel de stats en la parte inferior de la figura.

    Layout:
        Fila 1: 4 columnas (TIROS / GOLES / xG / xG/TIRO) con label + valor
        Fila 2: TOP TIRADOR (full-width, dorado)
    """
    # Fila 1 — 4 columnas centradas
    labels = ["TIROS", "GOLES", "xG TOTAL", "xG / TIRO"]
    values = [
        f"{stats['total']}",
        f"{stats['goles']}",
        f"{stats['xg_total']:.2f}",
        f"{stats['xg_por_tiro']:.2f}",
    ]
    xs = [0.18, 0.40, 0.62, 0.84]

    for x, label, value in zip(xs, labels, values):
        fig.text(
            x, y_base + 0.05,
            label,
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=10,
            color=MUTED,
            fontweight="bold",
        )
        fig.text(
            x, y_base + 0.015,
            value,
            ha="center",
            fontfamily=FONT_DATA,
            fontsize=22,
            color=ACCENT,
            fontweight="bold",
        )

    # Fila 2 — top tirador (full width)
    if stats["top_jugador"]:
        # Convertir nombre legal a nombre reconocible vía scripts.jugadores
        nombre_publico = display_name(stats["top_jugador"])
        fig.text(
            0.5, y_base - 0.035,
            "TOP TIRADOR",
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=9,
            color=MUTED,
            fontweight="bold",
        )
        fig.text(
            0.5, y_base - 0.065,
            f"{nombre_publico}  ·  {stats['top_tiros']} tiros  ·  {stats['top_xg']:.2f} xG",
            ha="center",
            fontfamily=FONT_DATA,
            fontsize=13,
            color=TEXT,
        )


def crear_shot_map(
    shots: pd.DataFrame,
    titulo: str,
    subtitulo: Optional[str] = None,
    fuente: str = "StatsBomb",
    figsize: tuple[float, float] = (8, 12),
    show_player_names: bool = False,
    mostrar_stats: bool = True,
) -> tuple[plt.Figure, plt.Axes]:
    """Genera un shot map con la identidad de @datafutbol_ar.

    Args:
        shots: DataFrame con tiros (eventos shot de StatsBomb).
        titulo: Título principal (ej: "ARG 3-3 FRA · Mundial 2022").
        subtitulo: Subtítulo opcional (ej: "Final · Lusail Stadium").
        fuente: Fuente de los datos para el watermark.
        figsize: Tamaño de la figura.
        show_player_names: Si True, anota el nombre del jugador junto al tiro.
        mostrar_stats: Si True, dibuja un panel inferior con tiros, goles,
            xG total, xG/tiro y top tirador. Default: True.

    Returns:
        (fig, ax): Para que el caller pueda agregar más cosas o guardar.

    Ejemplo:
        from statsbombpy import sb
        from scripts.shot_map import crear_shot_map

        events = sb.events(match_id=3869685)
        shots = events[
            (events["type"] == "Shot") &
            (events["team"] == "Argentina")
        ]
        fig, ax = crear_shot_map(
            shots,
            titulo="ARG 3-3 FRA · Mundial 2022",
            subtitulo="Final · todos los tiros de Argentina",
        )
        fig.savefig("outputs/2026-05/shotmap_arg_fra.png", dpi=200,
                    facecolor=BG, bbox_inches="tight")
    """
    shots = _normalizar_location(shots)

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        pitch_color=BG,
        line_color=TEXT,
        stripe=False,
        half=True,
        pad_top=2,
    )
    fig, ax = pitch.draw(figsize=figsize)
    fig.set_facecolor(BG)

    # Goles vs no-goles
    goles = shots[shots["shot_outcome"] == "Goal"]
    no_goles = shots[shots["shot_outcome"] != "Goal"]

    # No goles: círculo con borde celeste, sin relleno
    pitch.scatter(
        no_goles["x"], no_goles["y"],
        s=no_goles["shot_statsbomb_xg"] * 800 + 30,
        ax=ax,
        edgecolors=PRIMARY,
        facecolors="none",
        linewidth=1.8,
        alpha=0.85,
    )

    # Goles: círculo lleno celeste, borde dorado
    pitch.scatter(
        goles["x"], goles["y"],
        s=goles["shot_statsbomb_xg"] * 800 + 30,
        ax=ax,
        c=PRIMARY,
        edgecolors=ACCENT,
        linewidth=2.2,
        alpha=0.95,
    )

    if show_player_names:
        for _, shot in shots.iterrows():
            if pd.notna(shot.get("player")):
                pitch.annotate(
                    shot["player"].split()[-1],  # solo apellido
                    xy=(shot["x"], shot["y"]),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ax=ax,
                    fontsize=8,
                    color=TEXT,
                    fontfamily=FONT_BODY,
                    ha="center",
                )

    apply_branding(fig, title=titulo, subtitle=subtitulo)
    watermark(fig, source=fuente)

    # Panel de stats inferior (aprovecha el espacio vacío del half pitch)
    if mostrar_stats:
        stats = _calcular_stats(shots)
        _dibujar_panel_stats(fig, stats, y_base=0.18)

    # Leyenda mini al pie
    fig.text(
        0.5, 0.04,
        "● lleno = gol     ○ borde = no gol     tamaño = xG",
        ha="center",
        fontfamily=FONT_BODY,
        fontsize=10,
        color=MUTED,
    )

    return fig, ax
