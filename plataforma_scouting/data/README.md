# data/ — Datos (NO versionar los pesados)

- `raw/` — parquet crudo tal como sale de cada fuente (por loader).
- `processed/` — parquet limpio y normalizado al esquema, listo para la DB.

Los `.parquet` y `.duckdb` están en `.gitignore`. Se regeneran corriendo
`ingest/` + `db/build_db.py`. Solo se versiona la estructura (.gitkeep).
