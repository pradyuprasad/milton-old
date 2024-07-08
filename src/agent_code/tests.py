from .external_dataset_selector import select_Inflation_SuperSector, select_Inflation_sectors, select_dataset
from .models import GDP_sectors, Categories, InflationSuperSectors
from ..download.database_operations import DatabaseConnection
from typing import Union


'''
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
    
    
    
    

'''

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
}

    


sector_values_tests = {
    "How is manufacturing GDP doing?": GDP_sectors.MANUFACTURING,
    "How is the construction industry doing?": GDP_sectors.CONSTRUCTION,
    "How is the electricity industry doing?" : GDP_sectors.UTILITIES,
    "How is the gas industry doing?": GDP_sectors.UTILITIES,
    "How is retail sales sector doing?": GDP_sectors.WHOLESALE_RETAIL_TRADE,
    "How is consumer spending doing?": GDP_sectors.WHOLESALE_RETAIL_TRADE,
    "How is wholesale trade going?": GDP_sectors.WHOLESALE_RETAIL_TRADE,
    "How is the transportation industry doing?": GDP_sectors.TRANSPORTATION_STORAGE,
    "How is the airline industry doing": GDP_sectors.TRANSPORTATION_STORAGE,
    "How is public transport doing?": GDP_sectors.TRANSPORTATION_STORAGE,
    "How is the ride hailing industry doing?": GDP_sectors.TRANSPORTATION_STORAGE,
    "How has the self storage industry done?": GDP_sectors.TRANSPORTATION_STORAGE,
    "How is the restaurant industry doing?": GDP_sectors.ACCOMMODATION_FOOD_SERVICES,
    "How is the accomodation industry doing": GDP_sectors.ACCOMMODATION_FOOD_SERVICES,
    "How is the IT industry doing?": GDP_sectors.INFORMATION_COMMUNICATIONS,
    "How is the telecom industry doing?": GDP_sectors.INFORMATION_COMMUNICATIONS,
    "How is the internet industry doing?": GDP_sectors.INFORMATION_COMMUNICATIONS,
    "How is the finance industry doing": GDP_sectors.FINANCE_INSURANCE,
    "How is the banking sector doing?": GDP_sectors.FINANCE_INSURANCE,
    "How is the insurance industry doing?": GDP_sectors.FINANCE_INSURANCE,
    "How is the real estate industry doing?": GDP_sectors.REAL_ESTATE_PROFESSIONAL_SERVICES,    
}

temp_tests = {
    "How is retail sales sector doing?": GDP_sectors.REAL_ESTATE_PROFESSIONAL_SERVICES,
}

'''

test_cases = [
    ("Current price of rice and bread", InflationSuperSectors.FOOD),
    ("Average cost of restaurant meals in New York", InflationSuperSectors.FOOD_SERVING_SERVICES),
    ("Price trend for men's suits and women's dresses", InflationSuperSectors.CLOTHING_FOOTWEAR),
    ("Monthly rent and utility bills analysis", InflationSuperSectors.HOUSING_UTILITIES),
    ("Cost of furnitures and cleaning services", InflationSuperSectors.HOUSEHOLD_DURABLES_SERVICES),
    ("Health insurance premiums for families", InflationSuperSectors.HEALTH_CARE),
    ("Gasoline prices this summer", InflationSuperSectors.TRANSPORT),
    ("Mobile phone plan costs in Europe", InflationSuperSectors.COMMUNICATION),
    ("Tickets prices for movies and concerts", InflationSuperSectors.RECREATION_CULTURE),
    ("Tuition fees for private universities", InflationSuperSectors.EDUCATION),
    ("Price check on jewelry and personal care items", InflationSuperSectors.MISCELLANEOUS_GOODS_SERVICES)
]



for item in test_cases:
    print(item[0])
    output:Union[str, int] = select_Inflation_SuperSector(item)
    if isinstance(output, int):
        print("ambiguous")
    else:
        print(output)
    
    print("\n")'''

query = 'Current price of rice and bread'
print(select_dataset("What are the prices for doctors?"))
