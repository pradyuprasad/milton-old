from enum import Enum
import instructor
import os
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()
from typing import Type, Literal
from .models import LlamaModel
import time
from groq import Groq
client = Groq(
    api_key=os.environ.get('GROQ_API_KEY'),
)
client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)
#client = instructor.from_openai(OpenAI())
# Define new Enum class for multiple labels
class InflationSectors(str, Enum):
    BREAD_CEREALS = "Bread & Cereals"
    MEAT = "Meat"
    FISH_SEAFOOD = "Fish & Seafood"
    MILK_CHEESE_EGGS = "Milk, Cheese & Eggs"
    OILS_FATS = "Oils & Fats"
    FRUITS = "Fruits"
    VEGETABLES = "Vegetables"
    SUGAR_PRESERVES_CONFECTIONERY = "Sugar, Preserves & Confectionery"
    NON_ALCOHOLIC_BEVERAGES = "Non-Alcoholic Beverages"
    OTHER_FOOD = "Other Food"
    RESTAURANT_FOOD = "Restaurant Food"
    FAST_FOOD = "Fast Food"
    HAWKER_FOOD = "Hawker Food"
    CATERED_FOOD = "Catered Food"
    CLOTHING = "Clothing"
    OTHER_ARTICLES_RELATED_SERVICES = "Other Articles & Related Services"
    FOOTWEAR = "Footwear"
    ACCOMMODATION = "Accommodation"
    UTILITIES_OTHER_FUELS = "Utilities & Other Fuels"
    HOUSEHOLD_DURABLES = "Household Durables"
    HOUSEHOLD_SERVICES_SUPPLIES = "Household Services & Supplies"
    MEDICINES_HEALTH_PRODUCTS = "Medicines & Health Products"
    OUTPATIENT_SERVICES = "Outpatient Services"
    HOSPITAL_SERVICES = "Hospital Services"
    HEALTH_INSURANCE = "Health Insurance"
    PRIVATE_TRANSPORT = "Private Transport"
    PUBLIC_TRANSPORT = "Public Transport"
    OTHER_TRANSPORT_SERVICES = "Other Transport Services"
    POSTAGE_COURIER_SERVICES = "Postage & Courier Services"
    TELECOMMUNICATION_EQUIPMENT = "Telecommunication Equipment"
    TELECOMMUNICATION_SERVICES = "Telecommunication Services"
    RECREATIONAL_CULTURAL_GOODS = "Recreational & Cultural Goods"
    RECREATIONAL_CULTURAL_SERVICES = "Recreational & Cultural Services"
    NEWSPAPERS_BOOKS_STATIONERY = "Newspapers, Books & Stationery"
    HOLIDAY_EXPENSES = "Holiday Expenses"
    TUITION_OTHER_FEES = "Tuition & Other Fees"
    TEXTBOOKS_STUDY_GUIDES = "Textbooks & Study Guides"
    PERSONAL_CARE = "Personal Care"
    ALCOHOLIC_DRINKS_TOBACCO = "Alcoholic Drinks & Tobacco"
    PERSONAL_EFFECTS = "Personal Effects"
    SOCIAL_SERVICES = "Social Services"
    OTHER_MISCELLANEOUS_SERVICES = "Other Miscellaneous Services"

def add_unsure_member(enum_class: Type[Enum]) -> Type[Enum]:
    # Create a new enum with the same members as the existing one plus 'UNSURE'
    new_members = {name: member.value for name, member in enum_class.__members__.items()}
    new_members['UNSURE'] = "Unsure"
    return Enum(enum_class.__name__, new_members)

all_inf = add_unsure_member(InflationSectors)

# Adjust the prediction model to accommodate a list of labels
class MultiClassPrediction(BaseModel):
    predicted_labels: list[all_inf] # type: ignore

# Modify the classify function
def multi_classify(data: str) -> MultiClassPrediction:
    return client.chat.completions.create(
        model=LlamaModel.LLAMA_3_70B,
        response_model=MultiClassPrediction,
        messages=[
            {
                "role": "user",
                "content": f"Classify the following query: {data}",
            },
        ],
    )  # type: ignore


test_cases = {  
    "Inflation rates for consumer goods": "Sector Inflation",
    "Detailed unemployment rates by citizenship": "Citizen Unemployment",
    "How have food prices gone up?": "Sector Inflation",
    "GDP growth in 2022": "Main GDP",
    "Inflation rate for 2022": "Main Inflation",
    "Quarterly GDP change for small sectors": "Sector GDP",
    "Unemployment rates in 2022": "Total Unemployment",
    "Resident unemployment rates last year": "Resident Unemployment",
    "Citizen unemployment rate update": "Citizen Unemployment",
    "GDP by sector for agriculture": "Sector GDP",
    "OOga booga": ""
}

print("test case is?")
case = input()
start = time.time()
output = multi_classify(data=case)
print(len(output.predicted_labels)) 
print(output.predicted_labels)
print("time taken = ", time.time() - start, " seconds")