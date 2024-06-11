import requests
from typing import Dict, List
from .classes import TotalDownload, UnTransformed, KVPairList

def call_API(series_id:str, offset:int = 0) -> UnTransformed:
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
    return UnTransformed(**response.json())

def return_data_series_json(series_id:str) -> Dict[str, KVPairList]: 
    offset = 0
    total_data:Dict[str, KVPairList] = {}
    while True:
        
        response:UnTransformed = call_API(series_id, offset)
        data_detail = TotalDownload.DataDetail(**response.Data)
        try:
            data_count = int(response.DataCount)
            status_code = int(response.StatusCode)
            message = str(response.Message)
        except ValueError:
            break  # or handle conversion error

        currTotal = TotalDownload(
            Data=data_detail, 
            DataCount=data_count, 
            StatusCode=status_code, 
            Message=message
        )

       

        
        curr_data: List[TotalDownload.DataDetail.DataDetailRow] = currTotal.Data.row
        if len(curr_data) == 0:
            break
        else:
            start = 0
            first_dataset = curr_data[0]
            if (first_dataset.rowText in total_data):
                total_data[first_dataset.rowText].extend(first_dataset.columns) # if the element was cut off during download, add the data to the old one and set start to 1 (to skip the first one which was cut off)
                start = 1
            for i in range(start, len(curr_data)):
                total_data[curr_data[i].rowText] = curr_data[i].columns
        offset += 3000
    
    return total_data