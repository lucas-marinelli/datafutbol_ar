# %% [markdown]
# # Episodio 2 — Heatmap: Messi en la final del Mundial 2022
#
# **Post:** Episodio 2 — 5 visualizaciones que cuentan más que 1.000 stats
# **Esta visualización corresponde a la SLIDE 5 del carrusel.**
#
# ## Qué vamos a hacer
# 1. Cargar todos los eventos del partido ARG vs FRA (ya está en caché por el shot map)
# 2. Filtrar solo los toques de Messi (cualquier tipo de evento donde participa con la pelota)
# 3. Generar un heatmap KDE sobre el campo vertical
# 4. Guardar el PNG en `outputs/2026-05/`

# %% [markdown]
# ## Celda 1 — Setup
#
# `%load_ext autoreload` + `%autoreload 2` → recarga automática de los módulos
# de `scripts/` cuando los editamos. Evita tener que reiniciar el kernel.

# %%
# Autoreload (debe ir antes de los imports de scripts.*)
# Si NO sos un kernel IPython/Jupyter, estas dos líneas se ignoran.
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
import pandas as pd

from scripts.style import set_default_style, BG
from scripts.data_loaders import sb_events
from scripts.heatmap import crear_heatmap

set_default_style()
print("Setup OK ✓  (autoreload activo)")

# %% [markdown]
# ## Celda 2 — Cargar los eventos (cacheados de la viz anterior)

# %%
events = sb_events(match_id=3869685)
print(f"Eventos totales del partido: {len(events)}")

# %% [markdown]
# ## Celda 3 — Filtrar SOLO los toques de Messi
#
# El nombre legal en StatsBomb es "Lionel Andrés Messi Cuccittini".
# Filtramos por todos los eventos del partido en los que él participó,
# y excluimos la tanda de penales (period >= 5).

# %%
MESSI = "Lionel Andrés Messi Cuccittini"

toques_messi = events[(events["player"] == MESSI) & (events["period"] < 5)].copy()

print(f"Toques de Messi en el partido (sin shootout): {len(toques_messi)}")
print(f"\nTipos de evento de Messi:")
print(toques_messi["type"].value_counts())

# %% [markdown]
# ## Celda 4 — Generar el heatmap
#
# Llamamos a `crear_heatmap()` con método KDE (densidad suave).
# `bandwidth` controla qué tan difusa queda la mancha. Valores:
# - 0.3-0.4 → mancha definida, picos puntuales
# - 0.5-0.7 → mancha más suave, transiciones graduales

# %%
fig, ax = crear_heatmap(
    toques_messi,
    titulo="MESSI · Final Mundial 2022",
    subtitulo="Mapa de toques · vs Francia · 120 minutos",
    fuente="StatsBomb",
    metodo="kde",
    bandwidth=0.5,
    jugador=MESSI,  # se pasa el nombre completo, display_name lo convierte a "Messi"
)
plt.show()

# %% [markdown]
# ## Celda 5 — Guardar el PNG

# %%
OUTPUT_DIR = REPO_ROOT / "outputs" / "2026-05"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "2026-05-11_episodio2_heatmap_messi.png"

fig.savefig(
    output_path,
    dpi=200,
    facecolor=BG,
    bbox_inches="tight",
)

print(f"✓ Guardado en: {output_path}")
print(f"  Tamaño del archivo: {output_path.stat().st_size / 1024:.1f} KB")

# %% [markdown]
# ## ✅ Listo
#
# El PNG está en `outputs/2026-05/2026-05-11_episodio2_heatmap_messi.png`.
#
# **Próximos:**
# - `03_*.py` — Pass network (Argentina 1er tiempo vs Francia)
# - `04_*.py` — Radar de percentiles (Messi 14/15 vs delanteros top)

# %%
