# %% [markdown]
# # Episodio 2 — Shot Map: Argentina vs Francia, Final Mundial 2022
#
# **Post:** Episodio 2 — 5 visualizaciones que cuentan más que 1.000 stats
# **Draft:** `G:\Mi unidad\DATAFUTBOL_AR\04_Drafts\2026-05-11_episodio2_relanzamiento.md`
# **Esta visualización corresponde a la SLIDE 2 del carrusel.**
#
# ## Qué vamos a hacer
# 1. Cargar todos los eventos del partido ARG vs FRA, Mundial 2022 (final)
# 2. Filtrar solo los tiros (`type == "Shot"`) de Argentina
# 3. Generar un shot map con la paleta Combo C usando la función `crear_shot_map()` del repo
# 4. Guardar el PNG en `outputs/2026-05/`
#
# ## Cómo ejecutar este archivo
# - Cada bloque que empieza con `# %%` es una celda independiente
# - Para ejecutar una celda: clic dentro del bloque y `Shift + Enter`
# - VSCode te va a abrir una "Interactive Window" a la derecha con los outputs
# - La primera vez puede tardar unos segundos en arrancar el kernel

# %% [markdown]
# ## Celda 1 — Setup (imports + estilo)
#
# Importamos los scripts del repo y aplicamos el estilo Combo C por default a todos los plots.

# %%
import sys
from pathlib import Path

# Agregar la raíz del repo al PYTHONPATH (para poder importar `scripts.*`)
REPO_ROOT = Path(r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import matplotlib.pyplot as plt

from scripts.data_loaders import sb_events
from scripts.shot_map import crear_shot_map
from scripts.style import BG, COLORS, set_default_style

# Aplicar paleta Combo C a TODOS los plots de aquí en adelante
set_default_style()

print("Setup OK ✓")
print(f"Paleta cargada: {list(COLORS.keys())}")

# %% [markdown]
# ## Celda 2 — Cargar los eventos del partido
#
# Usamos `sb_events()` que es nuestro wrapper sobre `statsbombpy`. Cachea automáticamente
# en `data/raw/sb_events_3869685.parquet` para no descargar dos veces.
#
# **`match_id = 3869685`** corresponde a Argentina vs Francia, final del Mundial 2022.

# %%
events = sb_events(match_id=3869685)
print(f"Eventos totales del partido: {len(events)}")
print(f"\nColumnas disponibles: {list(events.columns)[:20]}...")

# %% [markdown]
# ## Celda 3 — Inspeccionar los tipos de evento
#
# Antes de filtrar, veamos qué tipos de evento hay en el partido para ubicarnos.

# %%
events["type"].value_counts().head(10)

# %% [markdown]
# ## Celda 4 — Filtrar SOLO los tiros de Argentina
#
# El tipo de evento que nos interesa es `"Shot"`. Filtramos también por equipo.

# %%
# Excluimos los penales del shootout (period >= 5 = tanda de penales).
# Estos tiros tienen coordenadas fijas (el penalty spot) y rompen el shot map.
shots_arg = events[
    (events["type"] == "Shot")
    & (events["team"] == "Argentina")
    & (events["period"] < 5)
].copy()

print(f"Tiros totales de Argentina en juego (excluye shootout): {len(shots_arg)}")
print(
    f"\nGoles en juego (excluye shootout): {(shots_arg['shot_outcome'] == 'Goal').sum()}"
)
print("\nJugadores que tiraron:")
print(shots_arg["player"].value_counts())

# Verificación: asegurarse de que no hay coordenadas faltantes
print("\n--- Verificación de coordenadas ---")
print(f"Tiros con `location` nulo: {shots_arg['location'].isna().sum()}")
print(f"Tipos de tiro en juego:\n{shots_arg['shot_type'].value_counts()}")

# %% [markdown]
# ## Celda 5 — Ver xG total y top 3 mejores tiros
#
# Inspección rápida de los xG para validar que los datos estén bien.

# %%
print(f"xG total Argentina: {shots_arg['shot_statsbomb_xg'].sum():.2f}")
print("\nTop 3 tiros con mayor xG:")
shots_arg.nlargest(3, "shot_statsbomb_xg")[
    ["minute", "player", "shot_statsbomb_xg", "shot_outcome"]
]

# %% [markdown]
# ## Celda 6 — Generar el shot map
#
# Llamamos a la función `crear_shot_map()` del repo. La función ya tiene la paleta
# Combo C aplicada y el watermark de @datafutbol_ar.
#
# Si querés ajustar algo (ej. mostrar nombres de jugadores), pasale `show_player_names=True`.

# %%
fig, ax = crear_shot_map(
    shots_arg,
    titulo="ARG 3-3 FRA · Mundial 2022",
    subtitulo="Final · todos los tiros de Argentina (sin penales)",
    show_player_names=False,
    fuente="StatsBomb",
)
plt.show()

# %% [markdown]
# ## Celda 7 — Guardar el PNG en outputs/2026-05/
#
# Lo guardamos con la convención de nombrado del proyecto:
# `YYYY-MM-DD_TITULO_FORMATO.png`

# %%
OUTPUT_DIR = REPO_ROOT / "outputs" / "2026-05"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

output_path = OUTPUT_DIR / "2026-05-11_episodio2_shotmap_arg_fra.png"

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
# El PNG ya está en `outputs/2026-05/2026-05-11_episodio2_shotmap_arg_fra.png`.
#
# **Próximos pasos:**
# - Abrirlo desde el explorer de VSCode para verificar que se ve bien.
# - Si te convence, pasamos al **heatmap** (siguiente notebook: `02_2026-05-11_episodio2_heatmap.py`).
# - Si querés modificar algo (ej. mostrar nombres, cambiar el subtítulo), volvés a la Celda 6 y ajustás.
#
# **Ideas de variantes que podés probar:**
# - Mostrar también los tiros de Francia (cambiar filtro en celda 4)
# - Cambiar a `crear_shot_map(... show_player_names=True)` para ver quién tiró cada uno
# - Probar con otro partido del Mundial: usar `sb_matches(43, 106)` para listar los disponibles

# %%
