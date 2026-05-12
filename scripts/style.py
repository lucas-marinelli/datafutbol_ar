"""
style.py — Identidad visual de @datafutbol_ar (Combo C "Celeste & Blanco")

Define la paleta, tipografías y helpers de estilo aplicables a cualquier
visualización (mplsoccer, matplotlib puro, plotly).

Uso típico:
    from scripts.style import COLORS, apply_branding, watermark

    fig, ax = plt.subplots()
    # ... tu plot ...
    apply_branding(fig, title="Shot Map · Argentina vs Francia")
    watermark(fig)
    plt.savefig("outputs/2026-05/mi_viz.png", facecolor=COLORS['bg'])
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


# ──────────────────────────────────────────────────────────────────────
# PALETA — Combo C "Celeste & Blanco" (confirmado 9 may 2026)
# ──────────────────────────────────────────────────────────────────────

COLORS: dict[str, str] = {
    # Core
    "bg": "#0E2A47",          # Azul profundo — fondos
    "primary": "#75AADB",     # Celeste — datos principales, líneas
    "accent": "#C9A227",      # Dorado — destacados (max 1-2 por pieza)
    "text": "#FFFFFF",        # Blanco — texto principal
    # Variaciones útiles
    "bg_alt": "#0A1628",      # Azul aún más oscuro — modo dark extremo
    "primary_dim": "#4A7AA8", # Celeste apagado — datos secundarios
    "muted": "#8FA7BC",       # Gris azulado — texto secundario, ejes
    "success": "#75AADB",     # = primary (no hay verde en la marca)
    "danger": "#C9A227",      # = accent (no hay rojo en la marca)
    "neutral": "#FFFFFF",
}

# Aliases cortos para usar en código
BG = COLORS["bg"]
PRIMARY = COLORS["primary"]
ACCENT = COLORS["accent"]
TEXT = COLORS["text"]
MUTED = COLORS["muted"]


# ──────────────────────────────────────────────────────────────────────
# TIPOGRAFÍAS
# ──────────────────────────────────────────────────────────────────────

FONTS: dict[str, str] = {
    "title": "Oswald",       # Display, títulos grandes
    "body": "Lato",          # Texto, labels, captions
    "data": "Space Mono",    # Datos, tablas, números
}

FONT_TITLE = FONTS["title"]
FONT_BODY = FONTS["body"]
FONT_DATA = FONTS["data"]


# ──────────────────────────────────────────────────────────────────────
# HELPERS de aplicación
# ──────────────────────────────────────────────────────────────────────

def apply_branding(
    fig: Figure,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
) -> None:
    """Aplica el fondo + título + subtítulo de la marca a una figura.

    Args:
        fig: Figura de matplotlib.
        title: Título principal (Oswald). None para no agregar.
        subtitle: Subtítulo (Lato, celeste). None para no agregar.

    Side-effects: setea `facecolor` de la figura, agrega suptitle y text.
    """
    fig.patch.set_facecolor(BG)
    for ax in fig.get_axes():
        ax.set_facecolor(BG)
        # Tick labels en blanco
        ax.tick_params(colors=TEXT, which="both")
        for spine in ax.spines.values():
            spine.set_color(MUTED)
        # Labels de ejes
        if ax.get_xlabel():
            ax.xaxis.label.set_color(TEXT)
        if ax.get_ylabel():
            ax.yaxis.label.set_color(TEXT)

    if title:
        fig.suptitle(
            title,
            fontfamily=FONT_TITLE,
            fontsize=22,
            color=TEXT,
            fontweight="bold",
            y=0.97,
        )
    if subtitle:
        fig.text(
            0.5, 0.92,
            subtitle,
            ha="center",
            fontfamily=FONT_BODY,
            fontsize=12,
            color=PRIMARY,
        )


def watermark(
    fig: Figure,
    handle: str = "@datafutbol_ar",
    source: Optional[str] = None,
) -> None:
    """Agrega watermark de marca en la esquina inferior.

    Args:
        fig: Figura de matplotlib.
        handle: Handle a mostrar (default: @datafutbol_ar).
        source: Texto adicional con la fuente de datos (ej: "StatsBomb").
    """
    text = handle
    if source:
        text = f"{handle}  ·  Datos: {source}"

    fig.text(
        0.99, 0.01,
        text,
        ha="right",
        va="bottom",
        fontfamily=FONT_BODY,
        fontsize=9,
        color=MUTED,
        alpha=0.85,
    )


def set_default_style() -> None:
    """Aplica los rcParams por default para que cualquier plt funcione
    con el branding sin tener que pasar argumentos.

    Llamar 1 vez al principio del notebook:
        from scripts.style import set_default_style
        set_default_style()
    """
    plt.rcParams.update({
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": TEXT,
        "axes.titlecolor": TEXT,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "text.color": TEXT,
        "grid.color": MUTED,
        "grid.alpha": 0.2,
        "savefig.facecolor": BG,
        "savefig.edgecolor": "none",
        "font.family": FONT_BODY,
        "axes.titleweight": "bold",
    })


# ──────────────────────────────────────────────────────────────────────
# UTILIDADES adicionales
# ──────────────────────────────────────────────────────────────────────

def color_by_value(value: float, max_value: float = 1.0) -> str:
    """Devuelve un color de la paleta según un valor normalizado.

    Útil para shot maps (color por xG), heatmaps, etc.

    - >= 0.7 * max → accent (dorado)
    - >= 0.3 * max → primary (celeste)
    - <  0.3 * max → muted (gris azulado)
    """
    ratio = value / max_value if max_value else 0
    if ratio >= 0.7:
        return ACCENT
    if ratio >= 0.3:
        return PRIMARY
    return MUTED


def get_repo_root() -> Path:
    """Devuelve la ruta raíz del repo (para construir paths relativos
    a /data, /outputs, /templates desde cualquier notebook)."""
    return Path(__file__).resolve().parent.parent


__all__ = [
    "COLORS", "BG", "PRIMARY", "ACCENT", "TEXT", "MUTED",
    "FONTS", "FONT_TITLE", "FONT_BODY", "FONT_DATA",
    "apply_branding", "watermark", "set_default_style",
    "color_by_value", "get_repo_root",
]
