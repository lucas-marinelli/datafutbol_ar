"""scoring_index.py — Índice compuesto de rendimiento por perfil.

Es nuestra versión del "Scoring Index %" del post de Capitán FI: un número 0-100
que resume el rendimiento de un jugador SEGÚN UN PERFIL de posición.

═══════════════════════════════════════════════════════════════════════════
METODOLOGÍA (leer antes de tocar)
═══════════════════════════════════════════════════════════════════════════

Pipeline:
    1. Filtrar pares: misma posición + mínimo de minutos (evita ruido).
    2. Normalizar cada métrica DENTRO del grupo de pares:
         · Percentil (0-100) → interpretable, ideal para radares.
         · Z-score → más fino para diferencias chicas (alternativa).
       Para métricas "malas" (ej. pérdidas) se invierte (100 - percentil).
    3. Ponderar por PERFIL: cada perfil (ej. "9 killer", "extremo desequilibrante",
       "mediocentro creador", "central de salida") define qué familias de métricas
       pesan y cuánto. Los pesos suman 1.
    4. Componer: índice = Σ (peso_i × percentil_i). Reescalar a 0-100.

⚠️ RIESGOS de los composite scores (ref. Marc Lamberts, "The risks of using
   composite scores in data scouting"):
   - Ocultan el "cómo": dos jugadores con el mismo índice pueden ser opuestos.
   - Súper sensibles a QUÉ métricas elegís y a los pesos.
   - Tentación de tratarlos como verdad absoluta.
   REGLA: el índice NUNCA se muestra solo. Siempre acompañado del radar de
   percentiles que lo componen. El índice ordena; los percentiles explican.

   Dato de decision science (ref. winningwithanalytics): pesos iguales suelen
   funcionar casi tan bien como esquemas sofisticados. Empezar simple.

Estado: 🟡 stub + perfiles de ejemplo. Implementar cálculo en Fase 3
(cuando existan db + percentiles.py).
"""
from __future__ import annotations

import pandas as pd

# ──────────────────────────────────────────────────────────────────────
# PERFILES — qué métricas pesan para cada tipo de jugador
# ──────────────────────────────────────────────────────────────────────
# Los nombres de métrica son placeholders del esquema (ver docs/diccionario_datos.md).
# Los pesos de cada perfil suman 1.0. Arrancar con pesos "redondos" y ajustar.
#
# ⚠️ FASE 3 — RECONCILIAR CON DATOS DISPONIBLES: estos perfiles describen el
# IDEAL. Algunas métricas (pases_clave_90, pct_pases, toques_area_90,
# conversion, presion_alta_90, centros/regates) NO vienen en
# soccerdata.read_player_season_stats 1.9 (solo standard/shooting/misc/playing_time/keeper).
# Antes de implementar el cálculo: o se reemplazan por métricas disponibles
# (xa, pases_progresivos_90, recuperaciones_90, duelos_aereos_pct, tackles_ganados_90)
# o se trae la data faltante por otra vía (read_player_match_stats / worldfootballR).

PERFILES: dict[str, dict[str, float]] = {
    "9_killer": {            # delantero finalizador
        "goles_90": 0.25,
        "xg_90": 0.20,
        "tiros_90": 0.10,
        "xg_per_tiro": 0.10,
        "toques_area_90": 0.15,
        "conversion": 0.10,
        "presion_alta_90": 0.10,
    },
    "extremo_desequilibrante": {
        "regates_completados_90": 0.20,
        "carries_progresivos_90": 0.20,
        "xa_90": 0.15,
        "pases_clave_90": 0.15,
        "goles_90": 0.10,
        "toques_area_90": 0.10,
        "centros_completados_90": 0.10,
    },
    "mediocentro_creador": {
        "xa_90": 0.20,
        "pases_clave_90": 0.20,
        "pases_progresivos_90": 0.20,
        "pct_pases": 0.15,
        "carries_progresivos_90": 0.15,
        "recuperaciones_90": 0.10,
    },
    "central_salida": {
        "pct_pases": 0.20,
        "pases_progresivos_90": 0.20,
        "duelos_aereos_pct": 0.20,
        "intercepciones_90": 0.15,
        "tackles_pct": 0.15,
        "errores_90": 0.10,   # métrica "mala" → se invierte
    },
}

# Métricas donde "más alto = peor" (se invierten en la normalización)
METRICAS_INVERTIR = {"errores_90", "perdidas_90", "faltas_90"}


def calcular_scoring_index(
    df: pd.DataFrame,
    perfil: str,
    col_posicion: str = "pos_grupo",
    col_minutos: str = "minutos",
    min_minutos: int = 600,
    metodo: str = "percentil",  # "percentil" | "zscore"
) -> pd.Series:
    """TODO Fase 3: devolver el Scoring Index (0-100) por jugador para un perfil.

    Pasos: filtrar minutos -> normalizar cada métrica del perfil dentro del grupo
    de posición -> invertir las 'malas' -> ponderar -> reescalar a 0-100.
    """
    if perfil not in PERFILES:
        raise ValueError(f"Perfil desconocido: {perfil}. Opciones: {list(PERFILES)}")
    raise NotImplementedError("Pendiente Fase 3 — cálculo del Scoring Index.")
