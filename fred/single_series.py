import os
import requests
import pandas as pd
from datetime import datetime
from typing import Dict, List
from .config import config, APIKeyNotFoundError
from .database_ops import get_units, check_series_exists
from .utils import store_series
from openai import OpenAI
from groq import Groq
import subprocess
import re
import instructor
import sqlite3
from pydantic import BaseModel
from .database import Database, DatabaseConnectionError



try:
    FRED_API_KEY = config.get_api_key('FRED_API_KEY')
    OPENAI_API_KEY = config.get_api_key("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    instructor_client = instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
except APIKeyNotFoundError as e:
    raise e

class Keywords(BaseModel):
    word: List[str]

def call_groq(messages: List[Dict[str, str]], model:str="llama3-70b-8192"):
    return client.chat.completions.create(messages=messages, model=model, temperature = 0.0)

def remove_all_extras(code:str):
    messages = [
        {
            "role": "system",
            "content": '''Your job is to remove EVERYTHING THAT IS NOT CODE. REMOVE EVERYTHING THAT IS NOT CODE. IF IT IS CODE IT STAYS. SOMETIMES THE CODE HAS THINGS LIKE "here is your code" or some other useless prefix. I need you to remove it. Just give me the code that is given to you. If only code is given to you, leave it untouched. Everything you put will be a python file. So don't output anything except code. '''
        },

        {
            "role": "user",
            "content": f"The input is {code}"
        }
    ]
    output = call_groq(messages, "llama3-8b-8192").choices[0].message.content
    return re.sub(r'^```|```$', '', output, flags=re.MULTILINE)
    


def load_series_observations(series_fred_id: str, output_file: str) -> bool:
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_fred_id}&api_key={FRED_API_KEY}&file_type=json"
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        ans = response.json()
        observations = ans['observations']

        observations_data = [
            {'date': datetime.strptime(obs['date'], '%Y-%m-%d').date(), 'value': float(obs['value'])}
            for obs in observations if 'date' in obs and 'value' in obs
        ]
        print(observations_data[0])
        
        # Convert list of dictionaries to DataFrame
        df = pd.DataFrame(observations_data)
        
        # Write DataFrame to CSV
        df.to_csv(output_file, index=False)
        return True
    
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Error occurred: {e}")
        return False
    
def run_code(file_name:str, code:str):
    with open(file_name, 'w') as file:
        file.write(code)

    script_output = subprocess.run(["python3", file_name], capture_output=True, text=True)
    if script_output.returncode != 0:
        print(script_output.stderr)
    else:
        print(script_output.stdout)


        

def ask_questions_about_series(series_fred_id: str, query:str):
    try:
        output_file = f"{series_fred_id}.csv" 
        series_exists = check_series_exists(series_fred_id)
        if not series_exists:
            store_series(series_fred_id=series_fred_id)
        else:
            print("series exists")
        
        units = get_units(fred_id=series_fred_id)
        if not units:
            raise ValueError("unable to get units")
        
        load_series_observations(series_fred_id=series_fred_id, output_file=output_file)

        df = pd.read_csv(output_file)
        head = df.head()
        prompt = f'''

    You have this csv file - {output_file}. It has the schema, {head}. The date is in YYYY-MM-DD format, and the data is in float. The units of the data are {units}. Write me python code which answer's the user's question. The code should print that and that only. Do not plot anything, do not graph anything.
    '''
        completion = openai_client.chat.completions.create(messages=[
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": f"The user query is {query}"}
        ], model="gpt-4o-mini")

        code = (remove_all_extras(completion.choices[0].message.content))
        print("got code!")
        run_code("LLMGenCode/test.py", code=code)

    except Exception as e:
        print(e)
        return None

def extract_keyword(user_query:str) -> Keywords:
    return instructor_client.chat.completions.create(model="gpt-4o-mini", response_model=Keywords, messages=[
        {"role": "user", "content": f"Pick keywords which I should input into my search box to search for this query: {user_query}. Return keywords that might give the answer. I will be doing a normal text search for string matching for datasets. So be wary of acronyms, include the full forms as well. Give me only your best 3 and nothing more. Just 3"}
    ])

def get_top_n_series(n:int = 100) -> List[Dict[str, str]]:
    try:
        # Ensure the database returns rows as dictionaries
        Database.connect()  # Make sure the connection is established
        Database._connection.row_factory = sqlite3.Row
        cursor = Database.get_cursor()

        # Fetch the top 100 series by popularity
        cursor.execute(f'''
            SELECT *
            FROM series
            ORDER BY popularity DESC
            LIMIT ?
        ''', (n,))
        
        rows = cursor.fetchall()
        
        # Convert rows to a list of dictionaries
        series_list = []
        for row in rows:
            series_list.append({
                'id': row['id'],
                'fred_id': row['fred_id'],
                'realtime_start': row['realtime_start'],
                'realtime_end': row['realtime_end'],
                'title': row['title'],
                'observation_start': row['observation_start'],
                'observation_end': row['observation_end'],
                'frequency': row['frequency'],
                'frequency_short': row['frequency_short'],
                'units': row['units'],
                'units_short': row['units_short'],
                'seasonal_adjustment': row['seasonal_adjustment'],
                'seasonal_adjustment_short': row['seasonal_adjustment_short'],
                'last_updated': row['last_updated'],
                'popularity': row['popularity'],
                'notes': row['notes']
            })
        
        return series_list
    
    except DatabaseConnectionError as e:
        print(f"Database connection error: {e}")
        return []
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return []
    finally:
        Database.close()

def search_series_by_keyword(keyword: str) -> List[Dict[str, str]]:
    series_list = get_top_n_series(n=500)
    keyword_lower = keyword.lower()
    return [series for series in series_list if keyword_lower in series['title'].lower()]

def print_series_list(series_list: List[Dict[str, str]]) -> None:
    for series in series_list:
        print(f"ID: {series['id']}")
        print(f"FRED ID: {series['fred_id']}")
        print(f"Title: {series['title']}")
        print(f"Popularity: {series['popularity']}")
        print(f"Units: {series['units']}")
        print(f"Last Updated: {series['last_updated']}")
        print(f"Notes: {series['notes']}\n")
        print("----------------------------")

# Example usage
ask_questions_about_series("UNRATE", "For how many months since the start of COVID-19 was unemployment consecutively going up? When did it stop going up and turn down. Print all the details a reader might know while reading the answer")