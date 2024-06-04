from typing import *
from datetime import date
import csv
import re
import os


def is_leap_year(year: int) -> bool:
    """
    Determines if a given year is a leap year.

    Args:
        year (int): The year to check.

    Returns:
        bool: True if the year is a leap year, False otherwise.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def fix_dates(old_date: str, date_type: str) -> Optional[date]:
    """
    Converts a string date into a date object according to the specified frequency
    (either 'monthly' or 'quarterly') by identifying the last day of the given period.

    Args:
        old_date (str): The original date string in the format "Year Period".
        date_type (str): The frequency of the data ("monthly" or "quarterly").

    Returns:
        Optional[date]: A date object representing the last day of the specified period,
                        or None if the input format is incorrect.
    """
    year, period = old_date.split()
    new_year: int = int(year)
    
    if date_type == "monthly":
        month_to_number = {
            "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
            "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
        }
        
        month_to_last_day = {
            "Jan": 31, "Feb": 29 if is_leap_year(new_year) else 28, "Mar": 31, "Apr": 30, "May": 31, "Jun": 30,
            "Jul": 31, "Aug": 31, "Sep": 30, "Oct": 31, "Nov": 30, "Dec": 31
        }
        month_int = month_to_number[period]
        date_int = month_to_last_day[period]
    elif date_type == "quarterly":
        quarter_to_number = {"1Q": 3, "2Q": 6, "3Q": 9, "4Q": 12}
        if period in ["1Q", "4Q"]:
            date_int = 31
        else:
            date_int = 30
        month_int = quarter_to_number[period]
    else:
        raise ValueError("Improper date formatting")
    
    return date(new_year, month_int, date_int)

def fix_pair(pair: Dict[str, str], date_type: str) -> Dict[str, Any]:
    """
    Converts a dictionary containing a date and value pair into a dictionary with corrected types,
    adjusting the date string into a date object and the value into a float.

    Args:
        pair (Dict[str, str]): The dictionary containing 'key' (date) and 'value' as strings.
        date_type (str): The frequency of the data ("monthly" or "quarterly").

    Returns:
        Dict[str, Any]: A dictionary with 'date' as a date object and 'value' as a float.
    """
    output = {"date": "", "value": ""}
    if 'key' in pair and 'value' in pair:
        output['date'] = fix_dates(pair['key'], date_type)
        output['value'] = float(pair['value'])
    return output

def element_to_csv_convertor(file_name: str, element_data: Dict[str, Any]) -> None:
    """
    Converts a series of data into a CSV file, determining the frequency of data points
    and writing to a file in a specified directory.

    Args:
        file_name (str): The name of the file to write, without extension.
        series_data (Dict[str, Any]): The dictionary containing the data to be written.

    Returns:
        None
    """
    frequency = "quarterly" if "GDP" in file_name or "Consumer" in file_name or "CPI" in file_name else "monthly"
    new_data = list(map(lambda pair: fix_pair(pair, frequency), element_data))
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    output_dir = '../data'
    print(file_name)
    with open(os.path.join(data_dir, f'{file_name}.csv'), 'w', newline='') as f:
        colnames = ['date', 'value']
        writer = csv.DictWriter(f, fieldnames=colnames)
        writer.writeheader()
        for row in new_data:
            writer.writerow(row)
    return



def find_parent_index(index: str) -> Optional[str]:
    """
    Finds the parent index of a given index by locating the last dot (.) and returning
    the substring up to this dot.

    Args:
        index (str): The index whose parent index needs to be found.

    Returns:
        Optional[str]: The parent index as a string, or None if no parent exists.
    """
    if "." in index:
        last_dot_index = index.rfind('.')
        return index[:last_dot_index]
    else:
        return None

def find_parent_csv(element_name: str, index_to_element: Dict[str, str], element_to_index: Dict[str, str], element_to_CSV: Dict[str, str]) -> Optional[str]:
    """
    Retrieves the parent CSV file name for a given dataset based on its index hierarchy.

    Args:
        element_name (str): The name of the dataset to find the parent for.
        index_to_element (Dict[str, str]): A mapping of index numbers to series names.
        element_to_index (Dict[str, str]): A mapping of series names to index numbers.
        element_to_CSV (Dict[str, str]): A mapping of series names to their corresponding CSV file names.

    Returns:
        Optional[str]: The name of the parent CSV file, or None if no parent exists.
    """
    index:str = element_to_index[element_name]
    parent_index:str = find_parent_index(index)
    if parent_index:
        return element_to_CSV[index_to_element[parent_index]]
    else:
        return None
    
def find_depth(index: str) -> str:
    """
    Determines the depth of the dataset within the hierarchy based on the number of dots in the index.

    Args:
        index (str): The index string to evaluate.

    Returns:
        str: The hierarchical level of the dataset ("TotalEconomy", "MajorSector", "Sector", "SubSector").
    """
    count = index.count('.')
    if count == 0:
        return "TotalEconomy"
    elif count == 1:
        return "MajorSector"
    elif count == 2:
        return "Sector"
    elif count == 3:
        return "SubSector"

def find_metadata(element_name: str, index_to_element: str, element_to_index: str, element_to_CSV: Dict[str, str], aggregation_name:str) -> Dict:
    """
    Constructs the metadata for a dataset, including the parent CSV, sector level, and basic identifiers
    like country and source.

    Args:
        element_name (str): The name of the dataset to find metadata for.
        index_to_element (Dict[str, str]): A mapping of index numbers to series names.
        element_to_index (Dict[str, str]): A mapping of series names to index numbers.
        element_to_CSV (Dict[str, str]): A mapping of series names to their corresponding CSV file names.

    Returns:
        Dict: A dictionary containing metadata information including parent CSV, sector level, name, country, and source.
    """
    parent_CSV = find_parent_csv(element_name, index_to_element, element_to_index, element_to_CSV)
    CSV_depth = find_depth(element_to_index[element_name])
    name_to_be_stored = element_name
    Country = "Singapore"
    Source = "SingStat"
    type_of_data = ""
    if "GDP" in aggregation_name:
        if "Real" in aggregation_name or "real" in aggregation_name:
            type_of_data = "Real_GDP"
        elif "Nominal" in aggregation_name or "nominal" in aggregation_name:
            type_of_data = "Nominal_GDP"

            
    seasonally_adjusted: bool = False
    if "adjusted" in aggregation_name or "Adjusted" in aggregation_name:
        seasonally_adjusted = True
    
    frequency = ""
    if "Quarterly" in aggregation_name or "quarterly" in aggregation_name:
        frequency = "quarterly"
    elif "Monthly" in aggregation_name or "monthly" in aggregation_name:
        frequency = "monthly"

    return {
        "parent_CSV": parent_CSV,
        "SectorLevel": CSV_depth,
        "name": name_to_be_stored, 
        "Country": Country, 
        "Source": Source,
        "data type": type_of_data ,
        "seasonally adjusted": seasonally_adjusted,
        "frequency": frequency
    }