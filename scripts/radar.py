"""
radar.py — Radar tipo polígono (spider chart) con identidad visual @datafutbol_ar

Usa `mplsoccer.Radar` (polígono) en vez de `PyPizza` (rebanadas).
El polígono es más familiar para audiencia general (estilo FIFA, videojuegos)
y al superponer dos polígonos (jugador vs promedio) la diferencia es OBVIA.

Plantilla reutilizable: para hacer un radar nuevo solo hay que pasar
- métricas (lista de nombres)
- min/max de cada métrica (rango del eje)
- valores del jugador analizado
- valores de un jugador / promedio de referencia
- títulos
"""

from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
from mplsoccer import Radar, FontManager

from scripts.style import (
    BG, PRIMARY, ACCENT, TEXT, MUTED,
    FONT_TITLE, FONT_BODY, FONT_DATA,
    watermark,
)
from scripts.jugadores import display_name


def _dibujar_panel_inferior(
    fig: plt.Figure,
    metricas: list[str],
    valores_jugador: list[float],
    valores_referencia: list[float],
    nombre_jugador: str,
    nombre_referencia: str,
    y_base: float = 0.13,
) -> None:
    """Panel inferior con frase narrativa (regla R11: gancho, no explicación técnica).

    Calcula:
    - En cuántas métricas el jugador supera a la referencia
    - Cuál es la métrica donde la brecha es mayor (en ratio)
    """
    n = len(metricas)
    supera = sum(1 for v, r in zip(valores_jugador, valores_referencia) if v > r)

    # Métrica con mayor brecha relativa
    ratios = [
        (valores_jugador[i] / valores_referencia[i]) if valores_referencia[i] > 0 else 1
        for i in range(n)
    ]
    idx_top = ratios.index(max(ratios))
    metrica_top = metricas[idx_top].replace("\n", " ")
    ratio_top = ratios[idx_top]

    # Frase principal — big number tipo "gancho"
    fig.text(
        0.5, y_base + 0.04,
        f"Mejor que el {nombre_referencia.lower()} en {supera} de {n} métricas",
        ha="center",
        fontfamily=FONT_BODY,
        fontsize=14,
        color=TEXT,
        fontweight="bold",
    )

    # Sub-frase — brecha máxima
    fig.text(
        0.5, y_base,
        f"Su mejor diferencia: {metrica_top} ({ratio_top:.1f}× el {nombre_referencia.lower()})",
        ha="center",
        fontfamily=FONT_BODY,
        fontsize=11,
        color=PRIMARY,
    )


