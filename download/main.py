# import libraries
import json
from typing import List, Dict, Any
import os
from .classes import Aggregation, KVPairList, ProcessedMetaData, DatabaseRow
from .dataset_downloader import return_data_series_json
from .json_to_csv import json_to_csv
from .get_metadata import get_metadata
from .make_metadata import make_metadata
from .utils import generate_elements_to_csv
from .database_operations import insert_database_row
count = 0

def process_aggregation(agg: Aggregation, data_dir:str) -> None:
    global count
    # 1. download the data for that SeriesId
    data_json:Dict[str, KVPairList] = return_data_series_json(agg.SeriesId)
    element_to_csv = generate_elements_to_csv(agg.InternalName, data_json)
    json_to_csv(agg=agg, data_dir=data_dir, data_json=data_json)

    metadata:ProcessedMetaData = get_metadata(agg.SeriesId)
    list_of_rows: List[DatabaseRow] =(make_metadata(elements_to_csv=element_to_csv, metadata=metadata, agg_internal_name=agg.InternalName))
    
    for row in list_of_rows:
        count += 1
        insert_database_row(row=row)

    
    print("\n\n\n")
    print("THE FINAL COUNT INSERTED IS", count)


        


def main() -> None:
    '''
    Main function to download and process all data
    '''
    print("running main")
    # set file path as absolute and not relative path
    current_dir:str = os.path.dirname(os.path.abspath(__file__))
    file_path:str = os.path.join(current_dir, 'aggregations_list.json')
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..','data')

    

    with open(file=file_path) as file:
        data: List[Dict[str, str]] = json.load(file)
        
    for aggregation in data:
        curr_aggregation:Aggregation =  Aggregation(**aggregation)
        process_aggregation(curr_aggregation, data_dir)


    
if __name__ == "__main__":
    main()

    