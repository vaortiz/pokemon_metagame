import pokepastes_scraper as pastes
import pandas as pd
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
from time import sleep
from sqlalchemy import create_engine
import mysql.connector
#%%
mydb = mysql.connector.connect(
  host = 'localhost' ,
  port = 3306 ,
  user = 'root',
  password = '3110',
  database = 'regf_vgc',
)

host = 'localhost'
port = 3306 
user = 'root'
password = '3110'
database = 'regf_vgc'

# Crea la conexión utilizando SQLAlchemy
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

query = "SELECT * FROM fact_run WHERE Tipo_Torneo = 'Oficial' "

max_ind=pd.read_sql(query, con=engine)['ID'].iloc[-1]
max_ind


#%%
def scrape_tours(url): #función que sirve para obtener los links en vivo de cada torneo
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    data = [{'Torneo': tour.find_all('li')[2].find('a')['href']} for tour in soup.find_all('article')]
    df = pd.DataFrame(data)
    df = df.drop(range(df.index[df['Torneo'] == "2024/regional-charlotte/masters"].tolist()[0]+1, len(df)), errors='ignore')
    df['Torneo'] = "https://standings.stalruth.dev/" + df['Torneo']
    return df
#%%

tours=scrape_tours("https://standings.stalruth.dev/")
tours['Nombre_Torneo'] = tours['Torneo'].str.extract(r'https://standings.stalruth.dev/\d+/(.*?)-(.*?)/').apply(lambda x: f"{x[0].title()} {x[1].title()}", axis=1)
#%%

query2="SELECT DISTINCT Torneo FROM fact_run"
tours_select=pd.read_sql(query2, con=engine)
tours_dif=tours[~tours['Nombre_Torneo'].isin(tours_select['Torneo'])]['Torneo']
#%%

def scrape_rondas(url):
    # Realizar la solicitud GET a la página
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa (código 200)
    if response.status_code == 200:
        # Obtener el contenido HTML de la página
        html_content = response.content

        # Crear un objeto BeautifulSoup para analizar el contenido HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Encontrar todas las tablas en la página
        tables = soup.find_all('tbody')

        # Crear una lista para almacenar los datos
        data = []

        # Iterar sobre cada tabla
        for table in tables:
            # Iterar sobre cada fila de la tabla
            for row in table.find_all('tr'):
                # Encontrar la celda que contiene la información del resultado
                result_cell = row.find('td', class_='round svelte-phsp0r')
                a = row.find('td', class_='team-cell svelte-phsp0r')

                # Verificar si la celda contiene la información deseada
                if  result_cell and row.find('td', class_='name svelte-phsp0r').text.strip() == 'LATE':
                    
                    result = "DROP"

                    # Obtener el nombre del jugador
                    player_name = "DROP"
                    res = "DROP"

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Rival': player_name, 'Resultado': res})
                    
                elif  result_cell and row.find('td', class_='name svelte-phsp0r').text.strip() == 'BYE':
                    
                    result = "DROP"

                    # Obtener el nombre del jugador
                    player_name = "DROP"
                    res = "DROP"

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Rival': player_name, 'Resultado': res})
                
                elif  result_cell and a.find('a', class_='svelte-1481izn', href=True)['href'].strip() == '':
                    
                    result = "DROP"

                    # Obtener el nombre del jugador
                    player_name = "DROP"
                    res = "DROP"

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Rival': player_name, 'Resultado': res})
                
                elif result_cell and row.find('td', class_='name svelte-phsp0r').text.strip() != 'BYE' and a.find('a', class_='svelte-1481izn', href=True)['href'].strip() != '' :                    
                    
                    result = row.find('td').text.strip()
                    
                    # Obtener el nombre del jugador
                    player_name = row.find('td', class_='name svelte-phsp0r').find('a').text.strip()
                    res = row.find_all('td')[1].text.strip()

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Rival': player_name, 'Resultado': res})
                    
        df = pd.DataFrame(data)
        return df 
#%%        
def scrape_pokepast(url):
    team = pastes.team_from_url(url)
    pokemon_data = {
        "Pokemon": [],
        "Objeto": [],
        "Habilidad": [],
        "Teratipo": [],
        'Mov1': [],
        'Mov2': [],
        'Mov3': [],
        'Mov4': []
    }

    for member in team.members:
        pokemon_data["Pokemon"].append(member.species)
        pokemon_data["Objeto"].append(member.item)
        pokemon_data["Habilidad"].append(member.ability)
        pokemon_data["Teratipo"].append(member.tera_type)

        moveset = member.moveset
        moveset_length = len(moveset)
        pokemon_data['Mov1'].append(moveset[0] if moveset_length >= 1 else None)
        pokemon_data['Mov2'].append(moveset[1] if moveset_length >= 2 else None)
        pokemon_data['Mov3'].append(moveset[2] if moveset_length >= 3 else None)
        pokemon_data['Mov4'].append(moveset[3] if moveset_length >= 4 else None)

    df_pokemon = pd.DataFrame(pokemon_data)
    return df_pokemon    
