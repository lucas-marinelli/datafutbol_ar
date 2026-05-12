# datafutbol_ar

Repo técnico de **[@datafutbol_ar](https://instagram.com/datafutbol_ar)** — football analytics en español con foco sudamericano.

> Notebooks, scripts y datos detrás de las visualizaciones que se publican en [Instagram](https://instagram.com/datafutbol_ar) y [X](https://twitter.com/datafutbol_ar).

---

## Stack

| Categoría | Herramientas |
|---|---|
| **Datos** | StatsBomb Open Data (`statsbombpy`), FBref + 6 fuentes (`soccerdata`), Liga Argentina (`LanusStats`), Capology + Understat + más (`ScraperFC`) |
| **Visualización** | `mplsoccer` (Pitch, VerticalPitch, PyPizza, Bumpy, Sonar), `matplotlib`, `seaborn` |
| **Análisis** | `pandas`, `numpy`, `pyarrow` (cache parquet) |
| **Notebooks** | JupyterLab |

Detalle exacto en [`requirements.txt`](./requirements.txt).

---

## Identidad visual — Combo C "Celeste & Blanco"

Toda visualización publicada usa esta paleta:

| Rol | Color | Hex |
|---|---|---|
| Fondo | Azul profundo | `#0E2A47` |
| Primario | Celeste | `#75AADB` |
| Acento | Dorado | `#C9A227` |
| Texto | Blanco | `#FFFFFF` |

Tipografías: **Oswald** (títulos), **Lato** (cuerpo), **Space Mono** (datos/tablas).

La paleta + helpers están en [`scripts/style.py`](./scripts/style.py). Cualquier visualización debería arrancar con:

```python
from scripts.style import set_default_style, apply_branding, watermark
set_default_style()
```

---

## Estructura del repo

```
datafutbol_ar/
├── notebooks/
│   ├── 00_aprendizaje_base/   ← notebooks de aprendizaje (10 viejos de mplsoccer)
│   ├── 01_exploracion/         ← análisis exploratorios
│   ├── 02_posts/               ← notebook por post publicado (1:1)
│   └── 03_scouting/            ← notebooks de informes scouting
├── scripts/
│   ├── style.py                ← paleta, fuentes, helpers de marca
│   ├── radar.py                ← crear_radar_comparativo() (mplsoccer.Radar polígono)
│   ├── shot_map.py             ← crear_shot_map()
│   ├── pass_network.py         ← crear_pass_network()
│   ├── heatmap.py              ← crear_heatmap()
│   ├── carrusel.py             ← portada + cierre de carrusel IG
│   ├── normalizar_carrusel.py  ← letterbox 1080×1350 para feed IG
│   ├── jugadores.py            ← nombres mostrables (display_name)
│   └── data_loaders.py         ← wrappers StatsBomb, FBref, LanusStats con cache
├── data/
│   ├── raw/                    ← datasets crudos descargados (cacheado, no subir)
│   ├── processed/              ← datasets procesados
│   └── external/               ← scrapes terceros
├── templates/
│   ├── canva/                  ← exportes de plantillas Canva
│   ├── matplotlib_styles/      ← .mplstyle de la marca
│   └── post_templates/         ← templates de captions, threads
├── outputs/                    ← PNG/PDF finales para publicar (organizados por mes)
│   ├── 2026-05/
│   ├── 2026-06/
│   └── ...
├── docs/                       ← documentación interna
├── .env.example                ← plantilla de variables de entorno
├── .gitignore
├── requirements.txt
├── LICENSE                     ← MIT
└── README.md
```

---

## Cómo arrancar (setup local)

```powershell
# 1. Activar el .venv compartido
D:\PROYECTOS_venv\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
cd D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar
pip install -r requirements.txt

# 3. Copiar template de .env
copy .env.example .env
# (editar .env con tus claves API si tenés)

# 4. Iniciar JupyterLab
jupyter lab
```

---

## Ejemplo rápido — Shot map del Mundial 2022

```python
from statsbombpy import sb
from scripts.shot_map import crear_shot_map
from scripts.style import set_default_style, COLORS

set_default_style()

# Argentina vs Arabia Saudita, debut Mundial 2022
# (descubrir match_id con sb.matches(competition_id=43, season_id=106))
events = sb.events(match_id=3869151)  # ajustar al ID correcto

shots_arg = events[
    (events["type"] == "Shot") &
    (events["team"] == "Argentina")
]

fig, ax = crear_shot_map(
    shots_arg,
    titulo="ARG 1-2 SAU · Mundial 2022",
    subtitulo="Debut · todos los tiros de Argentina",
    fuente="StatsBomb Open Data",
)

fig.savefig(
    "outputs/2026-05/shotmap_arg_sau_debut.png",
    dpi=200, facecolor=COLORS["bg"], bbox_inches="tight",
)
```

---

## Convenciones del repo

**Nombres de archivos:**
- Notebooks: `NN_titulo_descriptivo.ipynb` (NN = orden 01, 02, ...)
- Outputs: `YYYY-MM-DD_TITULO_FORMATO.png` (ej. `2026-05-12_messi_radar_carrusel.png`)
- Drafts de posts: en `G:\Mi unidad\DATAFUTBOL_AR\04_Drafts\` con formato `YYYY-MM-DD_titulo.md`

**Cada post publicado debería tener:**
1. Un notebook en `notebooks/02_posts/` que generó las visualizaciones
2. Los PNG finales en `outputs/YYYY-MM/`
3. El draft + caption en `04_Drafts/` del repo de marca (G:)

---

## Roadmap del repo

| Fase | Cuándo | Foco |
|---|---|---|
| **0 — Setup** | mayo 2026 | Estructura, scripts base, primer post (Episodio 2) |
| **1 — Mes 1** | 10 may - 9 jun 2026 | 8 notebooks de posts publicados (2/sem) |
| **2 — Mundial** | 11 jun - 19 jul 2026 | Plantillas pre-armadas para días críticos, ~30 notebooks de cobertura |
| **3 — Post-Mundial** | ago - oct 2026 | Notebooks de scouting comerciables (informes vendibles) |
| **4 — GitHub Pages** | nov 2026 | Portfolio público con galería de visualizaciones |

---

## Licencia

MIT — ver [`LICENSE`](./LICENSE).

Datos de StatsBomb Open Data sujetos a su propia licencia ([más info](https://github.com/statsbomb/open-data)).

---

## Otros enlaces

- [Instagram @datafutbol_ar](https://instagram.com/datafutbol_ar)
- [X @datafutbol_ar](https://twitter.com/datafutbol_ar)
- [Sitio web](https://datafutbolar.com)
- Contacto: `dfutbol.ar@gmail.com`

---

*Repo mantenido por Lucas Marinelli — Tolosa, La Plata, Argentina.*
