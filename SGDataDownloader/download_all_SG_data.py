import json
import re
from typing import Dict, List, Tuple
from download_dataseries import return_data_series_json
from utils import series_to_csv, find_metadata
from get_metadata import get_metadata

def load_data_series(file_path: str) -> List[Dict]:
    """Load data series identifiers from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def get_series_data(series_id: str) -> Dict:
    """Fetch the actual data for a series using its ID."""
    return return_data_series_json(series_id)

def get_series_metadata(series_id: str) -> Dict:
    """Fetch metadata for a series using its ID."""
    return get_metadata(series_id)

def create_mappings(metadata: Dict) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Create and return mappings from series numbers to names and vice versa."""
    index_to_series = {}
    series_to_index = {}
    for series_name in metadata['Data']['records']['row']:
        index_to_series[series_name['seriesNo']] = series_name['rowText']
        series_to_index[series_name['rowText']] = series_name['seriesNo']
    return index_to_series, series_to_index

def format_series_to_csv(series: Dict, index_to_series: Dict[str, str], series_to_index: Dict[str, str]) -> Dict[str, str]:
    """Generate CSV filenames and map them to their series names."""
    series_name_to_csv = {}
    for dataset_name in series.keys():
        internal_name = series['internal_name']
        csv_name = internal_name.replace(' ', '_') + '_' + re.sub(r'_+', '_', dataset_name.replace(' ', '_').replace('-', ''))
        series_name_to_csv[dataset_name] = csv_name + '.csv'
    return series_name_to_csv

def process_series_data(dataseries_list: List[Dict]):
    """Process each series in the dataseries list."""
    for series in dataseries_list:
        series_data = get_series_data(series['dataseries_id'])
        metadata = get_series_metadata(series['dataseries_id'])
        index_to_series, series_to_index = create_mappings(metadata)
        series_name_to_csv = format_series_to_csv(series_data, index_to_series, series_to_index)
        
        # Example operation (could be extended or modified)
        for dataset_name, csv_file in series_name_to_csv.items():
            series_to_csv(csv_file, series_data[dataset_name])
            meta_data = find_metadata(dataset_name, index_to_series, series_to_index, series_name_to_csv)
            
            

def main():
    dataseries_list = load_data_series("list_of_dataseries.json")
    process_series_data(dataseries_list)

if __name__ == "__main__":
    main()
