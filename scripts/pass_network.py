"""
pass_network.py — Redes de pases con identidad visual @datafutbol_ar

Genera la red de pases promedio de un equipo en un partido (o ventana).
Calcula posiciones promedio de cada jugador y conexiones por cantidad
de pases entre pares.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplsoccer import Pitch

from scripts.style import (
    BG, PRIMARY, ACCENT, TEXT, MUTED,
    FONT_TITLE, FONT_BODY, FONT_DATA,
    apply_branding, watermark,
)
from scripts.jugadores import display_name


def _extract_coord(loc, idx: int):
    """Saca x (idx=0) o y (idx=1) de location, robusto a list/ndarray/string/NaN."""
    if loc is None:
        return None
    try:
        if pd.isna(loc):
            return None
    except (TypeError, ValueError):
        pass
    try:
        if len(loc) >= idx + 1:
            return float(loc[idx])
    except (TypeError, IndexError, ValueError):
        pass
    return None


def _normalizar_eventos_pases(events: pd.DataFrame) -> pd.DataFrame:
    """Filtra pases completados y agrega columnas x, y desde location."""
    df = events.copy()
    df = df[df["type"] == "Pass"]
    if "pass_outcome" in df.columns:
        df = df[df["pass_outcome"].isna()]  # Pase completado = NaN

    if "location" in df.columns:
        df["x"] = df["location"].apply(lambda loc: _extract_coord(loc, 0))
        df["y"] = df["location"].apply(lambda loc: _extract_coord(loc, 1))

    return df.dropna(subset=["x", "y"])


def _calcular_stats_pass_network(
    df_pases: pd.DataFrame,
    posiciones: pd.DataFrame,
    conexiones: pd.DataFrame,
) -> dict:
    """Calcula stats del pass network para el panel inferior."""
    total_pases = len(df_pases)
    n_jugadores = len(posiciones)

    # Jugador con más pases jugados (más toques en general)
    top_jugador = None
    top_pases = 0
    if not posiciones.empty:
        top_row = posiciones.sort_values("pases", ascending=False).iloc[0]
        top_jugador = top_row["player"]
        top_pases = int(top_row["pases"])

    # Conexión más fuerte (par de jugadores con más pases entre ellos)
    conexion_top = None
    conexion_n = 0
    if not conexiones.empty:
        top_conn = conexiones.sort_values("cantidad", ascending=False).iloc[0]
        p1, p2 = top_conn["pair"]
        conexion_top = (display_name(p1), display_name(p2))
        conexion_n = int(top_conn["cantidad"])

    return {
        "total_pases": total_pases,
        "n_jugadores": n_jugadores,
        "top_jugador": top_jugador,
        "top_pases": top_pases,
        "conexion_top": conexion_top,
        "conexion_n": conexion_n,
    }


def _dibujar_panel_stats_pn(fig: plt.Figure, stats: dict, y_base: float = 0.22) -> None:
    """Panel inferior con stats del pass network."""
    labels = ["PASES", "JUGADORES", "TOP PASADOR", "MÁS PASES"]

    top_name = display_name(stats["top_jugador"]) if stats["top_jugador"] else "—"
    top_str = f"{top_name}  ({stats['top_pases']})" if stats["top_jugador"] else "—"

    values = [
        f"{stats['total_pases']}",
        f"{stats['n_jugadores']}",
        top_str,
        f"{stats['conexion_n']}",
    ]
    xs = [0.15, 0.35, 0.62, 0.86]

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
            fontsize=14 if x == 0.62 else 18,
            color=ACCENT,
            fontweight="bold",
        )

    # Conexión más fuerte como subtítulo del bloque
    if stats["conexion_top"]:
        p1, p2 = stats["conexion_top"]
        fig.text(
            0.5, y_base - 0.035,
            "DUPLA MÁS CONECTADA",
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=9,
            color=MUTED,
            fontweight="bold",
        )
        fig.text(
            0.5, y_base - 0.065,
            f"{p1}  ↔  {p2}  ·  {stats['conexion_n']} pases",
            ha="center",
            fontfamily=FONT_DATA,
            fontsize=13,
            color=TEXT,
        )


def crear_pass_network(
    events: pd.DataFrame,
    equipo: str,
    titulo: str,
    subtitulo: Optional[str] = None,
    fuente: str = "StatsBomb",
    hasta_minuto: Optional[int] = None,
    min_pases: int = 3,
    figsize: tuple[float, float] = (8, 12),
    mostrar_stats: bool = True,
) -> tuple[plt.Figure, plt.Axes]:
    """Genera una pass network del equipo en un partido.

    Args:
        events: DataFrame de eventos StatsBomb.
        equipo: Nombre exacto del equipo (ej: "Argentina").
        titulo: Título principal.
        subtitulo: Subtítulo opcional.
        fuente: Fuente de datos.
        hasta_minuto: Si se pasa, sólo considera eventos hasta ese minuto
            (típicamente hasta el primer cambio).
        min_pases: Mínimo de pases entre dos jugadores para mostrar la línea.
        figsize: Tamaño de la figura.

    Returns:
        (fig, ax)

    Ejemplo:
        from statsbombpy import sb
        from scripts.pass_network import crear_pass_network

        events = sb.events(match_id=3869685)
        fig, ax = crear_pass_network(
            events, equipo="Argentina",
            titulo="ARG · Pass Network 1er tiempo vs Francia",
            hasta_minuto=45,
        )
    """
    df = _normalizar_eventos_pases(events)
    df = df[df["team"] == equipo]

    if hasta_minuto:
        df = df[df["minute"] <= hasta_minuto]

    if df.empty:
        raise ValueError(f"No hay pases para {equipo} con esos filtros")

    # Posiciones promedio de cada jugador
    posiciones = (
        df.groupby("player")
        .agg(x=("x", "mean"), y=("y", "mean"), pases=("x", "count"))
        .reset_index()
    )

    # Conexiones (pase entre par de jugadores)
    df_pairs = df[["player", "pass_recipient"]].dropna()
    df_pairs["pair"] = df_pairs.apply(
        lambda r: tuple(sorted([r["player"], r["pass_recipient"]])), axis=1
    )
    conexiones = (
        df_pairs.groupby("pair")
        .size()
        .reset_index(name="cantidad")
    )
    conexiones = conexiones[conexiones["cantidad"] >= min_pases]

    # Pitch vertical full — usamos add_axes() para forzar el rectángulo exacto
    # (mplsoccer respeta el ax pre-creado en lugar de pisarlo con su layout).
    from mplsoccer import VerticalPitch

    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(BG)

    # Layout estricto — todo el "dato anexo" FUERA del pitch
    #   Zona títulos:  y = 0.84 - 0.98
    #   Zona pitch:    y = 0.34 - 0.84
    #   Zona stats:    y = 0.00 - 0.34
    ax = fig.add_axes([0.06, 0.34, 0.88, 0.50])

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        pitch_color=BG,
        line_color=TEXT,
        stripe=False,
        linewidth=1.2,
        half=False,
        line_zorder=0.5,
    )
    pitch.draw(ax=ax)

    # Aristas
    max_pases = conexiones["cantidad"].max() if len(conexiones) else 1
    for _, row in conexiones.iterrows():
        p1, p2 = row["pair"]
        n = row["cantidad"]
        try:
            x1, y1 = posiciones.loc[posiciones["player"] == p1, ["x", "y"]].iloc[0]
            x2, y2 = posiciones.loc[posiciones["player"] == p2, ["x", "y"]].iloc[0]
        except IndexError:
            continue
        ancho = 0.5 + (n / max_pases) * 4
        alpha = 0.3 + (n / max_pases) * 0.5
        pitch.lines(
            x1, y1, x2, y2,
            ax=ax, color=TEXT, lw=ancho, alpha=alpha, zorder=1,
        )

    # Nodos
    pitch.scatter(
        posiciones["x"], posiciones["y"],
        s=posiciones["pases"] * 18 + 200,
        ax=ax,
        c=PRIMARY,
        edgecolors=ACCENT,
        linewidth=2,
        zorder=3,
        alpha=0.95,
    )

    # Nombre público (Messi en vez de Cuccittini) + fondo oscuro para
    # que se lea sobre cualquier color del pitch (línea blanca, círculo celeste).
    for _, row in posiciones.iterrows():
        if pd.isna(row["player"]):
            continue
        nombre = display_name(row["player"])
        pitch.annotate(
            nombre,
            xy=(row["x"], row["y"]),
            ax=ax,
            fontsize=9,
            color=TEXT,
            fontfamily=FONT_BODY,
            ha="center",
            va="center",
            zorder=5,
            fontweight="bold",
            xytext=(0, 18),  # mueve el texto 18 puntos arriba del nodo
            textcoords="offset points",
            bbox=dict(
                facecolor=BG,        # fondo azul profundo
                edgecolor=ACCENT,    # borde dorado
                boxstyle="round,pad=0.3",
                alpha=0.85,
                linewidth=0.8,
            ),
        )

    # Título y subtítulo arriba del pitch
    fig.patch.set_facecolor(BG)
    fig.suptitle(
        titulo,
        fontfamily=FONT_TITLE,
        fontsize=22,
        color=TEXT,
        fontweight="bold",
        y=0.95,
    )
    if subtitulo:
        fig.text(
            0.5, 0.885,
            subtitulo,
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=12,
            color=PRIMARY,
        )

    watermark(fig, source=fuente)

    # Panel de stats abajo del pitch
    if mostrar_stats:
        stats = _calcular_stats_pass_network(df, posiciones, conexiones)
        _dibujar_panel_stats_pn(fig, stats, y_base=0.20)

    return fig, ax
