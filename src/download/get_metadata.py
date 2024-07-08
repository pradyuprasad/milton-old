import requests
from .classes import RawMetaData, ProcessedMetaData

def get_metadata(series_id:str) ->  ProcessedMetaData:
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
    output: RawMetaData = RawMetaData(**response.json())
    return process_metadata(output)

def process_metadata(raw: RawMetaData) -> ProcessedMetaData:
    processed_data = ProcessedMetaData(
        Data=ProcessedMetaData.MetaDataDetails(
            **raw.Data
        ),
        DataCount=raw.DataCount,
        StatusCode=raw.StatusCode,
        Message=raw.Message
    )
    return processed_data
 