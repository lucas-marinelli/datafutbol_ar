# Diccionario de datos — métricas de la plataforma

> Qué significa cada columna/métrica del esquema. Se completa a medida que
> entran las fuentes. Términos en español (R30). Glosario general de fútbol:
> `memory/glossary.md`.

## Convenciones
- Sufijo `_90` = la métrica por cada 90 minutos jugados (comparable entre jugadores con distinto tiempo de juego).
- Sufijo `_pct` = porcentaje (0-100).
- Sufijo `_tot` = acumulado de la temporada (sin normalizar).

## Identidad / perfil (dim_jugador)
| Campo | Significado |
|---|---|
| `pos_grupo` | ARQ / DEF / MED / DEL. Base para percentiles y Scoring Index. |
| `nacionalidad_2` | Segunda nacionalidad o pasaporte (filtro estilo Capitán FI). |

## Tiempo de juego
| Campo | Significado |
|---|---|
| `minutos` | Minutos totales en la temporada. Filtro mínimo para scouting (≥600). |
| `partidos` / `titular` | Partidos jugados / como titular. |

## Ataque
| Campo | Significado |
|---|---|
| `goles` / `asistencias` | Convertidos / asistidos. |
| `xg` / `xa` | Goles / asistencias esperadas (modelo de probabilidad). |
| `xg_90` | xG por 90'. |
| `xg_per_tiro` | Calidad media de tiro (xG ÷ tiros). |
| `toques_area_90` | Toques en el área rival por 90' (peligro/presencia). |
| `conversion` | Goles ÷ tiros (eficacia de definición). |

## Creación / progresión
| Campo | Significado |
|---|---|
| `pases_clave_90` | Pases que terminan en tiro, por 90'. |
| `pases_progresivos_90` | Pases que avanzan el juego hacia el arco rival. |
| `carries_progresivos_90` | Conducciones que progresan el balón. |
| `pct_pases` | % de pases completados. |

## Defensa
| Campo | Significado |
|---|---|
| `tackles_90` / `intercepciones_90` | Acciones defensivas por 90'. |
| `recuperaciones_90` | Recuperaciones de balón por 90'. |
| `duelos_aereos_pct` | % de duelos aéreos ganados. |
| `presion_alta_90` | Presiones en campo rival por 90'. |

## Derivadas (motor propio)
| Campo | Significado |
|---|---|
| `scoring_index` | Índice compuesto 0-100 por perfil (ver `metrics/scoring_index.py`). NO se ingesta: se calcula. |

## Métricas "malas" (se invierten en el Scoring Index)
`errores_90`, `perdidas_90`, `faltas_90` — más alto = peor.
