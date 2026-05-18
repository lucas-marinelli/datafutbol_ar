"""
generar_avatar_ig.py — Genera versión AVATAR del logo para IG/X/redes.

Diferencia con el isotipo_simple normal:
- Padding interno generoso (todo el contenido en el círculo central inscripto)
- Fondo BG opaco completo (no transparente)
- Las barras y texto quedan SAFE incluso cuando IG aplica el recorte circular

Uso:
    python scripts/generar_avatar_ig.py

Output:
    G:\\Mi unidad\\DATAFUTBOL_AR\\02_Branding\\logos\\png\\isotipo_avatar_1024.png
    (+ versiones 512, 256)
"""

from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


OUTPUT_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\logos\png")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Colores Combo C
BG = "#0E2A47"
PRIMARY = "#75AADB"
ACCENT = "#C9A227"
TEXT = "#FFFFFF"

# Datos del skyline (mismas alturas que el logo principal)
BAR_HEIGHTS = [65, 110, 35, 140, 90, 170, 50, 125, 190]
BAR_X_OFFSETS = [0, 44, 88, 132, 176, 220, 264, 308, 352]
BAR_WIDTH = 36


def hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)


def get_font(size: int) -> ImageFont.FreeTypeFont:
    win_fonts = Path(r"C:\Windows\Fonts")
    candidates = ["Oswald-Bold.ttf", "Oswald.ttf", "arialbd.ttf", "arial.ttf"]

    if win_fonts.exists():
        for name in candidates:
            f = win_fonts / name
            if f.exists():
                try:
                    return ImageFont.truetype(str(f), size)
                except (IOError, OSError):
                    continue
    return ImageFont.load_default()


def render_avatar(size: int = 1024) -> Image.Image:
    """Genera la versión avatar con padding seguro para el recorte circular de IG."""
    # ─── Setup ───
    # El círculo inscripto en un cuadrado tiene radio = size/2.
    # Para que TODO el contenido caiga dentro del círculo, lo limitamos al 80% del cuadrado (área safe).
    canvas = Image.new("RGBA", (size, size), hex_to_rgba(BG))
    draw = ImageDraw.Draw(canvas)

    # Factor de escala del diseño original (que es viewBox 500x500)
    # Pero queremos que el contenido use solo el 75% del cuadrado (más padding)
    safe_factor = 0.72
    inner_size = size * safe_factor
    scale = inner_size / 500
    # Offset para centrar el "inner" en el "outer"
    offset = (size - inner_size) / 2

    grid_x = offset + 70 * scale
    grid_y = offset + 110 * scale

    # ─── Barras ───
    primary = hex_to_rgba(PRIMARY)
    for i, h in enumerate(BAR_HEIGHTS):
        x = grid_x + BAR_X_OFFSETS[i] * scale
        y_top = grid_y + (200 - h) * scale
        bw = BAR_WIDTH * scale
        bh = h * scale
        radius = max(1, int(3 * scale))
        draw.rounded_rectangle((x, y_top, x + bw, y_top + bh), radius=radius, fill=primary)

    # ─── Peak dorado ───
    accent = hex_to_rgba(ACCENT)
    peak_x = grid_x + (BAR_X_OFFSETS[-1] + BAR_WIDTH / 2) * scale
    peak_y = grid_y + (200 - BAR_HEIGHTS[-1]) * scale
    peak_r = max(4, int(10 * scale))
    draw.ellipse((peak_x - peak_r, peak_y - peak_r, peak_x + peak_r, peak_y + peak_r), fill=accent)

    # ─── Línea de gol con mini-postes ───
    goal_y = grid_y + 200 * scale
    goal_x1 = grid_x + (-25) * scale
    goal_x2 = grid_x + 415 * scale
    goal_w = max(2, int(5 * scale))
    draw.line((goal_x1, goal_y, goal_x2, goal_y), fill=accent, width=goal_w)
    # Caps redondeados
    r = goal_w / 2
    draw.ellipse((goal_x1 - r, goal_y - r, goal_x1 + r, goal_y + r), fill=accent)
    draw.ellipse((goal_x2 - r, goal_y - r, goal_x2 + r, goal_y + r), fill=accent)

    # Mini-postes
    post_h = 16 * scale
    post_w = max(2, int(4 * scale))
    for px in [goal_x1, goal_x2]:
        draw.line((px, goal_y, px, goal_y - post_h), fill=accent, width=post_w)
        r2 = post_w / 2
        draw.ellipse((px - r2, goal_y - post_h - r2, px + r2, goal_y - post_h + r2), fill=accent)

    # ─── Texto "datafutbol Ar" ───
    font_size = max(8, int(56 * scale * 0.95))
    font = get_font(font_size)

    # "datafutbol " en blanco + "Ar" en dorado, centrados
    text1 = "datafutbol "
    text2 = "Ar"
    full = text1 + text2

    bbox_full = font.getbbox(full)
    bbox_p1 = font.getbbox(text1)
    full_w = bbox_full[2] - bbox_full[0]
    p1_w = bbox_p1[2] - bbox_p1[0]
    h_text = bbox_full[3] - bbox_full[1]

    # y del texto: bajo la línea de gol con margen
    text_y_center = grid_y + 240 * scale
    x_start = size / 2 - full_w / 2 - bbox_full[0]
    y_top = text_y_center - h_text / 2 - bbox_full[1]

    draw.text((x_start, y_top), text1, fill=hex_to_rgba(TEXT), font=font)
    draw.text((x_start + p1_w, y_top), text2, fill=accent, font=font)

    return canvas


if __name__ == "__main__":
    print("Generando avatares para redes sociales...")
    for size in [1024, 512, 256]:
        img = render_avatar(size)
        fname = f"isotipo_avatar_{size}.png"
        img.save(OUTPUT_DIR / fname)
        print(f"  ✅ {fname}")
    print(f"\n✅ Avatares en: {OUTPUT_DIR}")
    print("Usá el 1024 o 512 para IG, X, GitHub, etc.")
