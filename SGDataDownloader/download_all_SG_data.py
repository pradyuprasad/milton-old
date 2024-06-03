import json
from download_dataseries import return_data_series_json
from utils import series_to_csv
def main():
    file_path = "list_of_dataseries.json"
    with open(file_path, 'r') as file:
        dataseries_list = json.load(file)
    for series in dataseries_list:
        output = return_data_series_json(series['dataseries_id'])
        new_dataset_list = list(output.keys())
        print(len(new_dataset_list))
        for i in range(len(new_dataset_list)):
            series_to_csv(series["internal_name"].replace(' ', '_'), new_dataset_list[i], output[new_dataset_list[i]])

    return

main()