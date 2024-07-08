from dotenv import load_dotenv
import os
import requests

# Load the FRED API key from .env file
load_dotenv()
FRED_API_KEY = os.getenv('FRED_API_KEY')

def get_all_popular_series(total_limit=1000, batch_size=1000):
    series_list = []
    offset = 0

    while len(series_list) < total_limit:
        url = f"https://api.stlouisfed.org/fred/series/search"
        params = {
            'api_key': FRED_API_KEY,
            'file_type': 'json',
            'order_by': 'popularity',
            'sort_order': 'desc',
            'limit': batch_size,
            'offset': offset,
            'search_text': '*'  # Using a wildcard
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        print(data)
        
        if 'seriess' not in data or not data['seriess']:
            break
        
        series_batch = data['seriess']
        series_list.extend(series_batch)
        offset += batch_size
    
    return series_list[:total_limit]

# Retrieve the 1000 most popular series
all_popular_series = get_all_popular_series()

# Print the retrieved series
for series in all_popular_series:
    print(series)
