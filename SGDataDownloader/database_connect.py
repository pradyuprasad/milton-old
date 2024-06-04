from dotenv import load_dotenv
import os
import libsql_experimental as libsql

## config env vars
load_dotenv()  
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")
conn = libsql.connect("econ-data-gpt.db", sync_url=url, auth_token=auth_token, sync_interval=30)


def make_table():
    conn.execute('''CREATE TABLE dataDetails(
   file_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    file_path TEXT NOT NULL,
    data_type TEXT CHECK(data_type IN ('Real_GDP', 'Nominal_GDP', 'Unemployment', 'Consumer_Price_Index')),
    seasonally_adjusted INTEGER CHECK(seasonally_adjusted IN (0, 1)),
    sector_level TEXT,
    country TEXT,
    sector_name TEXT,
    parent TEXT, 
    frequency TEXT CHECK(frequency IN ('monthly', 'quarterly', 'annual'))
                 
)''')

    conn.commit()
    conn.sync()

def drop_table():
    conn.execute("DROP TABLE dataDetails")


def insert_elements(file_path:str, data_type:str, seasonally_adjusted:bool, sector_level:str, country:str, sector_name:str, parent:str, frequency:str):
   
    if seasonally_adjusted:
       seasonally_adjusted_int = 1
    else:
        seasonally_adjusted_int = 0
        
    sql_statement = f''' REPLACE INTO dataDetails (file_path, data_type, seasonally_adjusted, sector_level, country, sector_name, parent, frequency)
    
    VALUES ('{file_path}', '{data_type}', {seasonally_adjusted_int}, '{sector_level}', '{country}', '{sector_name}', '{parent}', '{frequency}')''' 
    print(sql_statement)
    conn.execute(sql_statement)
    conn.sync()
    conn.commit()
