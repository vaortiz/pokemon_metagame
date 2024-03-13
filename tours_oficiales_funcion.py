from sqlalchemy import create_engine
import pandas as pd
from bs4 import BeautifulSoup
import requests

host = 'localhost'
port = 3306  # Este es el puerto predeterminado para MySQL, puedes cambiarlo si es diferent
user = 'root'
password = '3110'
database = 'poke_db'

# Crea la conexión utilizando SQLAlchemy
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")

# Seleccionar todos los registros de la tabla 'main'
query = "SELECT * FROM main;"
pokedb = pd.read_sql_query(query, engine)
pokedb

pokedb['Name'] = pokedb['Name'].str.replace('^Ogrepon', 'Ogerpon', regex=True)

def scrape_pokepast(link):
    # Realizar la solicitud HTTP
    response = requests.get(link)
    
    if response.status_code != 200:
        print(f"Error: No se pudo acceder a la página. Código de estado: {response.status_code}")
        return None
    
    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Encontrar todas las secciones de Pokémon
    pokemon_sections = soup.find_all('article')
    
    data = {'Pokémon': [], 'Objeto': [], 'Habilidad': [], 'Teratipo': [], 'Mov1': [], 'Mov2': [], 'Mov3': [], 'Mov4': []}

    # Iterar sobre las secciones de Pokémon
    for pokemon_section in pokemon_sections:
        # Inicializar variables para cada Pokémon
        pokemon_data = {'Pokémon': '', 'Objeto': '', 'Habilidad': '', 'Teratipo': '', 'Mov1': '', 'Mov2': '', 'Mov3': '', 'Mov4': ''}
        
        # Encontrar todas las etiquetas span dentro de la sección de Pokémon
        span_tags = pokemon_section.find_all('span')
        
        # Verificar la cantidad de span en la sección y actuar en consecuencia
        if len(span_tags) == 9:
            # Caso con 9 span
            pokemon_data['Pokémon'] = span_tags[0].text
            pokemon_data['Objeto'] = span_tags[1].text
            pokemon_data['Habilidad'] = span_tags[2].next_sibling.strip()  
            pokemon_data['Teratipo'] = span_tags[4].text

            if '\n-' in span_tags[len(span_tags)-3].next_sibling.strip() or '\n-' in span_tags[len(span_tags)-2].next_sibling.strip() or '\n-' in span_tags[len(span_tags)-1].next_sibling.strip() : 

                mov_texts = [span_tags[len(span_tags)-3].next_sibling.strip(), span_tags[len(span_tags)-2].next_sibling.strip(), span_tags[len(span_tags)-1].next_sibling.strip()]

                movimientos = []

                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])

                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento

            else:
                pokemon_data['Mov1'] = span_tags[5].next_sibling.strip()  
                pokemon_data['Mov2'] = span_tags[6].next_sibling.strip() 
                pokemon_data['Mov3'] = span_tags[7].next_sibling.strip() 
                pokemon_data['Mov4'] = span_tags[8].next_sibling.strip() 

        elif len(span_tags) == 8:
            # Caso con 8 span
            pokemon_data['Pokémon'] = span_tags[0].text
            pokemon_data['Objeto'] = span_tags[0].next_sibling.strip()  # Texto después del primero
            pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()  # Texto después del segundo
            pokemon_data['Teratipo'] = span_tags[3].text

            if '\n-' in span_tags[len(span_tags)-3].next_sibling.strip() or '\n-' in span_tags[len(span_tags)-2].next_sibling.strip() or '\n-' in span_tags[len(span_tags)-1].next_sibling.strip() : 

                mov_texts = [span_tags[len(span_tags)-3].next_sibling.strip(), span_tags[len(span_tags)-2].next_sibling.strip(), span_tags[len(span_tags)-1].next_sibling.strip()]

                movimientos = []

                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])

                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento

            else:
                pokemon_data['Mov1'] = span_tags[4].next_sibling.strip()  # Texto después del quinto
                pokemon_data['Mov2'] = span_tags[5].next_sibling.strip()  # Texto después del sexto
                pokemon_data['Mov3'] = span_tags[6].next_sibling.strip()  # Texto después del séptimo
                pokemon_data['Mov4'] = span_tags[7].next_sibling.strip()  # Texto después del octavo


        elif len(span_tags) == 7:
            # Caso con 7 span

            if span_tags[2].text == 'Tera Type: ' and span_tags[0].next_sibling.strip()== '':  # Agregar condición adicional
                # Caso especial para 'Tera Type' con span_tags[0].previous_sibling no vacío
                # Extraer las variables específicas para este caso
                pokemon_data['Pokémon'] = span_tags[0].previous_sibling.strip().split('@')[0].strip() 
                pokemon_data['Objeto'] = span_tags[0].text  
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[3].text
                mov2_text = span_tags[4].next_sibling.strip()
                mov_texts = [span_tags[4].next_sibling.strip(), span_tags[5].next_sibling.strip(), span_tags[6].next_sibling.strip()]
                movimientos = []

                    # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                        # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                        mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                        # Agregar cada parte a la lista de movimientos
                        movimientos.extend([part.strip() for part in mov_parts])

                    # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                        pokemon_data[f'Mov{i + 1}'] = movimiento


            elif span_tags[2].next_sibling == "Stellar\n":

                # Caso especial para Teratipo "Stellar"
                # Extraer las variables como en el caso típico de longitud 7
                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[2].next_sibling.strip()
                pokemon_data['Mov1'] = span_tags[3].next_sibling.strip()  # Texto después del quinto
                pokemon_data['Mov2'] = span_tags[4].next_sibling.strip()  # Texto después del sexto
                pokemon_data['Mov3'] = span_tags[5].next_sibling.strip()  # Texto después del séptimo
                pokemon_data['Mov4'] = span_tags[6].next_sibling.strip()  # Texto después del octavo

            elif '\n-' in span_tags[len(span_tags)-3].next_sibling.strip() or '\n-' in span_tags[len(span_tags)-2].next_sibling.strip() or '\n-' in span_tags[len(span_tags)-1].next_sibling.strip() : 

                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[3].text
                mov_texts = [span_tags[len(span_tags)-3].next_sibling.strip(), span_tags[len(span_tags)-2].next_sibling.strip(), span_tags[len(span_tags)-1].next_sibling.strip()]

                movimientos = []

                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])

                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento

            elif '\n- ' in span_tags[3].next_sibling:

                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[3].text
                pokemon_data['Mov1'] = span_tags[3].next_sibling.strip()  # Texto después del quinto
                pokemon_data['Mov2'] = span_tags[4].next_sibling.strip()  # Texto después del sexto
                pokemon_data['Mov3'] = span_tags[5].next_sibling.strip()  # Texto después del séptimo
                pokemon_data['Mov4'] = span_tags[6].next_sibling.strip()  # Texto después del octavo
                
            elif span_tags[4].next_sibling.strip() == 'Sheer Cold' and span_tags[2].text == 'Tera Type: ' and span_tags[0].next_sibling.strip()!= '':
            
                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[3].text
                mov_texts = [span_tags[len(span_tags)-3].next_sibling.strip(), span_tags[len(span_tags)-2].next_sibling.strip(), span_tags[len(span_tags)-1].next_sibling.strip()]
        
                movimientos = []
        
                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]
        
                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])
        
                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento
            
            elif span_tags[0].text == 'Capsakid':
        
                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[3].text
                mov_texts = [span_tags[len(span_tags)-3].next_sibling.strip(), span_tags[len(span_tags)-2].next_sibling.strip(), span_tags[len(span_tags)-1].next_sibling.strip()]
        
                movimientos = []
        
                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]
        
                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])
        
                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento    
            
                
            else:
                # Caso típico de longitud 7
                pokemon_data['Pokémon'] = span_tags[0].previous_sibling.strip().split('@')[0].strip() 
                pokemon_data['Objeto'] = span_tags[0].previous_sibling.strip().split('@')[1].strip()  
                pokemon_data['Habilidad'] = span_tags[0].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[2].text
                pokemon_data['Mov1'] = span_tags[3].next_sibling.strip()  # Texto después del quinto
                pokemon_data['Mov2'] = span_tags[4].next_sibling.strip()  # Texto después del sexto
                pokemon_data['Mov3'] = span_tags[5].next_sibling.strip()  # Texto después del séptimo
                pokemon_data['Mov4'] = span_tags[6].next_sibling.strip()  # Texto después del octavo

        elif len(span_tags) == 6:
            
            if span_tags[0].previous_sibling is None and span_tags[2].next_sibling != "Stellar\n":
        
                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[3].text
                mov_texts = [span_tags[4].next_sibling.strip(), span_tags[5].next_sibling.strip()]

                movimientos = []

                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])

                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento
            
            elif span_tags[2].next_sibling == "Stellar\n":
        
                pokemon_data['Pokémon'] = span_tags[0].text 
                pokemon_data['Objeto'] = span_tags[0].next_sibling.strip() 
                pokemon_data['Habilidad'] = span_tags[1].next_sibling.strip()
                pokemon_data['Teratipo'] = span_tags[2].text

                mov_texts = [span_tags[3].next_sibling.strip(), span_tags[4].next_sibling.strip(), span_tags[5].next_sibling.strip()]

                movimientos = []

                # Procesar cada elemento en mov_texts
                for mov_text in mov_texts:
                    # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                    mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                    # Agregar cada parte a la lista de movimientos
                    movimientos.extend([part.strip() for part in mov_parts])

                # Asignar los movimientos a las columnas correspondientes
                for i, movimiento in enumerate(movimientos[:4]):
                    pokemon_data[f'Mov{i + 1}'] = movimiento
        
            else:    
                # Caso especial con 6 span
                pokemon_data['Pokémon'] = span_tags[0].previous_sibling.strip().split('@')[0].strip() 
                pokemon_data['Objeto'] = span_tags[0].previous_sibling.strip().split('@')[1].strip()   
                pokemon_data['Habilidad'] = span_tags[0].next_sibling.strip() # Texto después del segundo
                pokemon_data['Teratipo'] = span_tags[2].text
                 # Verificar si hay texto en span_tags[2].next_sibling.strip()
                mov2_text = span_tags[2].next_sibling.strip()

                if mov2_text:
                    # Caso donde hay un texto en span_tags[2].next_sibling.strip()
                    pokemon_data['Mov1'] = span_tags[2].next_sibling.strip()
                    pokemon_data['Mov2'] = span_tags[3].next_sibling.strip()
                    pokemon_data['Mov3'] = span_tags[4].next_sibling.strip()
                    pokemon_data['Mov4'] = span_tags[5].next_sibling.strip()

                else:
                    # Caso donde span_tags[2].next_sibling.strip() está vacío
                    mov_texts = [span_tags[3].next_sibling.strip(), span_tags[4].next_sibling.strip(), span_tags[5].next_sibling.strip()]

                    movimientos = []

                    # Procesar cada elemento en mov_texts
                    for mov_text in mov_texts:
                        # Separar por '\n-' si está presente, de lo contrario, solo agregar el texto
                        mov_parts = mov_text.split('\n-') if '\n-' in mov_text else [mov_text]

                        # Agregar cada parte a la lista de movimientos
                        movimientos.extend([part.strip() for part in mov_parts])

                    # Asignar los movimientos a las columnas correspondientes
                    for i, movimiento in enumerate(movimientos[:4]):
                        pokemon_data[f'Mov{i + 1}'] = movimiento

                # Agregar los datos a la estructura de datos
        for key, value in pokemon_data.items():
                    data[key].append(value)

    # Crear un DataFrame de pandas
    df = pd.DataFrame(data)
    # Removemos los @
    df['Objeto'] = df['Objeto'].str.replace('^@', '', regex=True)
    
    # Completamos los teratipos
    for index, row in df.iterrows():
    # Verifica si el valor en la columna "Teratipo" es "-"
        if row['Teratipo'] == '-':
            # Verifica las excepciones
            if row['Pokémon'] == 'Ogerpon-Wellspring':
                teratipo_value = 'Water'
            elif row['Pokémon'] == 'Ogerpon-Hearthflame':
                teratipo_value = 'Fire'
            elif row['Pokémon'] == 'Ogerpon-Cornerstone':
                teratipo_value = 'Rock'
            else:
                # Busca una coincidencia en la columna "Name" de pokedb
                matching_row = pokedb[pokedb['Name'] == row['Pokémon']]

                # Verifica si se encontró una coincidencia
                if not matching_row.empty:
                    # Obtiene el valor de la columna "Type1" de la primera coincidencia
                    teratipo_value = matching_row.iloc[0]['Type1']

                # Rellena la columna "Teratipo" en pokemon_data con el valor encontrado
            df.at[index, 'Teratipo'] = teratipo_value

    df_stacked=df.stack().to_frame().T
    df_stacked.columns = [f'{col[0]}_{col[1]}' for col in df_stacked.columns]

    return df_stacked

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
                    data.append({'Ronda': result, 'Nombre': player_name, 'Resultado': res})
                    
                elif  result_cell and row.find('td', class_='name svelte-phsp0r').text.strip() == 'BYE':
                    
                    result = "DROP"

                    # Obtener el nombre del jugador
                    player_name = "DROP"
                    res = "DROP"

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Nombre': player_name, 'Resultado': res})
                
                elif  result_cell and a.find('a', class_='svelte-1481izn', href=True)['href'].strip() == '':
                    
                    result = "DROP"

                    # Obtener el nombre del jugador
                    player_name = "DROP"
                    res = "DROP"

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Nombre': player_name, 'Resultado': res})
                
                elif result_cell and row.find('td', class_='name svelte-phsp0r').text.strip() != 'BYE' and a.find('a', class_='svelte-1481izn', href=True)['href'].strip() != '' :                    
                    
                    result = row.find('td').text.strip()
                    
                    # Obtener el nombre del jugador
                    player_name = row.find('td', class_='name svelte-phsp0r').find('a').text.strip()
                    res = row.find_all('td')[1].text.strip()

                    # Agregar los datos a la lista
                    data.append({'Ronda': result, 'Nombre': player_name, 'Resultado': res})
                    

        # Crear un DataFrame con los datos
        df = pd.DataFrame(data)
        pr2=df[::-1]
        pr2.reset_index(drop=True, inplace=True)
        pr3=pr2.drop("Ronda", axis=1)
        pr3['Nombre']=pr3['Nombre'].str.replace(r'\[.*?\]', '', regex=True)
        pr4=pd.DataFrame(pr3.values.flatten()).T
        
        columnas_nuevas_1 = [f'Ronda_{i+1}' for i in range(pr3.shape[0])]
        columnas_nuevas_2 = [f'Resultado_{i+1}' for i in range(pr3.shape[0])]
        columnas_nuevas=[columna for par in zip(columnas_nuevas_1, columnas_nuevas_2) for columna in par]
        pr4.columns = columnas_nuevas

        # Mostrar el DataFrame
        return pr4
    else:
        print(f"No se pudo acceder a la URL: {url}")


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse
from time import sleep

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
            'Nombre': nombre,
            'Enfrentamientos': enfrentamientos,
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
    
    df.insert(0, 'Torneo', nombre_torneo)
    df.insert(1, 'Tipo_Torneo', 'Oficial')
    
    df['Nacionalidad'] = df['Nombre'].str.extract(r'\[([A-Z]+)\]')
    df['Nombre'] = df['Nombre'].str.replace(r'\s*\[.*\]\s*', '', regex=True)
    
    # Crea una copia del DataFrame con la columna 8 eliminada
    columna_8 = df.pop(df.columns[7])

    # Inserta la columna en la posición 4
    df.insert(3, columna_8.name, columna_8)
    
    # Añadiendo los pokepastes  
    aw = pd.DataFrame()
    for enlace in df['Equipo']:
        # Aplicar la función de scraping a cada enlace
        resultado_scrape = scrape_pokepast(enlace)

        # Concatenar el resultado al DataFrame aw
        aw = pd.concat([aw, resultado_scrape])
    
    aw.reset_index(drop=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df2= pd.concat([df.iloc[:, :4], aw, df.iloc[:, 4:]], axis=1)    
    
    # añadiendo el detalle de las rondas
    
    aw2 = pd.DataFrame()
    for enlace in df['Enfrentamientos']:
        # Aplicar la función de scraping a cada enlace
        resultado_scrape = scrape_rondas(enlace)

        # Concatenar el resultado al DataFrame aw
        aw2 = pd.concat([aw2, resultado_scrape])
    
    aw2.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=True, inplace=True)
    df3= pd.concat([df2.iloc[:, :52], aw2, df2.iloc[:, 52:]], axis=1) 
    
    return df3

siete=scrape_standings_oficial("https://standings.stalruth.dev/2024/special-utrecht/masters/")
