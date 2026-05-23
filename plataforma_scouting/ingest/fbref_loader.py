"""fbref_loader.py — Ingesta de estadísticas de jugador desde FBref (Big-5).

Fuente: `soccerdata.FBref`, liga "Big 5 European Leagues Combined".
Confirmado en `memory/context/leccion_data_AR_may2026.md`: soccerdata cubre las
5 grandes ligas europeas (NO Argentina/Sudamérica). Para Big-5 es confiable.

⚠️ IMPORTANTE (descubierto 22/5/2026): `soccerdata >= 1.9` scrapea FBref con un
   NAVEGADOR (seleniumbase / undetected-chromedriver) porque FBref puso Cloudflare.
   Es decir: la PRIMERA corrida abre Chrome en tu máquina (igual que LanusStats.FotMob).
   - Necesitás Chrome instalado (lo tenés).
   - Si tira error de webdriver, probá: `pip install -U soccerdata seleniumbase`.
   - Todo se cachea en parquet → solo se scrapea la primera vez por temporada.
   - Alternativa si Chrome da guerra: el paquete R `worldfootballR` (mismo FBref).

Responsabilidad de este módulo:
1. Descargar las season stats de jugador (varios stat_types).
2. Aplanar índices/columnas multinivel de FBref.
3. Unir todos los stat_types en una tabla ancha por (league, season, team, player).
4. Cachear a parquet en ../data/raw/fbref/.
La normalización al esquema la hace `transformar.py` (siguiente paso del ETL).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "fbref"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Las 5 grandes ligas, combinadas en una sola tabla (más eficiente en soccerdata)
LIGA_BIG5 = "Big 5 European Leagues Combined"

# stat_types de FBref que sumamos a la tabla ancha del scouting.
# ⚠️ soccerdata 1.9 read_player_season_stats SOLO soporta estos 5:
#    standard, shooting, playing_time, keeper, misc.
#    (passing/defense/possession/gca NO están a nivel jugador-temporada en esta
#     versión → pases clave, % pases y toques en área no se pueden traer acá.
#     Para esas métricas, ver Fase 2: read_player_match_stats o worldfootballR.)
STAT_TYPES = [
    "standard",     # minutos, goles, asistencias, xG, xAG, progresión (PrgC/PrgP)
    "shooting",     # tiros, SoT, npxG, xG/tiro, distancia
    "misc",         # intercepciones, tackles ganados, recuperaciones, duelos aéreos, faltas
    "playing_time", # detalle de minutos / titularidades
    "keeper",       # stats de arqueros (NaN para jugadores de campo)
]


def _aplanar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplana columnas multinivel de FBref a 'Grupo_sub' y resetea el índice.

    Ej.: ('Playing Time','Min') -> 'Playing Time_Min'; ('nation','') -> 'nation'.
    """
    out = df.reset_index()
    out.columns = [
        "_".join(str(c) for c in col if str(c) not in ("", "nan")).strip("_")
        if isinstance(col, tuple) else str(col)
        for col in out.columns
    ]
    return out


def _fbref_client(season: str):
    """Crea el cliente FBref con mensaje claro si falla el navegador."""
    try:
        import soccerdata as sd
        return sd.FBref(leagues=LIGA_BIG5, seasons=season)
    except Exception as e:  # típicamente error de webdriver/Chrome
        raise RuntimeError(
            "No se pudo iniciar soccerdata.FBref. En soccerdata>=1.9 scrapea con "
            "Chrome (Cloudflare). Probá: pip install -U soccerdata seleniumbase, "
            "y confirmá que Chrome esté instalado. Detalle: " + repr(e)
        ) from e


def cargar_fbref_standard(season: str = "2025-2026", refrescar: bool = False) -> pd.DataFrame:
    """Descarga (o lee de cache) las stats 'standard' de jugador de las Big-5.

    Returns: DataFrame aplanado (player, nation, pos, age, born, team, Playing
    Time_Min, Performance_Gls, Expected_xG, ...).
    """
    cache = RAW_DIR / f"standard_{season}.parquet"
    if cache.exists() and not refrescar:
        return pd.read_parquet(cache)

    fbref = _fbref_client(season)
    raw = fbref.read_player_season_stats(stat_type="standard")
    flat = _aplanar_columnas(raw)
    flat.to_parquet(cache, index=False)
    print(f"✅ standard: {flat.shape[0]} jugadores → {cache.name}")
    return flat


def cargar_todo(season: str = "2025-2026", refrescar: bool = False) -> pd.DataFrame:
    """Descarga TODOS los STAT_TYPES y los une en una tabla ancha.

    La unión se hace sobre el índice (league, season, team, player) ANTES de
    aplanar, así no se duplican columnas comunes. Cachea el resultado final en
    ../data/raw/fbref/ancha_<season>.parquet.

    Returns: DataFrame ancho aplanado, listo para `transformar.py`.
    """
    cache = RAW_DIR / f"ancha_{season}.parquet"
    if cache.exists() and not refrescar:
        print(f"(cache) {cache.name}")
        return pd.read_parquet(cache)

    fbref = _fbref_client(season)

    base = None
    for st in STAT_TYPES:
        try:
            df_st = fbref.read_player_season_stats(stat_type=st)
        except Exception as e:
            print(f"⚠️ stat_type '{st}' falló: {type(e).__name__}: {e} — se omite.")
            continue
        if base is None:
            base = df_st
        else:
            # sumar solo las columnas nuevas (evita duplicar nation/pos/age/etc.)
            nuevas = [c for c in df_st.columns if c not in base.columns]
            base = base.join(df_st[nuevas], how="left")
        print(f"  · {st}: +{df_st.shape[1]} cols → total {base.shape[1]}")

    if base is None:
        raise RuntimeError("Ningún stat_type se pudo descargar.")

    flat = _aplanar_columnas(base)
    flat.to_parquet(cache, index=False)
    print(f"\n✅ Tabla ancha: {flat.shape[0]} jugadores × {flat.shape[1]} cols → {cache.name}")
    return flat


if __name__ == "__main__":
    df = cargar_todo()
    print(df.head(3).to_string())
