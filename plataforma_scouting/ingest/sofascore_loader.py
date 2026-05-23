"""sofascore_loader.py — Ingesta desde SofaScore vía ScraperFC.

Aprendido EN VIVO el 22/5/2026:
- `requests` y `cloudscraper` a la API de SofaScore → 403 (Cloudflare duro). NO sirven.
- **`ScraperFC.Sofascore` SÍ entra** (maneja la sesión por dentro). ⭐ Usar este wrapper.
- Cubre 37 competiciones: Big-5 europeas + Argentina Liga Profesional + Argentina
  Copa de la Liga + CONMEBOL Libertadores + México (Apertura/Clausura) + Perú +
  FIFA World Cup, etc. Lista completa: `src/ScraperFC/comps.yaml` del paquete.

Da lo que FBref-soccerdata 1.9 NO daba: rating, tackles, intercepciones, duelos,
pases clave + heatmaps por partido + bio (DOB/posición/contrato).
→ Es además el camino #1 para Sudamérica (Fase 3): SÍ trae Liga Profesional AR.

API de ScraperFC.Sofascore (confirmada):
- get_valid_seasons(league) -> {nombre_temporada: id}
- scrape_player_league_stats(year, league, accumulation='total'|'per90'|'perMatch',
      selected_positions=['Goalkeepers','Defenders','Midfielders','Forwards'])
- scrape_player_details(year, league) -> bio (name, DOB, posición, altura, contrato)
- get_match_dicts(year, league) -> partidos de la temporada
- get_match_id_from_url(url) / get_match_url_from_id(id)
- scrape_heatmaps(match_id) -> {jugador: {'id':.., 'heatmap':[[x,y],...]}}  (coords 0-100)
- scrape_match_shots(match_id) -> shot map del partido
- scrape_match_momentum / scrape_player_match_stats / scrape_team_*  ...

Año: usar get_valid_seasons(league). Europeas tipo '24/25'; AR/calendario '2025'.
Heatmap: coords 0-100 → mplsoccer pitch_type='opta'.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw" / "sofascore"
RAW_DIR.mkdir(parents=True, exist_ok=True)


def cliente():
    """Instancia de ScraperFC.Sofascore (la que esquiva Cloudflare)."""
    import ScraperFC as sfc
    return sfc.Sofascore()


def temporadas(league: str) -> dict:
    """Años válidos para una liga: {nombre_temporada: id}."""
    return cliente().get_valid_seasons(league)


def stats_liga(year: str, league: str, accumulation: str = "per90",
               refrescar: bool = False) -> pd.DataFrame:
    """Stats de TODOS los jugadores de una liga-temporada (rating, defensa, etc.).

    Lee del cache (data/raw/sofascore/) si ya existe; si no, scrapea y guarda.
    Pasá refrescar=True para forzar la re-descarga (ej. temporada en curso).

    ⚠️ Trampa: con accumulation='per90', la columna 'minutesPlayed' vale 90 para
    TODOS (está normalizada). Para minutos reales (y filtrar por minutos) usá
    accumulation='total'. Patrón recomendado: traer 'total' para minutos+rating y
    'per90' para las tasas, y mergear por ['player','team'].
    """
    safe = league.replace(" ", "_").lower()
    cache = RAW_DIR / f"stats_{safe}_{year.replace('/', '-')}_{accumulation}.parquet"
    if cache.exists() and not refrescar:
        df = pd.read_parquet(cache)
        print(f"[cache] {cache.name}: {df.shape[0]} jugadores x {df.shape[1]} cols")
        return df
    print(f"[API] scrapeando {league} {year} ({accumulation})...")
    df = cliente().scrape_player_league_stats(
        year=year, league=league, accumulation=accumulation)
    df.to_parquet(cache, index=False)
    print(f"[API] guardado {cache.name}: {df.shape[0]} jugadores x {df.shape[1]} cols")
    return df


def buscar_partido(year: str, league: str, equipo_a: str, equipo_b: str):
    """Devuelve (match_id, 'Local vs Visitante') del cruce entre dos equipos."""
    for m in cliente().get_match_dicts(year=year, league=league):
        h = (m.get("homeTeam") or {}).get("name", "")
        a = (m.get("awayTeam") or {}).get("name", "")
        nombres = f"{h} {a}".lower()
        if equipo_a.lower() in nombres and equipo_b.lower() in nombres:
            return m.get("id"), f"{h} vs {a}"
    return None, None


def heatmap_partido(match_id) -> dict:
    """Heatmaps de todos los jugadores de un partido. coords 0-100 (pitch 'opta')."""
    return cliente().scrape_heatmaps(match_id)


def heatmap_xy(hm: dict, nombre_jugador: str):
    """De la salida de scrape_heatmaps, devuelve (xs, ys) de un jugador para kdeplot."""
    for nombre, info in hm.items():
        if nombre_jugador.lower() in nombre.lower():
            pts = info.get("heatmap", [])
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            return xs, ys
    return [], []


# TODO Fase 2/3: normalizar stats_liga() al esquema de la plataforma (per-90, nombres ES);
#   guardar tabla de mapeo nombre->sofascore_id; sumar scrape_player_details() para bio.

if __name__ == "__main__":
    print(temporadas("Italy Serie A"))
