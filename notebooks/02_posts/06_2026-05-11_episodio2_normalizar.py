# %% [markdown]
# # Episodio 2 — Normalizar las 6 PNGs a 1080×1350
#
# **Problema:** las 6 PNGs del carrusel salen con tamaños distintos porque
# `bbox_inches="tight"` recorta los márgenes. Eso hace que IG las recorte
# automáticamente al subirlas como carrusel (necesita ratio uniforme),
# cortando el panel inferior y el watermark.
#
# **Solución:** llevarlas todas a 1080×1350 (4:5 = ratio IG carrusel) agregando
# bandas laterales de color azul Combo C. Las viz quedan completas y todas
# con el mismo ratio → IG no recorta nada.

# %% [markdown]
# ## Celda 1 — Setup

# %%
try:
    from IPython import get_ipython

    ip = get_ipython()
    if ip is not None:
        ip.run_line_magic("load_ext", "autoreload")
        ip.run_line_magic("autoreload", "2")
except ImportError:
    pass

import sys
from pathlib import Path

REPO_ROOT = Path(r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.normalizar_carrusel import normalizar_lote

print("Setup OK ✓")

# %% [markdown]
# ## Celda 2 — Definir las 6 PNGs en orden

# %%
OUTPUT_DIR = REPO_ROOT / "outputs" / "2026-05"

archivos = [
    OUTPUT_DIR / "2026-05-11_episodio2_slide1_portada.png",
    OUTPUT_DIR / "2026-05-11_episodio2_shotmap_arg_fra.png",
    OUTPUT_DIR / "2026-05-11_episodio2_radar_messi.png",
    OUTPUT_DIR / "2026-05-11_episodio2_passnetwork_arg.png",
    OUTPUT_DIR / "2026-05-11_episodio2_heatmap_messi.png",
    OUTPUT_DIR / "2026-05-11_episodio2_slide6_cierre.png",
]

# Verificar que todas existen
for p in archivos:
    estado = "✓" if p.exists() else "✗ FALTA"
    print(f"  {estado}  {p.name}")

# %% [markdown]
# ## Celda 3 — Normalizar todas a 1080×1350

# %%
carpeta_destino = OUTPUT_DIR / "carrusel_final"
paths_normalizados = normalizar_lote(
    archivos_input=archivos,
    carpeta_output=carpeta_destino,
    sufijo="",  # mantener el nombre original
)

print(f"\n✓ {len(paths_normalizados)} PNGs normalizadas a 1080×1350")
print(f"  Guardadas en: {carpeta_destino}")
print()
for p in paths_normalizados:
    print(f"  → {p.name}")

# %% [markdown]
# ## Celda 4 — Verificación visual rápida
#
# Abrir la primera PNG normalizada para confirmar que se ve bien.

# %%
from PIL import Image
import matplotlib.pyplot as plt

# Mostrar la primera PNG normalizada para confirmar
img = Image.open(paths_normalizados[0])
print(f"Dimensiones primera PNG: {img.size}  (debe ser 1080×1350)")

fig, ax = plt.subplots(figsize=(4, 5))
ax.imshow(img)
ax.axis("off")
ax.set_title(f"Vista previa: {paths_normalizados[0].name}", fontsize=8)
plt.show()

# %% [markdown]
# ## ✅ Listo
#
# Las 6 PNGs normalizadas están en `outputs/2026-05/carrusel_final/`.
#
# **Próximo paso:** subir las 6 PNGs de **esa carpeta** (no las originales)
# a Meta Business Suite → Crear publicación → IG → carrusel.
#
# Ahora todas tienen exactamente 1080×1350 y NO van a sufrir recorte
# automático en IG.

# %%
