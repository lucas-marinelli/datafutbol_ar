"""percentiles.py — Percentiles por posición.

El bloque base del scouting: para cada métrica, en qué percentil cae un jugador
respecto a sus pares de la MISMA posición y liga/temporada comparable.

⚠️ STUB — implementar en Fase 1.
"""
from __future__ import annotations

import pandas as pd


def percentil_por_posicion(
    df: pd.DataFrame,
    metrica: str,
    col_posicion: str = "pos_grupo",
    col_minutos: str = "minutos",
    min_minutos: int = 600,
) -> pd.Series:
    """TODO: devolver el percentil (0-100) de `metrica` dentro de cada grupo de posición.

    Filtra por un mínimo de minutos para evitar ruido de muestras chicas.
    """
    raise NotImplementedError("Pendiente Fase 1 — percentiles por posición.")
