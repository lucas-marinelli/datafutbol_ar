# dashboards/ — Apps de consulta (Streamlit)

Tres dashboards, un público cada uno (ver el plan maestro):

| App | Para qué | Usuario |
|---|---|---|
| `app_scouting.py` | Buscar jugadores por perfil + Scoring Index | Yo / clubes |
| `app_rendimiento.py` | Rendimiento de un jugador/equipo en la temporada | Análisis / posts |
| `app_informativo.py` | Consultas estadísticas rápidas y comparativas | Contenido IG/X |

Todas leen de `../db/futbol.duckdb` y reusan `../metrics/`.
Deploy gratis en Streamlit Cloud para tener URL pública (portfolio).
