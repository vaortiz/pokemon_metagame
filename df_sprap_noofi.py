import requests
import pandas as pd
import re
#%%
def obtener_datos_lista(torneo_id):
    url = f"https://play.limitlesstcg.com/api/tournaments/{torneo_id}/standings"
    api_key = "1e7f7868e9d5277dcfcac6c15fbd0ec2"
    headers = {"X-Access-Key": api_key}
    
    response = requests.get(url, headers=headers)
    json_data = response.json()
    
    datos_player = pd.DataFrame(json_data)
    part1 = datos_player[['player', 'country', 'decklist', 'record']]
    
    a = pd.concat([part1, pd.json_normalize(part1['record'])[['wins', 'losses']]], axis=1).drop('record', axis=1)

    pokemon = pd.DataFrame()

    for index, row in a.iterrows():
        expanded_df = row['decklist']
        new_row = {}

        for i in range(len(expanded_df)):
            new_row[f'{i}_Pokémon'] = expanded_df[i]['name']
            new_row[f'{i}_Objeto'] = expanded_df[i]['item']
            new_row[f'{i}_Habilidad'] = expanded_df[i]['ability']
            new_row[f'{i}_Teratipo'] = expanded_df[i]['tera']
            
            # Verificar si la lista de ataques tiene al menos 4 elementos
            attacks = expanded_df[i].get('attacks', [])
            new_row[f'{i}_Mov1'] = attacks[0] if len(attacks) > 0 else None
            new_row[f'{i}_Mov2'] = attacks[1] if len(attacks) > 1 else None
            new_row[f'{i}_Mov3'] = attacks[2] if len(attacks) > 2 else None
            new_row[f'{i}_Mov4'] = attacks[3] if len(attacks) > 3 else None

        pokemon = pd.concat([pokemon, pd.DataFrame([new_row])], ignore_index=True)

    a = pd.concat([a, pokemon], axis=1)
    a=a.drop('decklist', axis=1)
    column_order = [col for col in a.columns if col not in ['wins', 'losses']] + ['wins', 'losses']
    a = a[column_order]
    return a

