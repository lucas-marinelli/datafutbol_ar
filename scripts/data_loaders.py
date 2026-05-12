"""
data_loaders.py — Wrappers de fuentes de datos

Cada función devuelve un DataFrame de pandas listo para usar.
Cachea localmente en data/raw/ cuando es posible para no scrappear
de más.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd

from scripts.style import get_repo_root


def _cache_dir(subdir: str = "raw") -> Path:
    """Devuelve `data/{subdir}/` y lo crea si no existe."""
    p = get_repo_root() / "data" / subdir
    p.mkdir(parents=True, exist_ok=True)
    return p


# ──────────────────────────────────────────────────────────────────────
# StatsBomb Open Data — vía statsbombpy
# ──────────────────────────────────────────────────────────────────────

def sb_events(match_id: int, force_refresh: bool = False) -> pd.DataFrame:
    """Carga eventos de un partido de StatsBomb Open Data.

    Cachea en data/raw/sb_events_{match_id}.parquet.

    Args:
        match_id: ID del partido en StatsBomb.
        force_refresh: Si True, ignora el cache y vuelve a descargar.

    Returns:
        DataFrame de eventos.
    """
    cache_path = _cache_dir() / f"sb_events_{match_id}.parquet"
    if cache_path.exists() and not force_refresh:
        return pd.read_parquet(cache_path)

    from statsbombpy import sb
    df = sb.events(match_id=match_id)
    df.to_parquet(cache_path, index=False)
    return df


def sb_matches(competition_id: int, season_id: int, force_refresh: bool = False) -> pd.DataFrame:
    """Lista los partidos de una competencia/temporada.

    Cachea en data/raw/sb_matches_{competition_id}_{season_id}.parquet.
    """
    cache_path = _cache_dir() / f"sb_matches_{competition_id}_{season_id}.parquet"
    if cache_path.exists() and not force_refresh:
        return pd.read_parquet(cache_path)

    from statsbombpy import sb
    df = sb.matches(competition_id=competition_id, season_id=season_id)
    df.to_parquet(cache_path, index=False)
    return df


def sb_competitions() -> pd.DataFrame:
    """Lista todas las competencias disponibles en StatsBomb Open."""
    from statsbombpy import sb
    return sb.competitions()


# IDs útiles de StatsBomb Open Data
SB_IDS = {
    "mundial_2022": dict(competition_id=43, season_id=106),
    "mundial_2018": dict(competition_id=43, season_id=3),
    "copa_america_2024": dict(competition_id=223, season_id=282),  # verificar
    "messi_la_liga_2014_15": dict(competition_id=11, season_id=26),
    "euro_2024": dict(competition_id=55, season_id=282),  # verificar
}


# ──────────────────────────────────────────────────────────────────────
# FBref — vía soccerdata
# ──────────────────────────────────────────────────────────────────────

def fbref_player_season(
    league: str,
    season: str,
    stat_type: str = "standard",
) -> pd.DataFrame:
    """Stats por jugador de una liga/temporada vía soccerdata + FBref.

    Args:
        league: ej. "ENG-Premier League", "ARG-Liga Profesional".
        season: ej. "2025-2026".
        stat_type: "standard", "shooting", "passing", "defense", etc.

    Returns:
        DataFrame con stats de jugadores.

    Nota: la primera vez puede tardar (scraping). soccerdata cachea.
    """
    import soccerdata as sd
    fbref = sd.FBref(leagues=league, seasons=season)
    return fbref.read_player_season_stats(stat_type=stat_type)


# ──────────────────────────────────────────────────────────────────────
# LanusStats — fútbol argentino
# ──────────────────────────────────────────────────────────────────────

def lanus_match_data(match_id: str) -> pd.DataFrame:
    """Carga datos de un partido de Liga Profesional vía LanusStats.

    TODO: implementar wrapper específico una vez instalada la librería.
    """
    raise NotImplementedError(
        "LanusStats wrapper pendiente. Instalar con: pip install LanusStats"
    )


# ──────────────────────────────────────────────────────────────────────
# Helpers genéricos
# ──────────────────────────────────────────────────────────────────────

def guardar_processed(df: pd.DataFrame, nombre: str) -> Path:
    """Guarda un DataFrame procesado en data/processed/{nombre}.parquet"""
    p = _cache_dir("processed") / f"{nombre}.parquet"
    df.to_parquet(p, index=False)
    return p


def cargar_processed(nombre: str) -> pd.DataFrame:
    """Carga un DataFrame de data/processed/{nombre}.parquet"""
    p = _cache_dir("processed") / f"{nombre}.parquet"
    return pd.read_parquet(p)
