# Diseño — Scraping de SofaScore (API JSON)

> Por qué importa: SofaScore resuelve TRES cosas que hoy nos faltan:
> 1. **Heatmaps de temporada** (mapa de calor por dónde se mueve el jugador) — lo que queríamos para el slide del destacado.
> 2. **Métricas defensivas/avanzadas + rating** que el wrapper de `soccerdata.FBref` 1.9 NO da (tackles, intercepciones, duelos, pases clave, rating).
> 3. **Cobertura sudamericana**: el sitio SofaScore SÍ tiene Argentina y Sudamérica → es un camino real para la Fase 3 (no como soccerdata, que solo trae Big-5).

> Estado: 🟡 DISEÑO + stub. Falta probar contra la API en la máquina de Lucas
> (SofaScore usa Cloudflare → puede requerir headers o un wrapper).

---

## 1. Cómo funciona SofaScore

Toda la data vive en su **API JSON** (la misma que usa la web). Se ve en la
pestaña *Network* del navegador. Se replica con `requests`. Base:

```
https://api.sofascore.com/api/v1/
```

Las coordenadas de los heatmaps vienen en escala **0–100 en x y 0–100 en y**
(igual que Opta) → en mplsoccer se plotean con `pitch_type='opta'`.

⚠️ **Cloudflare (CONFIRMADO en vivo 22/5/2026):** la API de SofaScore devuelve
**403** tanto con `requests` (headers de navegador) como con `cloudscraper`. La
que **SÍ entra es `ScraperFC.Sofascore`** (maneja la sesión por dentro).
→ **Usar ScraperFC, no la API directa.** Los endpoints de la sección 2 quedan
como referencia teórica de qué datos existen.

### Cómo se usa con ScraperFC (lo que FUNCIONA)
```python
import ScraperFC as sfc
ss = sfc.Sofascore()
ss.get_valid_seasons("Italy Serie A")                  # {temporada: id}
df  = ss.scrape_player_league_stats("24/25", "Italy Serie A", accumulation="per90")
bio = ss.scrape_player_details("24/25", "Italy Serie A")   # DOB, pos, altura, contrato
mid, desc = None, None                                  # match_id de un partido:
matches = ss.get_match_dicts("2022", "FIFA World Cup")  # buscar ARG-Arabia y tomar m['id']
hm = ss.scrape_heatmaps(mid)                            # {jugador:{'id','heatmap':[[x,y]]}}
```
Cubre 37 ligas, **incluida Argentina Liga Profesional y CONMEBOL Libertadores**
(= camino a Sudamérica, Fase 3). Loader: `ingest/sofascore_loader.py`.

---

## 2. Endpoints clave (flujo)

Para un jugador necesitamos su **id** de SofaScore (se ve en la URL del jugador:
`.../player/matias-moreno/1496360` → id `1496360`).

| Paso | Endpoint | Devuelve |
|---|---|---|
| **Buscar jugador** | `https://www.sofascore.com/api/v1/search/all?q={nombre}` | resultados; filtrar `type == "player"` → `id` |
| **Ficha** | `/player/{id}` | nombre, club, posición, pie, altura, fecha nac., valor de mercado |
| **Temporadas con stats** | `/player/{id}/statistics/seasons` | `uniqueTournaments` (utid) + `seasons` (sid) disponibles |
| **Stats de temporada** ⭐ | `/player/{id}/unique-tournament/{utid}/season/{sid}/statistics/overall` | rating, goles, asistencias, **tackles, intercepciones, duelos, pases clave, regates**, minutos, etc. |
| **Heatmap de temporada** ⭐ | `/player/{id}/unique-tournament/{utid}/season/{sid}/heatmap/overall` | `{"points": [{"x":.., "y":.., "count":..}, ...]}` |
| **Atributos (radar oficial)** | `/player/{id}/attribute-overviews` | el pentágono de SofaScore (ataque, técnica, táctica, defensa, creatividad) |
| Heatmap de UN partido | `/event/{eventId}/player/{id}/heatmap` | puntos x,y de ese partido |

`{utid}` = id del torneo (ej. LaLiga), `{sid}` = id de la temporada (ej. 25/26).
Ambos salen del endpoint "Temporadas con stats".

---

## 3. Cómo se renderiza el heatmap (mplsoccer)

Los `points` traen x, y (0–100) y `count` (intensidad). Dos formas:

**A. KDE (suave, estilo SofaScore)** — repetir cada punto por su `count`:
```python
import numpy as np
from mplsoccer import Pitch
xs = np.repeat([p["x"] for p in points], [p["count"] for p in points])
ys = np.repeat([p["y"] for p in points], [p["count"] for p in points])
pitch = Pitch(pitch_type='opta', line_color=COLORS["text"], pitch_color=COLORS["bg"])
fig, ax = pitch.draw()
pitch.kdeplot(xs, ys, ax=ax, fill=True, levels=100, cmap="custom_cmap", zorder=-1)
```

**B. Binned (grilla, más "dato")** — `pitch.bin_statistic` + `pitch.heatmap`:
```python
stat = pitch.bin_statistic(xs, ys, statistic='count', bins=(12, 8))
pitch.heatmap(stat, ax=ax, cmap="custom_cmap")
```

Usar un `LinearSegmentedColormap` Combo C (azul profundo → celeste → dorado) para
que el heatmap quede on-brand (ver `scripts/style.py`).

---

## 4. Qué métricas trae `statistics/overall` (las que nos faltaban)

Entre muchas: `rating`, `goals`, `assists`, `expectedGoals` (¡xG!), `expectedAssists`,
`totalShots`, `keyPasses`, `accuratePassesPercentage`, `tackles`, `interceptions`,
`totalDuelsWon`/`Percentage`, `aerialDuelsWon`, `dribbledPast`, `successfulDribbles`,
`minutesPlayed`, `appearances`. → cubre creación, definición, progresión y defensa.

> Ojo: SofaScore da totales de temporada; para per-90 dividir por `minutesPlayed/90`.

---

## 5. Cómo encaja en la plataforma

- **Fuente nueva** `ingest/sofascore_loader.py` → normaliza al esquema (igual que FBref) y suma columnas de rating + defensa + xG.
- **Heatmaps**: una función `heatmap_jugador(player, season)` reutilizable para el slide del destacado y para informes de scouting.
- **Sudamérica (Fase 3)**: como SofaScore cubre Argentina/Brasil/etc., este loader es el candidato #1 para romper el muro de data AR. Probar con un jugador de Liga Profesional antes de comprometerse.

### Riesgos / cuidados
- Cloudflare (manejar headers / wrapper).
- Rate-limit: cachear todo en `data/raw/sofascore/` (parquet/json). No re-pedir.
- Términos de uso: data para análisis/contenido propio con cita. Para producto pago, revisar.
- IDs: guardar el `sofascore_id` por jugador en una tabla de mapeo para no re-buscar.

---

## 6. Próximo paso concreto

1. Probar en una celda: `requests.get(player_url, headers=...)` para Nico Paz.
   Si 403 → `pip install cloudscraper` o `ScraperFC.Sofascore`.
2. Bajar su `statistics/overall` + `heatmap/overall` de Serie A 25/26.
3. Renderizar el heatmap con `pitch_type='opta'` y la paleta Combo C.
4. Si anda: implementar `sofascore_loader.py` y reemplazar el radar del post Sub-23
   por (o sumarle) el heatmap real.
