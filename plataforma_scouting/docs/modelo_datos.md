# Modelo de datos — Plataforma de Scouting

> Esquema en **estrella**: dimensiones (el "quién/qué") + hechos (el "cuánto").
> DDL en [`../db/schema.sql`](../db/schema.sql).

## Diagrama lógico

```
                    ┌───────────────────┐
                    │ dim_competicion   │
                    │ (liga, país, tier)│
                    └─────────┬─────────┘
                              │
                    ┌─────────┴─────────┐
                    │     dim_club      │
                    └─────────┬─────────┘
                              │
   ┌──────────────┐   ┌───────┴────────────────────┐   ┌──────────────┐
   │ dim_jugador  │───│  fact_jugador_temporada     │───│ dim_competicion
   │ (perfil bio) │   │  (1 fila x jugador-club-temp│   └──────────────┘
   └──────┬───────┘   │   con TODAS las métricas)   │
          │           └─────────────────────────────┘
          │           ┌─────────────────────────────┐
          └───────────│  fact_evento  (Fase 2)       │
                      │  (1 fila x acción, StatsBomb)│
                      └─────────────────────────────┘
```

## Las tablas

**Dimensiones** (cambian poco):
- `dim_competicion` — cada liga/torneo con su país, confederación y tier.
- `dim_club` — clubes, ligados a su competición.
- `dim_jugador` — ficha biográfica: nombre, nacimiento, nacionalidad(es)/pasaporte, pie, altura, posición principal y `pos_grupo` (ARQ/DEF/MED/DEL, clave para los percentiles).

**Hechos** (la masa de datos):
- `fact_jugador_temporada` — **la tabla central del scouting**. Una fila por jugador-club-temporada con todas las métricas por 90'. Es la que alimenta los dashboards y el Scoring Index.
- `fact_evento` — granularidad por acción (StatsBomb), para análisis avanzado y mapas. Llega en Fase 2.

## Por qué este diseño

- **Estrella** = consultas simples y rápidas para dashboards (joins directos dim→fact).
- **Tabla ancha por temporada** = el scouting trabaja a nivel jugador-temporada; tenerlo "denormalizado" en una fila evita joins pesados en cada filtro.
- **`pos_grupo` separado** = los percentiles y el Scoring Index siempre se calculan dentro del grupo de posición (comparar arqueros con arqueros).
- **IDs estables** = idealmente el `player_id` de FBref como clave para poder cruzar fuentes (Transfermarkt, StatsBomb) sin duplicar jugadores.

## Flujo de datos (ETL)

```
  ingest/*.py                 transformar              db/build_db.py
fuente web ──> data/raw/*.parquet ──> data/processed/*.parquet ──> futbol.duckdb
  (crudo, por fuente)        (limpio, normalizado al        (vistas + tablas
                              esquema de arriba)             materializadas)
```

Los `.parquet` y `futbol.duckdb` **no se versionan** (se regeneran). Solo viaja
el código + la estructura de carpetas.
