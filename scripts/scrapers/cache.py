"""cache.py — Cache simple en disco para scrapers.

Guarda respuestas en JSON con timestamp. Default TTL: 24hs.
Pensado para evitar pegar a Wikipedia/AFA/etc. en cada iteración del notebook.
"""

from __future__ import annotations
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

DEFAULT_CACHE_DIR = Path(
    r"D:\PROYECTOS_venv\02_PROYECTOS\01_Python\datafutbol_ar\data\scraped"
)
DEFAULT_TTL_HOURS = 24


def _cache_path(key: str, cache_dir: Optional[Path] = None) -> Path:
    """Devuelve el path del archivo cache para una key dada."""
    d = cache_dir or DEFAULT_CACHE_DIR
    d.mkdir(parents=True, exist_ok=True)
    # Sanitizar key para que sea un filename válido
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in key)
    return d / f"{safe}.json"


def cache_get(key: str, ttl_hours: float = DEFAULT_TTL_HOURS,
              cache_dir: Optional[Path] = None) -> Optional[Any]:
    """Devuelve el contenido cacheado si existe y no expiró. Si no, None.

    Args:
        key: identificador único (típicamente combina fuente + país + tipo).
        ttl_hours: cuántas horas se considera "fresco" el cache.
        cache_dir: directorio de cache (default: data/scraped/).
    """
    path = _cache_path(key, cache_dir)
    if not path.exists():
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        ts = datetime.fromisoformat(payload["scraped_at"])
        if datetime.now() - ts > timedelta(hours=ttl_hours):
            return None  # expirado
        return payload["data"]
    except Exception as e:
        print(f"  [cache] error leyendo {path.name}: {e}")
        return None


def cache_set(key: str, data: Any, cache_dir: Optional[Path] = None) -> Path:
    """Guarda data en cache con timestamp actual. Devuelve el path."""
    path = _cache_path(key, cache_dir)
    payload = {
        "scraped_at": datetime.now().isoformat(),
        "key": key,
        "data": data,
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def cache_clear(key_pattern: Optional[str] = None,
                cache_dir: Optional[Path] = None) -> int:
    """Borra entradas del cache. Si key_pattern, solo las que matcheen.

    Returns:
        Cantidad de archivos borrados.
    """
    d = cache_dir or DEFAULT_CACHE_DIR
    if not d.exists():
        return 0

    borrados = 0
    for f in d.glob("*.json"):
        if key_pattern and key_pattern not in f.name:
            continue
        f.unlink()
        borrados += 1
    return borrados