def crear_radar_comparativo(
    metricas: list[str],
    valores_jugador: list[float],
    valores_referencia: list[float],
    nombre_jugador: str,
    nombre_referencia: str = "Promedio del grupo",
    min_range: Optional[list[float]] = None,
    max_range: Optional[list[float]] = None,
    titulo: str = "",
    subtitulo: Optional[str] = None,
    fuente: str = "StatsBomb · FBref",
    figsize: tuple[float, float] = (8, 12),
) -> tuple[plt.Figure, plt.Axes]:
    """Genera un radar polígono comparando dos jugadores (o jugador vs promedio).

    Args:
        metricas: 6-10 nombres de métricas a comparar. Cada nombre puede tener
            \\n para que el label se quiebre en 2 líneas si es muy largo.
        valores_jugador: valores reales del jugador analizado (no percentiles).
        valores_referencia: valores reales del jugador de referencia o promedio.
        nombre_jugador: nombre público (ej. "Messi"). Aparece en la leyenda.
        nombre_referencia: nombre del grupo de comparación (ej. "Promedio top 5 ligas").
        min_range: mínimo de cada eje radial. Si None, usa 0 para todas.
        max_range: máximo de cada eje radial. Si None, usa max(valores) × 1.1 para cada métrica.
        titulo: título principal (ej. "MESSI · La Liga 2014-15").
        subtitulo: subtítulo aclaratorio (ej. "vs 120 delanteros top 5 ligas · por 90 min").
        fuente: fuente de los datos (watermark).
        figsize: tamaño de la figura. Default (8, 12) para IG carrusel 1080×1350.

    Returns:
        (fig, ax)

    Ejemplo de uso (plantilla mínima):
        from scripts.radar import crear_radar_comparativo

        fig, ax = crear_radar_comparativo(
            metricas=["Goles", "Asistencias", "xG", "Tiros", "Pases prog.", "Carries prog."],
            valores_jugador=[1.13, 0.47, 0.85, 5.80, 7.50, 5.20],
            valores_referencia=[0.40, 0.15, 0.35, 2.50, 5.50, 2.50],
            min_range=[0, 0, 0, 0, 0, 0],
            max_range=[1.5, 0.7, 1.2, 7, 10, 7],
            nombre_jugador="Messi",
            nombre_referencia="Promedio del grupo",
            titulo="MESSI · La Liga 2014-15",
            subtitulo="vs 120 delanteros top 5 ligas · por 90 min",
        )
    """
    n = len(metricas)
    if len(valores_jugador) != n or len(valores_referencia) != n:
        raise ValueError("metricas, valores_jugador y valores_referencia deben tener el mismo largo")

    # Rangos por default si no se pasan
    if min_range is None:
        min_range = [0.0] * n
    if max_range is None:
        max_range = [max(v, r) * 1.1 for v, r in zip(valores_jugador, valores_referencia)]

    # ── Crear el Radar ──────────────────────────────────────────────
    radar = Radar(
        params=metricas,
        min_range=min_range,
        max_range=max_range,
        num_rings=4,
        ring_width=1,
        center_circle_radius=1,
    )

    # ── Setup figura + ax ───────────────────────────────────────────
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor(BG)

    # Layout estricto (regla R4): radar en el centro, texto afuera.
    ax = fig.add_axes([0.10, 0.32, 0.80, 0.52], polar=False)
    ax.set_facecolor(BG)

    # Dibujar anillos
    radar.setup_axis(ax=ax, facecolor=BG)
    rings_inner = radar.draw_circles(
        ax=ax,
        facecolor=BG,
        edgecolor=MUTED,
        linewidth=0.8,
    )

    # ── Dibujar los DOS polígonos superpuestos ──────────────────────
    radar_output = radar.draw_radar_compare(
        values=valores_jugador,
        compare_values=valores_referencia,
        ax=ax,
        kwargs_radar={
            "facecolor": ACCENT,    # dorado para el jugador analizado
            "alpha": 0.65,
            "edgecolor": ACCENT,
            "linewidth": 2,
        },
        kwargs_compare={
            "facecolor": MUTED,     # gris para la referencia
            "alpha": 0.30,
            "edgecolor": MUTED,
            "linewidth": 1.5,
        },
    )

    # Labels de los rangos (los números 25%, 50%, 75%, 100% del eje)
    radar.draw_range_labels(
        ax=ax,
        fontsize=8,
        color=MUTED,
        fontfamily=FONT_DATA,
    )

    # Labels de los parámetros (Goles, Asistencias, etc.)
    radar.draw_param_labels(
        ax=ax,
        fontsize=11,
        color=TEXT,
        fontfamily=FONT_BODY,
        fontweight="bold",
    )

    # ── Título y subtítulo ─────────────────────────────────────────
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
            0.5, 0.895,
            subtitulo,
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=11,
            color=PRIMARY,
        )

    # ── Leyenda CLARA (regla R10): jugador vs referencia ───────────
    # Dos cuadraditos de color con el nombre al lado.
    legend_y = 0.27
    # Cuadrado dorado + nombre jugador
    fig.patches.append(plt.Rectangle(
        (0.20, legend_y - 0.005), 0.025, 0.018,
        transform=fig.transFigure, facecolor=ACCENT, edgecolor="none",
    ))
    fig.text(
        0.235, legend_y,
        display_name(nombre_jugador),
        fontfamily=FONT_BODY,
        fontsize=13,
        color=TEXT,
        fontweight="bold",
        va="center",
    )
    # Cuadrado gris + nombre referencia
    fig.patches.append(plt.Rectangle(
        (0.55, legend_y - 0.005), 0.025, 0.018,
        transform=fig.transFigure, facecolor=MUTED, edgecolor="none", alpha=0.5,
    ))
    fig.text(
        0.585, legend_y,
        nombre_referencia,
        fontfamily=FONT_BODY,
        fontsize=13,
        color=TEXT,
        fontweight="bold",
        va="center",
    )

    # ── Panel inferior con frase narrativa ─────────────────────────
    _dibujar_panel_inferior(
        fig,
        metricas=metricas,
        valores_jugador=valores_jugador,
        valores_referencia=valores_referencia,
        nombre_jugador=nombre_jugador,
        nombre_referencia=nombre_referencia,
        y_base=0.13,
    )

    # ── Watermark ──────────────────────────────────────────────────
    watermark(fig, source=fuente)

    return fig, ax


# Alias para compatibilidad con el código viejo del notebook 04_*.py.
# Si querés migrar el notebook, usá crear_radar_comparativo directamente.
def crear_radar_pizza(*args, **kwargs):
    """⚠️ DEPRECADO: usar crear_radar_comparativo() en su lugar.

    Esta función queda como alias para no romper notebooks viejos.
    """
    raise DeprecationWarning(
        "crear_radar_pizza fue reemplazado por crear_radar_comparativo. "
        "Ver scripts/radar.py para la nueva firma."
    )