#%%
def scrape_standings_oficial(url):
    options = Options()
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(executable_path=r"C:\Users\victor\Downloads\chromedriver-win64\chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    
    driver.get(url)
    sleep(10)
    html_content = driver.page_source
    
    # Close the driver
    driver.quit()
    
    # Crea un objeto BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Extraer datos
    data = []
    for row in soup.find_all('tr', {'class': 'player svelte-1krfqoo'}):
        nombre = row.find('td', class_='name').find('a').text
        enfrentamientos = row.find('td', class_='name').find('a')['href']
        equipo = row.find('td', class_='team-cell').find('a')['href']
        wins, losses = map(int, row.find('td', class_='record').text.strip().split('-'))
        
        data.append({
            'Player': nombre,
            'Rondas': enfrentamientos,
            'Equipo': equipo,
            'Wins': wins,
            'Losses': losses
        })
    
    # Crear DataFrame de pandas
    df = pd.DataFrame(data)
    
    parsed_url = urlparse(url)

    # Obtener la parte de la ruta (path)
    ruta = parsed_url.path

    # Aislar la parte "regional-knoxville"
    nombre_torneo = ruta.split('/')[2]
    nuevo_nombre = ' '.join(word.capitalize() for word in nombre_torneo.split('-'))

    df.insert(0, 'Torneo', nuevo_nombre)
    df.insert(1, 'Tipo_Torneo', 'Oficial')
    
    return df
#%%
dfs = []

# Iterar sobre los torneos
for i in range(1, len(tours_dif)+1):
    # Obtener el DataFrame para el torneo actual
    df_torneo = scrape_standings_oficial(tours_dif[len(tours_dif) - i])
    # Agregar el DataFrame a la lista
    dfs.append(df_torneo)

# Concatenar todos los DataFrames en uno solo
fact_player_tour = pd.concat(dfs, ignore_index=True)
fact_player_tour.insert(0, 'ID', range(max_ind+1, max_ind+1 + len(fact_player_tour)))
#%%

team_list = pd.DataFrame()

# Iterar sobre cada jugador en resultado_final
for i in range(0, len(fact_player_tour)):
    # Obtener el equipo del jugador actual y el ID correspondiente
    equipo_actual = fact_player_tour['Equipo'][i]
    id_actual = fact_player_tour['ID'][i]
    
    try:
        # Obtener el DataFrame para el equipo actual utilizando la función scrape_pokepast
        df_equipo = scrape_pokepast(equipo_actual)
        
        # Insertar la columna de ID en la primera posición del DataFrame del equipo actual
        df_equipo.insert(0, 'ID', pd.Series(id_actual, index=df_equipo.index, name='ID'))
        
        # Agregar el DataFrame del equipo actual al DataFrame team_list
        team_list = pd.concat([team_list, df_equipo])
    
    except Exception as e:
        print(f"Error al procesar el equipo {equipo_actual}: {e}")
        continue  # Pasar a la siguiente iteración si se produce un error

# Restablecer el índice del DataFrame resultante
team_list.reset_index(drop=True, inplace=True)
team_list.loc[team_list['Teratipo'].str.startswith('Stellar\n-'), 'Mov4'] = team_list['Teratipo'].str.split('\n-').str[1]
team_list.loc[team_list['Teratipo'].str.startswith('Stellar\n-'), 'Teratipo'] = 'Stellar'
#%%

round_list = pd.DataFrame()

# Iterar sobre cada jugador en resultado_final
for i in range(0, len(fact_player_tour)):
    # Obtener el equipo del jugador actual y el ID correspondiente
    pairings_actual = fact_player_tour['Rondas'][i]
    id_actual = fact_player_tour['ID'][i]
    
    try:
        # Obtener el DataFrame para el equipo actual utilizando la función scrape_pokepast
        df_pairings = scrape_rondas(pairings_actual)
        
        # Insertar la columna de ID en la primera posición del DataFrame del equipo actual
        df_pairings.insert(0, 'ID', pd.Series(id_actual, index=df_pairings.index, name='ID'))
        
        # Agregar el DataFrame del equipo actual al DataFrame team_list
        round_list = pd.concat([round_list, df_pairings])
    
    except Exception as e:
        print(f"Error al procesar las rondas en {pairings_actual}: {e}")
        continue  # Pasar a la siguiente iteración si se produce un error

# Restablecer el índice del DataFrame resultante
round_list.reset_index(drop=True, inplace=True)
#%%



fact_player_tour.to_sql("fact_run", con=engine, if_exists='append', index=False)

mydb.commit()

round_list.to_sql('rounds', con=engine, if_exists='append', index=False)

mydb.commit()

team_list.to_sql('team_ots', con=engine, if_exists='append', index=False)

mydb.commit()
