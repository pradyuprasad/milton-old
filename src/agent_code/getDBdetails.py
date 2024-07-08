from ..download.database_operations import DatabaseConnection
from typing import Any, Optional
DB: Optional[Any]  = DatabaseConnection().get_connection()
from .utils import convert_SQL_answer_to_list
import json
import os

if not DB:
    raise Exception("Unable to load DB")

def get_all_children(parent_csv_name: str):
    query = f"SELECT ElementName from datasets where parent = '{parent_csv_name}'"
    print(f'\n {query}')

    children = DB.execute(query).fetchall()
    return children


# 1. get a list of all filePaths at the sector level (Real GDP, seasonally adjusted)
# 2. for each filePath, find all the DBs whoich have that as the parent

sectorFilePaths = (DB.execute("SELECT filePath, ElementName from datasets WHERE datatype = 'Consumer_Price_Index' AND level = 'Sector' AND seasonally_adjusted = '0'").fetchall())

print(sectorFilePaths)
children = {}
for path in sectorFilePaths:
    children[path[1]] = (convert_SQL_answer_to_list(get_all_children(path[0])))


print(children)

with open('src/agent_code/SubSectorCPI.json', 'w') as file:
    json.dump(children, file)
