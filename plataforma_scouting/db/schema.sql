-- ════════════════════════════════════════════════════════════════════
-- schema.sql — Modelo de datos de la Plataforma (DuckDB)
-- Esquema en estrella: dimensiones + hechos. Ver docs/modelo_datos.md
-- ⚠️ BORRADOR Fase 1 — ajustar columnas a medida que entren las fuentes.
-- ════════════════════════════════════════════════════════════════════

-- ── DIMENSIONES ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_competicion (
    competicion_id   VARCHAR PRIMARY KEY,   -- ej. 'ENG-Premier League'
    nombre           VARCHAR,
    pais             VARCHAR,
    confederacion    VARCHAR,               -- UEFA / CONMEBOL
    tier             INTEGER,               -- 1 = primera división
    fuente           VARCHAR                -- 'fbref' | 'statsbomb' | ...
);

CREATE TABLE IF NOT EXISTS dim_club (
    club_id          VARCHAR PRIMARY KEY,
    nombre           VARCHAR,
    nombre_corto     VARCHAR,
    competicion_id   VARCHAR REFERENCES dim_competicion(competicion_id),
    pais             VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_jugador (
    jugador_id       VARCHAR PRIMARY KEY,   -- id estable (idealmente FBref)
    nombre           VARCHAR,
    nombre_mostrable VARCHAR,
    nacimiento       DATE,
    nacionalidad     VARCHAR,
    nacionalidad_2   VARCHAR,               -- doble nacionalidad / pasaporte
    pie              VARCHAR,
    altura_cm        INTEGER,
    pos_principal    VARCHAR,               -- ej. 'AM', 'CB'
    pos_grupo        VARCHAR                -- ARQ/DEF/MED/DEL (para percentiles)
);

-- ── HECHOS ──────────────────────────────────────────────────────────

-- Una fila por jugador-club-temporada (la tabla "ancha" del scouting).
-- Las métricas son por 90' salvo las marcadas _tot. Se completan por fase.
CREATE TABLE IF NOT EXISTS fact_jugador_temporada (
    jugador_id            VARCHAR REFERENCES dim_jugador(jugador_id),
    club_id               VARCHAR REFERENCES dim_club(club_id),
    competicion_id        VARCHAR REFERENCES dim_competicion(competicion_id),
    temporada             VARCHAR,          -- '2025-2026'
    edad                  INTEGER,
    valor_mercado_eur     BIGINT,           -- Transfermarkt (Fase 2)
    -- Tiempo de juego
    partidos              INTEGER,
    titular               INTEGER,
    minutos               INTEGER,
    -- Ataque
    goles                 DOUBLE,
    asistencias           DOUBLE,
    xg                    DOUBLE,
    xa                    DOUBLE,
    tiros_90              DOUBLE,
    xg_90                 DOUBLE,
    toques_area_90        DOUBLE,
    -- Creación / progresión
    pases_clave_90        DOUBLE,
    pases_progresivos_90  DOUBLE,
    carries_progresivos_90 DOUBLE,
    pct_pases             DOUBLE,
    -- Defensa
    tackles_90            DOUBLE,
    intercepciones_90     DOUBLE,
    recuperaciones_90     DOUBLE,
    duelos_aereos_pct     DOUBLE,
    -- Derivadas (motor propio)
    scoring_index         DOUBLE,           -- se calcula, no se ingesta
    PRIMARY KEY (jugador_id, club_id, temporada)
);

-- Eventos (StatsBomb) — Fase 2. Granularidad por acción.
CREATE TABLE IF NOT EXISTS fact_evento (
    evento_id        VARCHAR PRIMARY KEY,
    partido_id       VARCHAR,
    jugador_id       VARCHAR,
    club_id          VARCHAR,
    minuto           INTEGER,
    tipo             VARCHAR,               -- Pass / Shot / ...
    x                DOUBLE,
    y                DOUBLE,
    xg               DOUBLE
);

-- ── VISTAS de ayuda (ejemplos) ──────────────────────────────────────
-- DuckDB puede leer parquet directo; estas vistas materializan lo común.
-- CREATE VIEW v_scouting AS
--   SELECT j.nombre_mostrable, j.pos_grupo, c.nombre AS club, f.*
--   FROM fact_jugador_temporada f
--   JOIN dim_jugador j USING (jugador_id)
--   JOIN dim_club    c USING (club_id);
