import requests
from typing import *

def call_API(series_id:str, offset:int = 0) -> Dict:
    print("calling series id", series_id, "with offset", offset)
    '''
    Downloads data series from singstat API. returns entire series as json
    '''
    headers = {
    'accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    } 

    url = f"https://tablebuilder.singstat.gov.sg/api/table/tabledata/{series_id}?offset={offset}&limit=3000"

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def return_data_series_json(series_id:str): 
    offset = 0
    total_data:Dict[str, Any] = {}
    while True:
        response: Dict[str, Dict] = call_API(series_id, offset)
        data_list: List[Dict] = response['Data']['row']
        if len(data_list) == 0:
            break
        else:
            start = 0
            first_dataset = data_list[0]
            if (first_dataset['rowText'] in total_data):
                total_data[first_dataset['rowText']].extend(first_dataset['columns'])
                start = 1
            for i in range(start, len(data_list)):
                total_data[data_list[i]['rowText']] = data_list[i]['columns']
        offset += 3000
    
    return total_data