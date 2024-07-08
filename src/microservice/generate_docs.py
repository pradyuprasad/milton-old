import requests
import json

# Set the base URL for the FastAPI application
BASE_URL = "http://0.0.0.0:10000"

def send_request(endpoint, description, data):
    """ Send a POST request to the specified endpoint with the provided data. """
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)
    return f"### {endpoint}\n**Description:**\n{description}\n**Output:**\n```json\n{response.json()}\n```\n\n"

def format_markdown(endpoint, description, data, response):
    """ Format the information into a Markdown-friendly string. """
    input_json = json.dumps(data, indent=2)  # Nicely format the input data as JSON
    response_json = json.dumps(response, indent=2)  # Format the response data as JSON
    return f"### {endpoint}\n**Description:**\n{description}\n**Input:**\n```json\n{input_json}\n```\n**Output:**\n```json\n{response_json}\n```\n\n"



def main():
    # Define endpoints, their descriptions, and sample inputs
    requests_info = [
        ("/select-dataset-external", "Selects an appropriate dataset based on a user's query.", {"query": "food inflation"}),
        ("/select-datapoints", "Fetches specific data points based on the user's query.", {"query": "unemployment rates in 2021"}),
        ("/select-datapoints-sector", "Fetches data points from a specific sector.", {"sector": "Manufacturing", "type": "GDP", "query": "YoY growth rate this year"}),
        ("/compare-between-specific-sectors", "Compares data between specified sectors.", {"sectors": ["Manufacturing", "Construction"], "type": "GDP", "query": "which grew more in 2023"}),
        ("/compare-all-sectors", "Compares data across all sectors for a specified type.", {"type": "GDP", "query": "which sector has highest growth rate in 2023?"}),
        ("/ask-anything", "Handles any type of query and tries to provide a relevant answer.", {"query": "How is the economy doing?"}),
        ("/whole-economy", "Analyzes data across the entire economy.", {"type": "GDP", "query": "overview of economic performance"})
    ]

    with open("api_output.md", "w") as file:
        for endpoint, description, data in requests_info:
            response = send_request(endpoint, description, data)  # Perform the API request
            markdown_output = format_markdown(endpoint=endpoint, description=description, data=data, response=response)  # Get formatted Markdown content
            print(markdown_output)
            file.write(markdown_output)


    # Create or open the Markdown file to write the output

if __name__ == "__main__":
    main()
