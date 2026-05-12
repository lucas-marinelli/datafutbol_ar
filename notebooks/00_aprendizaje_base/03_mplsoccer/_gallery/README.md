# _gallery/ — Cookbook mplsoccer

> Galería oficial completa de **mplsoccer** descargada como referencia. NO son para estudiar en orden — son para **consultar cuando necesités hacer algo específico**.

Fuente original: https://mplsoccer.readthedocs.io/en/latest/gallery/

---

## Cómo usar esta carpeta

1. **Buscás cómo hacer algo** (ej. "voronoi", "heatmap posicional", "shot freeze frame").
2. **Buscás el script** en la subcarpeta correspondiente.
3. **Lo abrís, lo copiás**, lo adaptás a tu caso.

NO ejecutes secuencialmente — son independientes.

---

## Estructura

```
_gallery/
├── pitch_setup/          → Cómo crear y configurar canchas
├── pitch_plots/          → Plots SOBRE el campo (la mayoría de tus posts)
├── pizza_plots/          → PyPizza (radares tipo rebanada)
├── radar/                → Radar polígono (lo que usamos en Episodio 2)
├── bumpy_charts/         → Evolución de rankings semana a semana
├── sonars/               → Sonares de pase (dirección + frecuencia)
├── statsbomb/            → Cómo cargar datos StatsBomb Open
└── tutorials/            → Tutoriales más complejos (xT, wedges, etc.)
```

---

## pitch_setup/ (5 archivos)

| Script | Para qué |
|---|---|
| `plot_quick_start.py` | El "hola mundo" de mplsoccer. Empezá por acá si nunca usaste la lib. |
| `plot_pitches.py` | Dibujar canchas con distintos formatos. |
| `plot_pitch_types.py` | Comparar `Pitch` vs `VerticalPitch` vs `Pitch(half=True)`. |
| `plot_compare_pitches.py` | Cómo varias coordenadas según el proveedor (StatsBomb vs Wyscout vs Opta). |
| `plot_explain_standardizer.py` | Estandarizar coordenadas entre proveedores. |

**Cuándo lo usás:** la primera vez que arrancás un viz nuevo. Después casi nunca lo volvés a abrir.

---

## pitch_plots/ (25+ archivos) — **EL MÁS USADO**

Plots que van sobre el campo. La mayoría de tus posts van a usar algo de acá.

| Script | Para qué | Aplica a |
|---|---|---|
| `plot_scatter.py` | Puntos con tamaño/color custom | ⭐ Shot maps |
| `plot_heatmap.py` | Heatmap basico de bins | Mapas de calor |
| `plot_heatmap_positional.py` | Heatmap por zonas posicionales | Análisis territorial |
| `plot_kde.py` | KDE (densidad suave) | ⭐ Heatmap que ya usamos |
| `plot_hexbin.py` | Hexbins (paneles hexagonales) | Alternativa al heatmap |
| `plot_arrows.py` | Flechas para pases/movimientos | Análisis de pase |
| `plot_lines.py` | Líneas (también pases) | Análisis pase |
| `plot_pass_network.py` | ⭐ Pass network (red de pases) | YA USAMOS |
| `plot_flow.py` | Flow map (densidad direccional) | Innovador |
| `plot_voronoi.py` | Voronoi (espacios controlados) | Análisis táctico avanzado |
| `plot_delaunay.py` | Triangulación Delaunay | Análisis defensivo |
| `plot_convex_hull.py` | Convex hull (área ocupada por un equipo) | Posicionamiento equipo |
| `plot_formations.py` | Visualizar formaciones tácticas | Análisis táctico |
| `plot_animation.py` | Animaciones (frame por frame) | Videos cortos para Reels |
| `plot_grid.py` | Grid de múltiples plots | Comparativas |
| `plot_jointgrid.py` | Plot principal + marginales | Análisis estadístico |
| `plot_markers.py` | Marcadores custom (escudos, fotos) | Branding |
| `plot_shot_freeze_frame.py` | Frame de un tiro con todos los jugadores | Análisis muy técnico |
| `plot_sb360_frame.py` | StatsBomb 360 — todos los jugadores en el momento | Pro analytics |
| `plot_cmap.py` | Colormaps custom | Estilo visual |
| `plot_cyberpunk.py` | Estilo cyberpunk | Inspiración estética |
| `plot_textured_background.py` | Fondos con textura | Estilo visual |
| `plot_photo.py` | Foto de fondo | Headers |
| `plot_twitter_powerpoint.py` | Plot adaptado a X y PPT | Multiformato |
| `plot_standardize.py` | Estandarizar a un pitch común | Cross-proveedor |

