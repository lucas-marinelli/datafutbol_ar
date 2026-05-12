"""
heatmap.py — Mapas de calor con identidad visual @datafutbol_ar

Genera heatmaps de densidad (KDE) o por bins de eventos sobre el campo.
Útil para mostrar dónde se mueve un jugador o dónde un equipo tiene
mayor actividad.
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from mplsoccer import Pitch

from scripts.style import (
    BG, PRIMARY, ACCENT, TEXT, MUTED,
    FONT_TITLE, FONT_BODY, FONT_DATA,
    apply_branding, watermark,
)
from scripts.jugadores import display_name


# Custom colormap: azul profundo → celeste → blanco → dorado
DATAFUTBOL_CMAP = LinearSegmentedColormap.from_list(
    "datafutbol",
    [BG, "#1F4870", PRIMARY, "#E0EBF5", ACCENT],
    N=256,
)


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


def _normalizar_location(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura que el DataFrame tenga columnas `x` e `y` con coordenadas float."""
    df = df.copy()
    if "location" in df.columns:
        df["x"] = df["location"].apply(lambda loc: _extract_coord(loc, 0))
        df["y"] = df["location"].apply(lambda loc: _extract_coord(loc, 1))
    return df.dropna(subset=["x", "y"])


def _calcular_stats_heatmap(eventos: pd.DataFrame, jugador: Optional[str] = None) -> dict:
    """Calcula stats agregadas para el panel inferior del heatmap.

    Devuelve:
        total: toques totales del DataFrame
        ultimo_tercio: cantidad de toques en x > 80 (ataque)
        ultimo_tercio_pct: porcentaje de toques en último tercio
        area_rival: toques en el área rival (x > 102 y 18 <= y <= 62)
        intensidad: toques por minuto (toques / minutos jugados)
        minutos: minutos jugados (estimado por max - min de minuto)
        jugador: nombre del jugador (si se pasa)
    """
    total = len(eventos)
    minutos = 0
    if total and "minute" in eventos.columns:
        try:
            min_min = int(eventos["minute"].min())
            min_max = int(eventos["minute"].max())
            minutos = max(min_max - min_min, 1)
        except (ValueError, TypeError):
            minutos = 0

    ultimo_tercio = int((eventos["x"] > 80).sum()) if total else 0
    ultimo_tercio_pct = (ultimo_tercio / total * 100) if total else 0
    area_rival = int(
        ((eventos["x"] > 102) & (eventos["y"] >= 18) & (eventos["y"] <= 62)).sum()
    ) if total else 0
    intensidad = (total / minutos) if minutos else 0

    return {
        "total": total,
        "ultimo_tercio": ultimo_tercio,
        "ultimo_tercio_pct": ultimo_tercio_pct,
        "area_rival": area_rival,
        "intensidad": intensidad,
        "minutos": minutos,
        "jugador": jugador,
    }


def _dibujar_panel_stats_heatmap(fig: plt.Figure, stats: dict, y_base: float = 0.18) -> None:
    """Dibuja panel inferior con stats del heatmap."""
    labels = ["TOQUES", "ÚLTIMO TERCIO", "ÁREA RIVAL", "TOQUES / MIN"]
    values = [
        f"{stats['total']}",
        f"{stats['ultimo_tercio']}  ({stats['ultimo_tercio_pct']:.0f}%)",
        f"{stats['area_rival']}",
        f"{stats['intensidad']:.2f}",
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
            fontsize=18,
            color=ACCENT,
            fontweight="bold",
        )

    # Sub-fila — minutos jugados o nombre jugador
    if stats.get("jugador"):
        fig.text(
            0.5, y_base - 0.035,
            "JUGADOR",
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=9,
            color=MUTED,
            fontweight="bold",
        )
        fig.text(
            0.5, y_base - 0.065,
            f"{display_name(stats['jugador'])}  ·  {stats['minutos']} min jugados",
            ha="center",
            fontfamily=FONT_DATA,
            fontsize=13,
            color=TEXT,
        )


def crear_heatmap(
    eventos: pd.DataFrame,
    titulo: str,
    subtitulo: Optional[str] = None,
    fuente: str = "StatsBomb",
    metodo: str = "kde",
    figsize: tuple[float, float] = (8, 12),
    bandwidth: float = 0.4,
    mostrar_stats: bool = True,
    jugador: Optional[str] = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Genera un heatmap a partir de eventos con coordenadas.

    Args:
        eventos: DataFrame con columnas `x`, `y` o `location`.
        titulo: Título principal.
        subtitulo: Subtítulo opcional.
        fuente: Fuente de datos.
        metodo: "kde" (suave) o "bins" (cuadrícula).
        figsize: Tamaño de la figura.
        bandwidth: Sólo para método KDE. Más alto = más difuso.

    Returns:
        (fig, ax)

    Ejemplo:
        from statsbombpy import sb
        from scripts.heatmap import crear_heatmap

        events = sb.events(match_id=3869685)
        toques_messi = events[events["player"] == "Lionel Andrés Messi Cuccittini"]
        fig, ax = crear_heatmap(
            toques_messi,
            titulo="MESSI · Final Mundial 2022",
            subtitulo="Mapa de toques",
        )
    """
    df = _normalizar_location(eventos)

    if df.empty:
        raise ValueError("No hay eventos con coordenadas válidas")

    # Pitch vertical full — formato 1080x1350 IG
    # Estrategia: crear la fig + ax MANUALMENTE con posición controlada,
    # y después pedirle a mplsoccer que dibuje sobre ese ax. Más confiable
    # que pitch.draw(figsize) + ax.set_position() porque mplsoccer
    # respeta nuestro rectángulo en lugar de forzar aspect ratio.
    from mplsoccer import VerticalPitch

    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(BG)

    # Zona PITCH: rectángulo central (50% del alto)
    # Arriba (y > 0.84) queda libre para título + subtítulo.
    # Abajo (y < 0.34) queda libre para el panel de stats.
    ax = fig.add_axes([0.06, 0.34, 0.88, 0.50])

    pitch = VerticalPitch(
        pitch_type="statsbomb",
        pitch_color=BG,
        line_color=TEXT,
        stripe=False,
        linewidth=1.2,
        half=False,
        line_zorder=10,
    )
    pitch.draw(ax=ax)

    if metodo == "kde":
        pitch.kdeplot(
            df["x"], df["y"],
            ax=ax,
            fill=True,
            levels=100,
            thresh=0.05,
            cmap=DATAFUTBOL_CMAP,
            bw_adjust=bandwidth,
            alpha=0.70,
            zorder=2,
        )
    elif metodo == "bins":
        bin_stats = pitch.bin_statistic(
            df["x"], df["y"],
            statistic="count",
            bins=(12, 8),
        )
        pitch.heatmap(bin_stats, ax=ax, cmap=DATAFUTBOL_CMAP, alpha=0.75, zorder=2)
    else:
        raise ValueError(f"método desconocido: {metodo} (usar 'kde' o 'bins')")

    # Título y subtítulo — zona arriba del pitch (y > 0.84)
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

    # Panel de stats — zona abajo del pitch (y < 0.34)
    # y_base=0.20 → distribuye mejor entre pitch arriba y watermark abajo.
    if mostrar_stats:
        stats = _calcular_stats_heatmap(df, jugador=jugador)
        _dibujar_panel_stats_heatmap(fig, stats, y_base=0.20)

    return fig, ax
