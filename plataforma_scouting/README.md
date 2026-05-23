# Plataforma de Datos & Scouting — @datafutbol_ar

> Módulo del repo `datafutbol_ar`. Base de datos de jugadores/clubes/partidos +
> dashboards de consulta + motor de métricas propias y **Scoring Index**.
> Inspirado en el enfoque "Capitán FI" (XI ideal por índice de rendimiento).
>
> 📋 **Plan maestro:** `G:\Mi unidad\DATAFUTBOL_AR\00_Plan\plan_plataforma_scouting.md`
> *(codename provisional: "Plataforma de Scouting" — renombrable)*

## Qué es

Tres cosas, en orden de prioridad:
1. **Producto de scouting** — buscar jugadores por perfil, con percentiles y un índice compuesto, exportable a informe.
2. **Motor de contenido** — alimentar los posts de @datafutbol_ar (rankings, radares, comparativas) más rápido y consistente.
3. **Portfolio técnico** — demostrar ETL + SQL + dashboards + modelos.

## Decisiones de arquitectura (confirmadas 22/5/2026)

| Decisión | Valor | Por qué |
|---|---|---|
| Alcance fase 1 | **Big-5 europeas** | Data confiable vía FBref/soccerdata. Sudamérica = Fase 3. |
| Base de datos | **Parquet + DuckDB** | Cero servidores, SQL analítico veloz, portable casa↔notebook. |
| Dashboards | **Streamlit** | Ya está en el stack; deploy gratis con URL pública. |
| Ubicación | subcarpeta de `datafutbol_ar` | Comparte venv, `scripts/style.py` y marca. |

## Estructura

```
plataforma_scouting/
├── ingest/      ETL: un loader por fuente → data/raw/*.parquet
├── data/        raw/ y processed/ (parquet — NO van a git)
├── db/          schema.sql + build_db.py → futbol.duckdb
├── metrics/     percentiles, scoring_index, métricas propias
├── dashboards/  apps Streamlit (scouting / rendimiento / informativo)
├── notebooks/   exploración y prototipado
└── docs/        modelo_datos.md · fuentes.md · diccionario_datos.md
```

## Flujo

```
fuente web → ingest → data/raw → (transformar) → data/processed → db/build_db → futbol.duckdb → dashboards
```

## Estado actual

🟢 **Fase 1 — código listo y validado offline (22/5/2026).** El pipeline
`ingest → transformar → DuckDB → consulta` está implementado y probado de punta
a punta con datos sintéticos. Falta correr el **pull real de FBref** en tu
máquina (abre Chrome la 1ra vez — ver `docs/fuentes.md`).

➡️ **Para correrlo:** abrí `notebooks/01_fase1_smoke.py` en VSCode y ejecutá las
celdas de arriba a abajo.

Pendiente: Fase 2 (Transfermarkt + percentiles), Fase 3 (Scoring Index + dashboard).

## Cómo se corre

```bash
# Opción notebook (recomendada): notebooks/01_fase1_smoke.py celda por celda.
# Opción scripts:
python ingest/transformar.py     # ingesta FBref + normaliza (abre Chrome 1ra vez)
python db/build_db.py            # arma futbol.duckdb
# (Fase 3) streamlit run dashboards/app_scouting.py
```