a=obtener_datos_lista("6601700561164605cc78dca5")
#%%
def obtener_datos_rondas(torneo_id):
    # URL del torneo
    api_key = "1e7f7868e9d5277dcfcac6c15fbd0ec2"
    url_torneo = f"https://play.limitlesstcg.com/api/tournaments/{torneo_id}/pairings"
    
    # Incluye la clave de acceso como encabezado HTTP
    headers = {"X-Access-Key": api_key}
    
    # Realiza la solicitud para obtener los datos de las rondas
    response = requests.get(url_torneo, headers=headers)
    json_data = response.json()
    datos_rondas = pd.DataFrame(json_data)
    
    # Crear un nuevo DataFrame para almacenar la información de las rondas
    rondas = pd.DataFrame()
    
    # Filtrar la fase 1
    datos_rondas_fase1 = datos_rondas[datos_rondas['phase'] == 1]

    # Filtrar la fase 2
    datos_rondas_fase2 = datos_rondas[datos_rondas['phase'] == 2]

    # Procesar la fase 1
    lista_rondas = []
    for jugador in set(datos_rondas_fase1['player1'].unique()).union(set(datos_rondas_fase1['player2'].unique())):
        enfrentamientos = datos_rondas_fase1[(datos_rondas_fase1['player1'] == jugador) | (datos_rondas_fase1['player2'] == jugador)]
        info_rondas = {'Nombre': jugador}

        for index, enfrentamiento in enfrentamientos.iterrows():
            ronda_actual = enfrentamiento['round']
            resultado = enfrentamiento['winner']
            rival = enfrentamiento['player2'] if enfrentamiento['player1'] == jugador else enfrentamiento['player1']
            info_rondas[f'Ronda_{int(ronda_actual)}'] = rival
            info_rondas[f'Resultado_{int(ronda_actual)}'] = resultado

        lista_rondas.append(info_rondas)

    # Procesar la fase 2
    jugadores2 = set(datos_rondas_fase2['player1'].unique()).union(set(datos_rondas_fase2['player2'].unique()))
    pattern = re.compile(r'([^-]+)-')
    top_types = set([pattern.match(top).group(1) for top in datos_rondas_fase2[datos_rondas_fase2['match'].str.startswith('T')]['match']])
    top_types=sorted(top_types, key=lambda x: int(re.search(r'\d+', x).group()), reverse=True)
    lista_rondas_fase2 = []

    for jugador in jugadores2:
        enfrentamientos = datos_rondas_fase2[(datos_rondas_fase2['player1'] == jugador) | (datos_rondas_fase2['player2'] == jugador)]
        info_rondas = {'Nombre': jugador}

        for index, enfrentamiento in enfrentamientos.iterrows():
            ronda_actual = enfrentamiento['round']
            resultado = enfrentamiento['winner']
            rival = enfrentamiento['player2'] if enfrentamiento['player1'] == jugador else enfrentamiento['player1']
            posicion_top = top_types.index(pattern.match(enfrentamiento['match']).group(1))
            nueva_ronda = int(posicion_top + max(datos_rondas_fase1['round']) + 1)

            info_rondas[f'Ronda_{nueva_ronda}'] = rival
            info_rondas[f'Resultado_{nueva_ronda}'] = resultado

        lista_rondas_fase2.append(info_rondas)

    # Concatenar la lista de diccionarios de ambas fases en un DataFrame
    rondas_fase1 = pd.concat([pd.DataFrame([x]) for x in lista_rondas], ignore_index=True)
    rondas_fase2 = pd.concat([pd.DataFrame([x]) for x in lista_rondas_fase2], ignore_index=True)

    # Juntar los DataFrames de ambas fases en uno solo
    # Juntar los DataFrames por la columna 'Nombre'
    rondas = pd.merge(rondas_fase1, rondas_fase2, on='Nombre', how='outer')

    # Devolver el DataFrame final
    return rondas
a=obtener_datos_rondas("6601700561164605cc78dca5")
#%%
url = "https://play.limitlesstcg.com/api/tournaments"
api_key = "1e7f7868e9d5277dcfcac6c15fbd0ec2"


# Incluye la clave de acceso como encabezado HTTP
headers = {
    "X-Access-Key": api_key
}

# Parámetros de consulta opcionales (por ejemplo, limit para especificar la cantidad de resultados)
params = {
    "limit": 100,
    "game": "VGC",
    'format': 'SVF'
}

# Realizar una solicitud GET a la API con encabezados y parámetros de consulta
response = requests.get(url, headers=headers, params=params)
response

data = response.json()

tours = pd.DataFrame(data)[pd.DataFrame(data)['players'] > 80][['id', 'name']]

#%%
def combinar_datos_torneos(tours):
    # Crear un DataFrame vacío para almacenar los resultados
    resultados = pd.DataFrame()

    for index, row in tours.iterrows():
        torneo_id = row['id']
        nombre_torneo = row['name']

        # Obtener datos de la lista y las rondas para el torneo actual
        df_lista = obtener_datos_lista(torneo_id)
        df_rondas = obtener_datos_rondas(torneo_id)

        # Agregar las columnas adicionales
        df_lista['Torneo'] = nombre_torneo
        df_lista['Tipo_torneo'] = 'No-Oficial'

        # Combina los DataFrames y agrega los resultados al DataFrame principal
        resultado_torneo = pd.merge(df_lista, df_rondas, left_on='player', right_on='Nombre', how='inner').drop('Nombre', axis=1)
        resultados = pd.concat([resultados, resultado_torneo], ignore_index=True)

    return resultados

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

resultados_torneos = combinar_datos_torneos(tours)
print(resultados_torneos)

resultados_torneos.to_excel("no_ofi.xlsx", index= False)
tours
