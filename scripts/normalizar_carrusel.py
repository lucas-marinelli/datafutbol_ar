"""
normalizar_carrusel.py — Normaliza PNGs a 1080×1350 (formato IG carrusel)

Toma cualquier PNG y la lleva a 1080×1350 (4:5) sin recortar contenido,
agregando bandas (letterbox/pillarbox) del color de fondo de la marca.

Uso:
    from scripts.normalizar_carrusel import normalizar_a_carrusel
    normalizar_a_carrusel("input.png", "output.png")

O para procesar varias de un saque:
    from scripts.normalizar_carrusel import normalizar_lote
    normalizar_lote(
        archivos_input=[path1, path2, path3],
        carpeta_output=Path("outputs/2026-05/normalized"),
    )
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PIL import Image

# Constantes — formato IG carrusel
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1350
TARGET_RATIO = TARGET_WIDTH / TARGET_HEIGHT  # 0.8

# Color de fondo de la marca (Combo C — azul profundo #0E2A47)
BG_COLOR_RGB = (14, 42, 71)


def normalizar_a_carrusel(
    input_path: str | Path,
    output_path: str | Path,
    bg_color: tuple[int, int, int] = BG_COLOR_RGB,
) -> Path:
    """Convierte una PNG a 1080×1350 sin recortar contenido.

    Si la imagen es más ALTA que 4:5 → agrega bandas LATERALES de color bg.
    Si la imagen es más ANCHA que 4:5 → agrega bandas ARRIBA/ABAJO.
    Si ya es 4:5 → solo redimensiona.

    Args:
        input_path: ruta del PNG original
        output_path: dónde guardar el normalizado
        bg_color: color de las bandas (default = azul Combo C)

    Returns:
        Path al PNG normalizado.
    """
    img = Image.open(input_path).convert("RGB")
    w, h = img.size
    img_ratio = w / h

    # Margen de tolerancia para "ya es 4:5"
    if abs(img_ratio - TARGET_RATIO) < 0.005:
        # Ya está bien, solo redimensionar
        img_final = img.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.LANCZOS)

    elif img_ratio < TARGET_RATIO:
        # Más ALTA que 4:5 → bandas laterales (pillarbox)
        new_h = TARGET_HEIGHT
        new_w = int(round(new_h * img_ratio))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), bg_color)
        offset_x = (TARGET_WIDTH - new_w) // 2
        canvas.paste(img_resized, (offset_x, 0))
        img_final = canvas

    else:
        # Más ANCHA que 4:5 → bandas arriba/abajo (letterbox)
        new_w = TARGET_WIDTH
        new_h = int(round(new_w / img_ratio))
        img_resized = img.resize((new_w, new_h), Image.LANCZOS)
        canvas = Image.new("RGB", (TARGET_WIDTH, TARGET_HEIGHT), bg_color)
        offset_y = (TARGET_HEIGHT - new_h) // 2
        canvas.paste(img_resized, (0, offset_y))
        img_final = canvas

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_final.save(output_path, "PNG", optimize=True)
    return output_path


def normalizar_lote(
    archivos_input: Sequence[str | Path],
    carpeta_output: str | Path,
    sufijo: str = "_1080x1350",
) -> list[Path]:
    """Normaliza varias PNGs a 1080×1350 y las guarda en una carpeta destino.

    Args:
        archivos_input: lista de rutas a PNGs originales.
        carpeta_output: dónde guardar los normalizados.
        sufijo: se agrega al nombre antes de la extensión (ej. "_1080x1350").
            Pasar "" si querés mantener el nombre exacto.

    Returns:
        Lista de paths a los PNGs normalizados, en el mismo orden de entrada.
    """
    carpeta_output = Path(carpeta_output)
    carpeta_output.mkdir(parents=True, exist_ok=True)

    paths_output = []
    for input_path in archivos_input:
        input_path = Path(input_path)
        output_name = input_path.stem + sufijo + input_path.suffix
        output_path = carpeta_output / output_name
        normalizar_a_carrusel(input_path, output_path)
        paths_output.append(output_path)

    return paths_output
