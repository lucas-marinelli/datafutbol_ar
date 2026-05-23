"""
style.py — Identidad visual de @datafutbol_ar (Combo C "Celeste & Blanco")

Define la paleta, tipografías y helpers de estilo aplicables a cualquier
visualización (mplsoccer, matplotlib puro, plotly).

Sistema visual:
- COLORS         : paleta base de marca (Combo C)
- ROLES          : jerarquía funcional (qué color va para qué función) — R20
- PAISES_COLORS  : colores patrón por selección nacional — R21
- helpers        : apply_branding, watermark, draw_card_box, etc.

Uso típico:
    from scripts.style import COLORS, ROLES, PAISES_COLORS, set_default_style

    set_default_style()
    titulo = ROLES["title"]       # color para títulos (blanco)
    dato   = ROLES["data_key"]    # color para datos clave (dorado)
    arg    = PAISES_COLORS["Argentina"]["primary"]
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap


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
    "muted": "#8FA7BC",       # Gris azulado — texto secundario SOBRE FONDO OSCURO
    "muted_light": "#3E5266", # Slate oscuro — texto secundario SOBRE FONDO BLANCO (R31)
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
MUTED_LIGHT = COLORS["muted_light"]

# ──────────────────────────────────────────────────────────────────────
# COLORMAP de marca para heatmaps / mapas de calor (Combo C)
# ──────────────────────────────────────────────────────────────────────
# Gradiente de baja → alta densidad: azul profundo (se funde con el pitch)
# → celeste → dorado → dorado claro (zona "caliente"). Usar en pitch.kdeplot(cmap=CMAP_DF).
CMAP_DF = LinearSegmentedColormap.from_list(
    "datafutbol", ["#0E2A47", "#244B6E", "#75AADB", "#C9A227", "#F4E3A1"], N=256)

# Variante "fría" (todo en azules/celeste, sin dorado) por si el dorado satura:
CMAP_DF_FRIO = LinearSegmentedColormap.from_list(
    "datafutbol_frio", ["#0E2A47", "#1E4A6E", "#4A7AA8", "#75AADB", "#FFFFFF"], N=256)


# ──────────────────────────────────────────────────────────────────────
# TIPOGRAFÍAS
# ──────────────────────────────────────────────────────────────────────

FONTS: dict[str, str] = {
    "title": "Oswald",          # Display, títulos grandes
    "body":  "Inter",           # Texto, labels, captions (migrado de Lato — más tech 2026)
    "data":  "JetBrains Mono",  # Datos, tablas, números (migrado de Space Mono — mejor legibilidad)
}

FONT_TITLE = FONTS["title"]
FONT_BODY = FONTS["body"]
FONT_DATA = FONTS["data"]


# ──────────────────────────────────────────────────────────────────────
# ROLES — Jerarquía funcional de colores (R20)
# ──────────────────────────────────────────────────────────────────────
# Cada función tiene UN color asignado. Esto evita que el dorado se repita
# en headers + frases + stats. El dorado se reserva SOLO para datos clave.

ROLES: dict[str, str] = {
    # Texto
    "title":       TEXT,        # Encabezados de slide → blanco (limpio, lee primero)
    "subtitle":    MUTED,       # Subtítulos / descripciones → gris azulado
    "body":        TEXT,        # Texto principal → blanco
    "caption":     MUTED,       # Pie de foto, fuentes → gris azulado
    # Datos
    "data_key":    ACCENT,      # Datos CLAVE / números grandes → dorado (¡máximo 1-2 por slide!)
    "data_normal": TEXT,        # Datos secundarios → blanco
    "highlight":   PRIMARY,     # Frase/insight a destacar (sin ser dato) → celeste
    # Decorativo
    "divider":     PRIMARY,     # Líneas decorativas → celeste
    "card_bg":     "#163654",   # Fondo de cajas/cards → azul medio (BG aclarado)
    "card_border": PRIMARY,     # Borde de cards → celeste
    # Estado de un tiro / evento
    "goal":        ACCENT,      # Goles, eventos positivos → dorado
    "no_goal":     PRIMARY,     # Sin gol → celeste
}


# ──────────────────────────────────────────────────────────────────────
# PAISES_COLORS — Colores patrón por selección nacional (R21)
# ──────────────────────────────────────────────────────────────────────
# Cuando compares 2 países, usá su color de marca nacional. Esto hace que
# el slide se entienda de un vistazo, sin leer leyendas.
#
# Cada país tiene:
#   "primary"   → color principal para representarlo
#   "secondary" → color secundario (opcional, para detalles)
#
# Si analizás un solo país (ej. Argentina sola), usá COLORS["primary"]
# del Combo C. Estos colores son para CONTRASTAR países entre sí.

PAISES_COLORS: dict[str, dict[str, str]] = {
    # Sudamérica
    "Argentina":     {"primary": "#75AADB", "secondary": "#FFFFFF"},  # Celeste y blanco
    "Brasil":        {"primary": "#009C3B", "secondary": "#FFDF00"},  # Verde + amarillo
    "Brazil":        {"primary": "#009C3B", "secondary": "#FFDF00"},  # Alias inglés (StatsBomb)
    "Uruguay":       {"primary": "#5DADE2", "secondary": "#FFFFFF"},  # Celeste uruguayo
    "Chile":         {"primary": "#D52B1E", "secondary": "#FFFFFF"},  # Rojo + blanco
    "Colombia":      {"primary": "#FCD116", "secondary": "#003893"},  # Amarillo + azul
    "Paraguay":      {"primary": "#D52B1E", "secondary": "#0038A8"},  # Rojo + azul
    "Perú":          {"primary": "#D52B1E", "secondary": "#FFFFFF"},
    "Peru":          {"primary": "#D52B1E", "secondary": "#FFFFFF"},  # Alias
    "Ecuador":       {"primary": "#FCD116", "secondary": "#034EA2"},
    "Bolivia":       {"primary": "#007934", "secondary": "#FCD116"},
    "Venezuela":     {"primary": "#CE1126", "secondary": "#FCD116"},

    # Top selecciones
    "Francia":       {"primary": "#0055A4", "secondary": "#EF4135"},
    "France":        {"primary": "#0055A4", "secondary": "#EF4135"},  # Alias StatsBomb
    "España":        {"primary": "#AA151B", "secondary": "#F1BF00"},
    "Spain":         {"primary": "#AA151B", "secondary": "#F1BF00"},
    "Alemania":      {"primary": "#FFCE00", "secondary": "#DD0000"},
    "Germany":       {"primary": "#FFCE00", "secondary": "#DD0000"},
    "Italia":        {"primary": "#0066CC", "secondary": "#FFFFFF"},
    "Italy":         {"primary": "#0066CC", "secondary": "#FFFFFF"},
    "Inglaterra":    {"primary": "#C8102E", "secondary": "#FFFFFF"},
    "England":       {"primary": "#C8102E", "secondary": "#FFFFFF"},
    "Portugal":      {"primary": "#006600", "secondary": "#DA020E"},
    "Países Bajos":  {"primary": "#FF6900", "secondary": "#21468B"},
    "Netherlands":   {"primary": "#FF6900", "secondary": "#21468B"},
    "Bélgica":       {"primary": "#FAE042", "secondary": "#ED2939"},
    "Belgium":       {"primary": "#FAE042", "secondary": "#ED2939"},
    "México":        {"primary": "#006847", "secondary": "#CE1126"},
    "Mexico":        {"primary": "#006847", "secondary": "#CE1126"},
    "Estados Unidos": {"primary": "#3C3B6E", "secondary": "#B22234"},
    "United States":  {"primary": "#3C3B6E", "secondary": "#B22234"},
    "Croacia":       {"primary": "#FF0000", "secondary": "#FFFFFF"},
    "Croatia":       {"primary": "#FF0000", "secondary": "#FFFFFF"},
    "Marruecos":     {"primary": "#C1272D", "secondary": "#006233"},
    "Morocco":       {"primary": "#C1272D", "secondary": "#006233"},
    "Arabia Saudita": {"primary": "#006C35", "secondary": "#FFFFFF"},
    "Saudi Arabia":  {"primary": "#006C35", "secondary": "#FFFFFF"},  # StatsBomb usa esto
    "Argelia":       {"primary": "#006633", "secondary": "#FFFFFF"},
    "Algeria":       {"primary": "#006633", "secondary": "#FFFFFF"},
    "Japón":         {"primary": "#BC002D", "secondary": "#FFFFFF"},
    "Japan":         {"primary": "#BC002D", "secondary": "#FFFFFF"},
    "Corea del Sur": {"primary": "#003478", "secondary": "#CD2E3A"},
    "South Korea":   {"primary": "#003478", "secondary": "#CD2E3A"},
}


def pais_color(nombre: str, role: str = "primary") -> str:
    """Devuelve el color de un país, o fallback a PRIMARY del Combo C.

    Args:
        nombre: nombre del país (en español o inglés según fuente).
        role: 'primary' o 'secondary'.

    Returns:
        Color hex. Si no encontró el país, devuelve PRIMARY (#75AADB).
    """
    p = PAISES_COLORS.get(nombre)
    if p is None:
        return PRIMARY
    return p.get(role, p["primary"])


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


# ──────────────────────────────────────────────────────────────────────
# LOGOS — Sistema con múltiples variantes
# ──────────────────────────────────────────────────────────────────────
# Cada variante tiene una función. Ver G:\...\02_Branding\logos\README_USO.md

LOGOS_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\logos\png")

# Mapeo de variant → tamaño de PNG a usar (el que mejor calidad da según uso)
# Logo "Skyline + Sparkline + Línea de Gol" — final 15 may 2026
LOGO_VARIANTS = {
    "completo":  "isotipo_completo_512.png",   # cuadrado con sparkline (avatar, presentación)
    "simple":    "isotipo_simple_512.png",     # cuadrado sin sparkline (cierres de carrusel)
    "watermark": "isotipo_watermark_256.png",  # solo símbolo, 5 barras (esquinas chicas)
    "horizontal":"horizontal_1200x343.png",    # lockup horizontal (banners)
    "blanco":    "monocolor_blanco_512.png",   # sobre fondos saturados
    "dorado":    "monocolor_dorado_512.png",   # acentos/premium
    "celeste":   "monocolor_celeste_512.png",  # sobre fondos claros
}


def place_logo(
    fig,
    x: float = 0.5,
    y: float = 0.97,
    size: float = 0.06,
    alpha: float = 1.0,
    variant: str = "watermark",
):
    """Coloca el logo de la marca en la figura.

    Args:
        fig: figura de matplotlib.
        x, y: coordenadas (0-1) del CENTRO del logo en la figura.
        size: ancho del logo (proporción de la figura).
              · 0.04-0.06 → watermark en esquina
              · 0.08-0.12 → logo en cierre de slide
              · 0.20+     → logo en portada de informe
        alpha: transparencia (1.0 = sólido).
        variant: cuál usar:
              · "watermark" → versión ultra-simple (default, para esquinas)
              · "simple"    → isotipo sin texto rodeando (para cierres)
              · "completo"  → versión oficial con texto en arco
              · "horizontal"→ lockup horizontal (banners — ojo proporción)
              · "blanco"    → todo blanco (fondos saturados)
              · "dorado"    → acento premium
              · "celeste"   → fondos claros

    Returns:
        El axes que contiene el logo, o None si no se pudo cargar.
    """
    import matplotlib.image as mpimg

    if variant not in LOGO_VARIANTS:
        print(f"⚠️ Variante de logo desconocida: {variant}. Usando 'watermark'.")
        variant = "watermark"

    logo_path = LOGOS_DIR / LOGO_VARIANTS[variant]

    if not logo_path.exists():
        # Fallback al logo viejo (compatibilidad mientras no se hayan generado los PNGs)
        fallback = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\logos\logo_datafutbol_ar.png")
        if fallback.exists():
            print(f"⚠️ Logo nuevo no encontrado ({logo_path.name}). Usando logo viejo como fallback.")
            print("   Tip: corré `python scripts/generar_logos.py` para generar los PNGs nuevos.")
            logo_path = fallback
        else:
            print(f"❌ Ningún logo disponible en {LOGOS_DIR}")
            return None

    try:
        img = mpimg.imread(str(logo_path))
    except Exception as e:
        print(f"❌ Error cargando logo: {e}")
        return None

    # Ajustar proporciones para variante horizontal (1400x400)
    if variant == "horizontal":
        height_size = size * (400 / 1400)
    else:
        height_size = size

    logo_ax = fig.add_axes((x - size / 2, y - height_size / 2, size, height_size))
    logo_ax.imshow(img, alpha=alpha)
    logo_ax.axis("off")
    return logo_ax


def draw_comparison_bar(
    ax,
    label_left: str,
    label_right: str,
    value_left: float,
    value_right: float,
    color_left: str,
    color_right: str,
    y: float,
    x_center: float = 5,
    width_max: float = 4,
    height: float = 0.4,
    show_values: bool = True,
):
    """Dibuja DOS barras horizontales comparativas (una a cada lado del centro).

    Útil para mostrar xG, posesión, pases, etc. entre 2 equipos.
    Más visual que números sueltos y más profesional que cards.

    Args:
        ax: axes donde dibujar.
        label_left, label_right: nombres (ej. "ARG", "SAU").
        value_left, value_right: valores a comparar.
        color_left, color_right: colores patrón de cada lado.
        y: altura vertical donde dibujar.
        x_center: centro horizontal.
        width_max: ancho máximo de la barra más grande.
        height: alto de las barras.
        show_values: si mostrar el número al final de cada barra.

    Ejemplo:
        draw_comparison_bar(ax, "ARG", "SAU", 2.49, 0.15,
                            COLOR_ARG, COLOR_SAU, y=5)
    """
    # Normalizar al máximo para que la barra más grande tenga width_max
    max_val = max(value_left, value_right) or 1
    width_left = (value_left / max_val) * width_max
    width_right = (value_right / max_val) * width_max

    # Barra izquierda (crece hacia la izquierda)
    ax.barh(
        y, -width_left, left=x_center, height=height,
        color=color_left, edgecolor=TEXT, linewidth=1, zorder=3,
        align="center",
    )
    # Barra derecha
    ax.barh(
        y, width_right, left=x_center, height=height,
        color=color_right, edgecolor=TEXT, linewidth=1, zorder=3,
        align="center",
    )

    # Labels (a los extremos)
    ax.text(x_center - width_max - 0.3, y, label_left,
            ha="right", va="center", fontsize=12, fontweight="bold",
            color=color_left, family=FONT_TITLE, zorder=4)
    ax.text(x_center + width_max + 0.3, y, label_right,
            ha="left", va="center", fontsize=12, fontweight="bold",
            color=color_right, family=FONT_TITLE, zorder=4)

    # Valores (al final de cada barra)
    if show_values:
        ax.text(x_center - width_left - 0.15, y, f"{value_left:.2f}",
                ha="right", va="center", fontsize=11, fontweight="bold",
                color=TEXT, family=FONT_DATA, zorder=4)
        ax.text(x_center + width_right + 0.15, y, f"{value_right:.2f}",
                ha="left", va="center", fontsize=11, fontweight="bold",
                color=TEXT, family=FONT_DATA, zorder=4)


def draw_section_label(
    ax,
    x: float,
    y: float,
    label: str,
    width: float = 2.5,
    color: str = None,
):
    """Dibuja una etiqueta de sección con dos líneas decorativas a los lados.

    Útil para separar secciones dentro de un slide sin usar cajas.

    Ejemplo visual:    ─── EN NÚMEROS ───

    Args:
        ax: axes.
        x, y: centro.
        label: texto.
        width: ancho total (incluyendo líneas).
        color: color de las líneas (default: divider).
    """
    if color is None:
        color = ROLES["divider"]

    # Líneas decorativas a izquierda y derecha
    line_half = width / 2 - 0.7  # dejar espacio para el texto
    ax.plot([x - width / 2, x - width / 2 + line_half], [y, y],
            color=color, linewidth=1.2, alpha=0.6, zorder=2)
    ax.plot([x + width / 2 - line_half, x + width / 2], [y, y],
            color=color, linewidth=1.2, alpha=0.6, zorder=2)

    # Label centrado
    ax.text(x, y, label, ha="center", va="center",
            fontsize=12, fontweight="bold",
            color=ROLES["subtitle"], family=FONT_TITLE, zorder=3)


def draw_big_number(
    ax,
    x: float,
    y: float,
    number: str,
    label: str,
    color_number: str = None,
    color_label: str = None,
    fontsize_number: int = 64,
    fontsize_label: int = 12,
):
    """Dibuja un número grande con su label debajo (estadística destacada).

    Patrón visual estándar para "stat tickers" sin necesidad de card.

    Args:
        ax: axes.
        x, y: posición del número.
        number: texto del número (puede incluir %, etc.).
        label: descripción debajo.
        color_number: color del número (default: data_key dorado).
        color_label: color del label (default: subtitle gris).
    """
    if color_number is None:
        color_number = ROLES["data_key"]
    if color_label is None:
        color_label = ROLES["subtitle"]

    ax.text(x, y, number, ha="center", va="center",
            fontsize=fontsize_number, fontweight="bold",
            color=color_number, family=FONT_DATA)
    ax.text(x, y - fontsize_number * 0.012, label, ha="center", va="center",
            fontsize=fontsize_label, color=color_label,
            family=FONT_BODY, fontweight="bold")


def draw_quote(
    ax,
    x: float,
    y: float,
    text: str,
    width: float = 7,
    fontsize: int = 16,
    color: str = None,
):
    """Dibuja una cita con comillas decorativas (sin caja).

    Útil para frases peso, sentencias, conclusiones.

    Args:
        ax: axes.
        x, y: centro de la cita.
        text: texto (puede incluir \\n para multilinea).
        width: ancho disponible.
        fontsize: tamaño del texto.
        color: color del texto (default: highlight celeste).
    """
    if color is None:
        color = ROLES["highlight"]

    # Comilla de apertura — grande, italicizada, transparente
    ax.text(x - width / 2, y + 0.5, "“", ha="center", va="center",
            fontsize=fontsize * 3, color=color, family=FONT_TITLE,
            alpha=0.5, fontweight="bold")

    # Comilla de cierre
    ax.text(x + width / 2, y - 0.5, "”", ha="center", va="center",
            fontsize=fontsize * 3, color=color, family=FONT_TITLE,
            alpha=0.5, fontweight="bold")

    # Texto
    ax.text(x, y, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold",
            color=color, family=FONT_TITLE, style="italic")


# ──────────────────────────────────────────────────────────────────────
# ICONOGRAFÍA DE COMPETICIONES — logos oficiales descargados (PNG locales)
# ──────────────────────────────────────────────────────────────────────

COMPETICION_ICONS_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\iconos_competicion")
ESCUDOS_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\escudos_equipos")
BANDERAS_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\banderas_paises")


def _load_png_robust(path: Path):
    """Carga un PNG usando Pillow (robusto, lee cualquier formato real).

    Convierte a RGBA siempre (asegura canal alpha para transparencia).
    Devuelve un numpy array o None si falla.
    """
    if not path.exists():
        print(f"⚠️ Archivo no encontrado: {path}")
        return None
    try:
        from PIL import Image
        import numpy as np
        img_pil = Image.open(str(path))
        if img_pil.mode != "RGBA":
            img_pil = img_pil.convert("RGBA")
        return np.asarray(img_pil)
    except Exception as e:
        print(f"❌ Error cargando {path.name}: {e}")
        return None


def _place_image_at(fig, x: float, y: float, size: float,
                    img_array, alpha: float = 1.0):
    """Helper interno: coloca una imagen array en una posición (x, y) de la figura.

    Args:
        fig: figura matplotlib.
        x, y: coords (0-1) del centro.
        size: ancho (proporción figura). El height se ajusta proporcional.
        img_array: numpy array de la imagen RGBA.
        alpha: transparencia.
    """
    # Alto preservando el aspecto REAL de la imagen y el de la figura
    # (size = ancho en fracción de figura; el alto se ajusta para no deformar).
    try:
        h_px, w_px = float(img_array.shape[0]), float(img_array.shape[1])
        fw, fh = fig.get_size_inches()
        height = size * (h_px / w_px) * (float(fw) / float(fh))
    except Exception:
        height = size

    left = max(0, x - size / 2)
    bottom = max(0, y - height / 2)
    width = min(size, 1 - left)
    height = min(height, 1 - bottom)

    icon_ax = fig.add_axes((left, bottom, width, height))
    icon_ax.imshow(img_array, alpha=alpha)
    icon_ax.axis("off")
    return icon_ax


def place_team_badge(fig, x: float, y: float, size: float = 0.06,
                     liga: str = None, equipo: str = None, alpha: float = 1.0):
    """Coloca el escudo de un equipo en la figura.

    Los escudos viven en `02_Branding/escudos_equipos/<liga>/<equipo>.png`.

    Args:
        fig: figura matplotlib.
        x, y: coords (0-1) del centro.
        size: ancho del escudo (proporción figura). Recomendado:
              · 0.04-0.06 → escudo chico para rankings
              · 0.08-0.10 → headers de comparativa
              · 0.12+ → análisis individual destacado
        liga: subcarpeta (ej: "liga_pro_ar", "primera_nacional", "brasileirao").
        equipo: nombre del archivo PNG (ej: "river_plate.png").
        alpha: transparencia.

    Ejemplo:
        place_team_badge(fig, x=0.30, y=0.85, size=0.06,
                         liga="liga_pro_ar", equipo="river_plate.png")
    """
    if liga is None or equipo is None:
        print("⚠️ place_team_badge: faltan 'liga' o 'equipo'")
        return None

    badge_path = ESCUDOS_DIR / liga / equipo
    img = _load_png_robust(badge_path)
    if img is None:
        return None
    return _place_image_at(fig, x, y, size, img, alpha)


def _slug_club(nombre: str) -> str:
    """'Real Betis' -> 'real_betis' (snake_case sin tildes, convención R26)."""
    import re
    import unicodedata
    t = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")


def buscar_escudo(club: str):
    """Busca el PNG de un escudo por slug del club, en CUALQUIER subcarpeta de
    escudos_equipos/ (no importa si están sueltos o por liga).

    Devuelve un Path o None. Match por nombre de archivo == slug del club.
    """
    if not club or not ESCUDOS_DIR.exists():
        return None
    slug = _slug_club(club)
    compact = slug.replace("_", "")
    loose = None
    for p in ESCUDOS_DIR.rglob("*.png"):
        stem = _slug_club(p.stem)
        if stem == slug:
            return p                       # match exacto (prioridad)
        if stem.replace("_", "") == compact:
            loose = loose or p             # match tolerante (sin separadores)
    return loose


def place_escudo_club(fig, x: float, y: float, size: float = 0.04,
                      club: str = None, alpha: float = 1.0):
    """Coloca el escudo de un club buscándolo por nombre (slug), sin necesidad
    de saber la liga/subcarpeta. Degradación elegante: si no lo encuentra,
    devuelve None y no rompe el render.

    Ejemplo:
        place_escudo_club(fig, x=0.10, y=0.80, size=0.035, club="Real Madrid")
    """
    path = buscar_escudo(club)
    if path is None:
        return None
    img = _load_png_robust(path)
    if img is None:
        return None
    return _place_image_at(fig, x, y, size, img, alpha)


def place_country_flag(fig, x: float, y: float, size: float = 0.04,
                       pais: str = None, alpha: float = 1.0):
    """Coloca la bandera de un país en la figura.

    Las banderas viven en `02_Branding/banderas_paises/<pais>.png`.

    Args:
        fig: figura matplotlib.
        x, y: coords (0-1) del centro.
        size: ancho de la bandera (proporción figura). Recomendado:
              · 0.025-0.04 → identificador de nacionalidad en ranking
              · 0.05-0.08 → header de comparativa de selecciones
        pais: nombre del archivo PNG (ej: "argentina.png", "brasil.png").
        alpha: transparencia.

    Ejemplo:
        place_country_flag(fig, x=0.30, y=0.85, size=0.04, pais="argentina.png")
    """
    if pais is None:
        print("⚠️ place_country_flag: falta 'pais'")
        return None

    flag_path = BANDERAS_DIR / pais
    img = _load_png_robust(flag_path)
    if img is None:
        return None
    return _place_image_at(fig, x, y, size, img, alpha)


def place_competition_icon(fig, x: float, y: float, size: float = 0.08,
                           file: str = None, alpha: float = 1.0):
    """Coloca un logo oficial de competición en la figura.

    Los logos viven en G:\\...\\02_Branding\\iconos_competicion\\
    Descargados de fuentes oficiales en PNG con fondo transparente.

    Args:
        fig: figura de matplotlib.
        x, y: coords (0-1) del CENTRO del logo en la figura.
        size: ancho del logo (proporción de la figura). Recomendado:
              · 0.06-0.08 → header/footer de slide
              · 0.10-0.12 → contexto importante en portada
        file: nombre del PNG (ej: "qatar_2022.png", "liga_pro_ar.png").
        alpha: transparencia.

    Logos disponibles (ir agregando):
        · qatar_2022.png      → Mundial Qatar 2022
        · mundial_2026.png    → Mundial USA/Canadá/México 2026
        · liga_pro_ar.png     → Liga Profesional Argentina
        · primera_nacional.png → Primera Nacional Argentina
        · copa_libertadores.png
        · copa_sudamericana.png
        · copa_america.png    → Copa América
        · brasileirao.png
        · uefa_champions.png
    """
    if file is None:
        print("⚠️ place_competition_icon: falta parámetro 'file'")
        return None

    icon_path = COMPETICION_ICONS_DIR / file

    if not icon_path.exists():
        print(f"⚠️ Icono no encontrado: {icon_path}")
        return None

    # Usar Pillow en vez de matplotlib.imread → lee cualquier formato (JPG, WebP, PNG, etc.)
    # incluso si el archivo tiene extensión .png pero internamente es otro formato
    try:
        from PIL import Image
        import numpy as np
        img_pil = Image.open(str(icon_path))
        if img_pil.mode != "RGBA":
            img_pil = img_pil.convert("RGBA")  # asegura canal alpha (transparencia)
        img = np.asarray(img_pil)
    except Exception as e:
        print(f"❌ Error cargando icono {file}: {e}")
        return None

    # Coords seguras (no salir del frame)
    left = max(0, x - size / 2)
    bottom = max(0, y - size / 2)
    width = min(size, 1 - left)
    height = min(size, 1 - bottom)

    icon_ax = fig.add_axes((left, bottom, width, height))
    icon_ax.imshow(img, alpha=alpha)
    icon_ax.axis("off")
    return icon_ax


def draw_trofeo_mundial(ax, x: float, y: float, size: float = 0.6,
                        color: str = None, alpha: float = 1.0):
    """Dibuja un TROFEO abstracto estilizado (para referencia a Mundial / torneo grande).

    NO es el logo oficial FIFA. Es nuestra propia interpretación visual.
    Composición: copa con asas + base + estrella encima.

    Args:
        ax: axes donde dibujar.
        x, y: coordenadas del CENTRO del trofeo (en coords del ax).
        size: altura total del trofeo (en unidades del ax).
        color: color principal (default: dorado).
        alpha: transparencia.
    """
    if color is None:
        color = ACCENT

    from matplotlib.patches import Polygon, Circle, FancyBboxPatch
    import numpy as np

    # Escala proporcional
    w = size * 0.6  # ancho del cuerpo de la copa
    h_cup = size * 0.5  # alto del cuerpo
    h_base = size * 0.15  # alto de la base

    # ── Estrella encima (5 puntas) ──
    star_r = size * 0.13
    star_cx = x
    star_cy = y + size * 0.5
    star_pts = []
    for i in range(10):
        angle = (i * 36 - 90) * np.pi / 180  # comenzar arriba, alternar largo/corto
        r = star_r if i % 2 == 0 else star_r * 0.4
        star_pts.append((star_cx + r * np.cos(angle), star_cy + r * np.sin(angle)))
    star = Polygon(star_pts, closed=True, facecolor=color, edgecolor="none",
                   alpha=alpha, zorder=5)
    ax.add_patch(star)

    # ── Cuerpo de la copa (forma trapezoidal invertida) ──
    cup_top_y = y + size * 0.32
    cup_bot_y = y - size * 0.05
    cup_pts = [
        (x - w / 2, cup_top_y),       # top-left
        (x + w / 2, cup_top_y),       # top-right
        (x + w / 2 * 0.55, cup_bot_y),  # bottom-right (más angosto)
        (x - w / 2 * 0.55, cup_bot_y),  # bottom-left
    ]
    cup = Polygon(cup_pts, closed=True, facecolor=color, edgecolor="none",
                  alpha=alpha, zorder=4)
    ax.add_patch(cup)

    # ── Asas (dos arcos a los costados) ──
    asa_left_pts = [
        (x - w / 2, cup_top_y - size * 0.05),
        (x - w * 0.75, cup_top_y - size * 0.10),
        (x - w * 0.78, cup_top_y - size * 0.22),
        (x - w * 0.75, cup_top_y - size * 0.32),
        (x - w / 2, cup_top_y - size * 0.30),
    ]
    asa_left = Polygon(asa_left_pts, closed=True, facecolor="none",
                       edgecolor=color, linewidth=size * 3, alpha=alpha, zorder=3)
    ax.add_patch(asa_left)

    asa_right_pts = [(2 * x - px, py) for px, py in asa_left_pts]
    asa_right = Polygon(asa_right_pts, closed=True, facecolor="none",
                        edgecolor=color, linewidth=size * 3, alpha=alpha, zorder=3)
    ax.add_patch(asa_right)

    # ── Cuello (entre copa y base) ──
    neck = FancyBboxPatch(
        (x - w * 0.15, cup_bot_y - size * 0.05),
        w * 0.30, size * 0.10,
        boxstyle="round,pad=0,rounding_size=0.02",
        facecolor=color, edgecolor="none", alpha=alpha, zorder=3,
    )
    ax.add_patch(neck)

    # ── Base (rectángulo redondeado) ──
    base = FancyBboxPatch(
        (x - w * 0.40, y - size * 0.30),
        w * 0.80, h_base,
        boxstyle="round,pad=0,rounding_size=0.03",
        facecolor=color, edgecolor="none", alpha=alpha, zorder=3,
    )
    ax.add_patch(base)


def draw_card_box(
    ax,
    x: float,
    y: float,
    width: float,
    height: float,
    facecolor: str = None,
    edgecolor: str = None,
    pad: float = 0.02,
    alpha: float = 1.0,
    zorder: int = 1,
) -> FancyBboxPatch:
    """Dibuja una caja redondeada (estilo card) para destacar contenido.

    Útil para datos clave, citas, insights, headers de stats.

    Args:
        ax: axes donde dibujar.
        x, y: coordenadas de la esquina inferior izquierda.
        width, height: dimensiones.
        facecolor: color de fondo (default: ROLES['card_bg']).
        edgecolor: color del borde (default: ROLES['card_border']).
        pad: padding del estilo "round" (más grande = más redondeado).
        alpha: transparencia del fondo.
        zorder: orden de dibujo (más alto = encima).

    Returns:
        El FancyBboxPatch creado (por si querés modificarlo después).

    Ejemplo:
        # Dentro de un slide
        draw_card_box(ax, 1, 5, 8, 2)  # caja ocupando lo ancho
        ax.text(5, 6, "DATO CLAVE: 2.55 xG", ha="center", ...)
    """
    if facecolor is None:
        facecolor = ROLES["card_bg"]
    if edgecolor is None:
        edgecolor = ROLES["card_border"]

    box = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad={pad},rounding_size=0.3",
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=1.5,
        alpha=alpha,
        zorder=zorder,
    )
    ax.add_patch(box)
    return box


__all__ = [
    "COLORS", "BG", "PRIMARY", "ACCENT", "TEXT", "MUTED", "MUTED_LIGHT",
    "CMAP_DF", "CMAP_DF_FRIO",
    "ROLES", "PAISES_COLORS", "pais_color",
    "FONTS", "FONT_TITLE", "FONT_BODY", "FONT_DATA",
    "apply_branding", "watermark", "set_default_style",
    "color_by_value", "get_repo_root",
    "draw_card_box", "draw_comparison_bar", "draw_section_label",
    "draw_big_number", "draw_quote", "place_logo",
    "draw_trofeo_mundial",
    "place_competition_icon", "place_team_badge", "place_country_flag",
    "buscar_escudo", "place_escudo_club",
    "LOGO_PATH_ABS", "COMPETICION_ICONS_DIR", "ESCUDOS_DIR", "BANDERAS_DIR",
]
