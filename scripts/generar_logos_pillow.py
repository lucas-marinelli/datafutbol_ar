"""
generar_logos_pillow.py — Renderiza los logos directamente con Pillow.

NO depende de Cairo/SVG. Pure Python + Pillow.
Funciona en Windows sin DLLs nativas externas.

Uso:
    python scripts/generar_logos_pillow.py

Genera todos los PNGs en G:\\Mi unidad\\DATAFUTBOL_AR\\02_Branding\\logos\\png\\
en tamaños 1024, 512, 256, 128, 64, 32 (cuadrados) y 2000, 1200, 800, 400 (horizontales).
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# ──────────────────────────────────────────────────────────────────────
# Configuración
# ──────────────────────────────────────────────────────────────────────

OUTPUT_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\logos\png")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colores Combo C
BG       = "#0E2A47"
PRIMARY  = "#75AADB"
ACCENT   = "#C9A227"
TEXT     = "#FFFFFF"

# Datos del skyline (alturas en grid 0-200, ancho de barra 36)
BAR_HEIGHTS = [65, 110, 35, 140, 90, 170, 50, 125, 190]
BAR_X_OFFSETS = [0, 44, 88, 132, 176, 220, 264, 308, 352]
BAR_WIDTH = 36

# Para variante watermark (5 barras más anchas)
WATERMARK_BAR_HEIGHTS = [70, 120, 50, 160, 220]
WATERMARK_BAR_X_OFFSETS = [0, 65, 130, 195, 260]
WATERMARK_BAR_WIDTH = 55


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    """Convierte '#RRGGBB' a (R, G, B, A)."""
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """Carga Oswald Bold con búsqueda flexible. Fallback a Arial Bold."""
    win_fonts = Path(r"C:\Windows\Fonts")

    # 1) Buscar archivos que empiecen con "Oswald" y contengan "Bold"
    if win_fonts.exists():
        oswald_bold_candidates = sorted(
            list(win_fonts.glob("*Oswald*Bold*.ttf")) +
            list(win_fonts.glob("*Oswald*Bold*.otf")) +
            list(win_fonts.glob("Oswald-Bold.ttf"))
        )
        for f in oswald_bold_candidates:
            try:
                return ImageFont.truetype(str(f), size)
            except (IOError, OSError):
                continue

        # 2) Si no hay Bold, cualquier Oswald
        oswald_any = sorted(win_fonts.glob("*Oswald*.ttf"))
        for f in oswald_any:
            try:
                return ImageFont.truetype(str(f), size)
            except (IOError, OSError):
                continue

    # 3) Fallback por nombre (Pillow resolverá)
    for name in ["Oswald-Bold.ttf", "Oswald.ttf", "arialbd.ttf", "arial.ttf"]:
        try:
            return ImageFont.truetype(name, size)
        except (IOError, OSError):
            continue

    print("⚠️ No se encontró Oswald ni Arial — usando default (limitada)")
    return ImageFont.load_default()


def draw_rounded_bar(draw: ImageDraw.ImageDraw, x: float, y: float,
                     w: float, h: float, color: tuple, radius: int = 3) -> None:
    """Barra con esquinas redondeadas."""
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=color)


def draw_thick_line_round(draw: ImageDraw.ImageDraw, x1: float, y1: float,
                          x2: float, y2: float, color: tuple, width: int) -> None:
    """Línea con extremos redondeados (linecap='round')."""
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    r = width / 2
    draw.ellipse((x1 - r, y1 - r, x1 + r, y1 + r), fill=color)
    draw.ellipse((x2 - r, y2 - r, x2 + r, y2 + r), fill=color)


def draw_filled_circle(draw: ImageDraw.ImageDraw, cx: float, cy: float,
                       r: float, fill: tuple, stroke: tuple = None,
                       stroke_width: float = 0) -> None:
    """Círculo opcional con borde."""
    if stroke and stroke_width > 0:
        draw.ellipse((cx - r - stroke_width, cy - r - stroke_width,
                      cx + r + stroke_width, cy + r + stroke_width), fill=stroke)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)


def draw_polyline_round(draw: ImageDraw.ImageDraw, points: list,
                        color: tuple, width: int) -> None:
    """Polyline con joins redondeados."""
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    # Redondear vértices con círculos
    r = width / 2
    for x, y in points:
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)


def draw_centered_text_multicolor(draw: ImageDraw.ImageDraw, cx: float, cy: float,
                                  part1: str, color1: tuple,
                                  part2: str, color2: tuple,
                                  font: ImageFont.FreeTypeFont) -> None:
    """Dibuja '{part1}{part2}' centrado, cada parte en su color."""
    full = part1 + part2
    bbox_full = font.getbbox(full)
    bbox_p1 = font.getbbox(part1)
    full_w = bbox_full[2] - bbox_full[0]
    p1_w = bbox_p1[2] - bbox_p1[0]
    # text_y para que cy quede centrado en la altura del texto
    h = bbox_full[3] - bbox_full[1]
    x_start = cx - full_w / 2 - bbox_full[0]
    y_top = cy - h / 2 - bbox_full[1]
    draw.text((x_start, y_top), part1, fill=color1, font=font)
    draw.text((x_start + p1_w, y_top), part2, fill=color2, font=font)


def draw_centered_text(draw: ImageDraw.ImageDraw, cx: float, cy: float,
                       text: str, color: tuple,
                       font: ImageFont.FreeTypeFont) -> None:
    """Dibuja texto centrado en (cx, cy)."""
    bbox = font.getbbox(text)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), text, fill=color, font=font)


# ──────────────────────────────────────────────────────────────────────
# Renderers por variante
# ──────────────────────────────────────────────────────────────────────

def render_skyline_base(canvas_size: int, draw_sparkline: bool, color_bars: str,
                        color_accent: str, sparkline_alpha: int = 165) -> Image.Image:
    """Renderiza el bloque "skyline + sparkline + línea de gol" en canvas cuadrado.

    Devuelve una imagen RGBA con FONDO TRANSPARENTE (solo el símbolo).
    Caller debe componer sobre el fondo deseado.
    """
    scale = canvas_size / 500
    layer = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    grid_x = 70 * scale
    grid_y = 110 * scale
    baseline_y = 200 * scale

    # Color barras: con o sin opacidad
    if draw_sparkline:
        bar_color = hex_to_rgba(color_bars, sparkline_alpha)
    else:
        bar_color = hex_to_rgba(color_bars)

    # Dibujar barras
    for i, h in enumerate(BAR_HEIGHTS):
        x = grid_x + BAR_X_OFFSETS[i] * scale
        y_top = grid_y + (baseline_y / scale - h) * scale  # baseline ya escalado
        # ojo: recalculo bien
        y_top = grid_y + (200 - h) * scale
        bw = BAR_WIDTH * scale
        bh = h * scale
        radius = max(1, int(3 * scale))
        draw_rounded_bar(draw, x, y_top, bw, bh, bar_color, radius=radius)

    accent = hex_to_rgba(color_accent)
    white = hex_to_rgba("#FFFFFF")

    # Puntos top de cada barra (centro horizontal, top)
    points = []
    for i, h in enumerate(BAR_HEIGHTS):
        x = grid_x + (BAR_X_OFFSETS[i] + BAR_WIDTH / 2) * scale
        y = grid_y + (200 - h) * scale
        points.append((x, y))

    # Sparkline
    if draw_sparkline:
        line_w = max(1, int(3 * scale))
        draw_polyline_round(draw, points, accent, line_w)
        # Vértices intermedios
        vr = max(2, int(4 * scale))
        for px, py in points[:-1]:
            draw_filled_circle(draw, px, py, vr, accent)

    # Peak (último vértice) — sin sparkline también lleva el peak
    peak_x, peak_y = points[-1]
    peak_r = max(4, int(8 * scale))
    halo_r = max(5, int(10 * scale))
    if draw_sparkline:
        # Con halo blanco
        draw_filled_circle(draw, peak_x, peak_y, halo_r, white)
        draw_filled_circle(draw, peak_x, peak_y, peak_r, accent)
    else:
        # Solo dorado
        draw_filled_circle(draw, peak_x, peak_y, peak_r + 2, accent)

    # Línea de gol con mini-postes
    goal_y = grid_y + baseline_y
    goal_x1 = grid_x + (-25) * scale
    goal_x2 = grid_x + 415 * scale
    goal_w = max(2, int(5 * scale))
    draw_thick_line_round(draw, goal_x1, goal_y, goal_x2, goal_y, accent, goal_w)

    # Mini-postes
    post_h = 16 * scale
    post_w = max(2, int(4 * scale))
    draw_thick_line_round(draw, goal_x1, goal_y, goal_x1, goal_y - post_h, accent, post_w)
    draw_thick_line_round(draw, goal_x2, goal_y, goal_x2, goal_y - post_h, accent, post_w)

    return layer


def render_isotipo(size: int, variant: str) -> Image.Image:
    """Renderiza variantes cuadradas del isotipo (500x500 base)."""
    bg_transparent = variant in ("blanco", "dorado", "celeste")
    bg = (0, 0, 0, 0) if bg_transparent else hex_to_rgba(BG)

    canvas = Image.new("RGBA", (size, size), bg)

    # Determinar colores según variante
    if variant == "completo":
        color_bars = PRIMARY
        color_accent = ACCENT
        draw_spark = True
        text_color_2 = ACCENT  # "Ar" dorado
        text_color_1 = TEXT
    elif variant == "simple":
        color_bars = PRIMARY
        color_accent = ACCENT
        draw_spark = False
        text_color_1 = TEXT
        text_color_2 = ACCENT
    elif variant == "watermark":
        return render_watermark(size)
    elif variant == "blanco":
        color_bars = "#FFFFFF"
        color_accent = "#FFFFFF"
        draw_spark = False
        text_color_1 = TEXT
        text_color_2 = TEXT
    elif variant == "dorado":
        color_bars = ACCENT
        color_accent = ACCENT
        draw_spark = False
        text_color_1 = hex_to_rgba(ACCENT)
        text_color_2 = hex_to_rgba(ACCENT)
    elif variant == "celeste":
        color_bars = PRIMARY
        color_accent = PRIMARY
        draw_spark = False
        text_color_1 = hex_to_rgba(PRIMARY)
        text_color_2 = hex_to_rgba(PRIMARY)
    else:
        raise ValueError(f"Variante desconocida: {variant}")

    # Renderizar bloque skyline
    skyline = render_skyline_base(size, draw_spark, color_bars, color_accent)
    canvas = Image.alpha_composite(canvas, skyline)

    # Texto marca
    draw = ImageDraw.Draw(canvas)
    font_size = max(10, int(56 * size / 500))
    font = get_font(font_size)
    text_y = int(430 * size / 500)

    if variant == "completo" or variant == "simple":
        draw_centered_text_multicolor(
            draw, size / 2, text_y,
            "datafutbol ", hex_to_rgba(TEXT),
            "Ar", hex_to_rgba(ACCENT),
            font,
        )
    else:
        # Monocolor: todo el texto en el mismo color
        if variant == "blanco":
            color = hex_to_rgba("#FFFFFF")
        elif variant == "dorado":
            color = hex_to_rgba(ACCENT)
        elif variant == "celeste":
            color = hex_to_rgba(PRIMARY)
        draw_centered_text(draw, size / 2, text_y, "datafutbol Ar", color, font)

    return canvas


def render_watermark(size: int) -> Image.Image:
    """Watermark — solo símbolo. FONDO TRANSPARENTE (para poder superponer sobre slides)."""
    scale = size / 500
    # Fondo transparente para que NO tape lo que está debajo cuando se usa como watermark
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    grid_x = 85 * scale
    grid_y = 130 * scale

    primary = hex_to_rgba(PRIMARY)
    accent = hex_to_rgba(ACCENT)
    white = hex_to_rgba(TEXT)

    # 5 barras
    for i, h in enumerate(WATERMARK_BAR_HEIGHTS):
        x = grid_x + WATERMARK_BAR_X_OFFSETS[i] * scale
        y_top = grid_y + (240 - h) * scale
        bw = WATERMARK_BAR_WIDTH * scale
        bh = h * scale
        radius = max(1, int(4 * scale))
        draw_rounded_bar(draw, x, y_top, bw, bh, primary, radius=radius)

    # Peak grande con halo (sobre la última barra)
    peak_x = grid_x + (WATERMARK_BAR_X_OFFSETS[-1] + WATERMARK_BAR_WIDTH / 2) * scale
    peak_y = grid_y + (240 - WATERMARK_BAR_HEIGHTS[-1]) * scale
    peak_r = max(5, int(14 * scale))
    halo_w = max(2, int(2 * scale))
    draw_filled_circle(draw, peak_x, peak_y, peak_r, accent, stroke=white, stroke_width=halo_w)

    # Línea de gol GRUESA con mini-postes pronunciados
    goal_y = grid_y + 250 * scale
    goal_x1 = grid_x - 25 * scale
    goal_x2 = grid_x + 340 * scale
    goal_w = max(3, int(8 * scale))
    draw_thick_line_round(draw, goal_x1, goal_y, goal_x2, goal_y, accent, goal_w)
    # Postes
    post_h = 30 * scale
    post_w = max(3, int(7 * scale))
    draw_thick_line_round(draw, goal_x1, goal_y, goal_x1, goal_y - post_h, accent, post_w)
    draw_thick_line_round(draw, goal_x2, goal_y, goal_x2, goal_y - post_h, accent, post_w)

    return canvas


def render_horizontal(width: int) -> Image.Image:
    """Logo horizontal — viewBox 1400x400. Width custom, height proporcional."""
    target_w = width
    target_h = int(width * 400 / 1400)
    scale = width / 1400

    canvas = Image.new("RGBA", (target_w, target_h), hex_to_rgba(BG))

    # ─── Símbolo izquierda (mini skyline) ───
    # Posición del grid en coords SVG (80, 140) + tamaño de barras escalado
    grid_x = 80 * scale
    grid_y = 140 * scale

    primary_op = hex_to_rgba(PRIMARY, 165)
    accent = hex_to_rgba(ACCENT)
    white = hex_to_rgba(TEXT)

    # Barras pequeñas (ancho 22, separación 28)
    h_bar_widths = 22
    h_bar_offsets = [0, 28, 56, 84, 112, 140, 168, 196, 224]
    h_bar_heights = [40, 70, 20, 88, 57, 108, 30, 80, 120]

    bar_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    bar_draw = ImageDraw.Draw(bar_layer)
    for i, h in enumerate(h_bar_heights):
        x = grid_x + h_bar_offsets[i] * scale
        y_top = grid_y + (120 - h) * scale
        bw = h_bar_widths * scale
        bh = h * scale
        draw_rounded_bar(bar_draw, x, y_top, bw, bh, primary_op, radius=max(1, int(2 * scale)))

    canvas = Image.alpha_composite(canvas, bar_layer)
    draw = ImageDraw.Draw(canvas)

    # Sparkline + vértices
    points = []
    for i, h in enumerate(h_bar_heights):
        x = grid_x + (h_bar_offsets[i] + h_bar_widths / 2) * scale
        y = grid_y + (120 - h) * scale
        points.append((x, y))

    spark_w = max(1, int(2.5 * scale))
    draw_polyline_round(draw, points, accent, spark_w)

    vr = max(1, int(3 * scale))
    for px, py in points[:-1]:
        draw_filled_circle(draw, px, py, vr, accent)
    # Peak
    pr = max(3, int(6 * scale))
    halo_w = max(1, int(1.5 * scale))
    px, py = points[-1]
    draw_filled_circle(draw, px, py, pr, accent, stroke=white, stroke_width=halo_w)

    # Línea de gol
    goal_y = grid_y + 128 * scale
    goal_x1 = grid_x - 18 * scale
    goal_x2 = grid_x + 265 * scale
    gw = max(2, int(4 * scale))
    draw_thick_line_round(draw, goal_x1, goal_y, goal_x2, goal_y, accent, gw)
    post_h = 10 * scale
    post_w = max(1, int(3 * scale))
    draw_thick_line_round(draw, goal_x1, goal_y, goal_x1, goal_y - post_h, accent, post_w)
    draw_thick_line_round(draw, goal_x2, goal_y, goal_x2, goal_y - post_h, accent, post_w)

    # ─── Wordmark derecha ───
    # Posición en SVG: x=430, y=220 — fuente size 130
    font_size = max(12, int(130 * scale))
    font = get_font(font_size)

    # En matplotlib bbox top sería ~baseline - asc. Hacemos manual:
    text_x_left = 430 * scale
    text_y_center = 200 * scale  # ajuste manual para verse centrado verticalmente
    # Pillow text(): coord = top-left
    # Calculamos baseline aprox
    bbox = font.getbbox("datafutbol Ar")
    text_y = text_y_center - (bbox[3] - bbox[1]) / 2 - bbox[1]

    # "datafutbol " blanco
    df_text = "datafutbol "
    df_bbox = font.getbbox(df_text)
    df_w = df_bbox[2] - df_bbox[0]
    draw.text((text_x_left - df_bbox[0], text_y), df_text, fill=white, font=font)

    # "Ar" dorado
    draw.text((text_x_left + df_w - df_bbox[0], text_y), "Ar", fill=accent, font=font)

    # Línea decorativa dorada debajo
    line_y = (text_y_center + (bbox[3] - bbox[1]) / 2) + 8 * scale
    line_x1 = text_x_left
    line_x2 = text_x_left + 820 * scale
    draw.line((line_x1, line_y, line_x2, line_y), fill=accent + (0,) if False else (*accent[:3], 140), width=max(1, int(2 * scale)))
    # arriba: usé hack feo. Hago simple:
    line_color = (*hex_to_rgba(ACCENT)[:3], 140)
    draw.line((line_x1, line_y, line_x2, line_y), fill=line_color, width=max(1, int(2 * scale)))

    return canvas


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────

SIZES_SQUARE = [1024, 512, 256, 128, 64, 32]
SIZES_HORIZONTAL = [2000, 1200, 800, 400]

VARIANTS_SQUARE = ["completo", "simple", "watermark", "blanco", "dorado", "celeste"]


def main():
    print("=" * 60)
    print("Generando logos datafutbol_ar (Pillow puro, sin Cairo)")
    print("=" * 60)
    print(f"Output: {OUTPUT_DIR}\n")

    total = 0
    ok = 0

    # Variantes cuadradas
    for variant in VARIANTS_SQUARE:
        print(f"📐 {variant}")
        for size in SIZES_SQUARE:
            total += 1
            try:
                img = render_isotipo(size, variant)
                fname = f"isotipo_{variant}_{size}.png" if variant in ("completo", "simple", "watermark") else f"monocolor_{variant}_{size}.png"
                img.save(OUTPUT_DIR / fname)
                print(f"  ✅ {fname}")
                ok += 1
            except Exception as e:
                print(f"  ❌ {variant} {size}: {e}")

    # Horizontal
    print(f"\n📐 horizontal")
    for width in SIZES_HORIZONTAL:
        total += 1
        height = int(width * 400 / 1400)
        try:
            img = render_horizontal(width)
            fname = f"horizontal_{width}x{height}.png"
            img.save(OUTPUT_DIR / fname)
            print(f"  ✅ {fname}")
            ok += 1
        except Exception as e:
            print(f"  ❌ horizontal {width}: {e}")

    print("\n" + "=" * 60)
    print(f"✅ {ok}/{total} PNGs generados en: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
