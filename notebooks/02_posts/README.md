# 02 — Posts publicados

Un notebook por cada post publicado. Genera las visualizaciones finales que van a `outputs/YYYY-MM/`.

Convención:
```
NN_AAAA-MM-DD_titulo_post.ipynb
```
Ejemplo: `01_2026-05-11_episodio2_5_visualizaciones.ipynb`

**Cada notebook debe:**
1. Cargar datos vía `scripts.data_loaders` (no usar APIs raw acá)
2. Aplicar branding vía `scripts.style.set_default_style()`
3. Usar las funciones de `scripts/{shot_map,radar,pass_network,heatmap}.py`
4. Guardar PNG finales en `outputs/YYYY-MM/`
5. Linkear al draft del post en `G:\Mi unidad\DATAFUTBOL_AR\04_Drafts\` (en el primer cell con un comentario)

**Plantilla mínima para arrancar un notebook nuevo:**

```python
# Post: <título del post>
# Draft: G:\Mi unidad\DATAFUTBOL_AR\04_Drafts\YYYY-MM-DD_titulo.md
# Publicado: <pendiente / fecha>

from pathlib import Path
import matplotlib.pyplot as plt

from scripts.style import set_default_style, BG, apply_branding, watermark
from scripts.data_loaders import sb_events
# from scripts.shot_map import crear_shot_map
# from scripts.radar import crear_radar_pizza

set_default_style()

OUTPUT_DIR = Path("outputs/2026-05")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ... tu análisis ...
```
