import requests
import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
import re
import json
#%%
def obtener_datos_lista(torneo_id):
    url = f"https://play.limitlesstcg.com/api/tournaments/{torneo_id}/standings"
    api_key = "1e7f7868e9d5277dcfcac6c15fbd0ec2"
    headers = {"X-Access-Key": api_key}
    
    response = requests.get(url, headers=headers)
    json_data = response.json()
    
    datos_player = pd.DataFrame(json_data)
    part1 = datos_player[['player','decklist', 'record']]
    
    a = pd.concat([part1, pd.json_normalize(part1['record'])[['wins', 'losses']]], axis=1).drop('record', axis=1)

    return a
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
tours
#%%

def combinar_datos_torneos(tours):
    # Crear un DataFrame vacío para almacenar los resultados
    resultados = pd.DataFrame()
    for index, row in tours.iterrows():
        torneo_id = row['id']
        nombre_torneo = row['name']

        # Obtener datos de la lista y las rondas para el torneo actual
        df_lista = obtener_datos_lista(torneo_id)
        
        # Agregar las columnas adicionales
        df_lista.insert(0, 'Torneo', nombre_torneo)
        df_lista.insert(1, 'Tipo_Torneo', 'No-Oficial')
        df_lista.rename(columns={'wins': 'Wins', 'losses': 'Losses', 'decklist': 'Equipo', 'player': 'Player'}, inplace=True)
        df_lista.insert(3, 'Rondas', f'https://play.limitlesstcg.com/api/tournaments/{torneo_id}/pairings')
        # Combina los DataFrames y agrega los resultados al DataFrame principal
        resultados = pd.concat([resultados, df_lista], ignore_index=True)
        
    id_sequence = [f'NOf-{i+1001}' for i in range(len(resultados))]
    resultados.insert(0,'ID',id_sequence)
    return resultados

fact_run=combinar_datos_torneos(tours)

#%%
res=pd.DataFrame()
for i in range(0,len(fact_run)):
    d=pd.DataFrame(fact_run['Equipo'][i])
    d['ID'] = fact_run['ID'][i]
    d=d[['ID','name','item','ability','tera','attacks']]
    res=pd.concat([res, d], ignore_index=True)

res[['Mov1', 'Mov2', 'Mov3', 'Mov4']] = res['attacks'].apply(pd.Series)
res=res[['ID', 'name','item','ability','tera', 'Mov1', 'Mov2', 'Mov3', 'Mov4']]
team_ots=res.rename(columns={'name': 'Pokemon', 'item': 'Objeto', 'ability': 'Habilidad', 'tera': 'Teratipo'})

#%% 
api_key = "1e7f7868e9d5277dcfcac6c15fbd0ec2"
headers = {"X-Access-Key": api_key}
uni_torn=fact_run['Rondas'].unique()

def rondas_torneo(url_torneo):
    response = requests.get(url_torneo, headers=headers)
    json_data = response.json()
    datos_rondas = pd.DataFrame(json_data)
    df2 = datos_rondas[['round', 'winner', 'player1', 'player2', 'match']]
    df2.loc[~df2['match'].isna(), 'round'] = df2['match']
    return df2

dicc_torneos = {}

for i in range(len(uni_torn)):
    df = rondas_torneo(uni_torn[i])
    dicc_torneos[uni_torn[i]] = df    

#%%
rounds = pd.DataFrame()

def process_round(i):
    url_torneo = fact_run['Rondas'][i]
    datos_rondas = dicc_torneos.get(url_torneo)
    df2 = datos_rondas[['round', 'winner', 'player1', 'player2', 'match']]
    df2.loc[~df2['match'].isna(), 'round'] = df2['match']
    df3 = df2[(df2['player1'] == fact_run['Player'][i]) | (df2['player2'] == fact_run['Player'][i])]
    df3['Rival'] = df3.apply(lambda row: row['player1'] if row['player2'] == fact_run['Player'][i] else row['player2'], axis=1)
    df3['Resultado'] = df3.apply(lambda row: 'Win' if row['winner'] == fact_run['Player'][i] else 'Loss', axis=1)
    df3['ID'] = fact_run['ID'][i]
    df4 = df3[['ID', 'round', 'Rival', 'Resultado']]
    df4.rename(columns={'round': 'Ronda'}, inplace=True)
    df4.loc[df4['Rival'].isna(), ['Rival', 'Resultado', 'Ronda']] = 'DROP'
    return df4

for i in range(0, len(fact_run)):
    df=process_round(i)
    rounds = pd.concat([rounds, df], ignore_index=True)
#%%


def semantic_layer_rounds(df):
    df['Ronda'] = df['Ronda'].replace(to_replace={
        r'^T4-.+': 'Top 4',
        r'^T8-.+': 'Top 8',
        r'^T2-.+': 'Finals',
        r'^T16-.+': 'Top 16',
        r'^T32-.+': 'Top 32'
    }, regex=True)
    return df

