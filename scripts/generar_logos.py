"""
generar_logos.py — Renderiza los SVG fuente de logo a PNGs en varios tamaños.

Uso:
    python scripts/generar_logos.py

Genera PNGs en:
    G:\\Mi unidad\\DATAFUTBOL_AR\\02_Branding\\logos\\png\\

Requiere:
    pip install cairosvg

Si cairosvg falla en Windows, alternativa:
    pip install svglib reportlab
    (el script intenta ambos)
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


# ──────────────────────────────────────────────────────────────────────
# Rutas
# ──────────────────────────────────────────────────────────────────────
SOURCE_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\logos\source")
OUTPUT_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\logos\png")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Tamaños a generar por cada SVG (en píxeles, ancho)
# Para SVGs cuadrados (viewBox 500x500), height = width
SIZES_SQUARE = [1024, 512, 256, 128, 64, 32]
# Para el horizontal (viewBox 1400x400), proporcional
SIZES_HORIZONTAL = [(2000, 571), (1200, 343), (800, 229), (400, 114)]


def render_svg_to_png(svg_path: Path, png_path: Path, width: int, height: int = None):
    """Renderiza UN SVG a PNG. Intenta cairosvg primero, después svglib."""
    if height is None:
        height = width

    # Intento 1: cairosvg (más rápido y fiel)
    try:
        import cairosvg
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=width,
            output_height=height,
            background_color=None,  # transparente
        )
        return True
    except ImportError:
        pass
    except Exception as e:
        print(f"  ⚠️ cairosvg falló para {svg_path.name}: {e}")

    # Intento 2: svglib + reportlab (fallback)
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM

        drawing = svg2rlg(str(svg_path))
        # Calcular factor de escala
        scale_x = width / drawing.width
        scale_y = height / drawing.height
        drawing.width = width
        drawing.height = height
        drawing.scale(scale_x, scale_y)

        renderPM.drawToFile(drawing, str(png_path), fmt="PNG", bg=0xFFFFFF, configPIL={"transparent": 0xFFFFFF})
        return True
    except ImportError:
        print("  ⚠️ Ni cairosvg ni svglib están instalados.")
        print("     Ejecutá: pip install cairosvg")
        print("     o:      pip install svglib reportlab")
        return False
    except Exception as e:
        print(f"  ❌ svglib también falló: {e}")
        return False


def generar_variantes(svg_path: Path, sizes: Iterable):
    """Genera todas las variantes de tamaño de un SVG."""
    stem = svg_path.stem  # ej. "isotipo_completo"
    print(f"\n📐 Procesando: {svg_path.name}")

    for size in sizes:
        if isinstance(size, tuple):
            w, h = size
            png_name = f"{stem}_{w}x{h}.png"
        else:
            w, h = size, size
            png_name = f"{stem}_{w}.png"

        png_path = OUTPUT_DIR / png_name
        ok = render_svg_to_png(svg_path, png_path, w, h)
        if ok:
            print(f"  ✅ {png_name}")
        else:
            print(f"  ❌ {png_name}")


def main():
    print("=" * 60)
    print("Generando logos datafutbol_ar")
    print("=" * 60)
    print(f"Fuente: {SOURCE_DIR}")
    print(f"Output: {OUTPUT_DIR}")

    if not SOURCE_DIR.exists():
        print(f"❌ No existe la carpeta de fuentes: {SOURCE_DIR}")
        return

    svgs = sorted(SOURCE_DIR.glob("*.svg"))
    if not svgs:
        print(f"❌ No hay SVGs en {SOURCE_DIR}")
        return

    print(f"\nEncontrados {len(svgs)} SVGs:")
    for svg in svgs:
        print(f"  · {svg.name}")

    for svg in svgs:
        # El horizontal usa proporción 1400x400
        if "horizontal" in svg.stem.lower():
            generar_variantes(svg, SIZES_HORIZONTAL)
        else:
            generar_variantes(svg, SIZES_SQUARE)

    print("\n" + "=" * 60)
    print(f"✅ Logos generados en: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
