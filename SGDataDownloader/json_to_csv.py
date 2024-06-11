from .classes import KVPairList, DateValuePairList, Aggregation, Frequency
import csv
from .utils import fix_pair, make_csv_name
import os
from typing import Dict
import re

def json_to_csv(agg: Aggregation, data_dir:str, data_json:Dict[str, KVPairList]) -> None:
    cleaned_aggregation_name = agg.InternalName.replace(' ', '_').replace('-', '').replace("'", "")
    cleaned_aggregation_name = re.sub(r'\(', '_', cleaned_aggregation_name)
    cleaned_aggregation_name = re.sub(r'\)', '_', cleaned_aggregation_name)
    frequency:Frequency = Frequency.MONTHLY
    if "Monthly" in agg.InternalName or "monthly" in agg.InternalName:
        frequency = Frequency.MONTHLY
    elif "quarterly" in agg.InternalName or "Quarterly" in agg.InternalName:
        frequency = Frequency.QUARTERLY
    else:
        raise ValueError("Wrong frequency type")
    

    for element in data_json:
        csv_name = make_csv_name(agg.InternalName, element=element)
        #print(csv_name)
        write_to_csv(data_dir=data_dir, csv_name=csv_name, data=data_json[element], date_type=frequency)

def write_to_csv(data_dir:str, csv_name:str, data:KVPairList, date_type:Frequency) -> None:
    print()
    ListToWrite: DateValuePairList = list(map(lambda x: fix_pair(x, date_type), data))
    csv_path = os.path.join(data_dir, csv_name)
    with open(csv_path, mode='w', newline='') as file:
        colnames = ['date', 'value']
        writer = csv.writer(file)
        writer.writerow(colnames)
        for pair in ListToWrite:
            writer.writerow([pair.date, pair.value])