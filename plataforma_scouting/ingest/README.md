# ingest/ — Capa de ingesta (ETL)

Un loader por fuente. Cada loader:
1. Descarga datos crudos (soccerdata / statsbombpy / scrapers).
2. Los **normaliza** a nombres de columna y tipos del esquema (ver `../docs/modelo_datos.md`).
3. Cachea a `../data/raw/<fuente>/*.parquet` (NO va a git).

| Loader | Fuente | Estado |
|---|---|---|
| `fbref_loader.py` | FBref (Big-5) vía soccerdata | 🟡 stub funcional |
| `statsbomb_loader.py` | StatsBomb Open (event data) | ⏸️ Fase 2 |
| `transfermarkt_loader.py` | Valor de mercado (ScraperFC) | ⏸️ Fase 2 |
| `sudamerica_loader.py` | Promiedos/ESPN custom | ⏸️ Fase 3 |

**Regla de oro (ver bitácora `memory/context/leccion_data_AR_may2026.md`):**
soccerdata NO trae ligas sudamericanas. Para AR/Sudamérica hace falta scraping
custom — queda para fase posterior.