---

## pizza_plots/ (7 archivos)

Radares tipo "rebanada de pizza" (lo que tenías en la primera versión del radar antes de migrar a polígono).

| Script | Para qué |
|---|---|
| `plot_pizza_basic.py` | El básico |
| `plot_pizza_colorful.py` | Con colores variados por categoría |
| `plot_pizza_dark_theme.py` | Estilo dark (parecido a Combo C) |
| `plot_pizza_comparison.py` | Comparar 2 jugadores (lo que necesitábamos) |
| `plot_pizza_comparison_vary_scales.py` | Comparación con escalas variables |
| `plot_pizza_different_units.py` | Métricas en distintas unidades |
| `plot_pizza_scales_vary.py` | Escalas distintas por métrica |

**Estado:** ya migraste a `Radar` polígono. Estos quedan como referencia si en el futuro querés volver al estilo pizza para un post específico.

---

## radar/ (2 archivos)

Radar polígono (lo que usás actualmente).

| Script | Para qué |
|---|---|
| `plot_radar.py` | ⭐ Tu base — el ejemplo oficial que adaptamos en `scripts/radar.py` |
| `plot_turbine.py` | Variante con "turbinas" — radar con efecto giratorio |

---

## bumpy_charts/ (1 archivo)

| Script | Para qué |
|---|---|
| `plot_bumpy.py` | Evolución de posiciones a lo largo del tiempo (ej. tabla de liga semana a semana) |

**Idea de post:** "Cómo evolucionó la tabla de Liga Profesional semana a semana".

---

## sonars/ (3 archivos)

Sonares — combinan dirección + frecuencia de pases por zona.

| Script | Para qué |
|---|---|
| `plot_sonar.py` | Sonar básico |
| `plot_sonar_grid.py` | Grid de sonares por jugador |
| `plot_bin_statistic_sonar.py` | Sonar combinado con bin statistics |

**Idea de post:** "El sonar de pases de Messi vs el de Rodri". Innovador en español.

---

## statsbomb/ (1 archivo)

| Script | Para qué |
|---|---|
| `plot_statsbomb_data.py` | Tutorial canónico de cargar datos StatsBomb |

---

## tutorials/ (4 archivos) — **AVANZADOS**

| Script | Para qué |
|---|---|
| `plot_xt.py` | ⭐⭐⭐ **Expected Threat (xT)** — modelo Markov chain. Avanzado pero clave para scouting. |
| `plot_xt_improvements.py` | Mejoras al xT base |
| `plot_pass_sonar_kde.py` | Sonar + KDE combinados (post viral potencial) |
| `plot_wedges.py` | Wedges (cuñas) — visualización específica |

**xT es la próxima frontera técnica de tu marca.** Es lo que usan los pros (Karun Singh popularizó la métrica). Si dominás esto, sos diferencial.

---

## Cómo encontrar lo que buscás (cheat sheet)

| Si necesitás… | Andá a |
|---|---|
| Empezar de cero | `pitch_setup/plot_quick_start.py` |
| Hacer un shot map | `pitch_plots/plot_scatter.py` |
| Mostrar un heatmap | `pitch_plots/plot_kde.py` |
| Visualizar pases | `pitch_plots/plot_arrows.py` o `plot_lines.py` |
| Pass network | `pitch_plots/plot_pass_network.py` |
| Comparar 2 jugadores radar | `radar/plot_radar.py` o `pizza_plots/plot_pizza_comparison.py` |
| Evolución temporal | `bumpy_charts/plot_bumpy.py` |
| Análisis táctico avanzado | `pitch_plots/plot_voronoi.py` o `plot_convex_hull.py` |
| Animación para Reel | `pitch_plots/plot_animation.py` |
| Métricas pro (xT) | `tutorials/plot_xt.py` |

---

## Lo MÁS valioso del cookbook (top 5 a estudiar este mes)

1. **`tutorials/plot_xt.py`** — Expected Threat. Diferencial técnico fuerte.
2. **`pitch_plots/plot_voronoi.py`** — Análisis táctico avanzado, casi nadie lo hace en español.
3. **`pitch_plots/plot_animation.py`** — Animaciones para Reels durante el Mundial.
4. **`pitch_plots/plot_shot_freeze_frame.py`** — Análisis post-gol "frame por frame".
5. **`sonars/plot_pass_sonar_kde.py`** — Combinación innovadora.

---

*Cookbook organizado el 12 may 2026. Actualizar cuando agregues nuevos scripts.*
