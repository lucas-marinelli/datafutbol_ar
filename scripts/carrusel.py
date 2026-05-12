"""
carrusel.py — Plantillas reusables para portadas y cierres de carruseles IG

Genera las slides "estáticas" del carrusel (las que NO llevan datos):
- Portada (Slide 1): hook + título grande + subtítulo + flecha "→"
- Cierre (Slide 6): título + subtítulo + CTA + handle

Todas las slides se generan en formato 1080×1350 (IG carrusel vertical)
con la paleta Combo C aplicada.

Plantilla reutilizable (Regla R13): para crear un carrusel nuevo, solo
hay que cambiar los textos. Toda la estética y composición está adentro.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

from scripts.style import (
    BG, PRIMARY, ACCENT, TEXT, MUTED,
    FONT_TITLE, FONT_BODY, FONT_DATA,
)


# Proporción IG carrusel vertical (1080×1350 = 4:5)
FIGSIZE_CARRUSEL = (8, 10)  # 8×10 = 4:5 ✅


def _setup_fig() -> tuple[plt.Figure, plt.Axes]:
    """Setup común: fig + ax invisible que ocupa toda la fig, fondo azul."""
    fig, ax = plt.subplots(figsize=FIGSIZE_CARRUSEL)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def crear_portada_carrusel(
    titulo: str,
    subtitulo: str,
    handle: str = "@datafutbol_ar",
    mostrar_flecha: bool = True,
) -> tuple[plt.Figure, plt.Axes]:
    """Genera la SLIDE 1 (portada) de un carrusel IG.

    Args:
        titulo: el "hook" principal (ej. "5 VISUALIZACIONES\\nQUE CUENTAN MÁS\\nQUE 1.000 STATS").
            Usar \\n para quiebres de línea.
        subtitulo: subtítulo / promesa (ej. "Lo que vas a ver acá, todo el año.")
        handle: tu handle en la marca. Default: @datafutbol_ar.
        mostrar_flecha: si True, dibuja flecha "→" abajo a la derecha (indica carrusel).

    Returns:
        (fig, ax) — usar fig.savefig() para guardar.

    Ejemplo:
        from scripts.carrusel import crear_portada_carrusel

        fig, ax = crear_portada_carrusel(
            titulo="5 VISUALIZACIONES\\nQUE CUENTAN MÁS\\nQUE 1.000 STATS",
            subtitulo="Lo que vas a ver acá, todo el año.",
        )
        fig.savefig("outputs/2026-05/portada.png", dpi=200, facecolor=BG)
    """
    fig, ax = _setup_fig()

    # Banda decorativa horizontal arriba — línea fina dorada
    ax.plot([0.10, 0.30], [0.85, 0.85], color=ACCENT, lw=2)

    # Tag de marca arriba (sobre la banda)
    # Simulamos letter-spacing manualmente con espacios entre caracteres,
    # porque matplotlib no soporta letter_spacing nativo.
    ax.text(
        0.10, 0.88,
        "D A T A F U T B O L   ·   E P I S O D I O   2",
        fontfamily=FONT_BODY,
        fontsize=10,
        color=ACCENT,
        fontweight="bold",
    )

    # Título principal centrado verticalmente
    ax.text(
        0.5, 0.55,
        titulo,
        ha="center",
        va="center",
        fontfamily=FONT_TITLE,
        fontsize=44,
        color=TEXT,
        fontweight="bold",
        linespacing=1.1,
    )

    # Subtítulo
    ax.text(
        0.5, 0.30,
        subtitulo,
        ha="center",
        va="center",
        fontfamily=FONT_BODY,
        fontsize=15,
        color=PRIMARY,
        style="italic",
    )

    # Footer izquierda: handle
    ax.text(
        0.10, 0.06,
        handle,
        fontfamily=FONT_BODY,
        fontsize=12,
        color=MUTED,
    )

    # Flecha "→" indicando carrusel (abajo derecha)
    if mostrar_flecha:
        arrow = FancyArrowPatch(
            (0.78, 0.06), (0.92, 0.06),
            arrowstyle="->",
            mutation_scale=22,
            color=ACCENT,
            lw=2,
        )
        ax.add_patch(arrow)
        ax.text(
            0.85, 0.10,
            "D E S L I Z Á",
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=9,
            color=MUTED,
            fontweight="bold",
        )

    return fig, ax


def crear_cierre_carrusel(
    titulo: str,
    subtitulo: str,
    cta: str,
    handle: str = "@datafutbol_ar",
    sitio: str = "datafutbolar.com",
    logo_path: Optional[str] = None,
) -> tuple[plt.Figure, plt.Axes]:
    """Genera la SLIDE final (cierre) de un carrusel IG con CTA.

    Args:
        titulo: cierre principal (ej. "ESTAS 5 VAS A VER\\nCADA SEMANA POR ACÁ.")
        subtitulo: descripción de la cuenta (ej. "xG, scouting, partidos, Mundial 2026.")
        cta: call-to-action (ej. "¿Cuál te explico primero?\\n👉 Comentá el número (2, 3, 4 o 5).")
        handle: tu handle (default @datafutbol_ar).
        sitio: tu URL (default datafutbolar.com).
        logo_path: ruta opcional a un PNG del logo para mostrar arriba.

    Returns:
        (fig, ax)
    """
    fig, ax = _setup_fig()

    # Si pasaron logo, lo dibujamos arriba centrado
    if logo_path and Path(logo_path).exists():
        from matplotlib.image import imread
        from matplotlib.offsetbox import OffsetImage, AnnotationBbox
        img = imread(logo_path)
        imagebox = OffsetImage(img, zoom=0.4)
        ab = AnnotationBbox(
            imagebox, (0.5, 0.85),
            xycoords="axes fraction",
            frameon=False,
        )
        ax.add_artist(ab)
    else:
        # Sin logo: tag de marca arriba grande
        ax.text(
            0.5, 0.85,
            handle.upper(),
            ha="center",
            fontfamily=FONT_TITLE,
            fontsize=36,
            color=ACCENT,
            fontweight="bold",
        )

    # Línea decorativa horizontal
    ax.plot([0.20, 0.80], [0.77, 0.77], color=ACCENT, lw=1.5, alpha=0.7)

    # Título principal
    ax.text(
        0.5, 0.62,
        titulo,
        ha="center",
        va="center",
        fontfamily=FONT_TITLE,
        fontsize=30,
        color=TEXT,
        fontweight="bold",
        linespacing=1.2,
    )

    # Subtítulo
    ax.text(
        0.5, 0.46,
        subtitulo,
        ha="center",
        va="center",
        fontfamily=FONT_BODY,
        fontsize=14,
        color=PRIMARY,
        linespacing=1.4,
    )

    # CTA (call to action) en caja con borde dorado
    ax.text(
        0.5, 0.27,
        cta,
        ha="center",
        va="center",
        fontfamily=FONT_BODY,
        fontsize=15,
        color=TEXT,
        fontweight="bold",
        linespacing=1.4,
        bbox=dict(
            boxstyle="round,pad=0.8",
            facecolor=BG,
            edgecolor=ACCENT,
            linewidth=1.5,
        ),
    )

    # Footer: handle + sitio web
    ax.text(
        0.5, 0.08,
        f"{handle}     ·     {sitio}",
        ha="center",
        fontfamily=FONT_DATA,
        fontsize=11,
        color=MUTED,
    )

    return fig, ax
