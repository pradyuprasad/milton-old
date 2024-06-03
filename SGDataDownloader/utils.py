from typing import *
from datetime import date
import csv
import re


def is_leap_year(year:int) -> bool:
   return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) 

def fix_dates(old_date: str, date_type: str) -> Optional[date]:
    """
    Converts a string date into a date object according to the specified frequency.

    Args:
        old_date: The original date string in the format "Year Period".
        date_type: The frequency of the data ("monthly" or "quarterly").

    Returns:
        A date object representing the last day of the given period.
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
    
    return date(new_year, month_int, date_int)

def fix_pair(pair: Dict[str, str], date_type: str) -> Dict[str, Any]:
    """
    Converts a dictionary containing a date and value pair into a dictionary with corrected types.

    Args:
        pair: A dictionary with 'key' and 'value' as strings.
        date_type: The frequency of the data ("monthly" or "quarterly").

    Returns:
        A dictionary with 'date' as a date object and 'value' as a float.
    """
    output = {"date": "", "value": ""}
    if 'key' in pair and 'value' in pair:
        output['date'] = fix_dates(pair['key'], date_type)
        output['value'] = float(pair['value'])
    return output

'''
take a series
take a prefix
convert that series to a csv
write that csv 
'''
def series_to_csv(prefix:str, series_name, series_data:Dict[str, Any]):
    new_data = list(map(lambda pair: fix_pair(pair, "quarterly"), series_data))
    print("old series name", series_name)
    new_series_name = re.sub(r'_+', '_', series_name.replace(' ', '_').replace('-', ''))
    file_name = prefix + '_' + new_series_name
    output_dir = '../data'
    print(file_name)
    with open(f'{output_dir}/{file_name}.csv', 'w', newline='') as f:
        colnames = ['date', 'value']
        writer = csv.DictWriter(f, fieldnames=colnames)
        writer.writeheader()
        for row in new_data:
            writer.writerow(row)
    return