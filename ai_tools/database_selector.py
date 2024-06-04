from dotenv import load_dotenv
load_dotenv()  
from groq import Groq
import os
import libsql_experimental as libsql
import re


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)
url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")
conn = libsql.connect("econ-data-gpt.db", sync_url=url, auth_token=auth_token, sync_interval=30)
conn.sync()

all_cols = conn.execute('PRAGMA table_info(dataDetails)').fetchall()
data_types_possible = list(map(lambda x: x[0], conn.execute('SELECT DISTINCT data_type from dataDetails').fetchall()))
sector_levels_possible = list(map(lambda x: x[0], conn.execute('SELECT DISTINCT sector_level from dataDetails').fetchall()))
cols_list = []
for col in all_cols:
    cols_list.append((col[1], col[2]))





def write_dataset_picking_instructions(query:str) -> str:
    prompt = f'''
    You are a planner in a data analysis system. You are given access to a SQLite database called dataDetails which has details of all the datasets that are available to you. The columns of this database with their types are {cols_list}. Each column with an explanation is below
    - file_id is the id of each file. ignore this for now
    - file_path is the path of each file. In the plan you must ask the AI agent to focus on this along with sector_name. 
    - data_type is the type of the data. The allowed values are {data_types_possible}
    - seasonally_adjusted is an Integer showing 0 for not adjusted, and 1 for adjusted. These are the only 2 values possible 
    - sector_level is one of {sector_levels_possible}
    - Country is only Singapore
    - sector_name refers to which sector it is talking about. Focus on this along with file_path
    - frequency refers to how often the data is published. Ignore this for now.

    Not all levels of data are available for all types
    - for GDP (real and nominal) and Consumer Price Index all 3 are available
    - for Consumer Price Index only TotalEconomy is available
    Write detailed instructions for a ONE LINE SQL query the model should pick to get the broad CLASS of datasets to look at. Don't search for a specific sector name, (but it is ok for a sector level) or use the LIKE QUERY. Don't just write the query, but just outline your thought process and explain what to do. 

    Here are some rules you must follow
    - Unemployment is TotalEconomy only, do not ask for sector specific data.
    - For all values unless otherwise instructed, you must always pick seasonally adjusted to be true
    - For general queries about the economy, always pick Real GDP seasonally adjusted, and Consumer Price Index, and Unemployment at the total economy level
    - DO NOT EVER DO SECTOR_NAME= ANYTHING. DO NOT FILTER BY SECTOR_NAME AT ALL EVER! 
    - DO NOT EVER USE THE LIKE COMMAND. That is for a future step to solve!

    The data about GDP's sector_level values are like this:
    - MajorSector always refers to some large part of the economy: Like broad general queries about only manufacturing or services. For queries that ask about those two, focus on MajorSector. 
    - Sector refers to a sector of the economy, like "Accommodation & Food Services" - a broad category which can have further subdivisions
    - SubSector is the smallest possible unit. It refers to minute industries which add to form a sector. Examples are: "Accommodation" SubSector which falls under "Accommodation & Food Services" Sector above. 

    For Inflation data sector_level values are like this. The values are more fine-grained and detailed, so do not go overly deep unless the user asks for 
    - Unlike GDP, MajorData here refers to a broad area. For example MajorSectors refer to a moderately sized area like "Housing & Utilities" or "Communication". This is because CPI is more fine_grained data. In CPI, MajorSector covers an area of the economy, while in GDP it covers a massive sector.
    - Sector refers to specific classes of goods and services. It is more sepcific than MajorSector. Example are "Clothing" and "Footwear" who belong to the MajorSector "Clothing & Footwear". Remember that these instructions are for illustration only and you must never search for sector name. You can search for sector_level, but never sector_name. 
    - in Consumer Price Index, SubSector is the most specific level of data possible. For example it refers to prices pf products like "Womens Clothing", "Mens Clothing", "Childrens Footwear" etc. 
    - When in doubt, think if the user is asking for a broad class of items  (MajorSector), or a specific good and service (Sector), or a fine-grained good or service (SubSector)

    again before you write it remember that do not ever search for the sector name, and do not ever use the like command. This violates our terms of service and could shut the service down
    - The table name is dataDetails
    - Always select only 2 columns: file_path, sector_name
    - DO NOT EVER DO SECTOR_NAME= ANYTHING. DO NOT FILTER BY SECTOR_NAME AT ALL EVER! 

    '''

    instructions = client.chat.completions.create(
    messages = [
        {
            "role": "system", 
            "content": prompt

        }, 

        {
            "role": "user", 
            "content": "The user query is: " + query
        }
    ], model = "llama3-70b-8192"
    )

    return (instructions.choices[0].message.content)


def write_SQL_query(instructions:str) -> str:
    prompt = '''Write the SQL query and nothing but the SQL query. Your output will be given to the SQL engine right now and right here so do not write anything except a SQL query. If the user query is ambiguous, select * from datasets'''
    SQL_query_raw = client.chat.completions.create(
    messages= [{
        "role": "system",
        "content": prompt 
    }, 
    {
        "role": "user",
        "content": instructions
    }], 

    model="llama3-70b-8192"
    )

    clean_SQL_query = re.sub(r'^```|```$', '', SQL_query_raw.choices[0].message.content)
    print(clean_SQL_query)

    dataset_names = conn.execute(clean_SQL_query).fetchall()
    return dataset_names


def main():
    print("What is your query?")
    query = input()
    instructions = write_dataset_picking_instructions(query)
    print(instructions)
    dataset_names = write_SQL_query(instructions)
    print(dataset_names)
    


main()
