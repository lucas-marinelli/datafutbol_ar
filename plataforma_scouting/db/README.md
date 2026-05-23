# db/ — Base de datos (DuckDB + Parquet)

- **`schema.sql`** — DDL del modelo (dimensiones + hechos). Ver `../docs/modelo_datos.md`.
- **`build_db.py`** — arma `futbol.duckdb` desde `../data/processed/*.parquet`.
- **`futbol.duckdb`** — la base (NO va a git; se reconstruye con `build_db.py`).

**Por qué DuckDB + Parquet:** cero servidores, SQL analítico rapidísimo,
portable (los parquet/duckdb viajan por Drive entre casa y la notebook).
Lee parquet directo: `SELECT * FROM 'data/processed/jugadores.parquet'`.