semantic_layer_rounds(rounds)


#%%    	

def semantic_layer_ots(nombre):
    # Diccionario de mapeo para los prefijos
    mapeo_prefijos = {
        'Alolan': 'Alola',
        'Galarian': 'Galar',
        'Hisuian': 'Hisui',
        'Paldean': 'Paldea'
    }
    
    # Expresión regular para capturar los prefijos
    regex_prefijos = re.compile(r'\b(Alolan|Galarian|Hisuian|Paldean)\b')
    
    # Verificar si el nombre contiene alguno de los prefijos específicos
    if regex_prefijos.search(nombre):
        # Buscar coincidencias con los prefijos y reemplazarlos según el mapeo
        nombre_transformado = regex_prefijos.sub(lambda match: mapeo_prefijos.get(match.group(0)), nombre)
        
        # Reorganizar el nombre para poner la segunda palabra en el primer lugar y separarlas con un guión
        partes = nombre_transformado.split(' ')
        
        # Verificar si hay al menos dos partes después de dividir el nombre
        if len(partes) >= 2:
            nombre_final = partes[1] + '-' + partes[0]
        else:
            # Si no hay suficientes partes, devolver el nombre original
            nombre_final = nombre
    else:
        # Si el nombre no contiene prefijos específicos, dejarlo sin cambios
        nombre_final = nombre
    
    # Realizar transformaciones adicionales
    transformaciones_adicionales = {
        'Bloodmoon Ursaluna': 'Ursaluna-Bloodmoon',
        'Cornerstone Mask Ogerpon': 'Ogerpon-Cornerstone',
        'Hearthflame Mask Ogerpon': 'Ogerpon-Hearthflame',
        'Wellspring Mask Ogerpon': 'Ogerpon-Wellspring',
        'Enamorus Therian': 'Enamorus-Therian',
        'Indeedee ♀': 'Indeedee-F',
        'Landorus Therian': 'Landorus-Therian',
        'Tauros-Paldea': 'Tauros-Paldea-Aqua',
        'Rapid Strike Urshifu': 'Urshifu-Rapid-Strike',
        'Tatsugiri Droopy Form': 'Tatsugiri-Droopy',
        'Tatsugiri Stretchy Form': 'Tatsugiri-Stretchy',
        'Thundurus Therian': 'Thundurus-Therian',
        'Wash Rotom': 'Rotom-Wash',
        'Heat Rotom': 'Rotom-Heat'
    }
    
    # Verificar si el nombre está en las transformaciones adicionales y aplicarlas si es necesario
    if nombre_final in transformaciones_adicionales:
        nombre_final = transformaciones_adicionales[nombre_final]
    
    return nombre_final


# Aplicar la función transformar_nombre a la columna 'Pokemon'
team_ots['Pokemon'] = team_ots['Pokemon'].apply(semantic_layer_ots)

fact_run['Equipo']

fact_run['Equipo']=pd.Series([float('nan')] * len(fact_run))
#%%

mydb = mysql.connector.connect(
  host = 'localhost' ,
  port = 3306 ,
  user = 'root',
  password = '3110',
  database = 'regf_vgc',
)
#%%
host = 'localhost'
port = 3306 
user = 'root'
password = '3110'
database = 'regf_vgc'

cursor = mydb.cursor()

# Definir la consulta SQL para filtrar los datos
query2 = """
    SELECT *
    FROM fact_run AS fr
    JOIN rounds AS r ON fr.id = r.fact_run_id
    JOIN team_ots AS tots ON fr.team_ots_id = tots.id
    WHERE fr.Tipo_Torneo = 'Oficial'
"""

# Ejecutar la consulta
cursor.execute(query2)
data = cursor.fetchall()

# Eliminar los datos existentes en las tablas
cursor.execute("DELETE FROM fact_run")
cursor.execute("DELETE FROM rounds")
cursor.execute("DELETE FROM team_ots")

# Insertar los nuevos datos en las tablas
for row in data:
    cursor.execute("INSERT INTO fact_run VALUES (%s, %s, %s, ...)", row[:len(fact_run.columns)])
    cursor.execute("INSERT INTO rounds VALUES (%s, %s, %s, ...)", row[len(fact_run.columns):len(fact_run.columns) + len(rounds.columns)])
    cursor.execute("INSERT INTO team_ots VALUES (%s, %s, %s, ...)", row[len(fact_run.columns) + len(rounds.columns):])

# Confirmar los cambios
mydb.commit()

# Cerrar la conexión
cursor.close()

# Crea la conexión utilizando SQLAlchemy
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

fact_run.to_sql("fact_run", con=engine, if_exists='append', index=False)

mydb.commit()

rounds.to_sql('rounds', con=engine, if_exists='append', index=False)

mydb.commit()

team_ots.to_sql('team_ots', con=engine, if_exists='append', index=False)

mydb.commit()

mydb.close()

