# Proyecto Final — Curso LanusStats

**Alumno:** Lucas Marinelli · **Cuenta:** [@datafutbol_ar](https://instagram.com/datafutbol_ar) · **Email:** lucasmarinelli_12@hotmail.com

Análisis del **Mundial 2022** con datos abiertos de **StatsBomb**, librerías `pandas` / `numpy` / `matplotlib` / `mplsoccer` y la identidad visual @datafutbol_ar (Combo C).

---

## Partido y jugador elegidos

| Rol | Detalle | `match_id` |
|---|---|---|
| **Principal** (Puntos 1–5) | **Argentina 1–2 Arabia Saudita** — debut Mundial 2022 | `3857300` |
| **Comparativo** (bonus) | **Argentina 3–3 Francia** — final (penales) | `3869685` |
| **Jugador analizado** | **Lionel Messi** (juega ambos → comparativa natural) | — |
| **Punto 6** | **Mundial 2022 completo** (64 partidos) | comp `43` / season `106` |

**¿Por qué ARG–SAU y no la final?** La final está hipersaturada de análisis. El debut lo analizó casi nadie y permite una narrativa más fuerte: *"el campeón perdió su primer partido"*. Da material para 2–3 posts de IG.

---

## Cómo correrlo

1. Abrí y corré **`00_setup.ipynb`** una sola vez → descarga y **cachea** los partidos en `data/*.parquet`.
2. Después, cada `punto_N.ipynb` arranca con `from helpers import *` y lee del cache (instantáneo, sin volver a bajar de la API).

> Requiere internet solo la primera vez (el setup). El resto trabaja sobre el cache local.

---

## Estructura

```
04_Proyecto_Final_CursoLS/
├── README.md              ← este archivo (índice del proyecto)
├── helpers.py             ← rutas + estilo de marca + carga cacheada de eventos
├── 00_setup.ipynb         ← descarga y cachea los partidos (correr 1 vez)
├── punto_1.ipynb          ← P1 · Cargar partido
├── punto_2.ipynb          ← P2 · Estadísticas del partido
├── punto_3.ipynb          ← P3 · Mapas de equipos (tiros + pases)
├── punto_4.ipynb          ← P4 · Análisis individual (Messi)
├── punto_5.ipynb          ← P5 · Dashboard del partido
├── punto_6.ipynb          ← P6 · Análisis del Mundial completo
├── extras.ipynb           ← Extra 1 (pases progresivos) + Extra 2 (replicar plot doc)
├── proyecto_final.ipynb   ← notebook MAESTRO de entrega (junta todo, con narrativa)
├── data/                  ← parquet cacheado (NO va a GitHub)
└── outputs/               ← PNGs finales en alta resolución
```

`helpers.py` importa la paleta y fuentes desde `scripts/style.py` del repo (no se hardcodea nada).

---

## Estado

| Punto | Tema | Estado |
|---|---|---|
| Setup | Cache de partidos + base | ✅ listo |
| 1 | Cargar partido (API + parser) | 🟡 en revisión (migrar a base nueva) |
| 2 | Stats: xG, pases, recuperaciones, tercios | ⬜ pendiente |
| 3 | Mapas de equipos (tiros + pases) | ⬜ pendiente |
| 4 | Análisis individual — Messi | ⬜ pendiente |
| 5 | Dashboard del partido | ⬜ pendiente |
| 6 | Mundial completo (64 partidos) | ⬜ pendiente |
| Extras | Pases progresivos + replicar plot | ⬜ pendiente |

---

## Librerías

`pandas` · `numpy` · `matplotlib` · `mplsoccer` · `statsbombpy` (datos abiertos del Mundial 2022).

---

## Consignas oficiales del curso

> Entrega: email a `lanusstats@gmail.com`, asunto *"Entrega Proyecto Final - [Nombre y mail]"*, adjuntando el notebook (`.ipynb`/`.py`) + las visualizaciones (o link).

**Punto 1 — Obtener información del partido.** Obtener la info de un partido del Mundial 2022 con la API de StatsBomb (forma directa de la doc o parser de mplsoccer).

**Punto 2 — Análisis de estadísticas del partido.** Equipo con más xG; jugador con más pases; jugador con más recuperaciones; zona de la cancha (en tercios) con más toques/acciones.

**Punto 3 — Mapas de equipos.** Mapa de tiros de ambos equipos; mapa de pases de ambos equipos.

**Punto 4 — Análisis individual de jugador.** Elegir un jugador y hacer: mapa de calor, mapa de tiros, mapa de acciones (recuperaciones, pases, faltas, intercepciones).

**Punto 5 — Dashboard del partido.** Mapa de tiros y pases de ambos equipos; resultado y detalles del partido; datos sobre jugadores destacados (criterio propio).

**Punto 6 — Análisis completo del Mundial.** Eventos de todos los partidos en un dataframe (ciclos + `pd.concat`). Responder: jugador con más xG en Holanda–Ecuador; jugador con más pases intentados y completados en Inglaterra–Irán; pases intentados/completados en Marruecos–Francia. Rankings: más tiros (total y por partido), más pases completados, más recuperaciones, + uno propio. Dashboard de 3 canchas (pases, calor, tiros) de un jugador. Gráficos de dispersión: xG/tiros, pases comp./% pases, intercepciones/faltas, + uno propio.

**Extras (opcional).** Calcular pases progresivos para los dataframes de pases; elegir un gráfico de la doc de mplsoccer y replicarlo.

---

*Plan estratégico completo (8 fases, narrativa, Streamlit, entrega): `G:\Mi unidad\DATAFUTBOL_AR\00_Plan\proyecto_final_curso.md`.*
