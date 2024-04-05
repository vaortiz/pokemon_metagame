import pandas as pd
import polars as pl
from sqlalchemy import create_engine



host = 'localhost'
port = 3306 
user = 'root'
password = '3110'
database = 'regf_vgc'

# Crea la conexión utilizando SQLAlchemy
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}")


query = '''

SELECT 
    ID ,
    MAX(CASE WHEN rn = 1 THEN Pokemon ELSE NULL END) AS Pokemon_1 , 
    MAX(CASE WHEN rn = 1 THEN Objeto ELSE NULL END) AS Objeto_1 , 
    MAX(CASE WHEN rn = 1 THEN Habilidad ELSE NULL END) AS Habilidad_1 , 
    MAX(CASE WHEN rn = 1 THEN Teratipo ELSE NULL END) AS Teratipo_1 , 
    MAX(CASE WHEN rn = 1 THEN Mov1 ELSE NULL END) AS Mov1_1,
    MAX(CASE WHEN rn = 1 THEN Mov2 ELSE NULL END) AS Mov2_1,
    MAX(CASE WHEN rn = 1 THEN Mov3 ELSE NULL END) AS Mov3_1,
    MAX(CASE WHEN rn = 1 THEN Mov4 ELSE NULL END) AS Mov4_1,
    MAX(CASE WHEN rn = 2 THEN Pokemon ELSE NULL END) AS Pokemon_2,
    MAX(CASE WHEN rn = 2 THEN Objeto ELSE NULL END) AS Objeto_2,
    MAX(CASE WHEN rn = 2 THEN Habilidad ELSE NULL END) AS Habilidad_2,
    MAX(CASE WHEN rn = 2 THEN Teratipo ELSE NULL END) AS Teratipo_2,
    MAX(CASE WHEN rn = 2 THEN Mov1 ELSE NULL END) AS Mov1_2,
    MAX(CASE WHEN rn = 2 THEN Mov2 ELSE NULL END) AS Mov2_2,
    MAX(CASE WHEN rn = 2 THEN Mov3 ELSE NULL END) AS Mov3_2,
    MAX(CASE WHEN rn = 2 THEN Mov4 ELSE NULL END) AS Mov4_2,
    MAX(CASE WHEN rn = 3 THEN Pokemon ELSE NULL END) AS Pokemon_3,
    MAX(CASE WHEN rn = 3 THEN Objeto ELSE NULL END) AS Objeto_3,
    MAX(CASE WHEN rn = 3 THEN Habilidad ELSE NULL END) AS Habilidad_3,
    MAX(CASE WHEN rn = 3 THEN Teratipo ELSE NULL END) AS Teratipo_3,
    MAX(CASE WHEN rn = 3 THEN Mov1 ELSE NULL END) AS Mov1_3,
    MAX(CASE WHEN rn = 3 THEN Mov2 ELSE NULL END) AS Mov2_3,
    MAX(CASE WHEN rn = 3 THEN Mov3 ELSE NULL END) AS Mov3_3,
    MAX(CASE WHEN rn = 3 THEN Mov4 ELSE NULL END) AS Mov4_3,
    MAX(CASE WHEN rn = 4 THEN Pokemon ELSE NULL END) AS Pokemon_4,
    MAX(CASE WHEN rn = 4 THEN Objeto ELSE NULL END) AS Objeto_4,
    MAX(CASE WHEN rn = 4 THEN Habilidad ELSE NULL END) AS Habilidad_4,
    MAX(CASE WHEN rn = 4 THEN Teratipo ELSE NULL END) AS Teratipo_4,
    MAX(CASE WHEN rn = 4 THEN Mov1 ELSE NULL END) AS Mov1_4,
    MAX(CASE WHEN rn = 4 THEN Mov2 ELSE NULL END) AS Mov2_4,
    MAX(CASE WHEN rn = 4 THEN Mov3 ELSE NULL END) AS Mov3_4,
    MAX(CASE WHEN rn = 4 THEN Mov4 ELSE NULL END) AS Mov4_4,
    MAX(CASE WHEN rn = 5 THEN Pokemon ELSE NULL END) AS Pokemon_5,
    MAX(CASE WHEN rn = 5 THEN Objeto ELSE NULL END) AS Objeto_5,
    MAX(CASE WHEN rn = 5 THEN Habilidad ELSE NULL END) AS Habilidad_5,
    MAX(CASE WHEN rn = 5 THEN Teratipo ELSE NULL END) AS Teratipo_5,
    MAX(CASE WHEN rn = 5 THEN Mov1 ELSE NULL END) AS Mov1_5,
    MAX(CASE WHEN rn = 5 THEN Mov2 ELSE NULL END) AS Mov2_5,
    MAX(CASE WHEN rn = 5 THEN Mov3 ELSE NULL END) AS Mov3_5,
    MAX(CASE WHEN rn = 5 THEN Mov4 ELSE NULL END) AS Mov4_5,
    MAX(CASE WHEN rn = 6 THEN Pokemon ELSE NULL END) AS Pokemon_6,
    MAX(CASE WHEN rn = 6 THEN Objeto ELSE NULL END) AS Objeto_6,
    MAX(CASE WHEN rn = 6 THEN Habilidad ELSE NULL END) AS Habilidad_6,
    MAX(CASE WHEN rn = 6 THEN Teratipo ELSE NULL END) AS Teratipo_6,
    MAX(CASE WHEN rn = 6 THEN Mov1 ELSE NULL END) AS Mov1_6,
    MAX(CASE WHEN rn = 6 THEN Mov2 ELSE NULL END) AS Mov2_6,
    MAX(CASE WHEN rn = 6 THEN Mov3 ELSE NULL END) AS Mov3_6,
    MAX(CASE WHEN rn = 6 THEN Mov4 ELSE NULL END) AS Mov4_6
FROM 
    (SELECT 
        ID,
        Pokemon,
        Objeto,
        Habilidad,
        Teratipo,
        Mov1,
        Mov2,
        Mov3,
        Mov4,
        ROW_NUMBER() OVER (PARTITION BY ID ORDER BY ID) AS rn 
    FROM 
        team_ots
    ) AS sub 
GROUP BY 
    ID;
'''    

df_pandas2 = pd.read_sql(query, engine)
df_pandas2
# Convertir el DataFrame de pandas a un DataFrame de Polars
team_agrup = pl.from_pandas(df_pandas2)
team_agrup=team_agrup.select(pl.col("*").exclude("ID"))
team_agrup.write_csv("team_agrup.csv", separator= ",")


