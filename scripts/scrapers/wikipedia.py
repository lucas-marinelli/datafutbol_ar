"""wikipedia.py — Scraper de Wikipedia (EN) para data de selecciones.

Funciones principales:
- get_partidos_recientes(seleccion, n=10) → últimos N partidos oficiales
- get_plantilla_actual(seleccion) → roster actual (TODO)
- get_eliminatorias_stats(seleccion) → stats de eliminatorias (TODO)

Por qué Wikipedia EN y no ES:
- Estructura HTML más estandarizada entre selecciones (los artículos en español
  varían más en cómo cada autor armó las tablas)
- Las tablas usan classes consistentes ('wikitable')
- Más mantenido día a día por la comunidad

Estrategia anti-fragilidad:
- Try-except sobre cada parser que pueda fallar.
- Si la estructura cambia, devuelve DataFrame vacío con columnas esperadas
  + mensaje claro de error.
- Cache 24hs (los partidos no cambian en tiempo real).
"""

from __future__ import annotations
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

# Resolución de path para que el módulo funcione tanto via "python -m" como
# desde un notebook con sys.path.insert(0, REPO_ROOT) ya hecho.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.scrapers.cache import cache_get, cache_set
from scripts.data_loaders import cargar_selecciones

WIKI_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Overrides para selecciones cuya URL Wikipedia no sigue el patrón estándar
# "<País>_national_football_team". USA por ejemplo usa "soccer" no "football".
WIKI_SLUG_OVERRIDES = {
    "USA": "United_States_men's_national_soccer_team",
    "Canada": "Canada_men's_national_soccer_team",
    "New Zealand": "New_Zealand_national_football_team",  # mismo patrón pero explícito
    # Agregar acá si alguna falla
}


def _wiki_url(nombre_en: str) -> str:
    """Construye la URL de Wikipedia EN para una selección.

    Args:
        nombre_en: nombre en inglés según CSV maestro (ej. "Argentina", "USA").

    Returns:
        URL completa.
    """
    if nombre_en in WIKI_SLUG_OVERRIDES:
        slug = WIKI_SLUG_OVERRIDES[nombre_en]
    else:
        slug = f"{nombre_en.replace(' ', '_')}_national_football_team"
    return f"https://en.wikipedia.org/wiki/{slug}"


def _resolver_seleccion(seleccion_es: str) -> dict:
    """Busca la fila del CSV maestro para la selección.

    Args:
        seleccion_es: nombre en español (ej. "Argentina", "España").

    Returns:
        Dict con la fila del CSV.

    Raises:
        ValueError si no se encuentra.
    """
    df = cargar_selecciones()
    mask = df["nombre_es"].str.lower() == seleccion_es.lower()
    if not mask.any():
        raise ValueError(
            f"Selección '{seleccion_es}' no encontrada en el CSV maestro. "
            f"Selecciones disponibles: {df['nombre_es'].tolist()[:5]}..."
        )
    return df[mask].iloc[0].to_dict()


def _resultado_de_score(score: str, perspectiva_local: bool) -> str:
    """Convierte un score tipo '3-1' en 'W'/'D'/'L' desde la perspectiva dada.

    Args:
        score: string '3-1' o '2-2'.
        perspectiva_local: True si la selección que nos interesa jugó de local.

    Returns:
        'W', 'D' o 'L'. Devuelve '?' si no pudo parsear.
    """
    try:
        # Limpiar referencias y notas
        score = re.sub(r"\[.*?\]", "", score).strip()
        # Pueden venir con prórroga: "3-3 (a.e.t.)" o "1-1 (4-2 pen.)"
        m = re.match(r"(\d+)\s*[-–]\s*(\d+)", score)
        if not m:
            return "?"
        gf, gc = int(m.group(1)), int(m.group(2))
        if not perspectiva_local:
            gf, gc = gc, gf  # invertir si fuimos visitante
        if gf > gc:
            return "W"
        elif gf < gc:
            return "L"
        else:
            return "D"
    except Exception:
        return "?"


