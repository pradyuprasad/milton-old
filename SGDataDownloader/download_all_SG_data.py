import json
from download_dataseries import return_data_series_json
def main():
    file_path = "list_of_dataseries.json"
    with open(file_path, 'r') as file:
        dataseries_list = json.load(file)
    for series in dataseries_list:
        output = return_data_series_json(series['dataseries_id'])
        print(output)
    return

main()