from pydantic import BaseModel
from enum import Enum
from typing import List, Optional
from ..download.classes import DateValuePair

class LlamaModel(str, Enum):
    LLAMA_3_70B = 'llama3-70b-8192'
    LLAMA_3_8B = 'llama3-8b-8192'

class Roles(str, Enum):
    system = 'system'
    user = 'user'
    assistant = 'assistant'

class SingleMessage(BaseModel):
    role: Roles
    content: str

    class Config:
        use_enum_values = True

class ModelInput(BaseModel):
    messages: List[SingleMessage]
    model: LlamaModel

    class Config:
        use_enum_values = True


class Categories(str, Enum):
    Inflation = 'Inflation and Consumer prices of goods and services or deflation'
    Unemployment = 'Unemployment and employment and jobs'
    GDP = 'Economic growth and sector growth'

class TotalEconomyOrNot(str, Enum):
    Whole_Economy = 'Referring to the whole total Economy in general'
    Sector_Specific = 'Referring to a specific industry and NOT the total economy'

class UnemploymentLevels(str, Enum):
    Total_Unemployment = 'Referring to total general unemployment in Singapore'
    Resident_Unemployment = 'Referring to unemployment for residents only'
    Citizen_Unemployment = 'Referring to unemployment for citizens only'

class GDP_sectors(str, Enum):
    MANUFACTURING = "Manufacturing"
    CONSTRUCTION = "Construction"
    UTILITIES = "Utilities"
    OTHER_GOODS_INDUSTRIES = "Other Goods Industries"
    WHOLESALE_RETAIL_TRADE = "Wholesale & Retail Trade"
    TRANSPORTATION_STORAGE = "Transportation & Storage"
    ACCOMMODATION_FOOD_SERVICES = "Accommodation & Food Services"
    INFORMATION_COMMUNICATIONS = "Information & Communications"
    FINANCE_INSURANCE = "Finance & Insurance"
    REAL_ESTATE_PROFESSIONAL_SERVICES = "Real Estate, Professional Services And Administrative & Support Services"
    OTHER_SERVICES_INDUSTRIES = "Other Services Industries"

class InflationSuperSectors(str, Enum):
    FOOD = "Food"
    FOOD_EXCL_FOOD_SERVING_SERVICES = "Food Excl Food Serving Services"
    FOOD_SERVING_SERVICES = "Food Serving Services"
    CLOTHING_FOOTWEAR = "Clothing & Footwear"
    HOUSING_UTILITIES = "Housing & Utilities"
    HOUSEHOLD_DURABLES_SERVICES = "Household Durables & Services"
    HEALTH_CARE = "Health Care"
    TRANSPORT = "Transport"
    COMMUNICATION = "Communication"
    RECREATION_CULTURE = "Recreation & Culture"
    EDUCATION = "Education"
    MISCELLANEOUS_GOODS_SERVICES = "Miscellaneous Goods & Services"

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


class SelectDatasetOutput(BaseModel):
    dataType: Optional[Categories] = None
    dataType_confidence: bool = True
    Level1: Optional[List[str]] = None
    L1_confidence: bool = False
    Level2: Optional[List[str]] = None
    L2_confidence: bool = False
    Level3: Optional[List[str]] = None
    L3_confidence: bool = False

    class Config:
        use_enum_values = True

class DatasetsToSend(BaseModel):
    exist: bool = True
    top_level: List[str] = []
    Sure: List[str] = []
    Unsure: List[str] = []


    

    

class SendData(BaseModel):
    Title: str
    Data: List[DateValuePair]
    Units: str

class SelectDataPointsOutput(BaseModel):
    working: bool
    answer: str
    data: List[SendData] = []