SCORE_REGEX = re.compile(r"^\s*\d+\s*[-–]\s*\d+")
FECHA_REGEX = re.compile(
    r"\d{1,2}\s+\w+\s+\d{4}"          # "15 March 2026"
    r"|\w+\s+\d{1,2},?\s+\d{4}"       # "March 15, 2026"
    r"|\d{4}-\d{2}-\d{2}"             # "2026-03-15"
)


def _es_fila_partido(texto_cells: list[str]) -> bool:
    """Heurística: una fila es 'de partido' si contiene una fecha Y un score."""
    blob = " | ".join(texto_cells)
    tiene_fecha = bool(FECHA_REGEX.search(blob))
    tiene_score = any(SCORE_REGEX.match(c) for c in texto_cells)
    return tiene_fecha and tiene_score


def _detectar_indices_columnas(headers: list[str]) -> dict:
    """Dado los headers de una tabla, intenta mapear cuál columna es qué.

    Devuelve dict con keys: date, opponent, score, competition (los que encuentre).
    """
    idx = {}
    for i, h in enumerate(headers):
        hl = h.lower()
        if "date" in hl and "date" not in idx:
            idx["date"] = i
        elif any(k in hl for k in ("opponent", "rival", "versus", "vs")):
            idx["opponent"] = i
        elif "score" in hl or hl == "result" or hl == "results":
            idx["score"] = i
        elif "competition" in hl or "tournament" in hl:
            idx["competition"] = i
    return idx


