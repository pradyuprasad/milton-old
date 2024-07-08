import json
from bs4 import BeautifulSoup

# Load the HTML content from the file
with open('popular.txt', 'r', encoding='utf-8') as file:
    html_content = file.read()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(html_content, 'html.parser')

# Function to extract series information
def extract_series_info(series_title_row, series_attr_row):
    title = series_title_row.find('a', class_='series-title').text.strip()
    series_id = series_attr_row.find('input')['value']
    details = {
        'title': title,
        'id': series_id
    }
    return details

# Find all series rows
series_rows = soup.find_all('tr', id='titleLink')

# Extract data for each series
series_data = []
for i in range(len(series_rows)):
    series_title_row = series_rows[i]
    series_attr_row = series_title_row.find_next_sibling('tr', class_='series-pager-attr')
    series_info = extract_series_info(series_title_row, series_attr_row)
    series_data.append(series_info)

# Count the number of series
series_count = len(series_data)

# Prepare the final JSON data with the count included
final_data = {
    'count': series_count,
    'series': series_data
}

# Convert the final data to JSON format
json_data = json.dumps(final_data, indent=4)
print(json_data)

# Save the JSON data to a file
with open('series_data_with_count.json', 'w', encoding='utf-8') as json_file:
    json_file.write(json_data)
