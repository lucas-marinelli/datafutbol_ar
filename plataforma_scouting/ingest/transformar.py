"""transformar.py — Normaliza la tabla ancha de FBref al esquema de la plataforma.

Entrada: tabla ancha aplanada de `fbref_loader.cargar_todo()`.
Salida:  data/processed/jugadores_big5_<season>.parquet con las columnas del
         esquema (ver ../docs/modelo_datos.md y ../db/schema.sql).

Diseño defensivo: los nombres EXACTOS de columnas de FBref cambian entre
versiones de soccerdata, así que buscamos cada métrica por candidatos de nombre
(`_find`) en vez de hardcodear. Si una métrica no aparece, queda NaN + warning.
Métricas "por 90" que no vienen directas se calculan: valor / (minutos / 90).
"""
from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

MIN_MINUTOS_DEFECTO = 0  # el filtro de minutos se aplica después, en scouting


def _slug(texto: str) -> str:
    """'Ángel Di María' -> 'angel_di_maria' (para IDs estables sin tildes)."""
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "_", t).strip("_").lower()
    return t or "na"


def _find(df: pd.DataFrame, *cands: str) -> str | None:
    """Devuelve la 1ra columna que matchea TODOS los términos de algún candidato.

    Cada candidato es un string con términos separados por '|' que deben estar
    todos en el nombre de columna (case-insensitive). Se prueban en orden.
    Ej.: _find(df, "playing|min", "min") prueba primero "playing"+"min".
    """
    cols = list(df.columns)
    for cand in cands:
        terms = [t.lower() for t in cand.split("|")]
        for c in cols:
            cl = str(c).lower()
            if all(t in cl for t in terms):
                return c
    return None


def _num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


# Mapeo de la posición FBref (GK/DF/MF/FW) al grupo del scouting
_POS_GRUPO = {"GK": "ARQ", "DF": "DEF", "MF": "MED", "FW": "DEL"}


def _pos_grupo(pos: str) -> str:
    if not isinstance(pos, str) or not pos:
        return "NA"
    primera = re.split(r"[,/ ]", pos.strip())[0].upper()
    return _POS_GRUPO.get(primera, "NA")


