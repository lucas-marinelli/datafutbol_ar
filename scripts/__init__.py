"""scripts — librería interna de @datafutbol_ar

Funciones reutilizables para visualizaciones, carga de datos y branding.

Submódulos:
    style         — paleta, tipografías, helpers de marca (Combo C)
    radar         — radar de percentiles (PyPizza)
    shot_map      — mapas de tiros (VerticalPitch)
    pass_network  — redes de pases
    heatmap       — mapas de calor
    data_loaders  — wrappers para StatsBomb, FBref, LanusStats, Understat
"""

from scripts.style import (
    COLORS,
    BG, PRIMARY, ACCENT, TEXT, MUTED,
    FONTS, FONT_TITLE, FONT_BODY, FONT_DATA,
    apply_branding, watermark, set_default_style,
)

__version__ = "0.1.0"

__all__ = [
    "COLORS",
    "BG", "PRIMARY", "ACCENT", "TEXT", "MUTED",
    "FONTS", "FONT_TITLE", "FONT_BODY", "FONT_DATA",
    "apply_branding", "watermark", "set_default_style",
]
