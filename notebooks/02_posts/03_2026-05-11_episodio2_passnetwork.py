# %% [markdown]
# # Episodio 2 — Pass Network: Argentina 1er tiempo vs Francia
#
# **Post:** Episodio 2 — 5 visualizaciones que cuentan más que 1.000 stats
# **Esta visualización corresponde a la SLIDE 4 del carrusel.**
#
# ## Qué vamos a hacer
# 1. Cargar eventos del partido ARG vs FRA (ya cacheado)
# 2. Filtrar solo pases COMPLETADOS de Argentina hasta el 1er tiempo (hasta_minuto=45)
# 3. Calcular posición promedio de cada jugador + nodos de conexión
# 4. Generar pass network con la paleta Combo C
# 5. Guardar PNG

# %% [markdown]
# ## Celda 1 — Setup
#
# `autoreload` activo → cambios en `scripts/` se reflejan sin reiniciar kernel.

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

from scripts.style import set_default_style, BG
from scripts.data_loaders import sb_events
from scripts.pass_network import crear_pass_network

set_default_style()
print("Setup OK ✓  (autoreload activo)")

# %% [markdown]
# ## Celda 2 — Cargar eventos (caché ya generado)

# %%
events = sb_events(match_id=3869685)
print(f"Eventos totales del partido: {len(events)}")

# %% [markdown]
# ## Celda 3 — Inspeccionar pases de Argentina antes de plotear
#
# Verificamos cuántos pases hay en el 1er tiempo de Argentina y cuántos
# fueron completados (sin pass_outcome).

# %%
pases_arg = events[
    (events["type"] == "Pass")
    & (events["team"] == "Argentina")
    & (events["minute"] <= 45)
]

print(f"Pases totales de Argentina en 1er tiempo: {len(pases_arg)}")
print(f"Pases completados: {pases_arg['pass_outcome'].isna().sum()}")
print(f"Pases fallados: {pases_arg['pass_outcome'].notna().sum()}")
print(f"\nTipos de pase outcome:")
print(pases_arg["pass_outcome"].value_counts(dropna=False))

# %% [markdown]
# ## Celda 4 — Generar el pass network
#
# `hasta_minuto=45` → considera solo 1er tiempo (típico para pass network
# porque después de los cambios cambia la formación)
# `min_pases=3` → mostrar solo conexiones con 3 o más pases entre dos jugadores

# %%
fig, ax = crear_pass_network(
    events,
    equipo="Argentina",
    titulo="ARG · Pass Network",
    subtitulo="1er tiempo vs Francia · Final Mundial 2022",
    fuente="StatsBomb",
    hasta_minuto=45,
    min_pases=3,
)
plt.show()

# %% [markdown]
# ## Celda 5 — Guardar el PNG

# %%
OUTPUT_DIR = REPO_ROOT / "outputs" / "2026-05"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "2026-05-11_episodio2_passnetwork_arg.png"

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
# Lo siguiente: `04_*.py` — Radar de percentiles (Messi 14/15 vs delanteros top).

# %%
