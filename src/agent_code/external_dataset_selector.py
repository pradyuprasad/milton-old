from dotenv import load_dotenv
from typing import Dict, Any, List, Tuple, Union, Optional
from .models import Categories, TotalEconomyOrNot, UnemploymentLevels, GDP_sectors, SelectDatasetOutput, InflationSuperSectors, InflationSectors
from .utils import classify_query
import json
from itertools import chain
load_dotenv()


with open('src/agent_code/SubSectorGDP.json', 'r') as file:
    GDP_subsectors_mapping = json.load(file)

with open('src/agent_code/SubSectorCPI.json', 'r') as file:
    CPI_subsectors_mapping = json.load(file) 

GDP_subsectors = list((chain.from_iterable(GDP_subsectors_mapping.values())))
CPI_subsectors = list(chain.from_iterable(CPI_subsectors_mapping.values()))

def find_category(input_query: str) -> List[Tuple[str, str]]:
    return classify_query(query_text=input_query, candidate_labels=[category.value for category in Categories])

def check_whole_economy(input_query: str) -> List[Tuple[str, str]]:
    return classify_query(query_text=input_query, candidate_labels=[item.value for item in TotalEconomyOrNot])

def check_unemployment_level(query: str) -> List[Tuple[str, str]]:
    return classify_query(query_text=query, candidate_labels=[unemploy_type.value for unemploy_type in UnemploymentLevels])

def find_possible_GDP_sectors(query:str) -> List[Tuple[str, str]]:
    output = classify_query(query_text=query, candidate_labels=[sector.value for sector in GDP_sectors])
    return output

def select_possible_GDP_subsectors(query:str, subsectors_list:List[str] =GDP_subsectors) -> List[Tuple[str, str]]:
    output = classify_query(query_text=query, candidate_labels=subsectors_list)
    return output

def select_Inflation_SuperSector(query: str) -> List[Tuple[str, str]]:
    return classify_query(query_text=query, candidate_labels=[sector.value for sector in InflationSuperSectors])

def select_Inflation_sectors(query: str) -> List[Tuple[str, str]]:
    return classify_query(query_text=query, candidate_labels=[sector.value for sector in InflationSectors])


def inflation_subsector_step(query: str, Level1:Optional[List[str]]=None, L1Confidence:bool=False, 
dataType_confidence:bool = True, dataType:Categories = Categories.Inflation, Level2:Optional[List[str]]=None, L2Confidence:bool = False) -> SelectDatasetOutput:
    print("\n\nrunning sub sector step")
    Level3 = None 
    L3confidence = False
    subsectors_input = []
    if Level2:
        for sector in Level2:
            subsectors_input.extend(CPI_subsectors_mapping[sector])
    
    if len(subsectors_input) == 0:
        return SelectDatasetOutput(dataType=dataType, dataType_confidence=dataType_confidence, Level1=Level1, L1_confidence=L1Confidence, Level2=Level2, L2_confidence=L2Confidence)


    possible_subsectors = classify_query(query_text=query, candidate_labels=subsectors_input)
    confidences = list(map(lambda x: float(x[1]), possible_subsectors))
    if confidences[0] > 0.8 or confidences[0] - confidences[1] > 0.3:
        Level3 = [possible_subsectors[0][0]]
        L3confidence = True
    else:
        Level3 = list(map(lambda x: x[0], possible_subsectors))
        L3confidence = False
    
    return SelectDatasetOutput(dataType=dataType, dataType_confidence=dataType_confidence, Level1=Level1, L1_confidence=L1Confidence, Level2=Level2, L2_confidence=L2Confidence, Level3=Level3, L3_confidence=L3confidence)



def inflation_sector_step(query: str, Level1:Optional[List[str]]=None, L1Confidence:bool=False, 
dataType_confidence:bool = True, dataType:Categories = Categories.Inflation) -> SelectDatasetOutput:
    print("\n starting sector selection")
    Level2 = None
    L2confidence = False 
    possible_sectors = select_Inflation_sectors(query=query)
    confidences = list(map(lambda x: float(x[1]), possible_sectors))
    if confidences[0] > 0.8 or confidences[0] - confidences[1] > 0.3:
        Level2 = [possible_sectors[0][0]]
        L2confidence = True
    else:
        Level2 = list(map(lambda x: x[0], possible_sectors))
        L2confidence = False
    
    return inflation_subsector_step(query=query, Level1=Level1, L1Confidence=L1Confidence, Level2=Level2, L2Confidence=L2confidence)


 
    