def _parsear_tabla_resultados(html: str, nombre_en: str) -> pd.DataFrame:
    """Parsea las tablas wikitable de un artículo y extrae partidos.

    Estrategia (más laxa que la versión inicial):
    1. Para cada wikitable encontrada, imprime sus headers (debug).
    2. Considera "tabla de partidos" cualquiera donde haya filas con fecha+score.
    3. Detecta automáticamente qué columna es date/opponent/score por headers.
    4. Si no detecta por headers, intenta por orden posicional (primera fecha,
       siguiente texto = rival, siguiente con "X-X" = score).

    Args:
        html: HTML completo del artículo.
        nombre_en: nombre de la selección en inglés.

    Returns:
        DataFrame con columnas: fecha, rival, score, resultado, competencia, local.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("  [ERROR] bs4 no instalado. Correr: pip install beautifulsoup4")
        return pd.DataFrame(columns=["fecha", "rival", "score", "resultado",
                                      "competencia", "local"])

    soup = BeautifulSoup(html, "html.parser")
    tablas = soup.find_all("table", class_=re.compile(r"wikitable"))
    print(f"  [scraper] {len(tablas)} tablas wikitable encontradas")

    filas_parseadas = []
    tablas_partido = 0

    for idx_tabla, tabla in enumerate(tablas):
        # Headers de la PRIMERA fila únicamente
        primera_fila = tabla.find("tr")
        if not primera_fila:
            continue
        headers = [th.get_text(" ", strip=True)
                   for th in primera_fila.find_all(["th", "td"])]

        # Logging de diagnóstico (solo si pocas columnas — las tablas raras tienen muchas)
        if 3 <= len(headers) <= 10:
            print(f"  [scraper] tabla #{idx_tabla}: headers = {headers}")

        # Mapeo de columnas según headers
        col_idx = _detectar_indices_columnas(headers)

        # Recorrer filas
        rows = tabla.find_all("tr")
        filas_validas_esta_tabla = 0
        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue
            texto_cells = [c.get_text(" ", strip=True) for c in cells]

            if not _es_fila_partido(texto_cells):
                continue

            try:
                # 1. Intentar por mapeo de columnas (si lo tenemos)
                fecha = rival = score = competencia = ""
                if "date" in col_idx and col_idx["date"] < len(texto_cells):
                    fecha = texto_cells[col_idx["date"]]
                if "opponent" in col_idx and col_idx["opponent"] < len(texto_cells):
                    rival = texto_cells[col_idx["opponent"]]
                if "score" in col_idx and col_idx["score"] < len(texto_cells):
                    score = texto_cells[col_idx["score"]]
                if "competition" in col_idx and col_idx["competition"] < len(texto_cells):
                    competencia = texto_cells[col_idx["competition"]]

                # 2. Fallback posicional: buscar fecha, score y rival entre las celdas
                if not fecha:
                    for c in texto_cells:
                        if FECHA_REGEX.search(c):
                            fecha = c
                            break
                if not score:
                    for c in texto_cells:
                        if SCORE_REGEX.match(c):
                            score = c
                            break
                if not rival:
                    # Tomar la celda siguiente a la fecha que no sea el score
                    for c in texto_cells:
                        if c and c != fecha and not SCORE_REGEX.match(c) \
                           and not FECHA_REGEX.search(c) and len(c) <= 50:
                            # heurística: nombre de país suele ser corto
                            rival = c
                            break

                if not fecha or not score:
                    continue

                # Detectar local/visitante
                local = True
                if re.search(r"\[A\]|\bA\b|\(A\)|away", rival, re.IGNORECASE):
                    local = False
                rival_limpio = re.sub(r"\[.*?\]|\(.*?\)|\bA\b|\bH\b|away|home",
                                      "", rival, flags=re.IGNORECASE).strip()

                resultado = _resultado_de_score(score, perspectiva_local=local)

                filas_parseadas.append({
                    "fecha": fecha,
                    "rival": rival_limpio,
                    "score": score,
                    "resultado": resultado,
                    "competencia": competencia,
                    "local": local,
                })
                filas_validas_esta_tabla += 1
            except Exception as e:
                continue

        if filas_validas_esta_tabla > 0:
            tablas_partido += 1
            print(f"  [scraper] tabla #{idx_tabla} aportó {filas_validas_esta_tabla} partidos")

    df = pd.DataFrame(filas_parseadas,
                       columns=["fecha", "rival", "score", "resultado",
                                "competencia", "local"])
    # Quitar duplicados (puede haber tablas que repiten partidos)
    df = df.drop_duplicates(subset=["fecha", "rival", "score"]).reset_index(drop=True)
    print(f"  [scraper] {tablas_partido} tablas con partidos · {len(df)} filas únicas extraídas")
    return df


def get_partidos_recientes(
    seleccion: str,
    n: int = 10,
    refresh: bool = False,
    ttl_hours: float = 24,
) -> pd.DataFrame:
    """Scrapea los últimos N partidos oficiales de la selección desde Wikipedia EN.

    Args:
        seleccion: nombre en español (ej. "Argentina"). Se mapea internamente a en.wikipedia.
        n: cuántos partidos devolver (default 10, los más recientes).
        refresh: si True, ignora cache y re-scrapea.
        ttl_hours: validez del cache (default 24hs).

    Returns:
        DataFrame con columnas: fecha, rival, score, resultado, competencia, local.
        Ordenado por fecha desc. Vacío si falla el scraping.

    Ejemplo:
        df = get_partidos_recientes("Argentina", n=10)
        print(df.head())
    """
    meta = _resolver_seleccion(seleccion)
    nombre_en = meta["nombre_en"]
    cache_key = f"wiki_partidos_{nombre_en}"

    # Intentar cache primero
    if not refresh:
        cached = cache_get(cache_key, ttl_hours=ttl_hours)
        if cached is not None:
            print(f"  [cache] usando cache de '{seleccion}' ({len(cached)} filas)")
            df = pd.DataFrame(cached)
            return df.head(n)

    # Scrape fresh
    url = _wiki_url(nombre_en)
    print(f"  [scraper] pegando a {url}")
    try:
        r = requests.get(url, headers=WIKI_HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] no se pudo bajar Wikipedia para '{seleccion}': {e}")
        return pd.DataFrame(columns=["fecha", "rival", "score", "resultado",
                                      "competencia", "local"])

    df = _parsear_tabla_resultados(r.text, nombre_en)
    if df.empty:
        print(f"  [WARN] Wikipedia no devolvió partidos para '{seleccion}'.")
        print(f"         Verificar URL: {url}")
        return df

    # Cachear el resultado completo (sin trimear a n)
    cache_set(cache_key, df.to_dict(orient="records"))

    return df.head(n)


def get_top_goleadores_historicos(seleccion: str, n: int = 5,
                                   refresh: bool = False,
                                   ttl_hours: float = 168) -> pd.DataFrame:
    """Scrapea top goleadores históricos desde el artículo principal de Wikipedia EN.

    Busca la tabla con headers tipo ['Rank', 'Player', 'Caps', 'Goals', 'Ratio', 'Career'].
    Es data 'evergreen' (cambia poco mes a mes), así que cache default de 7 días.

    Args:
        seleccion: nombre en español (ej. "Argentina").
        n: top N a devolver (default 5).
        refresh: si True ignora cache.
        ttl_hours: TTL cache (default 168 = 7 días).

    Returns:
        DataFrame con columnas: rank, player, caps, goals, ratio, career.
        Empty si falla.
    """
    meta = _resolver_seleccion(seleccion)
    nombre_en = meta["nombre_en"]
    cache_key = f"wiki_top_scorers_{nombre_en}"

    if not refresh:
        cached = cache_get(cache_key, ttl_hours=ttl_hours)
        if cached is not None:
            print(f"  [cache] top goleadores '{seleccion}' desde cache")
            return pd.DataFrame(cached).head(n)

    url = _wiki_url(nombre_en)
    print(f"  [scraper] pegando a {url}")
    try:
        r = requests.get(url, headers=WIKI_HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        return pd.DataFrame()

    from io import StringIO
    try:
        dfs = pd.read_html(StringIO(r.text))
    except Exception as e:
        print(f"  [ERROR] pd.read_html falló: {e}")
        return pd.DataFrame()

    print(f"  [scraper] {len(dfs)} tablas parseadas")

    # Buscar tabla con headers de top goleadores
    # Heurística: tiene "Goals" + "Ratio" + "Player" (Ratio diferencia top scorers
    # de top caps; top caps no tiene Ratio).
    for idx, df in enumerate(dfs):
        # Aplanar MultiIndex si existe
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join([str(c) for c in col if str(c) != "nan"]).strip()
                          for col in df.columns]
        cols = [str(c).strip() for c in df.columns]
        cols_lower = [c.lower() for c in cols]

        tiene_player = any("player" in c for c in cols_lower)
        tiene_goals = any(c == "goals" for c in cols_lower)
        tiene_ratio = any("ratio" in c for c in cols_lower)
        tiene_rank = any(c in ("rank", "no.", "#") for c in cols_lower)

        if not (tiene_player and tiene_goals and tiene_ratio):
            continue

        print(f"  [scraper] tabla #{idx} matchea top scorers: cols={cols}")

        # Renombrar columnas a estándar
        rename = {}
        for c in cols:
            cl = c.lower().strip()
            if "rank" in cl or cl == "no.":
                rename[c] = "rank"
            elif cl == "player":
                rename[c] = "player"
            elif cl == "caps":
                rename[c] = "caps"
            elif cl == "goals":
                rename[c] = "goals"
            elif "ratio" in cl:
                rename[c] = "ratio"
            elif "career" in cl:
                rename[c] = "career"

        df_clean = df.rename(columns=rename).copy()

        # Limpiar nombres — sacar referencias [1], (c), (list), y cualquier (...)
        if "player" in df_clean.columns:
            df_clean["player"] = (
                df_clean["player"].astype(str)
                .str.replace(r"\[.*?\]", "", regex=True)       # [1] referencias
                .str.replace(r"\(.*?\)", "", regex=True)       # (list), (c), (any)
                .str.strip()
            )

        # Convertir goals y caps a int si se puede
        for col in ("goals", "caps"):
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

        # Quedarnos con columnas estándar (todas o las disponibles)
        cols_std = [c for c in ["rank", "player", "caps", "goals", "ratio", "career"]
                    if c in df_clean.columns]
        df_clean = df_clean[cols_std].dropna(subset=["player"])

        if "goals" in df_clean.columns:
            df_clean = df_clean.sort_values("goals", ascending=False).reset_index(drop=True)

        cache_set(cache_key, df_clean.to_dict(orient="records"))
        print(f"  [scraper] ✅ {len(df_clean)} jugadores extraídos")
        return df_clean.head(n)

    print(f"  [WARN] no se encontró tabla de top scorers para '{seleccion}'")
    return pd.DataFrame()


def get_plantilla_actual(seleccion: str, refresh: bool = False) -> pd.DataFrame:
    """TODO: scrapea la plantilla actual de la selección desde Wikipedia EN.

    Plan:
    - Buscar sección "Current squad" o "Most recent squad" en el artículo.
    - Extraer tabla con: número, jugador, posición, club, edad, caps, goles.

    Por ahora devuelve DataFrame vacío. Implementar cuando se necesite el
    primer slide 3 de XI probable.
    """
    print(f"  [TODO] get_plantilla_actual('{seleccion}') aún no implementado.")
    print("         Mientras tanto, completar XI_PROBABLE manualmente en el notebook.")
    return pd.DataFrame(columns=["num", "jugador", "posicion", "club", "edad",
                                  "caps", "goles"])


# Para cada confederación intentamos VARIAS variantes — Wikipedia
# a veces usa em-dash, en-dash, paréntesis, etc. La primera que devuelva 200 gana.
WIKI_QUAL_URL_VARIANTES = {
    "CONMEBOL": [
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_CONMEBOL",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_(CONMEBOL)",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_AFC_first_round",  # fallback ilustrativo, no aplica
    ],
    "UEFA": [
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_UEFA",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_(UEFA)",
    ],
    "CAF": [
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_CAF",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_(CAF)",
    ],
    "AFC": [
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_AFC",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_(AFC)",
    ],
    "CONCACAF": [
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_CONCACAF",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_(CONCACAF)",
    ],
    "OFC": [
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_%E2%80%93_OFC",
        "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_qualification_(OFC)",
    ],
}


def _wiki_search_url(query: str) -> str | None:
    """Usa la API de Wikipedia para buscar el primer artículo que matchea.

    Más robusto que adivinar URL — Wikipedia te redirige al título correcto.
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "opensearch",
        "search": query,
        "limit": 1,
        "format": "json",
    }
    try:
        r = requests.get(search_url, params=params, headers=WIKI_HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        # opensearch devuelve [query, [titles], [descriptions], [urls]]
        if isinstance(data, list) and len(data) >= 4 and data[3]:
            return data[3][0]
    except Exception as e:
        print(f"  [search] {type(e).__name__}: {e}")
    return None


def _bajar_html_eliminatorias(confed: str) -> tuple[str | None, str | None]:
    """Intenta bajar el HTML del artículo de eliminatorias.

    Returns:
        (html, url_que_funcionó) o (None, None) si fallan todas.
    """
    # Paso 1: probar URLs candidatas hardcodeadas
    candidatas = WIKI_QUAL_URL_VARIANTES.get(confed, [])
    for url in candidatas:
        try:
            r = requests.get(url, headers=WIKI_HEADERS, timeout=15, allow_redirects=True)
            if r.status_code == 200:
                print(f"  [scraper] OK desde {url}")
                return r.text, r.url
        except Exception as e:
            print(f"  [WARN] {url} → {type(e).__name__}")
            continue

    # Paso 2: si fallaron todas, usar API de búsqueda de Wikipedia
    print(f"  [scraper] URLs hardcodeadas fallaron — usando API de búsqueda")
    query = f"2026 FIFA World Cup qualification {confed}"
    found = _wiki_search_url(query)
    if found:
        print(f"  [scraper] búsqueda encontró: {found}")
        try:
            r = requests.get(found, headers=WIKI_HEADERS, timeout=15)
            r.raise_for_status()
            return r.text, r.url
        except Exception as e:
            print(f"  [ERROR] fallo bajando URL de búsqueda: {e}")

    return None, None


def _safe_int(cell) -> int | None:
    """Extrae un entero del texto de una celda BeautifulSoup. None si no se puede."""
    text = cell.get_text(" ", strip=True) if hasattr(cell, "get_text") else str(cell)
    text = re.sub(r"\[.*?\]|\(.*?\)", "", text).strip()
    m = re.match(r"[-+]?(\d+)", text)
    return int(m.group(1)) if m else None


def _extraer_int_celda(valor) -> int | None:
    """Toma cualquier celda (str, int, float, NaN) y devuelve int o None."""
    if valor is None or pd.isna(valor):
        return None
    s = str(valor).strip()
    s = re.sub(r"\[.*?\]|\(.*?\)", "", s).strip()
    m = re.search(r"[-+]?\d+", s)
    return int(m.group(0)) if m else None


def get_eliminatorias_stats(seleccion: str, refresh: bool = False,
                            ttl_hours: float = 24, verbose: bool = False) -> dict:
    """Scrapea stats finales de la selección en eliminatorias del Mundial 2026.

    USA pandas.read_html (más robusto que BeautifulSoup para tablas regulares).
    Busca en todas las tablas del artículo y elige la que contenga la fila
    del país con stats típicos (Pld + W + D + L + Pts).

    Args:
        seleccion: nombre en español (ej. "Argentina").
        refresh: si True, ignora cache y re-scrapea.
        ttl_hours: validez del cache (default 24hs).
        verbose: si True, imprime info de cada tabla encontrada.

    Returns:
        Dict con keys: posicion, pj, pg, pe, pp, gf, gc, gd, puntos.
        Si la selección es 'host', devuelve dict con flag.
        Si falla, devuelve dict vacío.
    """
    meta = _resolver_seleccion(seleccion)
    confed = meta["confederacion"]
    nombre_en = meta["nombre_en"]
    estado = meta["estado_2026"]

    if estado == "host":
        return {
            "es_host": True,
            "mensaje": f"{seleccion} clasificó como anfitrión — no jugó eliminatorias.",
        }

    cache_key = f"wiki_qual_{nombre_en}"
    if not refresh:
        cached = cache_get(cache_key, ttl_hours=ttl_hours)
        if cached is not None:
            print(f"  [cache] stats eliminatorias '{seleccion}' desde cache")
            return cached

    # Bajar HTML probando URLs alternativas + API de búsqueda como fallback
    html, url = _bajar_html_eliminatorias(confed)
    if html is None:
        print(f"  [ERROR] no se pudo bajar artículo de eliminatorias {confed}")
        return {}

    # pandas.read_html parsea TODAS las tablas HTML del artículo de una.
    # IMPORTANTE: pandas >= 2.1 requiere envolver el HTML string en un buffer
    # (StringIO), sino interpreta el string como path de archivo y tira FileNotFoundError.
    from io import StringIO
    try:
        dfs = pd.read_html(StringIO(html))
    except Exception as e:
        print(f"  [ERROR] pd.read_html falló: {e}")
        return {}

    print(f"  [scraper] {len(dfs)} tablas parseadas con pd.read_html")

    # Aliases que el país puede tener en la tabla
    aliases = [nombre_en, meta["nombre_es"]]
    if nombre_en == "USA":
        aliases += ["United States"]
    if nombre_en == "Czech Republic":
        aliases += ["Czechia"]

    for idx, df in enumerate(dfs):
        if df.shape[0] < 2 or df.shape[1] < 5:
            continue

        # Las columnas pueden ser MultiIndex (Wikipedia a veces los usa).
        # Aplanamos a string simple.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join([str(c) for c in col if str(c) != "nan"]).strip()
                          for col in df.columns]
        df.columns = [str(c).strip() for c in df.columns]

        if verbose:
            print(f"\n  [scraper] tabla #{idx} (shape={df.shape}):")
            print(f"           cols: {list(df.columns)}")

        # Buscar fila del país en CUALQUIER columna (no asumimos cuál es "Team")
        mask = pd.Series([False] * len(df))
        for col in df.columns:
            try:
                col_str = df[col].astype(str)
                for alias in aliases:
                    mask = mask | col_str.str.contains(
                        re.escape(alias), case=False, na=False
                    )
            except Exception:
                continue

        if not mask.any():
            continue

        fila = df[mask].iloc[0]
        if verbose:
            print(f"  [scraper] encontrado '{nombre_en}' en tabla #{idx}:")
            print(fila)

        # Identificar las columnas de stats por nombre
        def find_col(*nombres, exact: bool = False):
            """Busca columna. exact=True requiere match exacto (case-insensitive)."""
            for nombre in nombres:
                for col in df.columns:
                    col_str = str(col).strip()
                    if exact:
                        if col_str.lower() == nombre.lower():
                            return col
                    else:
                        if nombre.lower() in col_str.lower():
                            return col
            return None

        col_pos = find_col("Pos", "Rank", "Position")
        col_pj  = find_col("Pld", "MP", "PJ") or find_col("P", exact=True)
        # W/D/L deben ser exactos para no chocar con "Win%", "Diff", "League" etc.
        col_pg  = find_col("W", exact=True) or find_col("Wins", "PG")
        col_pe  = find_col("D", exact=True) or find_col("Draws", "PE")
        col_pp  = find_col("L", exact=True) or find_col("Losses", "PP")
        col_gf  = find_col("GF")
        col_gc  = find_col("GA", "GC")
        col_gd  = find_col("GD", "+/-")
        col_pts = find_col("Pts", "Points", "Puntos")

        # Fallback: si no detectó por nombre, usar índices posicionales
        # Típica tabla CONMEBOL: Pos|Team|Pld|W|D|L|GF|GA|GD|Pts
        if col_pj is None and len(df.columns) >= 8:
            cols = list(df.columns)
            # Buscar columna "Team" para arrancar desde ahí
            for i, c in enumerate(cols):
                if "team" in c.lower() or nombre_en.lower() in str(fila[c]).lower():
                    # Las stats vienen después
                    if i + 7 < len(cols):
                        col_pj = cols[i+1]
                        col_pg = cols[i+2]
                        col_pe = cols[i+3]
                        col_pp = cols[i+4]
                        col_gf = cols[i+5]
                        col_gc = cols[i+6]
                        col_gd = cols[i+7] if i+7 < len(cols) else None
                        col_pts = cols[-1]  # típicamente la última
                    break

        stats = {
            "es_host": False,
            "posicion": _extraer_int_celda(fila[col_pos]) if col_pos else None,
            "pj":       _extraer_int_celda(fila[col_pj])  if col_pj  else None,
            "pg":       _extraer_int_celda(fila[col_pg])  if col_pg  else None,
            "pe":       _extraer_int_celda(fila[col_pe])  if col_pe  else None,
            "pp":       _extraer_int_celda(fila[col_pp])  if col_pp  else None,
            "gf":       _extraer_int_celda(fila[col_gf])  if col_gf  else None,
            "gc":       _extraer_int_celda(fila[col_gc])  if col_gc  else None,
            "gd":       _extraer_int_celda(fila[col_gd])  if col_gd  else None,
            "puntos":   _extraer_int_celda(fila[col_pts]) if col_pts else None,
            "url_fuente": url or "",
            "tabla_idx": idx,
        }

        print(f"  [scraper] ✅ stats encontradas para {nombre_en} en tabla #{idx}")
        cache_set(cache_key, stats)
        return stats

    print(f"  [WARN] no se encontró fila de '{seleccion}' en ninguna tabla.")
    print(f"         Para diagnóstico: get_eliminatorias_stats('{seleccion}', verbose=True)")
    return {}
