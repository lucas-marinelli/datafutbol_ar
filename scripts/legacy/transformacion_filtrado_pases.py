# 1. Creamos un nuevo DataFrame solo con los pases
# Esto es "Filtrado por Condición", una técnica básica de Data Engineering
df_pases = df_eventos[df_eventos['type_name'] == 'Pass'].copy()

# 2. Limpieza de columnas (de 75 nos quedamos con las vitales)
# Como no te interesa la visualización de negocio, nos enfocamos en coordenadas y técnica
columnas_tecnicas = [
    'id', 'period', 'minute', 'second', 'player_name', 
    'team_name', 'x', 'y', 'end_x', 'end_y', 'outcome_name'
]

df_pases_limpio = df_pases[columnas_tecnicas]

# 3. Verificación técnica del resultado
print(f"Total de eventos originales: {len(df_eventos)}")
print(f"Total de pases extraídos: {len(df_pases_limpio)}")
df_pases_limpio.head()