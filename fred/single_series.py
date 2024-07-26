from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Union, Optional
from .config import config, APIKeyNotFoundError
from .models import DateValuePair, SeriesData
from .database import Database
from .database_ops import get_units, check_series_exists
from .utils import store_series
db = Database()

try:
    FRED_API_KEY = config.get_api_key('FRED_API_KEY')
    OPENAI_API_KEY = config.get_api_key("OPENAI_API_KEY")
    
except APIKeyNotFoundError as e:
    raise e


def load_series_observations(series_fred_id: str) -> Optional[List[DateValuePair]]:
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_fred_id}&api_key={FRED_API_KEY}&file_type=json"
        response = requests.get(url)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
        
        ans = response.json()
        observations = ans['observations']

        observations_data = [
            DateValuePair(date=datetime.strptime(obs['date'], '%Y-%m-%d').date(), value=float(obs['value']))
            for obs in observations if 'date' in obs and 'value' in obs
        ]
        
        # Debug print to verify date conversion
        for obs in observations_data:
            print(f"Debug: DateValuePair(date={obs.date}, value={obs.value})")

        return observations_data
    
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        print(f"Error occurred: {e}")
        return None
        

def load_all_series_data(series_fred_id: str):
    series_exists = check_series_exists(series_fred_id)
    if not series_exists:
        store_series(series_fred_id=series_fred_id)
    
    units = get_units(fred_id=series_fred_id)
    if not units:
        raise ValueError("unable to get units")
    
    observations = load_series_observations(series_fred_id=series_fred_id)
    return SeriesData(units=units, ObservationsData=observations)



# Example usage
data = load_all_series_data('UNRATE')
if data:
    print(data)
else:
    print("Failed to load series data.")
