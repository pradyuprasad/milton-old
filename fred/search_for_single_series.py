import instructor
import sqlite3
from pydantic import BaseModel
from .database import Database, DatabaseConnectionError
import os
from typing import List, Dict
from .config import config, APIKeyNotFoundError
from openai import OpenAI
from groq import Groq

class Keywords(BaseModel):
    word: List[str]



try:
    FRED_API_KEY = config.get_api_key('FRED_API_KEY')
    OPENAI_API_KEY = config.get_api_key("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    client = Groq(api_key=config.get_api_key("GROQ_API_KEY"))
    instructor_client = instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
except APIKeyNotFoundError as e:
    raise e




try:
    FRED_API_KEY = config.get_api_key('FRED_API_KEY')
    OPENAI_API_KEY = config.get_api_key("OPENAI_API_KEY")
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    instructor_client = instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
except APIKeyNotFoundError as e:
    raise e


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

print("please enter your query")
query = input()
keyword_list = extract_keyword(query)
print(keyword_list)