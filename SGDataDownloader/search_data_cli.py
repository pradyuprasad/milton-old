import requests
import sys

def search_for_dataset(keyword:str, search_option="all") -> None:
    possible_search_options = ["all", "title", "variable"]
    if search_option not in possible_search_options:
        raise ValueError("Search option must be one of ", possible_search_options)
    headers = {
    'accept': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    final_url = f"https://tablebuilder.singstat.gov.sg/api/table/resourceid?keyword={keyword}&searchoption={search_option}"

    response = requests.get(final_url, headers=headers)
    response.raise_for_status()
    response_json = response.json()
    records_to_print = sorted(response_json['Data']['records'], key = lambda x: x['id'])
    for dataset in records_to_print:
        print(dataset)

def main():
    if (len(sys.argv) < 2):
        raise ValueError("Please enter a keyword along with the python run command. For example: search_data_cli.py [keyword]")
    else:
        if (len(sys.argv) >= 3):
            search_for_dataset(sys.argv[1], sys.argv[2])
        else:
            search_for_dataset(sys.argv[1])

if __name__ == "__main__":
    main()