# metrics/ — Motor de métricas

| Módulo | Qué hace | Estado |
|---|---|---|
| `percentiles.py` | Percentil por posición (base del scouting) | 🟡 stub |
| `scoring_index.py` | Índice compuesto ponderado por perfil | 🟡 stub + metodología |
| `nuevas_metricas.py` | Métricas propias / derivadas | ⏸️ Fase 2 |

**Lectura obligatoria antes de tocar `scoring_index.py`:**
los composite scores tienen riesgos conocidos (ocultan el "cómo", sensibles a la
elección de métricas y pesos). El índice se entrega SIEMPRE acompañado de los
percentiles que lo componen, nunca como número mágico aislado.
Ref: Marc Lamberts — "The risks of using composite scores in data scouting".
