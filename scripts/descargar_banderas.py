"""descargar_banderas.py — Baja banderas oficiales de flagcdn.com.

Lee la lista de selecciones del CSV maestro
(02_Branding/selecciones_mundial_2026.csv) y baja una bandera por cada una
usando su código ISO 3166-1 alpha-2.

flagcdn.com sirve banderas PNG. Para sub-regiones usa códigos compuestos:
    · gb-eng → Inglaterra
    · gb-sct → Escocia
    · gb-wls → Gales

Convención de archivos (R27 reglas editoriales):
    nombre en español, sin tildes, snake_case → ej: paises_bajos.png

Uso:
    python scripts/descargar_banderas.py            # Mundial: 48 banderas + Italia
    python scripts/descargar_banderas.py --conmebol # solo CONMEBOL
    python scripts/descargar_banderas.py --refresh  # re-descargar incluso si existe

Output:
    G:\\Mi unidad\\DATAFUTBOL_AR\\02_Branding\\banderas_paises\\<nombre>.png
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path

import requests

# Hacemos sys.path para poder importar data_loaders si se corre desde la raíz
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.data_loaders import cargar_selecciones  # noqa: E402

OUTPUT_DIR = Path(r"G:\Mi unidad\DATAFUTBOL_AR\02_Branding\banderas_paises")

URL_TEMPLATES = [
    "https://flagcdn.com/w320/{iso}.png",   # mejor calidad
    "https://flagcdn.com/w160/{iso}.png",   # fallback
    "https://flagcdn.com/w80/{iso}.png",    # último intento
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/png,image/*,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

MIN_VALID_SIZE = 250  # bytes mínimos para considerarla válida
SLEEP_BETWEEN = 0.8   # segundos entre requests


def descargar_bandera(nombre: str, iso: str, archivo: str, output_dir: Path,
                      refresh: bool = False) -> str:
    """Descarga una bandera. Devuelve 'ok', 'skip', o 'fail'."""
    dest = output_dir / archivo

    if dest.exists() and dest.stat().st_size >= MIN_VALID_SIZE and not refresh:
        print(f"  [SKIP] {archivo:<28} ya existe ({dest.stat().st_size:,} bytes)")
        return "skip"

    for template in URL_TEMPLATES:
        url = template.format(iso=iso)
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
        except Exception as e:
            print(f"  [WARN] {archivo}: {type(e).__name__} en {url}")
            continue

        if r.status_code != 200:
            print(f"  [WARN] {archivo}: HTTP {r.status_code} en {url}")
            continue

        size = len(r.content)
        if size < MIN_VALID_SIZE:
            print(f"  [WARN] {archivo}: respuesta chica ({size} bytes en {url})")
            continue

        dest.write_bytes(r.content)
        print(f"  [OK]   {archivo:<28} ({size:,} bytes)")
        return "ok"

    print(f"  [FAIL] {archivo}: ninguna URL devolvió bandera válida (iso={iso})")
    return "fail"


def main() -> int:
    parser = argparse.ArgumentParser(description="Baja banderas a banderas_paises/")
    parser.add_argument("--conmebol", action="store_true",
                        help="Solo CONMEBOL")
    parser.add_argument("--uefa", action="store_true",
                        help="Solo UEFA")
    parser.add_argument("--caf", action="store_true",
                        help="Solo CAF")
    parser.add_argument("--afc", action="store_true",
                        help="Solo AFC")
    parser.add_argument("--ofc", action="store_true",
                        help="Solo OFC")
    parser.add_argument("--concacaf", action="store_true",
                        help="Solo CONCACAF")
    parser.add_argument("--all", action="store_true",
                        help="Incluye también las no clasificadas (Italia, etc.)")
    parser.add_argument("--refresh", action="store_true",
                        help="Re-descargar incluso si el archivo ya existe")
    args = parser.parse_args()

    # Filtrar por confederación si corresponde
    confederacion = None
    for c in ("CONMEBOL", "UEFA", "CAF", "AFC", "OFC", "CONCACAF"):
        if getattr(args, c.lower()):
            confederacion = c

    # Por defecto solo bajamos las que juegan el Mundial (clasif + host)
    # --all incluye también no_clasificado, dudoso, repechaje
    estado = None if args.all else ["host", "clasificado"]

    df = cargar_selecciones(confederacion=confederacion, estado=estado)
    print(f"Selecciones a procesar: {len(df)}")
    if confederacion:
        print(f"Filtro confederación: {confederacion}")
    if args.all:
        print("Incluye no clasificadas")
    print(f"Destino: {OUTPUT_DIR}\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ok = skip = fail = 0
    fallidas = []
    for _, row in df.iterrows():
        result = descargar_bandera(
            row["nombre_es"],
            row["iso2"],
            row["archivo_bandera"],
            OUTPUT_DIR,
            refresh=args.refresh,
        )
        if result == "ok":
            ok += 1
            time.sleep(SLEEP_BETWEEN)
        elif result == "skip":
            skip += 1
        else:
            fail += 1
            fallidas.append(row["archivo_bandera"])
            time.sleep(SLEEP_BETWEEN)

    print(f"\nResumen: {ok} OK · {skip} skip · {fail} fail (total {len(df)})")
    if fallidas:
        print("Fallaron: " + ", ".join(fallidas))
        print("\nPodés bajar manualmente desde https://flagcdn.com/")
        print(f"Guardalas en: {OUTPUT_DIR}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