def GDP_subsector_step(query: str, Level1:Optional[List[str]]=None, L1Confidence:bool=False, 
dataType_confidence:bool = True, dataType:Categories = Categories.GDP) -> SelectDatasetOutput:
    print("\n starting subsector selection")
    Level2 = None
    L2confidence = False 
    Level3 = None 
    L3confidence = False
    children = []
    if Level1 and L1Confidence:
        children = GDP_subsectors_mapping[Level1[0]]
    else:
        children = GDP_subsectors 

    
    if len(children) > 0:
        subsectors_possible = select_possible_GDP_subsectors(query, subsectors_list=children)
        confidences = list(map(lambda x: float(x[1]), subsectors_possible))

        if confidences[0] > 0.8 or (confidences[0] - confidences[1] > 0.3):
            Level2 = [subsectors_possible[0][0]]
            L2confidence = True
        else:
            Level2 = list(map(lambda x: x[0], subsectors_possible))
            L2confidence = False


    return SelectDatasetOutput(dataType=dataType, dataType_confidence=dataType_confidence, Level1=Level1, L1_confidence=L1Confidence, Level2=Level2, L2_confidence=L2confidence, Level3=Level3, L3_confidence=L3confidence)

        
       




def GDP_sector_step(query: str, dataType_confidence:bool = True, dataType:Categories = Categories.GDP) -> SelectDatasetOutput:
    print("\n starting sector selection")
    Level1 = None
    L1confidence=False
    # 1. run find_possible_GDP_sectors
    sectors_possible = find_possible_GDP_sectors(query)

    # are we confident about the sector?
    confidences = list(map(lambda x: float(x[1]), sectors_possible))
    if confidences[0] > 0.8 or (confidences[0] - confidences[1] > 0.3):
        Level1 = [sectors_possible[0][0]]
        L1confidence = True
    else:
        Level1 = list(map(lambda x: x[0], sectors_possible))
    
    return GDP_subsector_step(query, Level1=Level1, L1Confidence=L1confidence)
    
def inflation_super_sector(query: str) -> SelectDatasetOutput:
    Level1 = None
    L1confidence=False 

    supersectors_possible =  select_Inflation_SuperSector(query=query)
    confidences = list(map(lambda x: float(x[1]), supersectors_possible))
    if confidences[0] > 0.8 or (confidences[0] - confidences[1] > 0.3):
        Level1 = [supersectors_possible[0][0]]
        L1confidence = True
    else:
        Level1 = list(map(lambda x: x[0], supersectors_possible))

    return inflation_sector_step(query, Level1=Level1, L1Confidence=L1confidence)

    



        



def select_dataset(query: str) -> SelectDatasetOutput:
    outputDataType = None
    dataType_confidence = False
    Level1 = None
    L1confidence = True
    Level2 = None
    Level3 = None 
    category = find_category(query)
    
    if float(category[0][1]) < 0.4:
        print("unclear")
        print(category)
        dataType_confidence = False
    else:
        dataType_confidence = True
        outputDataType = category[0][0]
        if category[0][0] == Categories.GDP:
            print("The category is the GDP category")
            WhichLevel = check_whole_economy(input_query=query)
            if WhichLevel[0][0] == TotalEconomyOrNot.Sector_Specific:
               print("Sector specific")
               return GDP_sector_step(query=query, dataType_confidence=dataType_confidence)
            else:
                Level1 = ["Total GDP"]
                L1confidence = True
                return SelectDatasetOutput(dataType=Categories.GDP, dataType_confidence=dataType_confidence, Level1=Level1, L1_confidence = L1confidence)

         
        elif category[0][0] == Categories.Inflation:
            print("The category is inflation")
            WhichLevel = check_whole_economy(input_query=query)
            if WhichLevel[0][0] == TotalEconomyOrNot.Whole_Economy:
                return SelectDatasetOutput(dataType=Categories.Inflation, dataType_confidence=True, Level1=["Total Inflation"], L1_confidence= True)
            else:
                return inflation_super_sector(query)

        else:
            print("The category is Unemployment")
            uLevel = check_unemployment_level(query=query)
            dataType = Categories.Unemployment  
            L1confidence = True
            if uLevel[0][0] == UnemploymentLevels.Total_Unemployment:
                Level1 = ["Total Unemployment"]
                
                
            elif uLevel[0][0] == UnemploymentLevels.Citizen_Unemployment:
                Level1 = ["Citizen unemployment"]
            else:
                Level1 = ["Resident Unemployment"]
            
            return SelectDatasetOutput(dataType=dataType, Level1=Level1, L1_confidence=L1confidence)
    
    return SelectDatasetOutput(dataType_confidence=False)