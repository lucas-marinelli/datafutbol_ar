"""scripts.scrapers — Scrapers reutilizables para data de selecciones.

Cada módulo expone funciones que devuelven DataFrames listos para usar
en notebooks de BAJO LA LUPA u otros posts del Mundial.

Cachean localmente en data/scraped/ para no pegarle a las páginas 100 veces
durante el desarrollo de un slide.

Patrón de uso:

    from scripts.scrapers import get_partidos_recientes

    df = get_partidos_recientes("Argentina", n=10)
    print(df)

Si una función falla por cambio de estructura HTML, devuelve un DataFrame
vacío con columnas esperadas + imprime un mensaje claro.
"""

from .wikipedia import (
    get_partidos_recientes,
    get_plantilla_actual,
    get_eliminatorias_stats,
    get_top_goleadores_historicos,
)

__all__ = [
    "get_partidos_recientes",
    "get_plantilla_actual",
    "get_eliminatorias_stats",
    "get_top_goleadores_historicos",
]
