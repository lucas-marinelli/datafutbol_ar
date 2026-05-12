# %% [markdown]
# # Episodio 2 — Portada + Cierre del carrusel
#
# Genera Slide 1 (portada) y Slide 6 (cierre con CTA) del carrusel del Episodio 2.
# Esto reemplaza la necesidad de armar esas slides a mano en Canva.
#
# **Plantilla reusable (Regla R13):** para futuros carruseles, solo cambiar
# los textos. La estética está toda dentro de `scripts/carrusel.py`.

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

import matplotlib.pyplot as plt

from scripts.carrusel import crear_cierre_carrusel, crear_portada_carrusel
from scripts.style import BG, set_default_style

set_default_style()
print("Setup OK ✓")

# %% [markdown]
# ## Celda 2 — Generar SLIDE 1 (portada)

# %%
fig_portada, ax = crear_portada_carrusel(
    titulo="5 VISUALIZACIONES\nQUE CUENTAN MÁS\nQUE 1.000 STATS",
    subtitulo="Lo que vas a ver acá, todo el año.",
    handle="@datafutbol_ar",
    mostrar_flecha=True,
)
plt.show()

# %% [markdown]
# ## Celda 3 — Guardar portada

# %%
OUTPUT_DIR = REPO_ROOT / "outputs" / "2026-05"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

portada_path = OUTPUT_DIR / "2026-05-11_episodio2_slide1_portada.png"
fig_portada.savefig(
    portada_path,
    dpi=200,
    facecolor=BG,
    bbox_inches="tight",
    pad_inches=0,
)
print(f"✓ Portada guardada: {portada_path}")
print(f"  Tamaño: {portada_path.stat().st_size / 1024:.1f} KB")

# %% [markdown]
# ## Celda 4 — Generar SLIDE 6 (cierre)

# %%
fig_cierre, ax = crear_cierre_carrusel(
    titulo="ESTAS 5 VAS A VER\nCADA SEMANA POR ACÁ.",
    subtitulo="xG, scouting, partidos, Mundial 2026.\nFootball analytics en español.",
    cta="¿Cuál te interesó más? \n 👉 Comentá cuál querés que te expliquemos",
    handle="@datafutbol_ar",
    sitio="datafutbolar.com",
    # logo_path=None,  # cuando tengas logo guardado, pasar la ruta acá
)
plt.show()

# %% [markdown]
# ## Celda 5 — Guardar cierre

# %%
cierre_path = OUTPUT_DIR / "2026-05-11_episodio2_slide6_cierre.png"
fig_cierre.savefig(
    cierre_path,
    dpi=200,
    facecolor=BG,
    bbox_inches="tight",
    pad_inches=0,
)
print(f"✓ Cierre guardado: {cierre_path}")
print(f"  Tamaño: {cierre_path.stat().st_size / 1024:.1f} KB")

# %% [markdown]
# ## ✅ Listo
#
# Ahora tenés las 6 PNGs del carrusel en `outputs/2026-05/`:
# - `slide1_portada.png` ← ESTE
# - `episodio2_shotmap_arg_fra.png`
# - `episodio2_radar_messi.png`
# - `episodio2_passnetwork_arg.png`
# - `episodio2_heatmap_messi.png`
# - `slide6_cierre.png` ← ESTE
#
# **Próximo paso:** subir las 6 a Instagram en orden, vía Meta Business Suite.
# **NO necesitás Canva** — las 6 PNGs ya están listas para publicar tal cual.
