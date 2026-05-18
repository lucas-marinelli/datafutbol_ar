"""descargar_banderas.py — Baja banderas oficiales de flagcdn.com.

flagcdn.com sirve banderas en PNG con códigos ISO 3166-1 alpha-2.
Para regiones (Inglaterra, Escocia, Gales) usa códigos con sub-región:
    · gb-eng → Inglaterra
    · gb-sct → Escocia
    · gb-wls → Gales

Tamaño descargado: 160px de ancho. Suficiente para mostrarlas en ranking
horizontal sin perder calidad al renderizar.

Convención de archivos (R27 reglas editoriales):
    nombre en español, sin tildes, snake_case → ejemplo: paises_bajos.png

Uso:
    python scripts/descargar_banderas.py

Output:
    G:\\Mi unidad\\DATAFUTBOL_AR\\02_Branding\\banderas_paises\\<nombre>.png
"""

from __future__ import annotations
from pathlib import Path
import sys
import time

import requests

OUTPUT_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\banderas_paises")

# Probamos varios tamaños en orden — flagcdn no siempre tiene todas las tallas.
URL_TEMPLATES = [
    "https://flagcdn.com/w320/{iso}.png",   # mejor calidad y soporte universal
    "https://flagcdn.com/w160/{iso}.png",   # fallback
    "https://flagcdn.com/w80/{iso}.png",    # último intento
]

# User-Agent que se ve como Chrome real (evita rate-limit/anti-bot)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/png,image/*,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

MIN_VALID_SIZE = 250  # bytes — debajo de esto asumimos placeholder/error

# Top 16 ranking FIFA mayo 2026.
# (archivo en español snake_case sin tildes, código flagcdn)
BANDERAS = [
    ("argentina",       "ar"),
    ("francia",         "fr"),
    ("espana",          "es"),
    ("inglaterra",      "gb-eng"),
    ("portugal",        "pt"),
    ("brasil",          "br"),
    ("paises_bajos",    "nl"),
    ("marruecos",       "ma"),
    ("belgica",         "be"),
    ("alemania",        "de"),
    ("croacia",         "hr"),
    ("italia",          "it"),
    ("colombia",        "co"),
    ("senegal",         "sn"),
    ("mexico",          "mx"),
    ("estados_unidos",  "us"),
]


def descargar_bandera(nombre: str, iso: str, output_dir: Path) -> bool:
    """Descarga una bandera probando varios tamaños. True si OK, False si falla."""
    dest = output_dir / f"{nombre}.png"

    # Si ya existe un archivo grande (>250 bytes), saltamos
    if dest.exists() and dest.stat().st_size >= MIN_VALID_SIZE:
        print(f"  [SKIP]  {nombre}.png ya existe ({dest.stat().st_size:,} bytes)")
        return True

    for template in URL_TEMPLATES:
        url = template.format(iso=iso)
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
        except Exception as e:
            print(f"  [WARN]  {nombre} @ {url}: {type(e).__name__}")
            continue

        if r.status_code != 200:
            print(f"  [WARN]  {nombre} @ {url}: HTTP {r.status_code}")
            continue

        size = len(r.content)
        if size < MIN_VALID_SIZE:
            print(f"  [WARN]  {nombre} @ {url}: respuesta muy chica ({size} bytes — placeholder)")
            continue

        dest.write_bytes(r.content)
        print(f"  [OK]    {nombre}.png ({size:,} bytes) desde {url.rsplit('/', 1)[-1]}")
        return True

    print(f"  [FALLO] {nombre}: ninguna URL devolvió bandera válida")
    return False


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Destino: {OUTPUT_DIR}\n")

    ok = 0
    fallidas = []
    for nombre, iso in BANDERAS:
        if descargar_bandera(nombre, iso, OUTPUT_DIR):
            ok += 1
        else:
            fallidas.append(nombre)
        time.sleep(0.8)  # delay más generoso para no gatillar anti-bot

    print(f"\nResumen: {ok}/{len(BANDERAS)} banderas OK.")
    if fallidas:
        print("Fallaron: " + ", ".join(fallidas))
        print("\nPodés bajar manualmente las que fallaron desde:")
        print("  https://flagcdn.com/  (buscá por nombre)")
        print(f"Guardalas en: {OUTPUT_DIR}")
        return 1
    print("Todo OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
