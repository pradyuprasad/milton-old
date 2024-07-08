from .external_dataset_selector import select_dataset
from .models import SelectDatasetOutput, Categories, DatasetsToSend
from ..download.database_operations import DatabaseConnection
from .utils import convert_SQL_answer_to_list
from typing import Optional, Any
category_map = {
    Categories.Inflation: ('Consumer_Price_Index', 0),
    Categories.GDP: ('REAL_GDP', 1),  
    Categories.Unemployment: ('Unemployment', 1)
}

def escape_single_quotes(value: str) -> str:
    """Escapes single quotes in a string for SQL statements."""
    return value.replace("'", "''")

DB:Optional[Any] = DatabaseConnection().get_connection()
if not DB:
    raise Exception("No DB found")


def get_CSV_from_element_name(element_name: str, category: Categories):
    """
    Retrieves CSV file paths for a given element name and category from the database using a SQL query.
    Args:
    element_name (str): The name of the element to retrieve datasets for.
    category (Categories): The category of the data.
    Returns:
    list: A list of CSV file paths corresponding to the element name and category.
    """
    new_elem_name = escape_single_quotes(element_name)
    dataType, seasonally_adjusted = category_map[category]
    query = f"SELECT filePath FROM datasets WHERE dataType = '{dataType}' AND seasonally_adjusted = '{seasonally_adjusted}' AND ElementName = '{new_elem_name}'"
    print(query)
    return convert_SQL_answer_to_list(DB.execute(query).fetchall())




def return_datasets(query: str) -> DatasetsToSend:
    """
    Processes a query to select appropriate datasets and classifies them into 'sure' and 'unsure' based on confidence levels.
    Args:
    query (str): The query string used to determine relevant datasets.
    Returns:
    DatasetsToSend: An object containing lists of 'sure' and 'unsure' datasets, or a status indicating no datasets exist.
    """
    output_from_model = select_dataset(query=query)
    print(output_from_model)
    if not output_from_model.dataType_confidence:
        return DatasetsToSend(exist=False)  # No datasets exist if dataType confidence is missing

    dataType, seasonally_adjusted = category_map[output_from_model.dataType]
    top_level = convert_SQL_answer_to_list(DB.execute(f"SELECT filePath FROM datasets WHERE dataType = '{dataType}' AND seasonally_adjusted = '{seasonally_adjusted}' AND level = 'TotalEconomy'").fetchall())
    print(top_level)  # Debugging output to check top-level datasets

    sure, unsure = [], []
    
    # Handle dataset levels based on confidence and number of elements in lists
    for level_suffix in ['1', '2', '3']:
        level = f"Level{level_suffix}"
        confidence_attr = f"L{level_suffix}_confidence"
        element_names = getattr(output_from_model, level)
        confidence = getattr(output_from_model, confidence_attr)
        
        # Check if there's confidence and adjust dataset list handling accordingly
        if confidence:
            # Assuming that when confident, there's only one relevant dataset
            if element_names:
                dataset = get_CSV_from_element_name(element_names[0], output_from_model.dataType)
                print(dataset)
                sure.extend(dataset)
        else:
            # Handle cases where there may be multiple datasets (up to three)
            if element_names:
                for name in element_names:
                    dataset = get_CSV_from_element_name(name, output_from_model.dataType)
                    unsure.extend(dataset)
    print("sure is", sure)
    return DatasetsToSend(top_level=top_level, Sure=sure, Unsure=unsure)


        

    

if __name__ == "__main__":
    print("whats ur query")
    q = input()
    output = (return_datasets(q))
    print(output)