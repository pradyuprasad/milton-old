import json
import re
from typing import *
from download_dataseries import return_data_series_json
from utils import element_to_csv_convertor, find_metadata
from get_metadata import get_metadata
import os
from database_connect import insert_elements

def load_aggregation_list(file_path: str) -> List[Dict]:
    """Loads the list of data aggregations from a JSON file.

    Args:
        file_path (str): Path to the JSON file containing the list of data aggregations.

    Returns:
        List[Dict]: List of data aggregation dictionaries.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def fetch_data_series(dataseries_id: str) -> Dict:
    """Fetches data series based on the provided dataseries ID.

    Args:
        dataseries_id (str): The ID of the data series to fetch.

    Returns:
        Dict: The data series dictionary.
    """
    return return_data_series_json(dataseries_id)

def fetch_metadata(dataseries_id: str) -> Dict:
    """Fetches metadata for the given dataseries ID.

    Args:
        dataseries_id (str): The ID of the data series to fetch metadata for.

    Returns:
        Dict: The metadata dictionary.
    """
    return get_metadata(dataseries_id)

def create_mappings(metadata: Dict) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Creates mappings between series indices and element names.

    Args:
        metadata (Dict): The metadata dictionary.

    Returns:
        Tuple[Dict[str, str], Dict[str, str]]: Two dictionaries, one mapping indices to element names, and the other mapping element names to indices.
    """
    index_to_element = {}
    element_to_index = {}
    for series_name in metadata['Data']['records']['row']:
        index_to_element[series_name['seriesNo']] = series_name['rowText']
        element_to_index[series_name['rowText']] = series_name['seriesNo']
    return index_to_element, element_to_index

def generate_csv_names(aggregation_name: str, new_element_list: List[str], data_agg_dict: Dict) -> Dict[str, str]:
    """Generates CSV filenames and converts elements to CSV files.

    Args:
        aggregation_name (str): The internal name of the aggregation.
        new_element_list (List[str]): List of new element names.
        data_agg_dict (Dict): The data aggregation dictionary.

    Returns:
        Dict[str, str]: Dictionary mapping element names to their respective CSV filenames.
    """
    element_name_to_csv = {}
    for element in new_element_list:
        csv_name = aggregation_name.replace(' ', '_') + '_' + re.sub(r'_+', '_', element.replace(' ', '_').replace('-', ''))
        element_name_to_csv[element] = csv_name + '.csv'
        element_to_csv_convertor(csv_name, data_agg_dict[element])
    return element_name_to_csv

def map_aggregation_to_metadata(elements_list: List[str], index_to_element: Dict[str, str], 
                        element_to_index: Dict[str, str], element_name_to_csv: Dict[str, str], 
                        aggregation_name: str) -> None:
    """Maps CSV filenames to metadata and prints the metadata.

    Args:
        elements_list (List[str]): List of element names.
        index_to_element (Dict[str, str]): Dictionary mapping indices to element names.
        element_to_index (Dict[str, str]): Dictionary mapping element names to indices.
        element_name_to_csv (Dict[str, str]): Dictionary mapping element names to CSV filenames.
        aggregation_name (str): The internal name of the aggregation.
    """
    for element in elements_list:
        meta_data = find_metadata(element, index_to_element, element_to_index, element_name_to_csv, aggregation_name)
        file_path = element_name_to_csv[element]
        data_type = meta_data["data type"]
        seasonally_adjusted = meta_data["seasonally adjusted"]
        sector_level = meta_data["SectorLevel"]
        country = meta_data["Country"]
        sector_name = element
        parent = meta_data["parent_CSV"]
        frequency = meta_data["frequency"]
        insert_elements(file_path, data_type, seasonally_adjusted, sector_level, country, sector_name, parent, frequency)
        







def process_aggregation(aggregation: Dict) -> None:
    """Processes a single data aggregation.

    Args:
        aggregation (Dict): The data aggregation dictionary.
    """
    data_agg_dict = fetch_data_series(aggregation['dataseries_id'])
    metadata = fetch_metadata(aggregation['dataseries_id'])
    index_to_element, element_to_index = create_mappings(metadata)
    new_element_list = list(data_agg_dict.keys())
    element_name_to_csv = generate_csv_names(aggregation['internal_name'], new_element_list, data_agg_dict)
    elements_list = list(element_name_to_csv.keys())
    map_aggregation_to_metadata(elements_list, index_to_element, element_to_index, element_name_to_csv, aggregation['internal_name'])

def main():
    """Main function to load and process data aggregations."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'list_of_aggregations.json')
    data_aggregation_list = load_aggregation_list(file_path)
    for aggregation in data_aggregation_list:
        process_aggregation(aggregation)

if __name__ == "__main__":
    main()
