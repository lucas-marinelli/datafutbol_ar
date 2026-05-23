# -*- coding: utf-8 -*-
"""
helpers.py — Funciones de apoyo del Proyecto Final (Curso LanusStats).

Idea: que cada notebook de punto (punto_1 ... punto_6, extras) arranque con
    from helpers import *
y tenga listo: rutas, estilo de marca, carga cacheada de eventos y guardado de figuras.

Partido principal (P1-P5):  Argentina 1 - 2 Arabia Saudita (debut Mundial 2022)
Partido comparativo (bonus): Argentina 3 - 3 Francia (final, penales)
Competición Punto 6:        Mundial 2022 completo (comp 43, season 106)

Todo el scraping/StatsBomb corre en la maquina de Lucas (con internet).
La primera vez baja de la API y guardalo en data/*.parquet; despues lee del cache.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ── Rutas del proyecto ───────────────────────────────────────────────
# helpers.py vive en  .../datafutbol_ar/notebooks/04_Proyecto_Final_CursoLS/
PROJECT_DIR = Path(__file__).resolve().parent
# 04_Proyecto_Final_CursoLS -> notebooks -> datafutbol_ar  (parents[1] = repo root)
REPO_ROOT   = PROJECT_DIR.parents[1]          # .../datafutbol_ar
DATA_DIR    = PROJECT_DIR / "data"            # parquet cacheado (NO va a GitHub)
OUTPUTS_DIR = PROJECT_DIR / "outputs"         # PNGs finales (alta resolucion)

DATA_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Para poder importar scripts.style (la identidad visual @datafutbol_ar)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ── Constantes del torneo / partidos ─────────────────────────────────
COMP_ID   = 43       # FIFA World Cup
SEASON_ID = 106      # 2022 (Qatar)

MATCH_ARG_SAU = 3857300   # Argentina 1-2 Arabia Saudita (debut)  -> partido principal
MATCH_ARG_FRA = 3869685   # Argentina 3-3 Francia (final, penales) -> comparativo

# ── Estilo de marca (Combo C) ────────────────────────────────────────
# Se importa de scripts/style.py para no hardcodear paletas en cada notebook.
try:
    from scripts.style import COLORS, FONTS, set_default_style, watermark  # noqa: F401
    set_default_style()
except Exception as _e:  # por si se corre fuera del repo
    print(f"[helpers] aviso: no pude cargar scripts.style ({_e}). "
          "Sigo sin estilo de marca.")
    COLORS = {
        "bg": "#0E2A47", "primary": "#75AADB", "accent": "#C9A227",
        "text": "#FFFFFF", "muted": "#8FA7BC", "muted_light": "#3E5266",
    }
    FONTS = {}
    def watermark(ax, *a, **k):  # no-op de respaldo
        return None


# ── Carga de eventos con cache ───────────────────────────────────────
def cargar_eventos(match_id: int, nombre: str, refrescar: bool = False) -> pd.DataFrame:
    """Devuelve los eventos de UN partido, leyendo de cache si existe.

    Parameters
    ----------
    match_id : int   id StatsBomb del partido.
    nombre   : str   slug corto para el archivo, ej "arg_sau".
    refrescar: bool  si True, ignora el cache y vuelve a bajar de la API.

    Returns
    -------
    pd.DataFrame con los eventos (incluye columna 'match_id').
    """
    cache = DATA_DIR / f"eventos_{nombre}.parquet"
    if cache.exists() and not refrescar:
        df = pd.read_parquet(cache)
        print(f"[cache] {nombre}: {df.shape[0]} eventos leidos de {cache.name}")
        return df

    from statsbombpy import sb  # import local: solo se necesita al bajar
    print(f"[API] bajando eventos del partido {match_id} ({nombre})...")
    df = sb.events(match_id=match_id)
    df["match_id"] = match_id
    df.to_parquet(cache, index=False)
    print(f"[API] guardado en {cache.name}: {df.shape[0]} eventos, {df.shape[1]} columnas")
    return df


def cargar_eventos_mundial(refrescar: bool = False) -> pd.DataFrame:
    """Eventos de los 64 partidos del Mundial 2022 concatenados (Punto 6).

    Usa ciclo + pd.concat como pide la consigna y cachea el resultado
    (es pesado: ~3 min la primera vez, instantaneo despues).
    """
    cache = DATA_DIR / "eventos_mundial_2022.parquet"
    if cache.exists() and not refrescar:
        df = pd.read_parquet(cache)
        print(f"[cache] mundial: {df.shape[0]} eventos de {df['match_id'].nunique()} partidos")
        return df

    from statsbombpy import sb
    partidos = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID)
    ids = partidos["match_id"].tolist()
    print(f"[API] bajando {len(ids)} partidos del Mundial 2022 (paciencia)...")

    trozos = []
    for i, mid in enumerate(ids, 1):
        try:
            e = sb.events(match_id=mid)
            e["match_id"] = mid
            trozos.append(e)
            print(f"  {i:>2}/{len(ids)}  match {mid}  ({e.shape[0]} eventos)")
        except Exception as err:
            print(f"  ERROR en {mid}: {err}")
    df = pd.concat(trozos, ignore_index=True)
    df.to_parquet(cache, index=False)
    print(f"[API] mundial cacheado: {df.shape[0]} eventos totales en {cache.name}")
    return df


def lista_partidos(refrescar: bool = False) -> pd.DataFrame:
    """Tabla de los 64 partidos del Mundial (para buscar match_id por equipos)."""
    cache = DATA_DIR / "partidos_mundial_2022.parquet"
    if cache.exists() and not refrescar:
        return pd.read_parquet(cache)
    from statsbombpy import sb
    m = sb.matches(competition_id=COMP_ID, season_id=SEASON_ID)
    m.to_parquet(cache, index=False)
    return m


def match_id_por_equipos(equipo_a: str, equipo_b: str) -> int | None:
    """Busca el match_id de un cruce por nombre de equipo (case-insensitive parcial)."""
    m = lista_partidos()
    a, b = equipo_a.lower(), equipo_b.lower()
    mask = (
        m["home_team"].str.lower().str.contains(a) & m["away_team"].str.lower().str.contains(b)
    ) | (
        m["home_team"].str.lower().str.contains(b) & m["away_team"].str.lower().str.contains(a)
    )
    res = m[mask]
    if res.empty:
        print(f"No encontre {equipo_a} vs {equipo_b}")
        return None
    fila = res.iloc[0]
    print(f"{fila['home_team']} {fila['home_score']}-{fila['away_score']} "
          f"{fila['away_team']}  (match_id={fila['match_id']})")
    return int(fila["match_id"])


# ── Utilidades comunes a varios puntos ───────────────────────────────
def _coord(loc, i: int):
    """Devuelve loc[i] sea loc lista, tupla o np.ndarray; si no, NaN.

    Importante: al leer de parquet, la columna 'location' (que en StatsBomb es
    una lista [x, y]) vuelve como np.ndarray, no como list. Por eso aceptamos
    ambos tipos (si solo chequeáramos `list`, daría NaN en todo).
    """
    if isinstance(loc, (list, tuple, np.ndarray)) and len(loc) > i:
        return loc[i]
    return np.nan


def añadir_xy(ev: pd.DataFrame) -> pd.DataFrame:
    """Agrega columnas x, y (origen) a partir de la columna 'location'."""
    ev = ev.copy()
    ev["x"] = ev["location"].apply(lambda l: _coord(l, 0))
    ev["y"] = ev["location"].apply(lambda l: _coord(l, 1))
    return ev


def guardar_fig(fig, nombre: str, dpi: int = 200) -> Path:
    """Guarda una figura en outputs/ y devuelve la ruta."""
    ruta = OUTPUTS_DIR / (nombre if nombre.endswith(".png") else f"{nombre}.png")
    fig.savefig(ruta, dpi=dpi, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"[fig] guardada {ruta.name}")
    return ruta


__all__ = [
    "PROJECT_DIR", "REPO_ROOT", "DATA_DIR", "OUTPUTS_DIR",
    "COMP_ID", "SEASON_ID", "MATCH_ARG_SAU", "MATCH_ARG_FRA",
    "COLORS", "FONTS", "watermark",
    "cargar_eventos", "cargar_eventos_mundial", "lista_partidos",
    "match_id_por_equipos", "añadir_xy", "guardar_fig",
    "np", "pd",
]
