from .classes import KVPair, DateValuePair, Frequency, KVPairList, DataType, Level, ProcessedMetaData
from datetime import date
from typing import Dict, Optional
import re

def is_leap_year(year: int) -> bool:
    """
    Determines if a given year is a leap year.

    Args:
        year (int): The year to check.

    Returns:
        bool: True if the year is a leap year, False otherwise.
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def fix_dates(old_date: str, date_type: Frequency) -> date:
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

def fix_pair(pair: KVPair, date_type: Frequency) -> DateValuePair:
    """
    Converts a dictionary containing a date and value pair into a dictionary with corrected types,
    adjusting the date string into a date object and the value into a float.

    Args:
        pair (Dict[str, str]): The dictionary containing 'key' (date) and 'value' as strings.
        date_type (str): The frequency of the data ("monthly" or "quarterly").

    Returns:
        Dict[str, Any]: A dictionary with 'date' as a date object and 'value' as a float.
    """
    outputDate: date = fix_dates(pair.key, date_type)
    outputValue: float = float(pair.value)
    return DateValuePair(date=outputDate, value=outputValue)

def make_csv_name(agg_internal_name: str, element:str) -> str:
    cleaned_aggregation_name = agg_internal_name.replace(' ', '_').replace('-', '').replace("'", "")
    cleaned_aggregation_name = re.sub(r'\(', '_', cleaned_aggregation_name)
    cleaned_aggregation_name = re.sub(r'\)', '_', cleaned_aggregation_name)
    element_name = element.replace(' ', '_').replace('-', '').replace("'", "")
    element_name = re.sub(r'\(', '_', element_name)
    element_name = re.sub(r'\)', '_', element_name)
    element_name = re.sub(r',', '', element_name)
    csv_name = cleaned_aggregation_name + '_' + element_name
    csv_name = re.sub(r'&', '_', csv_name)
    csv_name = re.sub(r'_+', '_', csv_name)
    csv_name += '.csv'
    return csv_name

    
def generate_elements_to_csv(agg_internal_name:str, element_to_valuesList: Dict[str, KVPairList]) -> Dict[str, str]:
    output: Dict[str, str] = {}
    for element in element_to_valuesList.keys():
        output[element] = make_csv_name(agg_internal_name, element)

    return output


def findType(agg_internal_name: str) -> DataType:
    if "GDP" in agg_internal_name:
        if "Real" in agg_internal_name or "real" in agg_internal_name:
           return DataType.Real_GDP 
        elif "Nominal" in agg_internal_name or "nominal" in agg_internal_name:
            return DataType.Nominal_GDP
        else:
            raise ValueError("Incorrect input!")
    elif "Consumer" in agg_internal_name:
        return DataType.Consumer_Price_Index
    elif "Unemployment" in agg_internal_name:
        return DataType.Unemployment
    else:
        raise ValueError("Incorrect input!")
    
def getLevel(seriesNo:str) -> Level:
    is_int = seriesNo.isdigit()
    count_dot = seriesNo.count('.')
    if is_int and count_dot == 0:
        return Level.TotalEconomy
    elif not is_int and count_dot == 1:
        return Level.SuperSector
    elif not is_int and count_dot == 2:
        return Level.Sector
    elif not is_int and count_dot == 3:
        return Level.SubSector
    else:
        raise ValueError("Wrong series number!")
    
def make_indexNo_to_element(metadata: ProcessedMetaData) -> Dict[str, str]:
    mapping = {}
    for element in metadata.Data.records.row:
        mapping[element.seriesNo] = element.rowText
    
    return mapping

def find_parent_index(indexNo: str) -> Optional[str]:
    last_dot_index = indexNo.rfind('.')
    if last_dot_index == -1:
        return None
    else:
        return indexNo[:last_dot_index]


def find_parent_csv(element: ProcessedMetaData.MetaDataDetails.MetaDataRecords.ElementMetaData, indexNo_to_elements: Dict[str, str], elements_to_csv: Dict[str, str]) ->  Optional[str]:
    parent_index = find_parent_index(element.seriesNo)
    if not parent_index:
        return None
    
    parent_name = indexNo_to_elements[parent_index]
    return elements_to_csv[parent_name]

