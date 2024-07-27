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


# Example usage
ask_questions_about_series("UNRATE", "For how many months since the start of COVID-19 was unemployment consecutively going up? When did it stop going up and turn down. Print all the details a reader might know while reading the answer")