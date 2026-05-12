


INTRUCCIONES DEL CURSO

Instrucciones para la entrega:

• Envía tu proyecto al email: lanusstats@gmail.com

• Asunto del email: "Entrega Proyecto Final - [Tu Nombre y mail]"

• Adjunta tu notebook (.ipynb) o archivo de Python (.py)

• Adjunta en el mail todas las visualizaciones o compartí un link donde se puedan ver

• En lo posible, describí que partidos o jugadores usaste para el análisis

• Ejemplo muy básico de entrega

• Si tenes alguna duda o comentario sobre tu trabajo, también incluilo en el email

Nota: Tu entrega será revisada personalmente y recibirás feedback detallado sobre tu trabajo.




  *Proyecto Final del Curso*


/Librerías a usar:/
pandas
numpy
matplotlib
mplsoccer



- PUNTO 1 -
Obtener información del partido
Obtener la información de un partido del Mundial 2022 usando la API de StatsBomb. Podés usar la manera directa de la documentación o el parser de mplsoccer.

- PUNTO 2 -
Análisis de estadísticas del partido
Con la información de ese partido, averiguar:

El equipo con más xG del partido
El jugador con más pases
El jugador con más recuperaciones
La zona de la cancha (en tercios) con más toques o acciones

- PUNTO 3 -
Mapas de equipos
Mapa de tiros de ambos equipos
Mapa de pases de ambos equipos

- PUNTO 4 -
Análisis individual de jugador
Elegir un jugador y realizar:

Mapa de calor
Mapa de tiros
Mapa de acciones:
• Recuperaciones
• Pases
• Faltas
• Intercepciones


- PUNTO 5 -
Dashboard del partido
Del partido hacer un dashboard que contenga:

Mapa de tiros y mapas de pases de ambos equipos
Resultado y detalles del partido
Datos sobre jugadores destacados
(Cómo definir "destacado" queda a criterio propio: más recuperaciones, pases clave, etc.)


- PUNTO 6 -
Análisis completo del Mundial
Conseguir en un dataframe los eventos de todos los partidos del Mundial (usá ciclos y pd.concat).

Preguntas a contestar:
• ¿Quién fue el jugador del partido Holanda vs. Ecuador con más xG?

• ¿Quién fue el jugador con más pases intentados y el que más completó en Inglaterra-Irán?

• ¿Cuántos pases intentados y completados hubo en Marruecos vs. Francia?

Rankings a hacer:

• Más tiros (total y por partido)
• Más pases completados
• Más recuperaciones
• Cualquier otro ranking que te guste.
Dashboard de 3 canchas:
Resaltando un jugador con su:

• Mapa de pases
• Mapa de calor
• Mapa de tiros
Gráficos de dispersión sobre jugadores:
• xG total / tiros totales
• Pases comp / % de pases
• Intercepciones / faltas
• Cualquier otro gráfico de dispersión que te guste.



- PUNTO EXTRAS (Opcional) -
Calcular pases progresivos para los dataframes de pases que se puedan generar
Elegir un gráfico de la documentación de mplsoccer y replicarlo
