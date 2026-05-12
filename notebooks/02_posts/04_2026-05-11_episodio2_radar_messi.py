# %% [markdown]
# # Episodio 2 — Radar polígono: Messi vs Promedio top 5 ligas
#
# **Post:** Episodio 2 — 5 visualizaciones que cuentan más que 1.000 stats
# **Esta visualización corresponde a la SLIDE 3 del carrusel.**
#
# ## Qué cambió respecto a la versión PyPizza anterior
# - Cambiamos de **PyPizza** (rebanadas) a **mplsoccer.Radar** (polígono tipo FIFA)
# - Mostramos VALORES REALES (no percentiles abstractos): goles/90, asistencias/90, etc.
# - Dos polígonos superpuestos: **Messi (dorado)** + **Promedio del grupo (gris)**
# - La diferencia visual es obvia: el polígono dorado envuelve al gris
#
# ## Filosofía editorial aplicada (regla R10 + R11)
# - Audiencia: persona que NO sabe de stats. Lectura inmediata.
# - Gancho > explicación técnica. Si querés saber la metodología, está en el caption.

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

from scripts.style import set_default_style, BG
from scripts.radar import crear_radar_comparativo

set_default_style()
print("Setup OK ✓  (autoreload activo)")

# %% [markdown]
# ## Celda 2 — Datos: Messi 14/15 vs promedio top 5 ligas
#
# Valores por 90 minutos:
# - Messi 14/15 (43 goles + 18 asistencias en 38 partidos La Liga)
# - Promedio aproximado de delanteros con >900 min en top 5 ligas

# %%
# Las 6 métricas a comparar (con \n para que entren en 2 líneas si hace falta)
metricas = [
    "Goles",
    "Asistencias",
    "xG",
    "Tiros",
    "Pases\nprogresivos",
    "Carries\nprogresivos",
]

# Valores REALES por 90 min de Messi en La Liga 2014-15
valores_messi = [
    1.13,    # Goles: 43 / 38 partidos
    0.47,    # Asistencias: 18 / 38
    0.85,    # xG/90
    5.80,    # Tiros/90
    7.50,    # Pases progresivos/90
    5.20,    # Carries progresivos/90
]

# Valores APROXIMADOS del jugador promedio del grupo (delantero top 5 ligas)
valores_promedio = [
    0.40,    # Goles
    0.15,    # Asistencias
    0.35,    # xG
    2.50,    # Tiros
    5.50,    # Pases progresivos
    2.50,    # Carries progresivos
]

# Rangos del eje radial (min y max de cada métrica para que el polígono use bien el espacio)
min_range = [0.0] * len(metricas)
max_range = [1.5, 0.7, 1.2, 7.0, 10.0, 7.0]

print(f"Métricas a comparar: {len(metricas)}")
print(f"\nComparativa rápida (Messi vs Promedio):")
for m, v_m, v_p in zip(metricas, valores_messi, valores_promedio):
    diff = (v_m / v_p) if v_p > 0 else 0
    print(f"  {m.replace(chr(10), ' '):<25}  Messi={v_m:>5}   Prom={v_p:>5}   ({diff:.1f}× mejor)")

# %% [markdown]
# ## Celda 3 — Generar el radar polígono

# %%
fig, ax = crear_radar_comparativo(
    metricas=metricas,
    valores_jugador=valores_messi,
    valores_referencia=valores_promedio,
    min_range=min_range,
    max_range=max_range,
    nombre_jugador="Messi",
    nombre_referencia="Promedio top 5 ligas",
    titulo="MESSI · La Liga 2014-15",
    subtitulo="38 partidos · valores por 90 min",
    fuente="StatsBomb · FBref",
)
plt.show()

# %% [markdown]
# ## Celda 4 — Guardar PNG

# %%
OUTPUT_DIR = REPO_ROOT / "outputs" / "2026-05"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "2026-05-11_episodio2_radar_messi.png"

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
# El PNG está en `outputs/2026-05/2026-05-11_episodio2_radar_messi.png`.
#
# **Cómo se lee este radar** (lo que va al caption):
# 1. El **polígono dorado** = Messi en cada métrica.
# 2. El **polígono gris** = un delantero promedio del grupo.
# 3. Si el dorado "envuelve" al gris → Messi es mejor que el promedio en esa métrica.
# 4. La distancia entre los dos contornos = la magnitud de la diferencia.
#
# **Para usar esta plantilla con OTRO jugador** (futuro Mundial):
# 1. Cambiar `valores_jugador` con los datos del jugador nuevo.
# 2. Cambiar `valores_referencia` con los datos del comparable.
# 3. Cambiar `nombre_jugador`, `titulo`, `subtitulo`.
# 4. Si las métricas son las mismas, dejar `metricas`, `min_range`, `max_range` iguales.
# 5. Ejecutar las celdas 3 y 4. PNG listo en outputs.
