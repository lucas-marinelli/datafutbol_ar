"""build_db.py — Construye/actualiza la base DuckDB desde los parquet procesados.

Flujo:
    data/processed/jugadores_big5_*.parquet  ──>  db/futbol.duckdb

DuckDB lee parquet directo, así que la base es liviana: cargamos la tabla ancha
de jugadores y derivamos las dimensiones (club, jugador) + una vista de scouting.

Uso:
    python db/build_db.py
"""
from __future__ import annotations

from pathlib import Path

import duckdb

BASE = Path(__file__).resolve().parent
PROCESSED = BASE.parent / "data" / "processed"
DB_PATH = BASE / "futbol.duckdb"


def build(db_path: Path = DB_PATH, processed_dir: Path = PROCESSED) -> Path:
    """Arma futbol.duckdb: tabla jugadores + dims + vista de scouting."""
    parquets = sorted(processed_dir.glob("jugadores_big5_*.parquet"))
    if not parquets:
        raise FileNotFoundError(
            f"No hay parquet en {processed_dir}. Corré antes ingest/transformar.py."
        )

    glob_pat = str(processed_dir / "jugadores_big5_*.parquet").replace("\\", "/")
    con = duckdb.connect(str(db_path))

    # Tabla central: une todas las temporadas disponibles
    con.execute("DROP TABLE IF EXISTS fact_jugador_temporada;")
    con.execute(f"""
        CREATE TABLE fact_jugador_temporada AS
        SELECT * FROM read_parquet('{glob_pat}', union_by_name=true);
    """)

    # Dimensión club (distinct)
    con.execute("DROP TABLE IF EXISTS dim_club;")
    con.execute("""
        CREATE TABLE dim_club AS
        SELECT DISTINCT club_id, club AS nombre, competicion_id, competicion
        FROM fact_jugador_temporada;
    """)

    # Dimensión jugador (un registro por jugador)
    con.execute("DROP TABLE IF EXISTS dim_jugador;")
    con.execute("""
        CREATE TABLE dim_jugador AS
        SELECT jugador_id, any_value(nombre) AS nombre,
               any_value(nacionalidad) AS nacionalidad,
               any_value(pos_principal) AS pos_principal,
               any_value(pos_grupo) AS pos_grupo,
               max(edad) AS edad
        FROM fact_jugador_temporada
        GROUP BY jugador_id;
    """)

    # Vista cómoda para los dashboards
    con.execute("DROP VIEW IF EXISTS v_scouting;")
    con.execute("""
        CREATE VIEW v_scouting AS
        SELECT nombre, nacionalidad, pos_grupo, pos_principal, club, competicion,
               temporada, edad, minutos, partidos,
               goles, asistencias,
               goles_90, asistencias_90, tiros_90, tiros_arco_90,
               precision_tiro_pct, conversion,
               tackles_ganados_90, intercepciones_90, recuperaciones_90,
               duelos_aereos_pct,
               xg, xa, xg_90  -- NaN en Fase 1; se llenan con Understat en Fase 2
        FROM fact_jugador_temporada;
    """)

    n_jug = con.execute("SELECT count(*) FROM fact_jugador_temporada").fetchone()[0]
    n_clubs = con.execute("SELECT count(*) FROM dim_club").fetchone()[0]
    con.close()

    print(f"✅ Base lista: {db_path}")
    print(f"   fact_jugador_temporada: {n_jug} filas")
    print(f"   dim_club: {n_clubs} clubes")
    print("   tablas: fact_jugador_temporada, dim_club, dim_jugador · vista: v_scouting")
    return db_path


if __name__ == "__main__":
    build()
