"""statsbomb_loader.py — Ingesta de StatsBomb Open Data.

Para event data de competiciones cubiertas (Mundiales 2018/2022, Copa América
2024, etc.). Útil para métricas avanzadas (xG por tiro, presiones, OBV-like).

⚠️ STUB — implementar en Fase 1/2. Hoy ya usamos statsbombpy en el repo
   (ver scripts/data_loaders.py). Este loader debe NORMALIZAR esos eventos al
   esquema de la plataforma (tablas fact_eventos) y cachear a parquet en data/raw/.
"""
from __future__ import annotations


def cargar_eventos_competicion(competition_id: int, season_id: int):
    """TODO: descargar eventos de todos los partidos y devolver DataFrame normalizado."""
    raise NotImplementedError("Pendiente Fase 2 — event data StatsBomb.")
