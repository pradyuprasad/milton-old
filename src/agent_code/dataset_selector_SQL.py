from ..download.database_operations import DatabaseConnection
from typing import Any, Optional, List, Tuple
from groq import Groq
import os
from dotenv import load_dotenv
import re
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"),)


DB:Optional[Any] = DatabaseConnection().get_connection()
if not DB:
    raise Exception("No DB found")

def convert_SQL_answer_to_list(input: List[tuple[str]]) -> List[str]:
    return list(map(lambda x: x[0], input))

columns_raw: List[List[Tuple[int, str, str, int, str, int]]] = DB.execute('PRAGMA table_info(datasets)').fetchall()
columns_list = list(map(lambda x: (x[1], x[2]), columns_raw))
#print(columns_list)
total_datatypes: List[str] = convert_SQL_answer_to_list(DB.execute('SELECT DISTINCT dataType from datasets').fetchall())
total_levels: List[str] = convert_SQL_answer_to_list(DB.execute('SELECT DISTINCT level from datasets').fetchall())
GDP_levels = convert_SQL_answer_to_list(DB.execute('SELECT DISTINCT level FROM datasets WHERE dataType = \'REAL_GDP\'').fetchall())
GDP_frequencies = convert_SQL_answer_to_list(DB.execute('SELECT DISTINCT frequency FROM datasets WHERE dataType = \'REAL_GDP\'').fetchall())


def load_dataset_values():
     

     prompt = '''Write the SQL query and nothing but the SQL query. Your output will be given to the SQL engine right now and right here so do not write anything except a SQL query. Always have it in the format SELECT * FROM datasets WHERE dataType = [data_type], AND level=[level] AND frequency=[frequenct] AND seasonally_adjusted=[seasonally adjusted]'''

     return prompt