def transformar(df_ancha: pd.DataFrame, season: str = "2025-2026",
                anio_ref: int = 2026) -> pd.DataFrame:
    """Normaliza la tabla ancha FBref → DataFrame con el esquema de la plataforma."""
    d = df_ancha.copy()

    c_player = _find(d, "player")
    c_nation = _find(d, "nation")
    c_pos    = _find(d, "pos")
    c_team   = _find(d, "team", "squad")
    c_league = _find(d, "league", "comp")
    c_born   = _find(d, "born")
    c_age    = _find(d, "age")

    # Tiempo de juego
    c_min    = _find(d, "playing|min", "min")
    c_mp     = _find(d, "playing|mp", "matches played", "|mp")
    c_starts = _find(d, "playing|starts", "starts")

    # Totales de ataque / creación
    c_gls    = _find(d, "performance|gls", "|gls", "goals")
    c_ast    = _find(d, "performance|ast", "|ast")
    c_xg     = _find(d, "expected|npxg+", "expected|xg", "|xg")
    c_xa     = _find(d, "expected|xag", "|xag", "|xa")
    # Per-90 que FBref ya entrega directo (preferimos estos sobre calcularlos)
    c_gls90d = _find(d, "per 90|gls", "90 minutes|gls")
    c_ast90d = _find(d, "per 90|ast", "90 minutes|ast")
    # Tiro (de 'shooting')
    c_sh     = _find(d, "standard|sh", "|sh")          # tiros totales
    c_sh90d  = _find(d, "standard|sh/90", "|sh/90")    # tiros/90 directo
    c_sot    = _find(d, "standard|sot", "|sot")        # tiros al arco
    c_sot90d = _find(d, "|sot/90")                     # tiros al arco/90 directo
    c_sotpct = _find(d, "|sot%")                       # % al arco
    c_gsh    = _find(d, "|g/sh")                       # goles por tiro (conversión)
    # Progresión / xG: NO vienen en soccerdata 1.9 → NaN (Understat en Fase 2)
    c_prgp   = _find(d, "progression|prgp", "|prgp")
    c_prgc   = _find(d, "progression|prgc", "carries|prgc", "|prgc")
    # De 'misc' (defensa) — aparecen cuando se baja el stat_type 'misc':
    c_tklw   = _find(d, "|tklw", "tackles won")        # tackles ganados
    c_int    = _find(d, "performance|int", "|int", "interception")  # intercepciones
    c_recov  = _find(d, "|recov", "recoveries")        # recuperaciones
    c_aerial = _find(d, "aerial|won%", "won%")         # % duelos aéreos

    out = pd.DataFrame()
    out["nombre"] = d[c_player].astype(str) if c_player else "NA"
    out["nacionalidad"] = (
        d[c_nation].astype(str).str.extract(r"([A-Z]{3})", expand=False)
        if c_nation else np.nan
    )
    out["pos_principal"] = d[c_pos].astype(str) if c_pos else "NA"
    out["pos_grupo"] = out["pos_principal"].apply(_pos_grupo)
    out["club"] = d[c_team].astype(str) if c_team else "NA"
    out["competicion"] = d[c_league].astype(str) if c_league else "NA"
    out["temporada"] = season

    # Edad: por año de nacimiento si está; sino parsear 'age' ("23-145" -> 23)
    if c_born:
        born = _num(d[c_born])
        out["edad"] = (anio_ref - born).astype("Int64")
        out["_born"] = born.astype("Int64")
    elif c_age:
        out["edad"] = _num(d[c_age].astype(str).str.split("-").str[0]).astype("Int64")
        out["_born"] = (anio_ref - out["edad"]).astype("Int64")
    else:
        out["edad"] = pd.NA
        out["_born"] = pd.NA

    # Tiempo de juego
    out["minutos"] = _num(d[c_min]).fillna(0).astype(int) if c_min else 0
    out["partidos"] = _num(d[c_mp]).fillna(0).astype(int) if c_mp else 0
    out["titular"] = _num(d[c_starts]).fillna(0).astype(int) if c_starts else 0

    noventas = (out["minutos"] / 90).replace(0, np.nan)

    def por90(col):
        if not col:
            return np.nan
        return (_num(d[col]) / noventas).round(3)

    # Totales (los dejamos también, útiles para captions/rankings absolutos)
    out["goles"] = _num(d[c_gls]).fillna(0) if c_gls else 0
    out["asistencias"] = _num(d[c_ast]).fillna(0) if c_ast else 0
    out["xg"] = _num(d[c_xg]) if c_xg else np.nan
    out["xa"] = _num(d[c_xa]) if c_xa else np.nan

    # Helper: usar la columna per-90 directa de FBref si existe; sino calcular
    def val90(c_directo, c_total):
        if c_directo:
            return _num(d[c_directo]).round(3)
        return por90(c_total)

    # Output / tiro (lo que FBref SÍ entrega)
    out["goles_90"] = val90(c_gls90d, c_gls)
    out["asistencias_90"] = val90(c_ast90d, c_ast)
    out["tiros_90"] = val90(c_sh90d, c_sh)
    out["tiros_arco_90"] = val90(c_sot90d, c_sot)
    out["precision_tiro_pct"] = _num(d[c_sotpct]) if c_sotpct else np.nan
    out["conversion"] = _num(d[c_gsh]) if c_gsh else np.nan
    # Defensa (de 'misc'; NaN si todavía no se bajó ese stat_type)
    out["tackles_ganados_90"] = por90(c_tklw)
    out["intercepciones_90"] = por90(c_int)
    out["recuperaciones_90"] = por90(c_recov)
    out["duelos_aereos_pct"] = _num(d[c_aerial]) if c_aerial else np.nan
    # Avanzadas NO disponibles en FBref de soccerdata 1.9 → NaN (Understat, Fase 2)
    out["xg_90"] = por90(c_xg)
    out["pases_progresivos_90"] = por90(c_prgp)
    out["carries_progresivos_90"] = por90(c_prgc)

    # IDs estables
    out["jugador_id"] = (out["nombre"].apply(_slug) + "__" +
                         out["_born"].astype(str).str.replace("<NA>", "na", regex=False))
    out["club_id"] = out["club"].apply(_slug)
    out["competicion_id"] = out["competicion"].apply(_slug)

    out = out.drop(columns=["_born"])

    # Diagnóstico: estas las esperamos de standard/shooting/misc.
    faltantes = [name for name, col in {
        "minutos": c_min, "goles": c_gls, "tiros": c_sh, "conversion": c_gsh,
        "tackles_ganados": c_tklw, "intercepciones": c_int,
        "recuperaciones": c_recov, "duelos_aereos%": c_aerial,
    }.items() if col is None]
    if faltantes:
        print(f"⚠️ Columnas esperadas no encontradas (quedan NaN): {faltantes}")
        print("   Si faltan las de defensa (tackles/int/recov), re-corré la ingesta")
        print("   con refrescar=True para bajar el stat_type 'misc'.")
    # xG/xAG/progresión NO vienen en FBref de soccerdata 1.9 (es esperado) → Fase 2 (Understat).

    return out


def guardar(out: pd.DataFrame, season: str = "2025-2026") -> Path:
    dst = PROCESSED_DIR / f"jugadores_big5_{season}.parquet"
    out.to_parquet(dst, index=False)
    print(f"✅ {len(out)} jugadores → {dst}")
    return dst


if __name__ == "__main__":
    from fbref_loader import cargar_todo
    ancha = cargar_todo()
    out = transformar(ancha)
    guardar(out)
    print(out.head(3).to_string())
