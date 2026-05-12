# 00 — Aprendizaje base

Notebooks de aprendizaje y referencia. Organizados por **tema** y por **orden sugerido de estudio**.

> Esta carpeta NO es para producir contenido publicable — eso va en `02_posts/`. Acá practicás, experimentás y dejás constancia de lo aprendido.

---

## Estructura

```
00_aprendizaje_base/
├── 01_python_pandas/          ← Python + pandas — la base de todo
│   ├── 01_introduccion.ipynb
│   ├── 02_seleccion_filtrado.ipynb
│   ├── 03_manipulacion.ipynb
│   ├── 04_agrupacion.ipynb
│   ├── 05_visualizacion_basica.ipynb
│   └── 06_joins.ipynb
│
├── 02_matplotlib/             ← Visualización general (matplotlib puro)
│   └── 01_introduccion.ipynb
│
├── 03_mplsoccer/              ← Visualización aplicada a fútbol
│   ├── 01_introduccion.ipynb
│   ├── 02_pitches.ipynb       (dibujar canchas)
│   ├── 03_tipos_de_pitch.ipynb
│   └── 04_dashboards.ipynb
│
├── 04_statsbomb/              ← Cargar y explorar datos StatsBomb
│   ├── 01_carga_eventos.ipynb
│   └── 02_explorar_partidos.ipynb
│
├── 05_visualizaciones_futbol/ ← Las viz que después usamos en posts
│   ├── 01_mapas_tiros.ipynb
│   ├── 02_mapas_calor.ipynb
│   ├── 03_pass_network.ipynb
│   ├── 04_radar.ipynb
│   └── 05_filtrado_pases.ipynb
│
├── 06_scraping/               ← Técnicas avanzadas de obtención de datos
│   ├── 01_scraping_basico.ipynb
│   └── 02_joins_dataframes.ipynb
│
└── _archive/duplicados/       ← Versiones viejas o duplicadas (a revisar después)
```

---

## Orden sugerido de estudio

Si arrancás desde cero y querés ir aprendiendo:

1. **`01_python_pandas/`** completo → la base. Sin manejar pandas, lo demás es muy difícil.
2. **`02_matplotlib/`** → entender qué es una figura, ejes, plots básicos.
3. **`03_mplsoccer/`** → librería específica para fútbol. Dibujar canchas.
4. **`04_statsbomb/`** → cómo cargar datos de partidos reales.
5. **`05_visualizaciones_futbol/`** → las viz finales que usaremos en posts.
6. **`06_scraping/`** → opcional, para cuando quieras obtener datos de fuentes que no tienen API.

---

## Convención de nombrado

| Regla | Ejemplo |
|---|---|
| **Carpetas:** `NN_tema/` con prefijo numérico 2 dígitos | `03_mplsoccer/` |
| **Notebooks:** `NN_descripcion_corta.ipynb` | `02_pitches.ipynb` |
| **Sin acentos, sin espacios, snake_case** | `pass_network.ipynb` ✓ — `Pass Network.ipynb` ✗ |
| **Numeración con cero adelante** (para ordenamiento alfabético) | `01_`, `02_`, ..., `10_` |

---

## Cómo agregar un notebook nuevo

1. Decidir a qué tema pertenece (¿es de pandas? ¿de mplsoccer? ¿de scraping?). Si no encaja en ninguno, considerá crear nueva carpeta `NN_tema_nuevo/`.
2. Mirar el último número usado dentro de esa carpeta (ej. si hay hasta `04_dashboards.ipynb`, el nuevo va `05_`).
3. Crear el notebook con nombre `NN_descripcion_corta.ipynb`.
4. Si después de un tiempo el contenido se queda obsoleto o lo reemplazás por uno mejor, mover el viejo a `_archive/` con el formato `nombre__YYYY-MM-DD__motivo.ipynb`.

---

## Pendientes

- ☐ Revisar contenido de `_archive/duplicados/` y borrar definitivamente los que sean duplicados peores (sin valor único).
- ☐ Sumar notas/aprendizaje al inicio de cada notebook explicando qué se cubre.

---

*Reorganizado el 12 may 2026. Versión inicial: 26 notebooks mezclados, ahora en 6 categorías.*
