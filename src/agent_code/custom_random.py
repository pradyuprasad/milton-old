import json
from enum import Enum
import os
current_dir:str = os.path.dirname(os.path.abspath(__file__))
subsector_path = os.path.join(current_dir, 'SubSectorGDP.json')


# Load the JSON data
with open(subsector_path, 'r') as file:
    industries_data = json.load(file)

# Function to create GDP_enums dynamically
def create_enum(name, items):
    return Enum(name, {item.replace(" ", "_").replace("&", "AND").upper(): item for item in items})

# Dictionary to hold the dynamically created GDP_enums
GDP_enums = {}

# Loop through the JSON data and create GDP_enums
for category, items in industries_data.items():
    if items:  # Skip if the list is empty
        enum_name = category.replace(" ", "").replace("&", "AND")
        GDP_enums[enum_name] = create_enum(enum_name, items)


for enum_name, enum_class in GDP_enums.items():
    print(f"Enum: {enum_name}")
    for item in enum_class:
        print(f"  {item.name} = {item.value}")
