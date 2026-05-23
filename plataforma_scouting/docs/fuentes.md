# Catálogo de fuentes de datos — Plataforma de Scouting

> Qué fuente sirve para qué, con sus límites reales. Antes de sumar una fuente
> nueva, leer también `memory/context/leccion_data_AR_may2026.md` (el muro de
> data del fútbol argentino) y `memory/context/tabla_librerias.md`.

## Resumen por fase

| Fase | Fuente | Librería | Cubre | Estado |
|---|---|---|---|---|
| **1** | FBref | `soccerdata.FBref` | **Big-5 europeas** (Premier, LaLiga, Serie A, Bundesliga, Ligue 1) | ✅ confiable |
| 1 | ClubElo | `soccerdata` / API | ratings de clubes | ✅ confiable |
| **2** | StatsBomb Open | `statsbombpy` | event data (Mundiales, Copa América 24, big-5 parcial) | ✅ confiable |
| 2 | Transfermarkt | `ScraperFC` | valor de mercado, edad, contrato | 🟡 scraping |
| 2 | Understat | `soccerdata` / `ScraperFC` | xG por tiro (big-5) | 🟡 |
| **3** | Promiedos / AFA / ESPN | scraping custom | **Argentina / Sudamérica** | 🔴 a construir |
| 3 | API-Football | api-sports.io (pago) | global, live | 💰 si hace falta |

## Detalle y caveats

### FBref (vía soccerdata) — el caballo de batalla de la Fase 1
- Datos de Opta: consistentes, con xG/xA y métricas avanzadas. Cobertura **solo Big-5** en soccerdata.
- soccerdata cachea local y devuelve DataFrames con columnas homogéneas.
- Liga eficiente: `"Big 5 European Leagues Combined"` (una tabla para las 5).
- Ojo: columnas **multinivel** (hay que aplanarlas — ver `ingest/fbref_loader.py`).
- Rate-limit: scrapea fbref.com, conviene cachear y no abusar.

### StatsBomb Open (statsbombpy) — Fase 2
- Event data gratis de calidad (incluye 360 en algunas competiciones).
- Cobertura por torneo, no "todas las ligas". Ideal para análisis profundo y mapas.
- Ya lo usamos en el repo (`scripts/data_loaders.py`).

### Transfermarkt (ScraperFC) — Fase 2
- Para el filtro "valor de mercado" estilo Capitán FI, edad y datos contractuales.
- Scraping → frágil; cachear y verificar.

### ⚠️ Fútbol argentino / sudamericano — Fase 3 (el muro)
- **soccerdata NO trae ligas sudamericanas** (confirmado 17/5/2026). No insistir.
- LanusStats.FotMob tiene Liga AR pero: sin temporada 2026, bug con Python 3.12,
  abre Chrome real. Sirve como proxy con season 2025.
- Camino real para AR live: scraping custom (Promiedos/ESPN) o API-Football (pago).
- **Decisión del proyecto:** Sudamérica entra en Fase 3, cuando el motor ya
  esté probado con Big-5. No frenar la Fase 1 esperando data AR.

## Principio de licencias / ética
- Datos para análisis y contenido propio. Citar fuente siempre (R26 reglas
  editoriales). Para un eventual producto pago, revisar términos de cada fuente.

---

## ⚠️ Actualización 22/5/2026 — soccerdata.FBref ahora usa navegador

Al probar la Fase 1 descubrimos que **`soccerdata >= 1.9` scrapea FBref con un
navegador headless** (seleniumbase / undetected-chromedriver), porque FBref
sumó protección Cloudflare. Implicancias:

- La primera corrida de `cargar_todo()` **abre Chrome** y tarda unos minutos.
  Después queda cacheado en parquet (instantáneo).
- Necesitás Chrome instalado (lo tenés). Si falla el webdriver:
  `pip install -U soccerdata seleniumbase`.
- Si Chrome diera demasiada guerra, alternativa: el paquete R **worldfootballR**
  (misma fuente FBref, sin browser) o exportar CSV a mano desde fbref.com.
- Esto NO afecta a `statsbombpy` (Fase 2), que sigue siendo descarga directa.

---

## ⚠️ Límite de `read_player_season_stats` (soccerdata 1.9)

A nivel **jugador-temporada**, soccerdata 1.9 SOLO expone 5 stat_types:
`standard`, `shooting`, `playing_time`, `keeper`, `misc`.
**NO** están `passing`, `defense`, `possession`, `goal_shot_creation`.

Qué SÍ tenemos (Fase 1): goles, asistencias, xG, xAG, tiros, progresión
(PrgC/PrgP) de *standard/shooting*; y de *misc*: intercepciones, tackles
ganados, recuperaciones, % duelos aéreos, faltas.

Qué NO (queda para Fase 2): **pases clave, % de pases, toques en área**.
Vías para traerlas: `read_player_match_stats` (por partido, agregando) o el
paquete R **worldfootballR** (tablas FBref completas).
