import requests
from typing import *

def get_metadata(series_id:str) -> Dict:
    '''
    Downloads data series from singstat API. returns entire series as json
    '''
    headers = {
    'accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    } 

    url = f"https://tablebuilder.singstat.gov.sg/api/table/metadata/{series_id}"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()