def get_instructions(query: str):

    prompt:str = f'''
    You are a planner whose job it is to select the right datasets (also called elements) for a given user query.  Your job is to write steps (and then a SQLite query), steps, to select the correct elements for a given user query. The table name is datasets. The columns of datasets are {columns_list}. Each row corresponds to a specific dataset (element) and contains details about it. One dataset is called an element.     

    Write detailed instructions for a ONE LINE SQL query the model should pick to get the broad CLASS of datasets to look at. Don't search for a specific sector name, (but it is ok for a sector level) or use the LIKE QUERY. Don't just write the query, but just outline your thought process and explain what to do. 

    Here are some rules you must follow
    - Unemployment is TotalEconomy only, do not ask for sector specific data.
    - For GDP AND unemployment unless otherwise instructed, you must always pick seasonally adjusted to be true. For Consumer Price Index, always pick seasonally adjusted to be false unless otherwise instructed. 
    - For general queries about the economy, always pick Real GDP seasonally adjusted, and Consumer Price Index, and Unemployment at the total economy level. 
    - More specifically, if the user asks for overall Inflation, unemployment, or the economy or inflation, for the relevant datatype, return TotalEconomy only
    - DO NOT EVER DO SECTOR_NAME= ANYTHING. DO NOT FILTER BY SECTOR_NAME AT ALL EVER! 
    - DO NOT EVER USE THE LIKE COMMAND. That is for a future step to solve!


    Datasets are part of Aggregations, which are shown below

    Let's go through the columns like this
    - frequency - This is the frequency at which this element is published
    - dataType - This refers to the dataType. The possible total_datatypes are {total_datatypes}
    - level - This refers to what level of the economy each dataset refers to. All the possible levels are {total_levels}
    - seasonally_adjusted - This is a boolean. The only values possible are 0 and 1. 1 for true and 2 for false.

    For the data_type REAL_GDP and Nominal_GDP, here are the rules:
    - Always pick REAL_GDP unless stataed otherwise
    - Always have seasonally adjusted to be True (1)
    - The levels are {GDP_levels}. No matter what the user asks, you must give quarterly. there is no option for anything else!
    - The frequencies are {GDP_frequencies}
    Here are some important descriptions about GDP's levels: GDP has 4 levels
    - TotalEconomy: This Refers to the total economy, as a whole
    - SuperSector: This always refers to some large part of the economy: Like broad general queries about only manufacturing or services.
    - Sector refers to a sector of the economy, like "Accommodation & Food Services" - a broad category which can have further subdivisions
    - SubSector is the smallest possible unit. It refers to minute industries which add to form a sector. Examples are: "Accommodation" SubSector which falls under "Accommodation & Food Services" Sector above. 

    For Consumer Price Index data sector_level values are like this. The values are more fine-grained and detailed, so do not go overly deep unless the user asks for 
    - Unlike GDP, SuperSector here refers to a moderately sized area. For example, SuperSector refers to a broad area like "Housing & Utilities" or "Communication". This is because CPI is more fine-grained data. In CPI, SuperSector covers an area of the economy, while in GDP it covers a massive sector.
    - If the user asks for a **general query** about inflation or broad categories of goods and services, select the `SuperSector` level. Examples include broad areas like "Housing & Utilities" or "Communication".
    - If the user asks for a **specific query** about a class of goods and services, select the `Sector` level. Examples include specific categories like "Clothing" and "Footwear".
    - If the user asks for a **product-level query** about detailed prices of specific products, select the `SubSector` level. Examples include detailed items like "Women’s Clothing", "Men’s Clothing", "Children’s Footwear".
    - DO NOT search for sector_name. You can search for sector_level, but never sector_name.


    Here are the compulsory rules to follow
    - When the user asks for GDP always pick real GDP. GDP is always quarterly frequency, no matter what the user asks
    - When the user asks for the state of the economy, always pick Total
    - By default the seasonally adjusted value should be true (1) unless the user specifies otherwise
    - DO NOT DO ANYTHING ELSE. FILE NAME FILTERING IS HANDLED BY A FURTHER PROCESS DOWN THE LINE
    - DO NOT DO ANY QUERY using SQL's LIKE COMMAND. THAT IS NOT ALLOWED IN THIS!
    - For unemployment, there is no sector data. Always use Total no matter what the user says
    - NEVER LIMIT ANYTHING. DO NOT USE A LIMIT EVER! YOUR JOB IS TO GIVE ALL THE RELEVANT DATA TO A FUTURE MODEL TO SELECT. DO NOT USE LIMIT IN ANY SQL STATEMENT EVER
    - If the user query is ambiguous, select file_name from datasets
    - DO NOT SELECT PARENT EVER.
    - Always write an SQLite query in the end which selects * from datasets. Always have it in the format SELECT * FROM datasets WHERE dataType = [data_type], AND level=[level] AND frequency=[frequenct] AND seasonally_adjusted=[seasonally adjusted]
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

def select_dataset(query:str, prompt:str, DB):
     SQL_query_raw = client.chat.completions.create(
          messages= [{
               "role": "system",
               "content": prompt
          }, 
          {
               "role": "user",
               "content": "The user query is:" + query
          }], 

          model="llama3-70b-8192"
     )

     clean_SQL_query = re.sub(r'^```|```$', '', SQL_query_raw.choices[0].message.content)
     print(clean_SQL_query)
     dataset_names = DB.execute(clean_SQL_query).fetchall()
     return dataset_names


    

def main():
    print("what is your query?")
    query = input()
    ans = select_datasets_using_SQL(query)
    print(ans)

def select_datasets_using_SQL(query: str):
    instructions = (get_instructions(query=query))
    print(instructions)
    prompt = load_dataset_values()
    datasets_possible = select_dataset(query=instructions, prompt=prompt, DB=DB)
    if len(datasets_possible) == 0:
        raise Exception("No datasets found")
    
    relevant_info = []
    for dataset in datasets_possible:
        relevant_info.append(dataset[9])
    return relevant_info
    



if __name__ == "__main__":
    main()