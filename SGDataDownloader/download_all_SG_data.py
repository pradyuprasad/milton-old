import json
from download_dataseries import return_data_series_json
from utils import series_to_csv, find_metadata
import re
from typing import *
from get_metadata import get_metadata

def main():
    file_path = "list_of_aggregations.json"
    with open(file_path, 'r') as file:
        dataseries_list = json.load(file)
    # process each list 
    for series in dataseries_list:
        # this is the actual data of the series
        output = return_data_series_json(series['dataseries_id'])

        # this is the metadata for each series
        metadata:Dict = get_metadata(series['dataseries_id'])

        # make mappings for index to series, and vice versa
        index_to_series: Dict[str, str] = {}
        series_to_index: Dict[str, str] = {}
        for series_name in (metadata['Data']['records']['row']):
            index_to_series[series_name['seriesNo']] = series_name['rowText']
            series_to_index[series_name['rowText']] = series_name['seriesNo']

        # list of subseries in each series
        new_dataset_list = list(output.keys())

        # store mappings of series name to CSV for metadata processing later
        series_name_to_csv:Dict = {}
        for i in range(len(new_dataset_list)):
            # for each subseries in new_dataset_list, write it to a csv
            dataset_name = series['internal_name']
            csv_name = dataset_name.replace(' ', '_') + '_'+ re.sub(r'_+', '_', new_dataset_list[i].replace(' ', '_').replace('-', '')) 
            series_name_to_csv[new_dataset_list[i]] = csv_name + '.csv'
            series_to_csv(csv_name, output[new_dataset_list[i]])
        
        series_list = list(series_name_to_csv.keys())
        # map CSV to metadata
        for i in range(len(series_list)):
            meta_data = find_metadata(series_list[i], index_to_series, series_to_index, series_name_to_csv)
            print(meta_data)



    return

main()
